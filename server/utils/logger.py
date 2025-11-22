"""
Utilidades de logging para el servidor de chat.

Patrón: Singleton (una única instancia del logger)
Principio SOLID: Single Responsibility
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class ChatLogger:
    """
    Logger singleton para el servidor de chat.
    Patrón: Singleton
    """
    _instance: Optional['ChatLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'ChatLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_file: str = "chat_server.log", level: int = logging.INFO):
        if ChatLogger._initialized:
            return
        
        self.logger = logging.getLogger("ChatServer")
        self.logger.setLevel(level)
        
        # Formato de logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"No se pudo crear archivo de log: {e}")
        
        ChatLogger._initialized = True
    
    def info(self, message: str) -> None:
        """Log de información."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log de advertencia."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log de error."""
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log de debug."""
        self.logger.debug(message)
    
    def user_connected(self, username: str, ip: str) -> None:
        """Log de conexión de usuario."""
        self.info(f"🔗 Usuario conectado: {username} desde {ip}")
    
    def user_disconnected(self, username: str) -> None:
        """Log de desconexión de usuario."""
        self.info(f"🔌 Usuario desconectado: {username}")
    
    def room_created(self, room_name: str, creator: str) -> None:
        """Log de creación de sala."""
        self.info(f"🏠 Sala creada: '{room_name}' por {creator}")
    
    def room_deleted(self, room_name: str) -> None:
        """Log de eliminación de sala."""
        self.info(f"🗑️ Sala eliminada: '{room_name}'")
    
    def user_joined_room(self, username: str, room_name: str) -> None:
        """Log de usuario entrando a sala."""
        self.info(f"➡️ {username} se unió a '{room_name}'")
    
    def user_left_room(self, username: str, room_name: str) -> None:
        """Log de usuario saliendo de sala."""
        self.info(f"⬅️ {username} abandonó '{room_name}'")
    
    def message_sent(self, username: str, room_name: str) -> None:
        """Log de mensaje enviado."""
        self.debug(f"💬 Mensaje de {username} en '{room_name}'")


# Función de conveniencia para obtener el logger
def get_logger() -> ChatLogger:
    """Retorna la instancia singleton del logger."""
    return ChatLogger()
