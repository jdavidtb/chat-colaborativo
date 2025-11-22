"""
Servidor de Chat Colaborativo con Salas Temáticas.

Arquitectura:
    - WebSockets para comunicación en tiempo real
    - Patrón Singleton para el servidor
    - Patrón Observer para notificaciones
    - Patrón Factory para mensajes
    - Patrón Strategy para handlers
"""

from .server import ChatServer

__all__ = ['ChatServer']
