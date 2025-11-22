"""
Modelo de Sala de Chat para el servidor.

Patrón: Observer (la sala notifica a sus usuarios/observadores)
Patrón: Iterator (permite iterar sobre los usuarios de la sala)
Principio SOLID:
    - Single Responsibility: Solo maneja la lógica de la sala
    - Open/Closed: Fácil extender con nuevos tipos de salas
"""

from dataclasses import dataclass, field
from typing import Set, List, Optional, Iterator
from datetime import datetime
from abc import ABC, abstractmethod
import asyncio

from .user import User


class RoomObserver(ABC):
    """
    Interfaz para observadores de eventos de sala.
    Patrón: Observer
    """
    
    @abstractmethod
    async def on_user_joined(self, room_name: str, username: str) -> None:
        """Llamado cuando un usuario se une a la sala."""
        pass
    
    @abstractmethod
    async def on_user_left(self, room_name: str, username: str) -> None:
        """Llamado cuando un usuario abandona la sala."""
        pass
    
    @abstractmethod
    async def on_message(self, room_name: str, username: str, content: str) -> None:
        """Llamado cuando se envía un mensaje en la sala."""
        pass


@dataclass
class Room:
    """
    Representa una sala de chat temática.
    Implementa el patrón Observer como sujeto que notifica cambios.
    """
    name: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    _users: Set[User] = field(default_factory=set)
    _message_history: List[dict] = field(default_factory=list)
    max_history: int = 100  # Máximo de mensajes en historial
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Room):
            return self.name == other.name
        return False
    
    def __repr__(self):
        return f"Room(name='{self.name}', users={len(self._users)})"
    
    def __iter__(self) -> Iterator[User]:
        """Permite iterar sobre los usuarios de la sala."""
        return iter(self._users)
    
    def __len__(self) -> int:
        """Retorna el número de usuarios en la sala."""
        return len(self._users)
    
    @property
    def users(self) -> Set[User]:
        """Retorna copia del set de usuarios."""
        return self._users.copy()
    
    @property
    def user_count(self) -> int:
        """Retorna el número de usuarios."""
        return len(self._users)
    
    @property
    def usernames(self) -> List[str]:
        """Retorna lista de nombres de usuario en la sala."""
        return [user.username for user in self._users]
    
    @property
    def is_empty(self) -> bool:
        """Verifica si la sala está vacía."""
        return len(self._users) == 0
    
    def add_user(self, user: User) -> bool:
        """
        Agrega un usuario a la sala.
        
        Args:
            user: Usuario a agregar
            
        Returns:
            True si se agregó, False si ya estaba
        """
        if user in self._users:
            return False
        self._users.add(user)
        user.join_room(self.name)
        return True
    
    def remove_user(self, user: User) -> bool:
        """
        Remueve un usuario de la sala.
        
        Args:
            user: Usuario a remover
            
        Returns:
            True si se removió, False si no estaba
        """
        if user not in self._users:
            return False
        self._users.discard(user)
        user.leave_room()
        return True
    
    def has_user(self, user: User) -> bool:
        """Verifica si un usuario está en la sala."""
        return user in self._users
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Busca un usuario por su nombre."""
        for user in self._users:
            if user.username == username:
                return user
        return None
    
    def add_message_to_history(self, username: str, content: str) -> None:
        """
        Agrega un mensaje al historial de la sala.
        
        Args:
            username: Nombre del usuario que envió el mensaje
            content: Contenido del mensaje
        """
        message = {
            "username": username,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self._message_history.append(message)
        
        # Mantener el historial dentro del límite
        if len(self._message_history) > self.max_history:
            self._message_history = self._message_history[-self.max_history:]
    
    def get_message_history(self, limit: int = 50) -> List[dict]:
        """
        Obtiene los últimos mensajes del historial.
        
        Args:
            limit: Número máximo de mensajes a retornar
            
        Returns:
            Lista de mensajes
        """
        return self._message_history[-limit:]
    
    async def broadcast(self, message: str, exclude: Optional[User] = None) -> None:
        """
        Envía un mensaje a todos los usuarios de la sala.
        Patrón Observer: Notifica a todos los observadores (usuarios).
        
        Args:
            message: Mensaje JSON a enviar
            exclude: Usuario a excluir del broadcast (opcional)
        """
        tasks = []
        for user in self._users:
            if exclude and user == exclude:
                continue
            tasks.append(user.send_message(message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def to_dict(self) -> dict:
        """Convierte la sala a diccionario."""
        return {
            "name": self.name,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "user_count": self.user_count,
            "users": self.usernames
        }
