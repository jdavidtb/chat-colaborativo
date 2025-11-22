# 💬 Chat Colaborativo con Salas Temáticas

Sistema de chat en tiempo real con arquitectura cliente-servidor, desarrollado en Python utilizando WebSockets.

## 📋 Características

- ✅ Comunicación en tiempo real mediante WebSockets
- ✅ Múltiples salas de chat temáticas
- ✅ Crear, unirse y abandonar salas
- ✅ Notificaciones de entrada/salida de usuarios
- ✅ Lista de usuarios actualizada en tiempo real
- ✅ Cliente de escritorio con interfaz gráfica (Tkinter)
- ✅ Cliente web para navegadores y dispositivos móviles
- ✅ Acceso desde múltiples dispositivos en la misma red
- ✅ Arquitectura basada en patrones de diseño
- ✅ Cumple principios SOLID

## 🏗️ Arquitectura del Proyecto

```
chat_colaborativo/
├── server/                     # Servidor de chat
│   ├── models/                 # Modelos de datos
│   │   ├── __init__.py
│   │   ├── user.py            # Modelo de Usuario
│   │   └── room.py            # Modelo de Sala (Observer)
│   ├── handlers/              # Manejadores de mensajes
│   │   ├── __init__.py
│   │   └── message_handler.py # Strategy Pattern
│   ├── utils/                 # Utilidades
│   │   ├── __init__.py
│   │   └── logger.py          # Logger (Singleton)
│   ├── __init__.py
│   └── server.py              # Servidor principal (Singleton)
├── client/                    # Cliente de escritorio
│   ├── gui/                   # Interfaz gráfica
│   │   ├── __init__.py
│   │   └── chat_gui.py        # GUI con Tkinter
│   ├── __init__.py
│   └── client.py              # Cliente principal (Mediator)
├── common/                    # Código compartido
│   ├── __init__.py
│   └── protocol.py            # Protocolo de mensajes (Factory)
├── web_client.html            # Cliente web - HTML
├── styles.css                 # Cliente web - Estilos
├── app.js                     # Cliente web - JavaScript
├── run_server.py              # Script para iniciar servidor de chat
├── run_client.py              # Script para iniciar cliente de escritorio
├── run_web_server.py          # Script para servir cliente web
├── requirements.txt           # Dependencias
└── README.md                  # Esta documentación
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

## 💻 Ejecución

El sistema requiere ejecutar servidores en terminales separadas:

### Terminal 1: Servidor de Chat (WebSocket)

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

### Terminal 2: Servidor Web (Para cliente web/móvil)

```bash
python run_web_server.py
```

Mostrará:
```
============================================================
   SERVIDOR WEB - Cliente de Chat
============================================================

🌐 Abre en tu navegador o celular:
   - Local:  http://localhost:8080/web_client.html
   - Red:    http://192.168.1.100:8080/web_client.html

============================================================
```

### Terminal 3+: Clientes

#### Opción A: Cliente de Escritorio (Tkinter)

```bash
python run_client.py
```

Se abrirá una ventana gráfica donde podrás:
1. Ingresar la dirección del servidor (localhost o IP de red)
2. Ingresar el puerto (por defecto 8765)
3. Elegir un nombre de usuario
4. Conectarte y comenzar a chatear

#### Opción B: Cliente Web (Navegador/Celular)

Abre en el navegador:
- **Local:** `http://localhost:8080/web_client.html`
- **Red:** `http://[IP-DEL-SERVIDOR]:8080/web_client.html`

## 🌐 Conexión desde Otros Dispositivos

### Diagrama de Red

```
┌─────────────────────────────────────────────────────────┐
│                    Tu Red WiFi/LAN                      │
│                                                         │
│   ┌──────────────┐         ┌──────────────┐            │
│   │   Tu PC      │         │  Otro PC/    │            │
│   │ 192.168.1.100│◄───────►│  Laptop      │            │
│   │              │  WiFi   │              │            │
│   │ [Servidor]   │         │ [Cliente]    │            │
│   │ Puerto 8765  │         │              │            │
│   │ Puerto 8080  │         └──────────────┘            │
│   └──────────────┘                                      │
│         ▲                  ┌──────────────┐            │
│         │                  │   Celular    │            │
│         └─────────────────►│ (navegador)  │            │
│              WiFi          │              │            │
│                            └──────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Configuración del Firewall (Windows)

Para permitir conexiones desde otros dispositivos:

```powershell
# Ejecutar como Administrador
netsh advfirewall firewall add rule name="Chat Server" dir=in action=allow protocol=tcp localport=8765
netsh advfirewall firewall add rule name="Chat Web" dir=in action=allow protocol=tcp localport=8080
```

### Desde otro dispositivo

1. **Asegúrate de estar en la misma red WiFi/LAN**
2. **Para cliente de escritorio:**
   - Copia la carpeta del proyecto
   - Instala dependencias: `pip install websockets`
   - Ejecuta: `python run_client.py`
   - Servidor: `[IP-DEL-PC]` (ej: 192.168.1.100)
   - Puerto: `8765`

3. **Para navegador/celular:**
   - Abre: `http://[IP-DEL-PC]:8080/web_client.html`
   - Servidor: `[IP-DEL-PC]`
   - Puerto: `8765`

## 📡 Arquitectura de Comunicación

### ¿Por qué dos servidores?

| Servidor | Puerto | Protocolo | Función |
|----------|--------|-----------|---------|
| `run_server.py` | 8765 | WebSocket | Chat en tiempo real |
| `run_web_server.py` | 8080 | HTTP | Entrega archivos web al navegador |

```
Navegador/Celular
       │
       │ 1️⃣ Solicita página (HTTP)
       ▼
   Puerto 8080  ──►  run_web_server.py  ──►  Entrega web_client.html
       │
       │ 2️⃣ JavaScript establece conexión (WebSocket)
       ▼
   Puerto 8765  ──►  run_server.py  ──►  Chat en tiempo real
```

### HTTP vs WebSocket

| Característica | HTTP | WebSocket |
|----------------|------|-----------|
| Conexión | Se abre y cierra cada petición | Permanece abierta |
| Comunicación | Cliente pregunta → Servidor responde | Bidireccional |
| Ideal para | Páginas web, descargas | Chat, juegos, tiempo real |

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

| Tipo | Dirección | Descripción |
|------|-----------|-------------|
| `connect` | Cliente → Servidor | Solicitud de conexión |
| `connection_ack` | Servidor → Cliente | Confirmación de conexión |
| `connection_error` | Servidor → Cliente | Error de conexión |
| `create_room` | Cliente → Servidor | Crear nueva sala |
| `join_room` | Cliente → Servidor | Unirse a sala |
| `leave_room` | Cliente → Servidor | Abandonar sala |
| `rooms_list` | Servidor → Cliente | Lista de salas |
| `room_users` | Servidor → Cliente | Usuarios en sala |
| `chat_message` | Bidireccional | Mensaje de chat |
| `system_message` | Servidor → Cliente | Mensaje del sistema |
| `user_joined` | Servidor → Cliente | Notificación de entrada |
| `user_left` | Servidor → Cliente | Notificación de salida |
| `error` | Servidor → Cliente | Mensaje de error |

## 🎯 Flujo de Uso

1. **Conectarse**: Usuario ingresa nombre → servidor valida → confirmación
2. **Ver salas**: Servidor envía lista de salas disponibles
3. **Crear/Unirse**: Usuario crea sala nueva o se une a existente
4. **Chatear**: Mensajes se envían a todos los usuarios de la sala
5. **Cambiar sala**: Usuario puede abandonar y unirse a otra
6. **Desconectar**: Usuario cierra aplicación o se desconecta

## 🔧 Uso en Visual Studio Code

1. **Abrir el proyecto:**
```bash
code chat_colaborativo/
```

2. **Configurar el intérprete de Python:**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Seleccionar Python 3.8+

3. **Ejecutar con la configuración incluida:**
   - Ve a "Run and Debug" (Ctrl+Shift+D)
   - Selecciona "🖥️ Servidor" y presiona F5
   - Abre otra instancia y selecciona "💻 Cliente"

## 🐛 Solución de Problemas

### "No se pudo conectar al servidor"
- Verificar que el servidor esté ejecutándose
- Verificar la dirección IP y puerto
- Revisar configuración del firewall

### "Nombre de usuario ya en uso"
- Elegir un nombre diferente

### "invalid Connection header: keep-alive"
- Esto ocurre cuando abres el puerto WebSocket (8765) en el navegador
- Es normal e inofensivo, el servidor sigue funcionando
- Para el navegador usa el puerto HTTP (8080)

### "OSError: [Errno 10048] address already in use"
- El puerto ya está en uso por otro proceso
- Cerrar el proceso anterior: `taskkill /IM python.exe /F`
- O usar otro puerto: `python run_server.py --port 9000`

### Cliente web no carga en celular
- Verificar que el celular esté en la misma red WiFi
- Verificar que el firewall permita el puerto 8080
- Probar con: `ping [IP-DEL-PC]` desde el celular

## 📁 Archivos del Cliente Web

El cliente web está separado en tres archivos siguiendo buenas prácticas:

| Archivo | Contenido |
|---------|-----------|
| `web_client.html` | Estructura HTML |
| `styles.css` | Estilos CSS |
| `app.js` | Lógica JavaScript |

## 👥 Casos de Uso Implementados

1. ✅ Conectarse al Servidor
2. ✅ Crear o Unirse a una Sala de Chat
3. ✅ Enviar Mensaje en la Sala
4. ✅ Ver usuarios conectados en tiempo real
5. ✅ Desconectarse del Servidor

## 📄 Licencia

Proyecto académico - Asignatura Cliente-Servidor

---

Desarrollado siguiendo las especificaciones del proyecto "Chat Colaborativo con Salas Temáticas"
