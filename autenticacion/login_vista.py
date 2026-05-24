import customtkinter as ctk
from config.style import *
from config.auth_session import AuthSession
from panel.panel_vista import PanelVista
from autenticacion.login_controlador import LoginControlador

class LoginVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inicio de Sesión")
        self.geometry("1024x768")
        self.state('zoomed')
        self.configure(fg_color=COLOR_CONTENIDO)
        
        self.controlador = LoginControlador(self)
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        # Panel izquierdo (Sidebar estético)
        self.panel_izq = ctk.CTkFrame(self, fg_color=COLOR_HOVER, corner_radius=0)
        self.panel_izq.grid(row=0, column=0, sticky="nsew")
        self.panel_izq.grid_rowconfigure(0, weight=1)
        self.panel_izq.grid_columnconfigure(0, weight=1)

        self.lbl_titulo_izq = ctk.CTkLabel(
            self.panel_izq, 
            text="Consejo Comunal\nLa Pedregosa", 
            font=("Inter", 36, "bold"), 
            text_color="#FFFFFF",
            justify="center"
        )
        self.lbl_titulo_izq.grid(row=0, column=0)

        # Panel derecho (Formulario)
        self.panel_der = ctk.CTkFrame(self, fg_color=COLOR_CONTENIDO, corner_radius=0)
        self.panel_der.grid(row=0, column=1, sticky="nsew")
        
        self.panel_der.grid_rowconfigure(0, weight=1)
        self.panel_der.grid_rowconfigure(2, weight=1)
        self.panel_der.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(self.panel_der, fg_color="transparent")
        form_frame.grid(row=1, column=0, padx=100)

        lbl_titulo_der = ctk.CTkLabel(form_frame, text="Iniciar Sesión", font=("Inter", 32, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo_der.pack(anchor="w", pady=(0, 30))

        # Campo Usuario
        lbl_usuario = ctk.CTkLabel(form_frame, text="Nombre de Usuario", font=FUENTE_SUBTITULO, text_color=COLOR_TEXTO)
        lbl_usuario.pack(anchor="w", pady=(0, 5))
        self.txt_usuario = ctk.CTkEntry(form_frame, placeholder_text="Ingrese su usuario", height=50, font=FUENTE_CUERPO, width=400)
        self.txt_usuario.pack(fill="x", pady=(0, 5))
        self.txt_usuario.bind("<Return>", lambda e: self.txt_contrasena.focus())

        self.lbl_error_usuario = ctk.CTkLabel(form_frame, text="", text_color=COLOR_ERROR, font=("Inter", 12))
        self.lbl_error_usuario.pack(anchor="w", pady=(0, 10))

        # Campo Contraseña
        lbl_contrasena = ctk.CTkLabel(form_frame, text="Contraseña", font=FUENTE_SUBTITULO, text_color=COLOR_TEXTO)
        lbl_contrasena.pack(anchor="w", pady=(0, 5))
        self.txt_contrasena = ctk.CTkEntry(form_frame, placeholder_text="Ingrese su contraseña", show="*", height=50, font=FUENTE_CUERPO, width=400)
        self.txt_contrasena.pack(fill="x", pady=(0, 5))
        self.txt_contrasena.bind("<Return>", lambda e: self.ejecutar_intentar_login())

        self.lbl_error_contrasena = ctk.CTkLabel(form_frame, text="", text_color=COLOR_ERROR, font=("Inter", 12))
        self.lbl_error_contrasena.pack(anchor="w", pady=(0, 10))

        # Mostrar contraseña checkbox
        self.chk_mostrar = ctk.CTkCheckBox(form_frame, text="Mostrar contraseña", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, command=self.toggle_password, font=FUENTE_CUERPO, text_color=COLOR_TEXTO)
        self.chk_mostrar.pack(anchor="w", pady=(0, 30))

        # Botón Login
        self.btn_login = ctk.CTkButton(form_frame, text="Ingresar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, height=50, font=FUENTE_SUBTITULO, command=self.ejecutar_intentar_login)
        self.btn_login.pack(fill="x")

    def toggle_password(self):
        if self.chk_mostrar.get() == 1:
            self.txt_contrasena.configure(show="")
        else:
            self.txt_contrasena.configure(show="*")

    def ejecutar_intentar_login(self):
        self.lbl_error_usuario.configure(text="")
        self.lbl_error_contrasena.configure(text="")
        
        usuario = self.txt_usuario.get().strip()
        contrasena = self.txt_contrasena.get()
        
        self.controlador.intentar_login(usuario, contrasena)

    def mostrar_error_usuario(self, mensaje):
        self.lbl_error_usuario.configure(text=mensaje)

    def mostrar_error_contrasena(self, mensaje):
        self.lbl_error_contrasena.configure(text=mensaje)

    def limpiar_campos_fallo_usuario(self):
        self.txt_usuario.delete(0, 'end')
        self.txt_contrasena.delete(0, 'end')
        self.txt_usuario.focus()

    def limpiar_campos_fallo_contrasena(self):
        self.txt_contrasena.delete(0, 'end')
        self.txt_contrasena.focus()

    def bloquear_boton(self, segundos):
        self.btn_login.configure(state="disabled")
        self.actualizar_boton_bloqueo(segundos)

    def actualizar_boton_bloqueo(self, segundos):
        if segundos > 0:
            self.btn_login.configure(text=f"Bloqueado ({segundos}s)")
            self.after(1000, lambda: self.actualizar_boton_bloqueo(segundos - 1))
        else:
            self.btn_login.configure(state="normal", text="Ingresar")

    def mostrar_carga(self, usuario_data):
        AuthSession.set_usuario(usuario_data)
        if usuario_data.cambio_password_obligatorio:
            self.mostrar_cambio_password(usuario_data.id_usuario)
        else:
            self.abrir_panel()

    def mostrar_cambio_password(self, id_usuario):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cambio de Contraseña Obligatorio")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Centrar
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        lbl_titulo = ctk.CTkLabel(dialog, text="Por seguridad, debe cambiar\nla contraseña por defecto", font=("Inter", 20, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=20)

        txt_nueva = ctk.CTkEntry(dialog, placeholder_text="Nueva contraseña", show="*", height=40, font=FUENTE_CUERPO, width=300)
        txt_nueva.pack(pady=10)

        txt_confirmar = ctk.CTkEntry(dialog, placeholder_text="Confirmar nueva contraseña", show="*", height=40, font=FUENTE_CUERPO, width=300)
        txt_confirmar.pack(pady=10)

        lbl_error = ctk.CTkLabel(dialog, text="", text_color=COLOR_ERROR)
        lbl_error.pack()

        def guardar():
            n = txt_nueva.get()
            c = txt_confirmar.get()
            if not n or not c:
                lbl_error.configure(text="Ambos campos son requeridos")
                return
            if n != c:
                lbl_error.configure(text="Las contraseñas no coinciden")
                return
            if len(n) < 6:
                lbl_error.configure(text="Debe tener al menos 6 caracteres")
                return

            if self.controlador.modelo.forzar_cambio_contrasena(id_usuario, n):
                dialog.destroy()
                self.abrir_panel()
            else:
                lbl_error.configure(text="Error al cambiar la contraseña")

        btn_guardar = ctk.CTkButton(dialog, text="Guardar y Continuar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, height=40, command=guardar)
        btn_guardar.pack(pady=20)

    def abrir_panel(self):
        self.withdraw()
        self.txt_usuario.delete(0, 'end')
        self.txt_contrasena.delete(0, 'end')
        panel = PanelVista(self)
        panel.mainloop()
