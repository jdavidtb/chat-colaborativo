"""
Manejadores de mensajes del servidor.

Patrón: Strategy - Diferentes estrategias para manejar distintos tipos de mensajes
Patrón: Chain of Responsibility - Cadena de manejadores
Principio SOLID:
    - Single Responsibility: Cada handler maneja un tipo de mensaje
    - Open/Closed: Fácil agregar nuevos handlers
    - Dependency Inversion: Depende de abstracciones
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, TYPE_CHECKING
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.protocol import Message, MessageType, MessageFactory

if TYPE_CHECKING:
    from ..server import ChatServer
    from ..models import User


class MessageHandler(ABC):
    """
    Clase base abstracta para manejadores de mensajes.
    Patrón: Strategy
    """
    
    @abstractmethod
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        """
        Maneja un mensaje recibido.
        
        Args:
            server: Instancia del servidor
            user: Usuario que envió el mensaje
            message: Mensaje a procesar
        """
        pass


class ConnectHandler(MessageHandler):
    """Manejador para mensajes de conexión."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        # La conexión ya está manejada en el servidor
        pass


class CreateRoomHandler(MessageHandler):
    """Manejador para crear salas."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        room_name = message.payload.get("room_name", "").strip()
        
        if not room_name:
            error = MessageFactory.create_error("El nombre de la sala no puede estar vacío")
            await user.send_message(error.to_json())
            return
        
        if len(room_name) > 50:
            error = MessageFactory.create_error("El nombre de la sala es demasiado largo (máx. 50 caracteres)")
            await user.send_message(error.to_json())
            return
        
        # Crear la sala y unir al usuario en una operación
        success = await server.create_room_and_join(room_name, user)
        
        if not success:
            error = MessageFactory.create_error(f"La sala '{room_name}' ya existe")
            await user.send_message(error.to_json())


class JoinRoomHandler(MessageHandler):
    """Manejador para unirse a salas."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        room_name = message.payload.get("room_name", "").strip()
        
        if not room_name:
            error = MessageFactory.create_error("Debe especificar el nombre de la sala")
            await user.send_message(error.to_json())
            return
        
        await server.join_room(user, room_name)


class LeaveRoomHandler(MessageHandler):
    """Manejador para abandonar salas."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        room_name = message.payload.get("room_name")
        
        if room_name:
            await server.leave_room(user, room_name)
        elif user.current_room:
            await server.leave_room(user, user.current_room)


class ListRoomsHandler(MessageHandler):
    """Manejador para listar salas."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        rooms_info = server.get_rooms_info()
        response = MessageFactory.create_rooms_list(rooms_info)
        await user.send_message(response.to_json())


class ChatMessageHandler(MessageHandler):
    """Manejador para mensajes de chat."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        content = message.payload.get("content", "").strip()
        room_name = message.payload.get("room_name") or user.current_room
        
        if not content:
            return  # Ignorar mensajes vacíos
        
        if not room_name:
            error = MessageFactory.create_error("No estás en ninguna sala")
            await user.send_message(error.to_json())
            return
        
        await server.broadcast_message(user, room_name, content)


class DisconnectHandler(MessageHandler):
    """Manejador para desconexiones."""
    
    async def handle(self, server: 'ChatServer', user: 'User', message: Message) -> None:
        await server.disconnect_user(user)


class MessageHandlerRegistry:
    """
    Registro de manejadores de mensajes.
    Patrón: Registry/Strategy
    Principio SOLID: Open/Closed - Fácil agregar nuevos manejadores
    """
    
    def __init__(self):
        self._handlers: Dict[MessageType, MessageHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Registra los manejadores por defecto."""
        self.register(MessageType.CONNECT, ConnectHandler())
        self.register(MessageType.CREATE_ROOM, CreateRoomHandler())
        self.register(MessageType.JOIN_ROOM, JoinRoomHandler())
        self.register(MessageType.LEAVE_ROOM, LeaveRoomHandler())
        self.register(MessageType.LIST_ROOMS, ListRoomsHandler())
        self.register(MessageType.CHAT_MESSAGE, ChatMessageHandler())
        self.register(MessageType.DISCONNECT, DisconnectHandler())
    
    def register(self, message_type: MessageType, handler: MessageHandler) -> None:
        """
        Registra un manejador para un tipo de mensaje.
        
        Args:
            message_type: Tipo de mensaje a manejar
            handler: Instancia del manejador
        """
        self._handlers[message_type] = handler
    
    def get_handler(self, message_type: MessageType) -> Optional[MessageHandler]:
        """
        Obtiene el manejador para un tipo de mensaje.
        
        Args:
            message_type: Tipo de mensaje
            
        Returns:
            Manejador correspondiente o None
        """
        return self._handlers.get(message_type)
    
    async def handle_message(self, server: 'ChatServer', user: 'User', message: Message) -> bool:
        """
        Procesa un mensaje usando el manejador apropiado.
        
        Args:
            server: Instancia del servidor
            user: Usuario que envió el mensaje
            message: Mensaje a procesar
            
        Returns:
            True si se procesó correctamente, False si no hay manejador
        """
        handler = self.get_handler(message.type)
        
        if handler:
            await handler.handle(server, user, message)
            return True
        
        return False