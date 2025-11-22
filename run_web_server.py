#!/usr/bin/env python3
"""
Servidor HTTP simple para servir el cliente web.
Ejecuta esto además del servidor de chat.
"""

import http.server
import socketserver
import os
import socket

PORT = 8080

def get_local_ip():
    """Obtiene la IP local."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Cambiar al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

local_ip = get_local_ip()

print("=" * 60)
print("   SERVIDOR WEB - Cliente de Chat")
print("=" * 60)
print(f"\n🌐 Abre en tu navegador o celular:")
print(f"   - Local:  http://localhost:{PORT}/web_client.html")
print(f"   - Red:    http://{local_ip}:{PORT}/web_client.html")
print(f"\n📱 Escanea el QR o escribe la URL en tu celular")
print("\n" + "=" * 60)
print("Presiona Ctrl+C para detener")
print("=" * 60 + "\n")

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor web detenido")
