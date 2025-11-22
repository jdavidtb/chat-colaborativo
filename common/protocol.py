"""
Protocolo de comunicación para el Chat Colaborativo.
Define los tipos de mensajes y su estructura.

Patrón: Factory Method para crear mensajes
Principio SOLID: Single Responsibility - Solo maneja la estructura de mensajes
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class MessageType(Enum):
    """Tipos de mensajes soportados por el protocolo."""
    # Conexión
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    CONNECTION_ACK = "connection_ack"
    CONNECTION_ERROR = "connection_error"
    
    # Salas
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    LIST_ROOMS = "list_rooms"
    ROOMS_LIST = "rooms_list"
    ROOM_USERS = "room_users"
    
    # Chat
    CHAT_MESSAGE = "chat_message"
    SYSTEM_MESSAGE = "system_message"
    
    # Notificaciones
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    
    # Errores
    ERROR = "error"


@dataclass
class Message:
    """Estructura base de un mensaje del protocolo."""
    type: MessageType
    payload: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_json(self) -> str:
        """Serializa el mensaje a JSON."""
        data = {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Deserializa un mensaje desde JSON."""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            payload=data["payload"],
            timestamp=data.get("timestamp")
        )


class MessageFactory:
    """
    Factory para crear mensajes del protocolo.
    Patrón: Factory Method
    Principio SOLID: Open/Closed - Fácil agregar nuevos tipos de mensajes
    """
    
    @staticmethod
    def create_connect(username: str) -> Message:
        """Crea mensaje de conexión."""
        return Message(
            type=MessageType.CONNECT,
            payload={"username": username}
        )
    
    @staticmethod
    def create_disconnect(username: str) -> Message:
        """Crea mensaje de desconexión."""
        return Message(
            type=MessageType.DISCONNECT,
            payload={"username": username}
        )
    
    @staticmethod
    def create_connection_ack(username: str, user_id: str) -> Message:
        """Crea mensaje de confirmación de conexión."""
        return Message(
            type=MessageType.CONNECTION_ACK,
            payload={"username": username, "user_id": user_id}
        )
    
    @staticmethod
    def create_connection_error(reason: str) -> Message:
        """Crea mensaje de error de conexión."""
        return Message(
            type=MessageType.CONNECTION_ERROR,
            payload={"reason": reason}
        )
    
    @staticmethod
    def create_room(room_name: str) -> Message:
        """Crea mensaje para crear sala."""
        return Message(
            type=MessageType.CREATE_ROOM,
            payload={"room_name": room_name}
        )
    
    @staticmethod
    def create_join_room(room_name: str) -> Message:
        """Crea mensaje para unirse a sala."""
        return Message(
            type=MessageType.JOIN_ROOM,
            payload={"room_name": room_name}
        )
    
    @staticmethod
    def create_leave_room(room_name: str) -> Message:
        """Crea mensaje para abandonar sala."""
        return Message(
            type=MessageType.LEAVE_ROOM,
            payload={"room_name": room_name}
        )
    
    @staticmethod
    def create_list_rooms() -> Message:
        """Crea mensaje para solicitar lista de salas."""
        return Message(
            type=MessageType.LIST_ROOMS,
            payload={}
        )
    
    @staticmethod
    def create_rooms_list(rooms: List[Dict]) -> Message:
        """Crea mensaje con lista de salas."""
        return Message(
            type=MessageType.ROOMS_LIST,
            payload={"rooms": rooms}
        )
    
    @staticmethod
    def create_room_users(room_name: str, users: List[str]) -> Message:
        """Crea mensaje con usuarios de una sala."""
        return Message(
            type=MessageType.ROOM_USERS,
            payload={"room_name": room_name, "users": users}
        )
    
    @staticmethod
    def create_chat_message(username: str, room_name: str, content: str) -> Message:
        """Crea mensaje de chat."""
        return Message(
            type=MessageType.CHAT_MESSAGE,
            payload={
                "username": username,
                "room_name": room_name,
                "content": content
            }
        )
    
    @staticmethod
    def create_system_message(content: str, room_name: str = None) -> Message:
        """Crea mensaje del sistema."""
        return Message(
            type=MessageType.SYSTEM_MESSAGE,
            payload={"content": content, "room_name": room_name}
        )
    
    @staticmethod
    def create_user_joined(username: str, room_name: str) -> Message:
        """Crea notificación de usuario que se unió."""
        return Message(
            type=MessageType.USER_JOINED,
            payload={"username": username, "room_name": room_name}
        )
    
    @staticmethod
    def create_user_left(username: str, room_name: str) -> Message:
        """Crea notificación de usuario que salió."""
        return Message(
            type=MessageType.USER_LEFT,
            payload={"username": username, "room_name": room_name}
        )
    
    @staticmethod
    def create_error(error_message: str) -> Message:
        """Crea mensaje de error."""
        return Message(
            type=MessageType.ERROR,
            payload={"message": error_message}
        )
