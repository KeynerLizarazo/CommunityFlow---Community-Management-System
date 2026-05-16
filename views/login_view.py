import customtkinter as ctk
from views.style import *

class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=BG_DARK)
        self.controller = controller

        # Configurar grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Panel de Login (Centrado)
        self.login_panel = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=15)
        self.login_panel.grid(row=0, column=0, padx=20, pady=20)
        
        # Título
        self.title_label = ctk.CTkLabel(self.login_panel, text="Sistema Comunitario", font=FONT_TITLE, text_color=PRIMARY_COLOR)
        self.title_label.pack(pady=(30, 10), padx=40)
        
        self.subtitle_label = ctk.CTkLabel(self.login_panel, text="Inicio de Sesión", font=FONT_SUBTITLE, text_color=TEXT_MAIN)
        self.subtitle_label.pack(pady=(0, 20))

        # Campos de texto
        self.username_entry = ctk.CTkEntry(self.login_panel, placeholder_text="Usuario", width=250, height=40, font=FONT_NORMAL, corner_radius=8)
        self.username_entry.pack(pady=(0, 15), padx=30)

        self.password_entry = ctk.CTkEntry(self.login_panel, placeholder_text="Contraseña", show="*", width=250, height=40, font=FONT_NORMAL, corner_radius=8)
        self.password_entry.pack(pady=(0, 5), padx=30)
        
        # Etiqueta de error (oculta inicialmente)
        self.error_label = ctk.CTkLabel(self.login_panel, text="", text_color=ERROR_COLOR, font=FONT_SMALL)
        self.error_label.pack(pady=(0, 10))

        # Botón de Login
        self.login_btn = ctk.CTkButton(self.login_panel, text="Ingresar", font=FONT_NORMAL_BOLD, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, height=40, width=250, corner_radius=8, command=self.attempt_login)
        self.login_btn.pack(pady=(0, 30), padx=30)

        # Bind enter key
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Por favor complete todos los campos")
            return
            
        # Llama al controlador
        self.controller.handle_login(username, password)

    def show_error(self, message):
        self.error_label.configure(text=message)
        
    def clear_error(self):
        self.error_label.configure(text="")
