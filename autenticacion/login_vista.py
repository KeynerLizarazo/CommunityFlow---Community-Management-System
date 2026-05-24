"""
autenticacion/login_vista.py – Pantalla de login CommunityFlow.
Diseño split: panel izquierdo (branding) + panel derecho (formulario).
"""
import customtkinter as ctk
from config.style import COLORS, FONTS, CORNER_RADIUS
from config.auth_session import AuthSession
from autenticacion.login_controlador import LoginControlador


class LoginVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CommunityFlow – Inicio de Sesión")
        self.geometry("1024x680")
        self.state("zoomed")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.resizable(True, True)

        self.controlador = LoginControlador(self)
        self._build_ui()

    # ─── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        self._build_panel_izq()
        self._build_panel_der()

    def _build_panel_izq(self):
        panel = ctk.CTkFrame(self, fg_color=COLORS["sidebar_bg"], corner_radius=0)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.grid(row=0, column=0, padx=40)

        # Logo badge
        ctk.CTkLabel(
            inner, text="CF",
            font=("Inter", 48, "bold"),
            fg_color=COLORS["primary"],
            text_color=COLORS["on_primary"],
            width=90, height=90,
            corner_radius=18,
        ).pack(pady=(0, 24))

        ctk.CTkLabel(
            inner, text="CommunityFlow",
            font=FONTS["display_lg"], text_color=COLORS["sidebar_text"],
            justify="center",
        ).pack()

        ctk.CTkLabel(
            inner, text="Sistema de Gestión Comunal",
            font=FONTS["body_base"], text_color=COLORS["sidebar_text_muted"],
            justify="center",
        ).pack(pady=(8, 32))

        # Decoración: tres chips informativos
        for txt in ["Censo Familiar", "Control Financiero", "Proyectos Comunales"]:
            chip = ctk.CTkFrame(
                inner, fg_color=COLORS["sidebar_active"],
                corner_radius=CORNER_RADIUS["chip"],
            )
            chip.pack(pady=4, fill="x")
            ctk.CTkLabel(
                chip, text=f"  ✓  {txt}",
                font=FONTS["body_base"],
                text_color=COLORS["sidebar_text"],
            ).pack(pady=6, padx=12, anchor="w")

    def _build_panel_der(self):
        panel = ctk.CTkFrame(self, fg_color=COLORS["surface_lowest"], corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.grid(row=1, column=0, padx=80)

        ctk.CTkLabel(
            form, text="Bienvenido de nuevo",
            font=FONTS["display_lg"], text_color=COLORS["neutral"],
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            form, text="Ingresa tus credenciales para continuar.",
            font=FONTS["body_base"], text_color=COLORS["on_surface_variant"],
        ).pack(anchor="w", pady=(0, 32))

        # Campo Usuario
        ctk.CTkLabel(form, text="Usuario", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_usuario = ctk.CTkEntry(
            form, placeholder_text="Ingrese su usuario",
            height=48, font=FONTS["body_base"], width=420,
            corner_radius=CORNER_RADIUS["input"],
            border_color=COLORS["outline_variant"],
        )
        self.txt_usuario.pack(fill="x", pady=(4, 2))
        self.txt_usuario.bind("<Return>", lambda e: self.txt_contrasena.focus())

        self.lbl_error_usuario = ctk.CTkLabel(
            form, text="", text_color=COLORS["error"], font=FONTS["helper_text"]
        )
        self.lbl_error_usuario.pack(anchor="w", pady=(0, 12))

        # Campo Contraseña
        ctk.CTkLabel(form, text="Contraseña", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_contrasena = ctk.CTkEntry(
            form, placeholder_text="Ingrese su contraseña",
            show="*", height=48, font=FONTS["body_base"], width=420,
            corner_radius=CORNER_RADIUS["input"],
            border_color=COLORS["outline_variant"],
        )
        self.txt_contrasena.pack(fill="x", pady=(4, 2))
        self.txt_contrasena.bind("<Return>", lambda e: self._ejecutar_login())

        self.lbl_error_contrasena = ctk.CTkLabel(
            form, text="", text_color=COLORS["error"], font=FONTS["helper_text"]
        )
        self.lbl_error_contrasena.pack(anchor="w", pady=(0, 8))

        # Mostrar contraseña
        self.chk_mostrar = ctk.CTkCheckBox(
            form, text="Mostrar contraseña",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_container"],
            font=FONTS["body_base"],
            text_color=COLORS["on_surface_variant"],
            command=self._toggle_password,
        )
        self.chk_mostrar.pack(anchor="w", pady=(0, 28))

        # Botón Login
        self.btn_login = ctk.CTkButton(
            form, text="Ingresar al sistema",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            height=50, font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._ejecutar_login,
        )
        self.btn_login.pack(fill="x")

        # Pie
        ctk.CTkLabel(
            form, text="Consejo Comunal La Pedregosa",
            font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
        ).pack(pady=(24, 0))

    # ─── Eventos ─────────────────────────────────────────────────────────────
    def _toggle_password(self):
        self.txt_contrasena.configure(
            show="" if self.chk_mostrar.get() == 1 else "*"
        )

    def _ejecutar_login(self):
        self.lbl_error_usuario.configure(text="")
        self.lbl_error_contrasena.configure(text="")
        self.controlador.intentar_login(
            self.txt_usuario.get().strip(),
            self.txt_contrasena.get(),
        )

    # ─── Métodos llamados por el controlador ─────────────────────────────────
    def mostrar_error_usuario(self, msg):
        self.lbl_error_usuario.configure(text=msg)

    def mostrar_error_contrasena(self, msg):
        self.lbl_error_contrasena.configure(text=msg)

    def limpiar_campos_fallo_usuario(self):
        self.txt_usuario.delete(0, "end")
        self.txt_contrasena.delete(0, "end")
        self.txt_usuario.focus()

    def limpiar_campos_fallo_contrasena(self):
        self.txt_contrasena.delete(0, "end")
        self.txt_contrasena.focus()

    def bloquear_boton(self, segundos: int):
        self.btn_login.configure(state="disabled")
        self._cuenta_regresiva(segundos)

    def _cuenta_regresiva(self, s: int):
        if s > 0:
            self.btn_login.configure(text=f"Bloqueado ({s}s)...")
            self.after(1000, lambda: self._cuenta_regresiva(s - 1))
        else:
            self.btn_login.configure(state="normal", text="Ingresar al sistema")

    def mostrar_carga(self, usuario_data):
        AuthSession.set_usuario(usuario_data)
        if usuario_data.cambio_password_obligatorio:
            self._mostrar_cambio_password(usuario_data.id_usuario)
        else:
            self._abrir_panel()

    def _mostrar_cambio_password(self, id_usuario: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cambio de Contraseña Obligatorio")
        dialog.geometry("500x460")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["surface_lowest"])

        dialog.update_idletasks()
        w, h = 500, 460
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        inner = ctk.CTkFrame(dialog, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=32)

        # Icono
        ctk.CTkLabel(
            inner, text="🔒",
            font=("Inter", 40),
            text_color=COLORS["primary"],
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            inner, text="Cambio de Contraseña Requerido",
            font=FONTS["headline_sm"], text_color=COLORS["neutral"],
        ).pack()

        ctk.CTkLabel(
            inner,
            text="Por seguridad, debes establecer una nueva contraseña\nantes de continuar.",
            font=FONTS["body_base"], text_color=COLORS["on_surface_variant"],
            justify="center",
        ).pack(pady=(8, 24))

        ctk.CTkLabel(inner, text="Nueva contraseña", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        txt_nueva = ctk.CTkEntry(
            inner, show="*", height=44, font=FONTS["body_base"],
            corner_radius=CORNER_RADIUS["input"],
        )
        txt_nueva.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(inner, text="Confirmar contraseña", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        txt_confirmar = ctk.CTkEntry(
            inner, show="*", height=44, font=FONTS["body_base"],
            corner_radius=CORNER_RADIUS["input"],
        )
        txt_confirmar.pack(fill="x", pady=(4, 12))

        lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                               font=FONTS["helper_text"])
        lbl_err.pack()

        def _guardar():
            n, c = txt_nueva.get(), txt_confirmar.get()
            if not n or not c:
                lbl_err.configure(text="Ambos campos son obligatorios.")
                return
            if n != c:
                lbl_err.configure(text="Las contraseñas no coinciden.")
                return
            if len(n) < 6:
                lbl_err.configure(text="Minimo 6 caracteres.")
                return
            if self.controlador.modelo.forzar_cambio_contrasena(id_usuario, n):
                dialog.destroy()
                self._abrir_panel()
            else:
                lbl_err.configure(text="Error al guardar. Intente de nuevo.")

        ctk.CTkButton(
            inner, text="Guardar y Continuar",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            height=46, font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=_guardar,
        ).pack(fill="x", pady=(16, 0))

    def _abrir_panel(self):
        self.withdraw()
        self.txt_usuario.delete(0, "end")
        self.txt_contrasena.delete(0, "end")
        from panel.panel_vista import PanelVista
        panel = PanelVista(self)
        panel.mainloop()

    # Alias compat
    ejecutar_intentar_login = _ejecutar_login
    toggle_password         = _toggle_password
    abrir_panel             = _abrir_panel
