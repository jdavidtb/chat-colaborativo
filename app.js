// Estado de la aplicación
let ws = null;
let username = '';
let currentRoom = null;

// Elementos del DOM
const loginScreen = document.getElementById('loginScreen');
const chatScreen = document.getElementById('chatScreen');
const serverInput = document.getElementById('serverInput');
const portInput = document.getElementById('portInput');
const usernameInput = document.getElementById('usernameInput');
const connectBtn = document.getElementById('connectBtn');
const errorMsg = document.getElementById('errorMsg');
const disconnectBtn = document.getElementById('disconnectBtn');
const usernameDisplay = document.getElementById('usernameDisplay');
const statusDot = document.getElementById('statusDot');
const roomList = document.getElementById('roomList');
const userList = document.getElementById('userList');
const currentRoomName = document.getElementById('currentRoomName');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newRoomBtn = document.getElementById('newRoomBtn');
const leaveRoomBtn = document.getElementById('leaveRoomBtn');
const newRoomModal = document.getElementById('newRoomModal');
const newRoomInput = document.getElementById('newRoomInput');
const createRoomBtn = document.getElementById('createRoomBtn');
const cancelRoomBtn = document.getElementById('cancelRoomBtn');

// Auto-detectar IP del servidor (misma que la página)
if (window.location.hostname && window.location.hostname !== 'localhost') {
    serverInput.value = window.location.hostname;
}

// Conectar al servidor
connectBtn.addEventListener('click', connect);
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') connect();
});

function connect() {
    const server = serverInput.value.trim();
    const port = portInput.value.trim();
    username = usernameInput.value.trim();

    if (!server || !port || !username) {
        showError('Completa todos los campos');
        return;
    }

    errorMsg.textContent = 'Conectando...';
    connectBtn.disabled = true;

    try {
        ws = new WebSocket(`ws://${server}:${port}`);

        ws.onopen = () => {
            send({
                type: 'connect',
                payload: { username: username },
                timestamp: new Date().toISOString()
            });
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleMessage(message);
        };

        ws.onerror = (error) => {
            showError('Error de conexión');
            connectBtn.disabled = false;
        };

        ws.onclose = () => {
            if (chatScreen.style.display !== 'none') {
                showLogin();
                showError('Conexión cerrada');
            }
            connectBtn.disabled = false;
        };
    } catch (e) {
        showError('Error al conectar: ' + e.message);
        connectBtn.disabled = false;
    }
}

function send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
    }
}

function handleMessage(msg) {
    switch (msg.type) {
        case 'connection_ack':
            username = msg.payload.username;
            showChat();
            break;

        case 'connection_error':
            showError(msg.payload.reason);
            connectBtn.disabled = false;
            break;

        case 'rooms_list':
            updateRoomList(msg.payload.rooms);
            break;

        case 'room_users':
            currentRoom = msg.payload.room_name;
            updateCurrentRoom();
            updateUserList(msg.payload.users);
            break;

        case 'chat_message':
            addMessage(msg.payload.username, msg.payload.content, msg.timestamp);
            break;

        case 'system_message':
            addSystemMessage(msg.payload.content, msg.timestamp);
            break;

        case 'user_joined':
            if (msg.payload.room_name === currentRoom) {
                addSystemMessage(`${msg.payload.username} se ha unido a la sala`, msg.timestamp);
            }
            break;

        case 'user_left':
            if (msg.payload.room_name === currentRoom) {
                addSystemMessage(`${msg.payload.username} ha abandonado la sala`, msg.timestamp);
            }
            break;

        case 'error':
            alert(msg.payload.message);
            break;
    }
}

function showChat() {
    loginScreen.style.display = 'none';
    chatScreen.style.display = 'flex';
    usernameDisplay.textContent = username;
    errorMsg.textContent = '';
}

function showLogin() {
    loginScreen.style.display = 'flex';
    chatScreen.style.display = 'none';
    currentRoom = null;
    messages.innerHTML = '';
    roomList.innerHTML = '';
    userList.innerHTML = '';
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.color = '#ff6b6b';
}

function updateRoomList(rooms) {
    roomList.innerHTML = '';
    rooms.forEach(room => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${room.name}</span>
            <span class="room-count">${room.user_count} usuarios</span>
        `;
        li.onclick = () => joinRoom(room.name);
        if (room.name === currentRoom) {
            li.classList.add('active');
        }
        roomList.appendChild(li);
    });
}

function updateUserList(users) {
    userList.innerHTML = '';
    users.forEach(user => {
        const li = document.createElement('li');
        li.textContent = user === username ? `👤 ${user} (tú)` : `   ${user}`;
        userList.appendChild(li);
    });
}

function updateCurrentRoom() {
    if (currentRoom) {
        currentRoomName.textContent = `💬 ${currentRoom}`;
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    } else {
        currentRoomName.textContent = 'Selecciona una sala';
        messageInput.disabled = true;
        sendBtn.disabled = true;
    }
}

function joinRoom(roomName) {
    messages.innerHTML = '';
    send({
        type: 'join_room',
        payload: { room_name: roomName },
        timestamp: new Date().toISOString()
    });
}

function leaveRoom() {
    if (currentRoom) {
        send({
            type: 'leave_room',
            payload: { room_name: currentRoom },
            timestamp: new Date().toISOString()
        });
        currentRoom = null;
        updateCurrentRoom();
        messages.innerHTML = '';
        userList.innerHTML = '';
    }
}

function addMessage(user, content, timestamp) {
    const div = document.createElement('div');
    div.className = 'message';
    
    const time = timestamp ? new Date(timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }) : '';
    const isOwn = user === username;
    
    div.innerHTML = `
        <div class="message-header">
            <span class="message-user ${isOwn ? 'own' : ''}">${user}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function addSystemMessage(content, timestamp) {
    const div = document.createElement('div');
    div.className = 'message system';
    
    const time = timestamp ? new Date(timestamp).toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }) : '';
    
    div.innerHTML = `
        <div class="message-header">
            <span class="message-user system">🔔 Sistema</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sendMessage() {
    const content = messageInput.value.trim();
    if (content && currentRoom) {
        send({
            type: 'chat_message',
            payload: {
                username: username,
                room_name: currentRoom,
                content: content
            },
            timestamp: new Date().toISOString()
        });
        messageInput.value = '';
    }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

disconnectBtn.addEventListener('click', () => {
    if (ws) {
        ws.close();
    }
    showLogin();
});

leaveRoomBtn.addEventListener('click', leaveRoom);

newRoomBtn.addEventListener('click', () => {
    newRoomModal.style.display = 'flex';
    newRoomInput.value = '';
    newRoomInput.focus();
});

cancelRoomBtn.addEventListener('click', () => {
    newRoomModal.style.display = 'none';
});

createRoomBtn.addEventListener('click', () => {
    const roomName = newRoomInput.value.trim();
    if (roomName) {
        send({
            type: 'create_room',
            payload: { room_name: roomName },
            timestamp: new Date().toISOString()
        });
        newRoomModal.style.display = 'none';
    }
});

newRoomInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') createRoomBtn.click();
});

// Cerrar modal al hacer clic fuera
newRoomModal.addEventListener('click', (e) => {
    if (e.target === newRoomModal) {
        newRoomModal.style.display = 'none';
    }
});