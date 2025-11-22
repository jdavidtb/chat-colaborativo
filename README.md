# 💬 Chat Colaborativo con Salas Temáticas

Sistema de chat en tiempo real con arquitectura cliente-servidor, desarrollado en Python utilizando WebSockets.

## 📋 Características

- ✅ Comunicación en tiempo real mediante WebSockets
- ✅ Múltiples salas de chat temáticas
- ✅ Crear, unirse y abandonar salas
- ✅ Notificaciones de entrada/salida de usuarios
- ✅ Interfaz gráfica intuitiva con Tkinter
- ✅ Acceso desde múltiples dispositivos en la misma red
- ✅ Arquitectura basada en patrones de diseño
- ✅ Cumple principios SOLID

## 🏗️ Arquitectura

```
chat_colaborativo/
├── server/                 # Servidor de chat
│   ├── models/            # Modelos de datos (User, Room)
│   ├── handlers/          # Manejadores de mensajes (Strategy)
│   ├── utils/             # Utilidades (Logger Singleton)
│   └── server.py          # Servidor principal (Singleton)
├── client/                # Cliente de chat
│   ├── gui/              # Interfaz gráfica (Tkinter)
│   └── client.py         # Cliente principal (Mediator)
├── common/               # Código compartido
│   └── protocol.py       # Protocolo de mensajes (Factory)
├── run_server.py         # Script para iniciar servidor
├── run_client.py         # Script para iniciar cliente
└── requirements.txt      # Dependencias
```

## 🎨 Patrones de Diseño Aplicados

| Patrón | Ubicación | Descripción |
|--------|-----------|-------------|
| **Singleton** | `ChatServer`, `ChatLogger` | Una única instancia del servidor y logger |
| **Factory Method** | `MessageFactory` | Creación de mensajes del protocolo |
| **Observer** | `Room.broadcast()` | Notificación a usuarios de eventos |
| **Strategy** | `MessageHandler` | Diferentes handlers para tipos de mensajes |
| **Mediator** | `ChatClient` | Coordina comunicación GUI-WebSocket |
| **Registry** | `MessageHandlerRegistry` | Registro de handlers por tipo |

## 📐 Principios SOLID

- **S** (Single Responsibility): Cada clase tiene una única responsabilidad
- **O** (Open/Closed): Fácil agregar nuevos handlers sin modificar existentes
- **L** (Liskov Substitution): Handlers intercambiables
- **I** (Interface Segregation): Interfaces mínimas y específicas
- **D** (Dependency Inversion): Dependencia de abstracciones, no implementaciones

## 🚀 Instalación y Uso

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar o copiar el proyecto**

2. **Instalar dependencias:**
   ```bash
   cd chat_colaborativo
   pip install -r requirements.txt
   ```

### Iniciar el Servidor

```bash
python run_server.py
```

El servidor mostrará:
```
============================================================
   SERVIDOR DE CHAT COLABORATIVO
============================================================

🚀 Servidor iniciado en:
   - Local:     ws://localhost:8765
   - Red:       ws://192.168.1.100:8765

📋 Para conectarse desde otro dispositivo en la red,
   usa la dirección: ws://192.168.1.100:8765

============================================================
```

**Opciones del servidor:**
```bash
python run_server.py --host 0.0.0.0 --port 9000
```

### Iniciar el Cliente

```bash
python run_client.py
```

Se abrirá una ventana gráfica donde podrás:
1. Ingresar la dirección del servidor (usa la IP de red para otros dispositivos)
2. Ingresar el puerto (por defecto 8765)
3. Elegir un nombre de usuario
4. Conectarte y comenzar a chatear

## 🌐 Conexión desde Otros Dispositivos

Para conectar desde otro dispositivo en la misma red:

1. **En el servidor**: Observa la dirección IP de red que muestra al iniciar
2. **En el cliente**: Ingresa esa IP en el campo "Servidor"
3. **Importante**: Asegúrate de que el firewall permita conexiones al puerto

### Configuración del Firewall (Windows)
```powershell
# Permitir puerto 8765
netsh advfirewall firewall add rule name="Chat Server" dir=in action=allow protocol=tcp localport=8765
```

### Configuración del Firewall (Linux)
```bash
# UFW
sudo ufw allow 8765/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
```

## 🔧 Uso en Visual Studio Code

1. **Abrir el proyecto:**
   ```bash
   code chat_colaborativo/
   ```

2. **Configurar el intérprete de Python:**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Seleccionar Python 3.8+

3. **Crear configuración de depuración** (.vscode/launch.json):
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Servidor",
               "type": "debugpy",
               "request": "launch",
               "program": "${workspaceFolder}/run_server.py",
               "console": "integratedTerminal"
           },
           {
               "name": "Cliente",
               "type": "debugpy",
               "request": "launch",
               "program": "${workspaceFolder}/run_client.py",
               "console": "integratedTerminal"
           }
       ]
   }
   ```

4. **Ejecutar:**
   - Primero iniciar el servidor (F5 con config "Servidor")
   - Luego iniciar uno o más clientes

## 📝 Protocolo de Mensajes

El sistema usa un protocolo JSON sobre WebSocket:

```json
{
    "type": "chat_message",
    "payload": {
        "username": "usuario1",
        "room_name": "General",
        "content": "Hola a todos!"
    },
    "timestamp": "2024-01-15T10:30:00"
}
```

### Tipos de Mensajes

| Tipo | Descripción |
|------|-------------|
| `connect` | Solicitud de conexión |
| `connection_ack` | Confirmación de conexión |
| `create_room` | Crear nueva sala |
| `join_room` | Unirse a sala |
| `leave_room` | Abandonar sala |
| `list_rooms` | Solicitar lista de salas |
| `chat_message` | Mensaje de chat |
| `system_message` | Mensaje del sistema |
| `user_joined` | Notificación de entrada |
| `user_left` | Notificación de salida |

## 🎯 Flujo de Uso

1. **Conectarse**: Usuario ingresa nombre → servidor valida → confirmación
2. **Ver salas**: Servidor envía lista de salas disponibles
3. **Crear/Unirse**: Usuario crea sala nueva o se une a existente
4. **Chatear**: Mensajes se envían a todos los usuarios de la sala
5. **Cambiar sala**: Usuario puede abandonar y unirse a otra
6. **Desconectar**: Usuario cierra aplicación o se desconecta

## 🐛 Solución de Problemas

**Error: "No se pudo conectar al servidor"**
- Verificar que el servidor esté ejecutándose
- Verificar la dirección IP y puerto
- Revisar configuración del firewall

**Error: "Nombre de usuario ya en uso"**
- Elegir un nombre diferente

**La interfaz no responde**
- El cliente usa hilos separados para WebSocket y GUI
- Si persiste, reiniciar el cliente

## 📄 Licencia

Proyecto académico - Asignatura Cliente-Servidor

## 👥 Casos de Uso Implementados

1. ✅ Conectarse al Servidor
2. ✅ Crear o Unirse a una Sala de Chat
3. ✅ Enviar Mensaje en la Sala
4. ✅ Desconectarse del Servidor

---

Desarrollado siguiendo las especificaciones del proyecto "Chat Colaborativo con Salas Temáticas"
