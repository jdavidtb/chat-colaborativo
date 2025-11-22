#!/usr/bin/env python3
"""
Script para iniciar el cliente de Chat Colaborativo.

Uso:
    python run_client.py
    
El cliente mostrará una interfaz gráfica donde podrás:
    1. Ingresar la dirección del servidor
    2. Ingresar tu nombre de usuario
    3. Conectarte y chatear
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.client import main

if __name__ == "__main__":
    main()
