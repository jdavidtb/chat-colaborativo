#!/usr/bin/env python3
"""
Script para iniciar el servidor de Chat Colaborativo.

Uso:
    python run_server.py [--host HOST] [--port PORT]
    
Ejemplos:
    python run_server.py                    # Inicia en 0.0.0.0:8765
    python run_server.py --port 9000        # Inicia en puerto 9000
"""

import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.server import main

if __name__ == "__main__":
    main()
