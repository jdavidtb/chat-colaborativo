"""
Modelo de Usuario para el servidor de chat.

Patrón: Observer (el usuario es un observador de las salas)
Principio SOLID: 
    - Single Responsibility: Solo maneja datos del usuario
    - Interface Segregation: Interfaz mínima necesaria
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol


@dataclass
class User:
    """
    Representa un usuario conectado al servidor.
    Implementa el patrón Observer como observador de eventos de sala.
    """
    username: str
    websocket: 'WebSocketServerProtocol'
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    connected_at: datetime = field(default_factory=datetime.now)
    current_room: Optional[str] = None
    
    def __hash__(self):
        """Permite usar User en sets y como clave de diccionario."""
        return hash(self.user_id)
    
    def __eq__(self, other):
        """Compara usuarios por su ID único."""
        if isinstance(other, User):
            return self.user_id == other.user_id
        return False
    
    def __repr__(self):
        return f"User(username='{self.username}', id='{self.user_id}', room='{self.current_room}')"
    
    async def send_message(self, message: str) -> bool:
        """
        Envía un mensaje al usuario a través de su websocket.
        
        Args:
            message: Mensaje JSON a enviar
            
        Returns:
            True si se envió correctamente, False si hubo error
        """
        try:
            await self.websocket.send(message)
            return True
        except Exception as e:
            print(f"Error enviando mensaje a {self.username}: {e}")
            return False
    
    def join_room(self, room_name: str) -> None:
        """Registra que el usuario se unió a una sala."""
        self.current_room = room_name
    
    def leave_room(self) -> Optional[str]:
        """
        Registra que el usuario abandonó su sala actual.
        
        Returns:
            Nombre de la sala que abandonó, o None si no estaba en ninguna
        """
        previous_room = self.current_room
        self.current_room = None
        return previous_room
    
    def is_in_room(self, room_name: str) -> bool:
        """Verifica si el usuario está en una sala específica."""
        return self.current_room == room_name
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario (sin websocket)."""
        return {
            "username": self.username,
            "user_id": self.user_id,
            "current_room": self.current_room,
            "connected_at": self.connected_at.isoformat()
        }
