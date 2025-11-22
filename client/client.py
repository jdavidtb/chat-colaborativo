"""
Cliente de Chat Colaborativo.

Integra la comunicación WebSocket con la interfaz gráfica.

Patrones:
    - Observer: Recibe notificaciones del servidor
    - Adapter: Adapta mensajes del servidor a la GUI
    
Principios SOLID:
    - Single Responsibility: Maneja solo la lógica del cliente
    - Dependency Inversion: Depende de abstracciones (GUI, Protocol)
"""

import asyncio
import websockets
from websockets.client import WebSocketClientProtocol
import threading
import sys
import os
from typing import Optional, Callable
import json

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Message, MessageType, MessageFactory
from client.gui import ChatGUI


class ChatClient:
    """
    Cliente de chat que conecta WebSocket con GUI.
    Patrón: Mediator - Coordina comunicación entre servidor y GUI
    """
    
    def __init__(self):
        self.gui = ChatGUI()
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.username: Optional[str] = None
        self.user_id: Optional[str] = None
        self.current_room: Optional[str] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ws_thread: Optional[threading.Thread] = None
        
        # Configurar callbacks de la GUI
        self.gui.set_callbacks(
            on_connect=self._on_gui_connect,
            on_disconnect=self._on_gui_disconnect,
            on_send_message=self._on_gui_send_message,
            on_create_room=self._on_gui_create_room,
            on_join_room=self._on_gui_join_room,
            on_leave_room=self._on_gui_leave_room
        )
    
    def _on_gui_connect(self, server: str, username: str, port: int):
        """Callback cuando la GUI solicita conectar."""
        self.username = username
        
        # Iniciar conexión en hilo separado
        self._ws_thread = threading.Thread(
            target=self._run_websocket,
            args=(server, port, username),
            daemon=True
        )
        self._ws_thread.start()
    
    def _on_gui_disconnect(self):
        """Callback cuando la GUI solicita desconectar."""
        self._schedule_coroutine(self._disconnect())
    
    def _on_gui_send_message(self, content: str):
        """Callback cuando la GUI envía un mensaje."""
        if self.current_room:
            msg = MessageFactory.create_chat_message(
                self.username,
                self.current_room,
                content
            )
            self._schedule_coroutine(self._send(msg))
    
    def _on_gui_create_room(self, room_name: str):
        """Callback cuando la GUI crea una sala."""
        msg = MessageFactory.create_room(room_name)
        self._schedule_coroutine(self._send(msg))
    
    def _on_gui_join_room(self, room_name: str):
        """Callback cuando la GUI se une a una sala."""
        msg = MessageFactory.create_join_room(room_name)
        self._schedule_coroutine(self._send(msg))
    
    def _on_gui_leave_room(self):
        """Callback cuando la GUI abandona la sala."""
        if self.current_room:
            msg = MessageFactory.create_leave_room(self.current_room)
            self._schedule_coroutine(self._send(msg))
            self.current_room = None
            self.gui.set_current_room(None)
            self.gui.clear_messages()
    
    def _schedule_coroutine(self, coro):
        """Programa una corutina en el loop de asyncio."""
        if self._loop and self._running:
            asyncio.run_coroutine_threadsafe(coro, self._loop)
    
    async def _send(self, message: Message) -> bool:
        """Envía un mensaje al servidor."""
        if self.websocket and self._running:
            try:
                await self.websocket.send(message.to_json())
                return True
            except Exception as e:
                print(f"Error enviando mensaje: {e}")
        return False
    
    async def _disconnect(self):
        """Desconecta del servidor."""
        self._running = False
        if self.websocket:
            try:
                msg = MessageFactory.create_disconnect(self.username)
                await self.websocket.send(msg.to_json())
                await self.websocket.close()
            except:
                pass
        self.websocket = None
        self.current_room = None
        self.gui.show_disconnected()
    
    def _run_websocket(self, server: str, port: int, username: str):
        """Ejecuta el cliente WebSocket en un hilo separado."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(
                self._websocket_handler(server, port, username)
            )
        except Exception as e:
            print(f"Error en WebSocket: {e}")
        finally:
            self._loop.close()
            self._loop = None
    
    async def _websocket_handler(self, server: str, port: int, username: str):
        """Maneja la conexión WebSocket."""
        uri = f"ws://{server}:{port}"
        
        try:
            async with websockets.connect(uri) as ws:
                self.websocket = ws
                self._running = True
                
                # Enviar mensaje de conexión
                connect_msg = MessageFactory.create_connect(username)
                await ws.send(connect_msg.to_json())
                
                # Escuchar mensajes
                async for raw_message in ws:
                    if not self._running:
                        break
                    
                    try:
                        message = Message.from_json(raw_message)
                        await self._handle_message(message)
                    except json.JSONDecodeError:
                        print("Mensaje inválido recibido")
                    except Exception as e:
                        print(f"Error procesando mensaje: {e}")
        
        except ConnectionRefusedError:
            self.gui.show_connection_error("No se pudo conectar al servidor")
        except Exception as e:
            self.gui.show_connection_error(f"Error de conexión: {str(e)}")
        finally:
            self._running = False
            self.websocket = None
    
    async def _handle_message(self, message: Message):
        """Procesa un mensaje recibido del servidor."""
        handlers = {
            MessageType.CONNECTION_ACK: self._handle_connection_ack,
            MessageType.CONNECTION_ERROR: self._handle_connection_error,
            MessageType.ROOMS_LIST: self._handle_rooms_list,
            MessageType.ROOM_USERS: self._handle_room_users,
            MessageType.CHAT_MESSAGE: self._handle_chat_message,
            MessageType.SYSTEM_MESSAGE: self._handle_system_message,
            MessageType.USER_JOINED: self._handle_user_joined,
            MessageType.USER_LEFT: self._handle_user_left,
            MessageType.ERROR: self._handle_error,
        }
        
        handler = handlers.get(message.type)
        if handler:
            await handler(message)
    
    async def _handle_connection_ack(self, message: Message):
        """Maneja confirmación de conexión."""
        self.username = message.payload.get("username")
        self.user_id = message.payload.get("user_id")
        self.gui.show_connected(self.username)
    
    async def _handle_connection_error(self, message: Message):
        """Maneja error de conexión."""
        reason = message.payload.get("reason", "Error desconocido")
        self.gui.show_connection_error(reason)
        self._running = False
    
    async def _handle_rooms_list(self, message: Message):
        """Maneja lista de salas."""
        rooms = message.payload.get("rooms", [])
        self.gui.update_rooms(rooms)
    
    async def _handle_room_users(self, message: Message):
        """Maneja lista de usuarios de sala."""
        room_name = message.payload.get("room_name")
        users = message.payload.get("users", [])
        
        if room_name:
            self.current_room = room_name
            self.gui.set_current_room(room_name)
            self.gui.update_users(users)
            self.gui.clear_messages()
    
    async def _handle_chat_message(self, message: Message):
        """Maneja mensaje de chat."""
        username = message.payload.get("username", "")
        content = message.payload.get("content", "")
        timestamp = message.timestamp
        
        self.gui.add_message(username, content, timestamp)
    
    async def _handle_system_message(self, message: Message):
        """Maneja mensaje del sistema."""
        content = message.payload.get("content", "")
        timestamp = message.timestamp
        
        self.gui.add_message("Sistema", content, timestamp, is_system=True)
    
    async def _handle_user_joined(self, message: Message):
        """Maneja notificación de usuario que se unió."""
        username = message.payload.get("username", "")
        room_name = message.payload.get("room_name", "")
        
        if room_name == self.current_room:
            self.gui.add_message(
                "Sistema",
                f"{username} se ha unido a la sala",
                message.timestamp,
                is_system=True
            )
            # Solicitar lista actualizada de usuarios
            list_msg = MessageFactory.create_join_room(room_name)
            # El servidor enviará ROOM_USERS
    
    async def _handle_user_left(self, message: Message):
        """Maneja notificación de usuario que salió."""
        username = message.payload.get("username", "")
        room_name = message.payload.get("room_name", "")
        
        if room_name == self.current_room:
            self.gui.add_message(
                "Sistema",
                f"{username} ha abandonado la sala",
                message.timestamp,
                is_system=True
            )
    
    async def _handle_error(self, message: Message):
        """Maneja mensaje de error."""
        error_msg = message.payload.get("message", "Error desconocido")
        self.gui.show_error(error_msg)
    
    def run(self):
        """Inicia el cliente."""
        self.gui.run()


def main():
    """Punto de entrada del cliente."""
    client = ChatClient()
    client.run()


if __name__ == "__main__":
    main()
