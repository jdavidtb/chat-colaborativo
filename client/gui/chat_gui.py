"""
Interfaz gráfica del cliente de chat usando Tkinter.

Patrón: MVC (Model-View-Controller separado)
Patrón: Observer (recibe notificaciones del servidor)
Principio SOLID: Single Responsibility - Solo maneja la UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from typing import Callable, Optional, List, Dict
from datetime import datetime
import threading


class ChatColors:
    """Paleta de colores para la interfaz."""
    BG_DARK = "#1a1a2e"
    BG_MEDIUM = "#16213e"
    BG_LIGHT = "#0f3460"
    ACCENT = "#e94560"
    TEXT = "#eaeaea"
    TEXT_DIM = "#a0a0a0"
    SUCCESS = "#4ecca3"
    WARNING = "#ffc107"
    ERROR = "#ff6b6b"
    USER_MSG = "#4a9eff"
    OTHER_MSG = "#6c757d"
    SYSTEM_MSG = "#ffc107"


class LoginFrame(ttk.Frame):
    """Frame de inicio de sesión."""
    
    def __init__(self, parent, on_connect: Callable[[str, str, int], None]):
        super().__init__(parent)
        self.on_connect = on_connect
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del login."""
        # Contenedor central
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title = ttk.Label(
            container,
            text="💬 Chat Colaborativo",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(0, 30))
        
        subtitle = ttk.Label(
            container,
            text="Conectarse al servidor",
            font=("Segoe UI", 12)
        )
        subtitle.pack(pady=(0, 20))
        
        # Frame para campos
        fields = ttk.Frame(container)
        fields.pack(fill="x", padx=20)
        
        # Servidor
        ttk.Label(fields, text="Servidor:", font=("Segoe UI", 10)).pack(anchor="w")
        self.server_entry = ttk.Entry(fields, width=30, font=("Segoe UI", 11))
        self.server_entry.insert(0, "localhost")
        self.server_entry.pack(fill="x", pady=(5, 15))
        
        # Puerto
        ttk.Label(fields, text="Puerto:", font=("Segoe UI", 10)).pack(anchor="w")
        self.port_entry = ttk.Entry(fields, width=30, font=("Segoe UI", 11))
        self.port_entry.insert(0, "8765")
        self.port_entry.pack(fill="x", pady=(5, 15))
        
        # Nombre de usuario
        ttk.Label(fields, text="Nombre de usuario:", font=("Segoe UI", 10)).pack(anchor="w")
        self.username_entry = ttk.Entry(fields, width=30, font=("Segoe UI", 11))
        self.username_entry.pack(fill="x", pady=(5, 20))
        self.username_entry.focus()
        
        # Botón conectar
        self.connect_btn = ttk.Button(
            fields,
            text="Conectar",
            command=self._on_connect_click,
            style="Accent.TButton"
        )
        self.connect_btn.pack(fill="x", pady=(10, 0))
        
        # Bind Enter
        self.username_entry.bind("<Return>", lambda e: self._on_connect_click())
        
        # Status
        self.status_label = ttk.Label(
            container,
            text="",
            font=("Segoe UI", 9),
            foreground=ChatColors.TEXT_DIM
        )
        self.status_label.pack(pady=(15, 0))
    
    def _on_connect_click(self):
        """Maneja el click en conectar."""
        server = self.server_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not server:
            self.show_error("Ingresa la dirección del servidor")
            return
        
        if not port_str.isdigit():
            self.show_error("Puerto inválido")
            return
        
        if not username:
            self.show_error("Ingresa un nombre de usuario")
            return
        
        if len(username) > 30:
            self.show_error("Nombre muy largo (máx. 30 caracteres)")
            return
        
        self.connect_btn.config(state="disabled")
        self.status_label.config(text="Conectando...", foreground=ChatColors.TEXT_DIM)
        
        self.on_connect(server, username, int(port_str))
    
    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.status_label.config(text=message, foreground=ChatColors.ERROR)
        self.connect_btn.config(state="normal")
    
    def reset(self):
        """Resetea el formulario."""
        self.connect_btn.config(state="normal")
        self.status_label.config(text="")


class ChatFrame(ttk.Frame):
    """Frame principal del chat."""
    
    def __init__(
        self,
        parent,
        username: str,
        on_send_message: Callable[[str], None],
        on_create_room: Callable[[str], None],
        on_join_room: Callable[[str], None],
        on_leave_room: Callable[[], None],
        on_disconnect: Callable[[], None]
    ):
        super().__init__(parent)
        self.username = username
        self.on_send_message = on_send_message
        self.on_create_room = on_create_room
        self.on_join_room = on_join_room
        self.on_leave_room = on_leave_room
        self.on_disconnect = on_disconnect
        self.current_room: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del chat."""
        # Panel izquierdo (salas y usuarios)
        left_panel = ttk.Frame(self, width=250)
        left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        
        # Info del usuario
        user_frame = ttk.LabelFrame(left_panel, text="👤 Usuario", padding=10)
        user_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(
            user_frame,
            text=self.username,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")
        
        ttk.Button(
            user_frame,
            text="Desconectar",
            command=self.on_disconnect,
            style="Danger.TButton"
        ).pack(fill="x", pady=(10, 0))
        
        # Lista de salas
        rooms_frame = ttk.LabelFrame(left_panel, text="🏠 Salas", padding=10)
        rooms_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Botones de salas
        btn_frame = ttk.Frame(rooms_frame)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="➕ Nueva",
            command=self._create_room_dialog,
            width=10
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="🚪 Salir",
            command=self.on_leave_room,
            width=10
        ).pack(side="left")
        
        # Lista de salas
        self.rooms_listbox = tk.Listbox(
            rooms_frame,
            font=("Segoe UI", 10),
            selectmode="single",
            bg=ChatColors.BG_MEDIUM,
            fg=ChatColors.TEXT,
            selectbackground=ChatColors.ACCENT,
            selectforeground=ChatColors.TEXT,
            highlightthickness=0,
            bd=0
        )
        self.rooms_listbox.pack(fill="both", expand=True)
        self.rooms_listbox.bind("<Double-1>", self._on_room_double_click)
        
        # Lista de usuarios
        users_frame = ttk.LabelFrame(left_panel, text="👥 Usuarios en sala", padding=10)
        users_frame.pack(fill="both", expand=True)
        
        self.users_listbox = tk.Listbox(
            users_frame,
            font=("Segoe UI", 10),
            bg=ChatColors.BG_MEDIUM,
            fg=ChatColors.TEXT,
            highlightthickness=0,
            bd=0
        )
        self.users_listbox.pack(fill="both", expand=True)
        
        # Panel derecho (chat)
        right_panel = ttk.Frame(self)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Header del chat
        self.chat_header = ttk.Label(
            right_panel,
            text="Selecciona una sala para chatear",
            font=("Segoe UI", 12, "bold")
        )
        self.chat_header.pack(fill="x", pady=(0, 10))
        
        # Área de mensajes
        self.messages_text = scrolledtext.ScrolledText(
            right_panel,
            font=("Segoe UI", 10),
            wrap="word",
            state="disabled",
            bg=ChatColors.BG_MEDIUM,
            fg=ChatColors.TEXT,
            insertbackground=ChatColors.TEXT,
            highlightthickness=0,
            bd=0,
            padx=10,
            pady=10
        )
        self.messages_text.pack(fill="both", expand=True)
        
        # Configurar tags para colores
        self.messages_text.tag_configure("user", foreground=ChatColors.USER_MSG, font=("Segoe UI", 10, "bold"))
        self.messages_text.tag_configure("other", foreground=ChatColors.OTHER_MSG, font=("Segoe UI", 10, "bold"))
        self.messages_text.tag_configure("system", foreground=ChatColors.SYSTEM_MSG, font=("Segoe UI", 9, "italic"))
        self.messages_text.tag_configure("time", foreground=ChatColors.TEXT_DIM, font=("Segoe UI", 8))
        self.messages_text.tag_configure("content", foreground=ChatColors.TEXT)
        
        # Área de entrada
        input_frame = ttk.Frame(right_panel)
        input_frame.pack(fill="x", pady=(10, 0))
        
        self.message_entry = ttk.Entry(
            input_frame,
            font=("Segoe UI", 11)
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", lambda e: self._send_message())
        
        self.send_btn = ttk.Button(
            input_frame,
            text="Enviar",
            command=self._send_message,
            style="Accent.TButton"
        )
        self.send_btn.pack(side="right")
    
    def _create_room_dialog(self):
        """Muestra diálogo para crear sala."""
        room_name = simpledialog.askstring(
            "Nueva Sala",
            "Nombre de la sala:",
            parent=self
        )
        if room_name and room_name.strip():
            self.on_create_room(room_name.strip())
    
    def _on_room_double_click(self, event):
        """Maneja doble click en una sala."""
        selection = self.rooms_listbox.curselection()
        if selection:
            room_text = self.rooms_listbox.get(selection[0])
            # Extraer nombre de sala (formato: "Nombre (N usuarios)")
            room_name = room_text.split(" (")[0]
            self.on_join_room(room_name)
    
    def _send_message(self):
        """Envía un mensaje."""
        content = self.message_entry.get().strip()
        if content and self.current_room:
            self.on_send_message(content)
            self.message_entry.delete(0, "end")
    
    def update_rooms(self, rooms: List[Dict]):
        """Actualiza la lista de salas."""
        self.rooms_listbox.delete(0, "end")
        for room in rooms:
            name = room.get("name", "")
            count = room.get("user_count", 0)
            self.rooms_listbox.insert("end", f"{name} ({count} usuarios)")
    
    def update_users(self, users: List[str]):
        """Actualiza la lista de usuarios de la sala."""
        self.users_listbox.delete(0, "end")
        for user in users:
            prefix = "👤 " if user == self.username else "   "
            self.users_listbox.insert("end", f"{prefix}{user}")
    
    def set_current_room(self, room_name: Optional[str]):
        """Establece la sala actual."""
        self.current_room = room_name
        if room_name:
            self.chat_header.config(text=f"💬 {room_name}")
            self.message_entry.config(state="normal")
            self.send_btn.config(state="normal")
            self.message_entry.focus()
        else:
            self.chat_header.config(text="Selecciona una sala para chatear")
            self.message_entry.config(state="disabled")
            self.send_btn.config(state="disabled")
            self.users_listbox.delete(0, "end")
    
    def add_message(
        self,
        username: str,
        content: str,
        timestamp: str = None,
        is_system: bool = False
    ):
        """Agrega un mensaje al área de chat."""
        self.messages_text.config(state="normal")
        
        # Formatear timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = ""
        else:
            time_str = datetime.now().strftime("%H:%M")
        
        if is_system:
            self.messages_text.insert("end", f"[{time_str}] ", "time")
            self.messages_text.insert("end", f"🔔 {content}\n", "system")
        else:
            is_own = username == self.username
            tag = "user" if is_own else "other"
            
            self.messages_text.insert("end", f"[{time_str}] ", "time")
            self.messages_text.insert("end", f"{username}: ", tag)
            self.messages_text.insert("end", f"{content}\n", "content")
        
        self.messages_text.config(state="disabled")
        self.messages_text.see("end")
    
    def clear_messages(self):
        """Limpia el área de mensajes."""
        self.messages_text.config(state="normal")
        self.messages_text.delete(1.0, "end")
        self.messages_text.config(state="disabled")


class ChatGUI:
    """
    Clase principal de la interfaz gráfica.
    Patrón: Mediator - Coordina la comunicación entre componentes
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Colaborativo")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # Callbacks
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_send_message: Optional[Callable] = None
        self._on_create_room: Optional[Callable] = None
        self._on_join_room: Optional[Callable] = None
        self._on_leave_room: Optional[Callable] = None
        
        self._setup_style()
        self._setup_ui()
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_style(self):
        """Configura el estilo de la aplicación."""
        self.root.configure(bg=ChatColors.BG_DARK)
        
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configurar colores base
        style.configure(".", 
            background=ChatColors.BG_DARK,
            foreground=ChatColors.TEXT,
            fieldbackground=ChatColors.BG_MEDIUM
        )
        
        style.configure("TFrame", background=ChatColors.BG_DARK)
        style.configure("TLabel", background=ChatColors.BG_DARK, foreground=ChatColors.TEXT)
        style.configure("TLabelframe", background=ChatColors.BG_DARK, foreground=ChatColors.TEXT)
        style.configure("TLabelframe.Label", background=ChatColors.BG_DARK, foreground=ChatColors.TEXT)
        
        # Botones
        style.configure("TButton",
            background=ChatColors.BG_LIGHT,
            foreground=ChatColors.TEXT,
            padding=(10, 5)
        )
        style.map("TButton",
            background=[("active", ChatColors.ACCENT)]
        )
        
        style.configure("Accent.TButton",
            background=ChatColors.ACCENT,
            foreground=ChatColors.TEXT,
            padding=(15, 8)
        )
        style.map("Accent.TButton",
            background=[("active", "#ff6b8a")]
        )
        
        style.configure("Danger.TButton",
            background=ChatColors.ERROR,
            foreground=ChatColors.TEXT
        )
        
        # Entries
        style.configure("TEntry",
            fieldbackground=ChatColors.BG_MEDIUM,
            foreground=ChatColors.TEXT,
            insertcolor=ChatColors.TEXT,
            padding=8
        )
    
    def _setup_ui(self):
        """Configura la interfaz inicial."""
        self.login_frame: Optional[LoginFrame] = None
        self.chat_frame: Optional[ChatFrame] = None
        self._show_login()
    
    def _show_login(self):
        """Muestra la pantalla de login."""
        if self.chat_frame:
            self.chat_frame.destroy()
            self.chat_frame = None
        
        self.login_frame = LoginFrame(self.root, self._handle_connect)
        self.login_frame.pack(fill="both", expand=True)
    
    def _show_chat(self, username: str):
        """Muestra la pantalla de chat."""
        if self.login_frame:
            self.login_frame.destroy()
            self.login_frame = None
        
        self.chat_frame = ChatFrame(
            self.root,
            username,
            on_send_message=self._handle_send_message,
            on_create_room=self._handle_create_room,
            on_join_room=self._handle_join_room,
            on_leave_room=self._handle_leave_room,
            on_disconnect=self._handle_disconnect
        )
        self.chat_frame.pack(fill="both", expand=True)
    
    def _handle_connect(self, server: str, username: str, port: int):
        """Maneja solicitud de conexión."""
        if self._on_connect:
            self._on_connect(server, username, port)
    
    def _handle_disconnect(self):
        """Maneja solicitud de desconexión."""
        if self._on_disconnect:
            self._on_disconnect()
    
    def _handle_send_message(self, content: str):
        """Maneja envío de mensaje."""
        if self._on_send_message:
            self._on_send_message(content)
    
    def _handle_create_room(self, room_name: str):
        """Maneja creación de sala."""
        if self._on_create_room:
            self._on_create_room(room_name)
    
    def _handle_join_room(self, room_name: str):
        """Maneja unirse a sala."""
        if self._on_join_room:
            self._on_join_room(room_name)
    
    def _handle_leave_room(self):
        """Maneja abandonar sala."""
        if self._on_leave_room:
            self._on_leave_room()
    
    def _on_close(self):
        """Maneja cierre de ventana."""
        if self._on_disconnect:
            self._on_disconnect()
        self.root.destroy()
    
    # Métodos públicos para el controlador
    
    def set_callbacks(
        self,
        on_connect: Callable = None,
        on_disconnect: Callable = None,
        on_send_message: Callable = None,
        on_create_room: Callable = None,
        on_join_room: Callable = None,
        on_leave_room: Callable = None
    ):
        """Establece los callbacks de eventos."""
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_send_message = on_send_message
        self._on_create_room = on_create_room
        self._on_join_room = on_join_room
        self._on_leave_room = on_leave_room
    
    def show_connected(self, username: str):
        """Muestra que el usuario está conectado."""
        self.root.after(0, lambda: self._show_chat(username))
    
    def show_disconnected(self):
        """Muestra que el usuario está desconectado."""
        self.root.after(0, self._show_login)
    
    def show_connection_error(self, message: str):
        """Muestra error de conexión."""
        def _show():
            if self.login_frame:
                self.login_frame.show_error(message)
        self.root.after(0, _show)
    
    def update_rooms(self, rooms: List[Dict]):
        """Actualiza lista de salas."""
        def _update():
            if self.chat_frame:
                self.chat_frame.update_rooms(rooms)
        self.root.after(0, _update)
    
    def update_users(self, users: List[str]):
        """Actualiza lista de usuarios."""
        def _update():
            if self.chat_frame:
                self.chat_frame.update_users(users)
        self.root.after(0, _update)
    
    def set_current_room(self, room_name: Optional[str]):
        """Establece sala actual."""
        def _set():
            if self.chat_frame:
                self.chat_frame.set_current_room(room_name)
        self.root.after(0, _set)
    
    def add_message(self, username: str, content: str, timestamp: str = None, is_system: bool = False):
        """Agrega mensaje al chat."""
        def _add():
            if self.chat_frame:
                self.chat_frame.add_message(username, content, timestamp, is_system)
        self.root.after(0, _add)
    
    def clear_messages(self):
        """Limpia mensajes."""
        def _clear():
            if self.chat_frame:
                self.chat_frame.clear_messages()
        self.root.after(0, _clear)
    
    def show_error(self, message: str):
        """Muestra mensaje de error."""
        self.root.after(0, lambda: messagebox.showerror("Error", message))
    
    def run(self):
        """Inicia el loop principal."""
        self.root.mainloop()
