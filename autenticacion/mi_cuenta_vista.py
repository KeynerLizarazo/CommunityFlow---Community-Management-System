import customtkinter as ctk
from config.style import *
from autenticacion.usuario_modelo import UsuarioModelo
from config.auth_session import AuthSession
from bitacora.bitacora_modelo import BitacoraModelo

class MiCuentaVista(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.usuario_data = AuthSession.get_usuario()
        self.modelo = UsuarioModelo()
        
        self.title("Mi Cuenta")
        self.geometry("500x450")
        self.resizable(False, False)
        self.grab_set() # Modal
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color=COLOR_CONTENIDO)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=40, pady=20, sticky="nsew")
        
        lbl_titulo = ctk.CTkLabel(frame, text="Ajustes de Cuenta", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=(0, 20))

        # Nombre y Rol
        lbl_rol = ctk.CTkLabel(frame, text=f"Rol actual: {self.usuario_data.rol}", font=FUENTE_SUBTITULO, text_color=COLOR_ACENTO)
        lbl_rol.pack(anchor="w", pady=(0, 10))

        # Usuario
        lbl_user = ctk.CTkLabel(frame, text="Nombre de usuario actual:", font=FUENTE_CUERPO, text_color=COLOR_TEXTO)
        lbl_user.pack(anchor="w")
        
        self.txt_usuario = ctk.CTkEntry(frame, height=35, font=FUENTE_CUERPO)
        self.txt_usuario.insert(0, self.usuario_data.nombre_usuario)
        self.txt_usuario.pack(fill="x", pady=(0, 10))
        
        btn_cambiar_user = ctk.CTkButton(
            frame, 
            text="Actualizar Usuario", 
            fg_color=COLOR_ACENTO, 
            hover_color=COLOR_HOVER,
            command=self.cambiar_usuario
        )
        btn_cambiar_user.pack(fill="x", pady=(0, 20))

        # Separador
        sep = ctk.CTkFrame(frame, height=2, fg_color=COLOR_SIDEBAR)
        sep.pack(fill="x", pady=(0, 20))

        # Contraseña
        lbl_pass_actual = ctk.CTkLabel(frame, text="Contraseña actual:", font=FUENTE_CUERPO, text_color=COLOR_TEXTO)
        lbl_pass_actual.pack(anchor="w")
        self.txt_pass_actual = ctk.CTkEntry(frame, show="*", height=35, font=FUENTE_CUERPO)
        self.txt_pass_actual.pack(fill="x", pady=(0, 10))

        lbl_pass_nueva = ctk.CTkLabel(frame, text="Nueva contraseña:", font=FUENTE_CUERPO, text_color=COLOR_TEXTO)
        lbl_pass_nueva.pack(anchor="w")
        self.txt_pass_nueva = ctk.CTkEntry(frame, show="*", height=35, font=FUENTE_CUERPO)
        self.txt_pass_nueva.pack(fill="x", pady=(0, 10))

        btn_cambiar_pass = ctk.CTkButton(
            frame, 
            text="Actualizar Contraseña", 
            fg_color=COLOR_ACENTO, 
            hover_color=COLOR_HOVER,
            command=self.cambiar_contrasena
        )
        btn_cambiar_pass.pack(fill="x", pady=(0, 10))
        
        self.lbl_mensaje = ctk.CTkLabel(frame, text="", font=("Inter", 12))
        self.lbl_mensaje.pack()

    def cambiar_usuario(self):
        nuevo = self.txt_usuario.get().strip()
        if " " in nuevo or len(nuevo) > 30 or not nuevo:
            self.lbl_mensaje.configure(text="Usuario inválido (sin espacios, max 30 carac.).", text_color=COLOR_ERROR)
            return
            
        if self.modelo.cambiar_usuario(self.usuario_data.id_usuario, nuevo):
            self.lbl_mensaje.configure(text="Usuario actualizado.", text_color=COLOR_EXITO)
            # Log action
            BitacoraModelo.registrar_accion(
                usuario_id=self.usuario_data.id_usuario,
                modulo="Mi Cuenta",
                accion="editar",
                registro_id=str(self.usuario_data.id_usuario),
                datos_previos={"nombre_usuario": self.usuario_data.nombre_usuario},
                datos_nuevos={"nombre_usuario": nuevo}
            )
            self.usuario_data.nombre_usuario = nuevo
        else:
            self.lbl_mensaje.configure(text="Error, el usuario ya existe.", text_color=COLOR_ERROR)

    def cambiar_contrasena(self):
        actual = self.txt_pass_actual.get()
        nueva = self.txt_pass_nueva.get()
        
        if not actual or not nueva or len(nueva) > 30 or len(nueva) < 6:
            self.lbl_mensaje.configure(text="Campos inválidos (mínimo 6 caracteres).", text_color=COLOR_ERROR)
            return
            
        if self.modelo.cambiar_contrasena(self.usuario_data.id_usuario, actual, nueva):
            self.lbl_mensaje.configure(text="Contraseña actualizada.", text_color=COLOR_EXITO)
            self.txt_pass_actual.delete(0, 'end')
            self.txt_pass_nueva.delete(0, 'end')
            
            # Log action
            BitacoraModelo.registrar_accion(
                usuario_id=self.usuario_data.id_usuario,
                modulo="Mi Cuenta",
                accion="editar",
                registro_id=str(self.usuario_data.id_usuario)
            )
        else:
            self.lbl_mensaje.configure(text="Contraseña actual incorrecta.", text_color=COLOR_ERROR)
