"""
Servidor principal del Chat Colaborativo.

Patrones aplicados:
    - Singleton: Una única instancia del servidor
    - Observer: Notificación de eventos a usuarios
    - Factory: Creación de mensajes
    - Strategy: Manejo de diferentes tipos de mensajes

Principios SOLID:
    - Single Responsibility: El servidor coordina, los handlers procesan
    - Open/Closed: Fácil extender con nuevos handlers
    - Dependency Inversion: Depende de abstracciones (MessageHandler)
"""

import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Dict, Set, Optional, List
import json
import sys
import os
import socket

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Message, MessageType, MessageFactory
from server.models import User, Room
from server.handlers import MessageHandlerRegistry
from server.utils import get_logger


class ChatServer:
    """
    Servidor de chat colaborativo con soporte para salas temáticas.
    Patrón: Singleton
    """
    _instance: Optional['ChatServer'] = None
    
    def __new__(cls, *args, **kwargs) -> 'ChatServer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        if self._initialized:
            return
        
        self.host = host
        self.port = port
        self._users: Dict[str, User] = {}  # user_id -> User
        self._rooms: Dict[str, Room] = {}  # room_name -> Room
        self._websocket_to_user: Dict[WebSocketServerProtocol, User] = {}
        self._handler_registry = MessageHandlerRegistry()
        self._logger = get_logger()
        self._lock = asyncio.Lock()
        self._initialized = True
        
        # Crear sala por defecto
        self._rooms["General"] = Room(name="General", created_by="Sistema")
        self._logger.room_created("General", "Sistema")
    
    @property
    def user_count(self) -> int:
        """Retorna el número de usuarios conectados."""
        return len(self._users)
    
    @property
    def room_count(self) -> int:
        """Retorna el número de salas activas."""
        return len(self._rooms)
    
    def get_rooms_info(self) -> List[dict]:
        """Retorna información de todas las salas."""
        return [room.to_dict() for room in self._rooms.values()]
    
    def get_room(self, room_name: str) -> Optional[Room]:
        """Obtiene una sala por nombre."""
        return self._rooms.get(room_name)
    
    async def create_room(self, room_name: str, creator: User) -> bool:
        """
        Crea una nueva sala de chat.
        
        Args:
            room_name: Nombre de la sala
            creator: Usuario que crea la sala
            
        Returns:
            True si se creó, False si ya existe
        """
        async with self._lock:
            if room_name in self._rooms:
                return False
            
            room = Room(name=room_name, created_by=creator.username)
            self._rooms[room_name] = room
            self._logger.room_created(room_name, creator.username)
            
            # Notificar a todos los usuarios sobre la nueva sala
            system_msg = MessageFactory.create_system_message(
                f"Se ha creado la sala '{room_name}'"
            )
            await self._broadcast_to_all(system_msg.to_json())
            
            return True
    
    async def create_room_and_join(self, room_name: str, creator: User) -> bool:
        """
        Crea una nueva sala y une al creador en una operación atómica.
        
        Args:
            room_name: Nombre de la sala
            creator: Usuario que crea la sala
            
        Returns:
            True si se creó y unió, False si ya existe
        """
        # Si el usuario está en otra sala, salir primero
        if creator.current_room:
            await self.leave_room(creator, creator.current_room)
        
        async with self._lock:
            if room_name in self._rooms:
                return False
            
            # Crear sala y agregar usuario inmediatamente
            room = Room(name=room_name, created_by=creator.username)
            room.add_user(creator)
            self._rooms[room_name] = room
            
            self._logger.room_created(room_name, creator.username)
            self._logger.user_joined_room(creator.username, room_name)
        
        # Notificar a todos sobre la nueva sala
        system_msg = MessageFactory.create_system_message(
            f"Se ha creado la sala '{room_name}'"
        )
        await self._broadcast_to_all(system_msg.to_json())
        
        # Actualizar lista de salas para todos
        rooms_list = MessageFactory.create_rooms_list(self.get_rooms_info())
        await self._broadcast_to_all(rooms_list.to_json())
        
        # Enviar confirmación al creador
        users_msg = MessageFactory.create_room_users(room_name, room.usernames)
        await creator.send_message(users_msg.to_json())
        
        welcome = MessageFactory.create_system_message(
            f"Has creado y te has unido a la sala '{room_name}'",
            room_name
        )
        await creator.send_message(welcome.to_json())
        
        return True
    
    async def delete_room(self, room_name: str) -> bool:
        """
        Elimina una sala vacía (excepto General).
        
        Args:
            room_name: Nombre de la sala a eliminar
            
        Returns:
            True si se eliminó, False si no se pudo
        """
        if room_name == "General":
            return False
        
        async with self._lock:
            room = self._rooms.get(room_name)
            if room and room.is_empty:
                del self._rooms[room_name]
                self._logger.room_deleted(room_name)
                
                # Notificar a todos los clientes la lista actualizada
                rooms_list = MessageFactory.create_rooms_list(self.get_rooms_info())
                await self._broadcast_to_all(rooms_list.to_json())
                
                return True
            return False
    
    async def join_room(self, user: User, room_name: str) -> bool:
        """
        Une a un usuario a una sala.
        
        Args:
            user: Usuario a unir
            room_name: Nombre de la sala
            
        Returns:
            True si se unió correctamente
        """
        # Si el usuario ya está en una sala, salir primero
        if user.current_room and user.current_room != room_name:
            await self.leave_room(user, user.current_room)
        
        room = self._rooms.get(room_name)
        if not room:
            error = MessageFactory.create_error(f"La sala '{room_name}' no existe")
            await user.send_message(error.to_json())
            return False
        
        if room.add_user(user):
            self._logger.user_joined_room(user.username, room_name)
            
            # Notificar a los demás usuarios de la sala
            notification = MessageFactory.create_user_joined(user.username, room_name)
            await room.broadcast(notification.to_json(), exclude=user)
            
            # Enviar lista de usuarios actualizada a TODOS en la sala (incluido el nuevo)
            users_msg = MessageFactory.create_room_users(room_name, room.usernames)
            await room.broadcast(users_msg.to_json())
            
            # Enviar mensaje de sistema al usuario
            welcome = MessageFactory.create_system_message(
                f"Te has unido a la sala '{room_name}'",
                room_name
            )
            await user.send_message(welcome.to_json())
            
            # Actualizar lista de salas para todos (muestra conteo actualizado)
            rooms_list = MessageFactory.create_rooms_list(self.get_rooms_info())
            await self._broadcast_to_all(rooms_list.to_json())
            
            return True
        
        return False
    
    async def leave_room(self, user: User, room_name: str) -> bool:
        """
        Remueve a un usuario de una sala.
        
        Args:
            user: Usuario a remover
            room_name: Nombre de la sala
            
        Returns:
            True si se removió correctamente
        """
        room = self._rooms.get(room_name)
        if not room:
            return False
        
        if room.remove_user(user):
            self._logger.user_left_room(user.username, room_name)
            
            # Notificar a los demás usuarios
            notification = MessageFactory.create_user_left(user.username, room_name)
            await room.broadcast(notification.to_json())
            
            # Enviar lista de usuarios actualizada a los que quedan en la sala
            if not room.is_empty:
                users_msg = MessageFactory.create_room_users(room_name, room.usernames)
                await room.broadcast(users_msg.to_json())
            
            # Eliminar sala si está vacía (excepto General)
            if room.is_empty and room_name != "General":
                await self.delete_room(room_name)
            else:
                # Actualizar lista de salas para todos
                rooms_list = MessageFactory.create_rooms_list(self.get_rooms_info())
                await self._broadcast_to_all(rooms_list.to_json())
            
            return True
        
        return False
    
    async def broadcast_message(self, user: User, room_name: str, content: str) -> bool:
        """
        Envía un mensaje a todos los usuarios de una sala.
        
        Args:
            user: Usuario que envía el mensaje
            room_name: Nombre de la sala
            content: Contenido del mensaje
            
        Returns:
            True si se envió correctamente
        """
        room = self._rooms.get(room_name)
        if not room:
            return False
        
        if not room.has_user(user):
            error = MessageFactory.create_error("No estás en esta sala")
            await user.send_message(error.to_json())
            return False
        
        # Guardar en historial
        room.add_message_to_history(user.username, content)
        
        # Crear y enviar mensaje
        chat_msg = MessageFactory.create_chat_message(user.username, room_name, content)
        await room.broadcast(chat_msg.to_json())
        
        self._logger.message_sent(user.username, room_name)
        return True
    
    async def _broadcast_to_all(self, message: str) -> None:
        """Envía un mensaje a todos los usuarios conectados."""
        tasks = [user.send_message(message) for user in self._users.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def register_user(self, websocket: WebSocketServerProtocol, username: str) -> Optional[User]:
        """
        Registra un nuevo usuario en el servidor.
        
        Args:
            websocket: Conexión websocket del usuario
            username: Nombre de usuario
            
        Returns:
            Usuario creado o None si el nombre ya existe
        """
        # Validar nombre de usuario
        username = username.strip()
        if not username:
            return None
        
        if len(username) > 30:
            return None
        
        # Verificar si el nombre ya está en uso
        async with self._lock:
            for existing_user in self._users.values():
                if existing_user.username.lower() == username.lower():
                    return None
            
            # Crear nuevo usuario
            user = User(username=username, websocket=websocket)
            self._users[user.user_id] = user
            self._websocket_to_user[websocket] = user
            
            # Obtener IP del cliente
            try:
                client_ip = websocket.remote_address[0]
            except:
                client_ip = "unknown"
            
            self._logger.user_connected(username, client_ip)
            
            return user
    
    async def disconnect_user(self, user: User) -> None:
        """
        Desconecta a un usuario del servidor.
        
        Args:
            user: Usuario a desconectar
        """
        # Salir de la sala actual
        if user.current_room:
            await self.leave_room(user, user.current_room)
        
        # Remover del servidor
        async with self._lock:
            self._users.pop(user.user_id, None)
            self._websocket_to_user.pop(user.websocket, None)
        
        self._logger.user_disconnected(user.username)
    
    async def handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """
        Maneja una conexión de websocket entrante.
        
        Args:
            websocket: Conexión websocket
        """
        user: Optional[User] = None
        
        try:
            # Esperar mensaje de conexión con nombre de usuario
            async for raw_message in websocket:
                try:
                    message = Message.from_json(raw_message)
                    
                    # Primer mensaje debe ser de conexión
                    if user is None:
                        if message.type != MessageType.CONNECT:
                            error = MessageFactory.create_connection_error(
                                "Primer mensaje debe ser de conexión"
                            )
                            await websocket.send(error.to_json())
                            continue
                        
                        username = message.payload.get("username", "")
                        user = await self.register_user(websocket, username)
                        
                        if user is None:
                            error = MessageFactory.create_connection_error(
                                "Nombre de usuario inválido o ya en uso"
                            )
                            await websocket.send(error.to_json())
                            continue
                        
                        # Enviar confirmación
                        ack = MessageFactory.create_connection_ack(user.username, user.user_id)
                        await websocket.send(ack.to_json())
                        
                        # Enviar lista de salas
                        rooms_list = MessageFactory.create_rooms_list(self.get_rooms_info())
                        await websocket.send(rooms_list.to_json())
                        
                        continue
                    
                    # Procesar otros mensajes
                    await self._handler_registry.handle_message(self, user, message)
                    
                except json.JSONDecodeError:
                    self._logger.warning(f"Mensaje JSON inválido recibido")
                except Exception as e:
                    self._logger.error(f"Error procesando mensaje: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if user:
                await self.disconnect_user(user)
    
    def get_local_ip(self) -> str:
        """Obtiene la IP local del servidor."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def start(self) -> None:
        """Inicia el servidor de chat."""
        local_ip = self.get_local_ip()
        
        print("=" * 60)
        print("   SERVIDOR DE CHAT COLABORATIVO")
        print("=" * 60)
        print(f"\n🚀 Servidor iniciado en:")
        print(f"   - Local:     ws://localhost:{self.port}")
        print(f"   - Red:       ws://{local_ip}:{self.port}")
        print(f"\n📋 Para conectarse desde otro dispositivo en la red,")
        print(f"   usa la dirección: ws://{local_ip}:{self.port}")
        print("\n" + "=" * 60)
        print("Presiona Ctrl+C para detener el servidor")
        print("=" * 60 + "\n")
        
        self._logger.info(f"Servidor escuchando en {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_connection,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10
        ):
            await asyncio.Future()  # Ejecutar indefinidamente


def main():
    """Punto de entrada del servidor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Servidor de Chat Colaborativo")
    parser.add_argument("--host", default="0.0.0.0", help="Host del servidor")
    parser.add_argument("--port", type=int, default=8765, help="Puerto del servidor")
    args = parser.parse_args()
    
    server = ChatServer(host=args.host, port=args.port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")


if __name__ == "__main__":
    main()