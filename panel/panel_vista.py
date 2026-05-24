"""
panel/panel_vista.py – Ventana principal de CommunityFlow
Sidebar + TopAppBar + área de contenido intercambiable.
"""
import importlib
import customtkinter as ctk
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from config.auth_session import AuthSession


# ─── Constantes de sidebar ────────────────────────────────────────────────────
SIDEBAR_W = 250
NAV_ITEMS = [
    ("  Dashboard",   "Dashboard"),
    ("  Censo",       "Censo"),
    ("  Voceria",     "Voceria"),
    ("  Finanzas",    "Finanzas"),
    ("  Proyectos",   "Proyectos"),
    ("  Bitacora",    "Bitacora"),
    ("  Documentos",  "Documentos"),
]

MODULE_MAP = {
    "Censo":       ("familias.familias_vista",   "FamiliasVista"),
    "Voceria":     ("voceros.voceros_vista",      "VocerosVista"),
    "Finanzas":    ("finanzas.finanzas_vista",    "FinanzasVista"),
    "Proyectos":   ("proyectos.proyectos_vista",  "ProyectosVista"),
    "Bitacora":    ("bitacora.bitacora_vista",    "BitacoraVista"),
    "Documentos":  ("documentos.documentos_vista","DocumentosVista"),
    "Configuracion":("autenticacion.usuarios_admin_vista", "UsuariosAdminVista"),
}


class PanelVista(ctk.CTkToplevel):
    """Ventana principal post-login."""

    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.usuario = AuthSession.get_usuario()
        self.modulo_activo = None

        aplicar_estilo_tabla()

        self.title("CommunityFlow – Consejo Comunal La Pedregosa")
        self.geometry("1400x820")
        self.state("zoomed")
        self.configure(fg_color=COLORS["surface"])
        self.protocol("WM_DELETE_WINDOW", self._cerrar_app)

        self._build_layout()
        self.navegar("Dashboard")

    # ─── Layout raíz ─────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_rowconfigure(0, weight=0)   # topbar
        self.grid_rowconfigure(1, weight=1)   # contenido
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # main

        self._build_sidebar()
        self._build_topbar()
        self._build_content_area()

    # ─── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_W, fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(99, weight=1)  # empuja cerrar-sesión abajo

        # Logo / título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(24, 8), sticky="ew")

        ctk.CTkLabel(
            logo_frame, text="CF", font=("Inter", 26, "bold"),
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            width=44, height=44, corner_radius=12,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            logo_frame, text="CommunityFlow",
            font=FONTS["headline_sm"], text_color=COLORS["sidebar_text"],
        ).pack(side="left")

        # Separador
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=COLORS["sidebar_active"]
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        # Etiqueta sección
        ctk.CTkLabel(
            self.sidebar, text="MÓDULOS",
            font=FONTS["label_caps"], text_color=COLORS["sidebar_text_muted"],
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(4, 2))

        # Botones de navegación
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for row_idx, (label, key) in enumerate(NAV_ITEMS, start=3):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                hover_color=COLORS["sidebar_active"],
                font=FONTS["body_base"],
                height=40,
                corner_radius=CORNER_RADIUS["button"],
                command=lambda k=key: self.navegar(k),
            )
            btn.grid(row=row_idx, column=0, sticky="ew", padx=10, pady=2)
            self._nav_buttons[key] = btn

        # Botón Configuración (solo admin)
        if getattr(self.usuario, "rol", "") == "Admin":
            btn_cfg = ctk.CTkButton(
                self.sidebar, text="  Configuracion", anchor="w",
                fg_color="transparent",
                text_color=COLORS["sidebar_text"],
                hover_color=COLORS["sidebar_active"],
                font=FONTS["body_base"],
                height=40,
                corner_radius=CORNER_RADIUS["button"],
                command=lambda: self.navegar("Configuracion"),
            )
            btn_cfg.grid(row=99, column=0, sticky="ew", padx=10, pady=2)
            self._nav_buttons["Configuracion"] = btn_cfg

        # Cerrar sesión
        ctk.CTkButton(
            self.sidebar, text="  Cerrar Sesion", anchor="w",
            fg_color=COLORS["error"],
            text_color=COLORS["on_primary"],
            hover_color="#B71C1C",
            font=FONTS["body_bold"],
            height=40,
            corner_radius=CORNER_RADIUS["button"],
            command=self._cerrar_sesion,
        ).grid(row=100, column=0, sticky="ew", padx=10, pady=(4, 20))

    # ─── TopAppBar ───────────────────────────────────────────────────────────
    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(
            self, fg_color=COLORS["surface_lowest"], height=60,
            corner_radius=0,
        )
        self.topbar.grid(row=0, column=1, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(1, weight=1)

        # Breadcrumb / título de módulo
        self.lbl_modulo = ctk.CTkLabel(
            self.topbar, text="Dashboard",
            font=FONTS["headline_sm"], text_color=COLORS["neutral"],
        )
        self.lbl_modulo.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Buscador global
        self.txt_busqueda = ctk.CTkEntry(
            self.topbar,
            placeholder_text="Buscar en el sistema...",
            width=280, height=36,
            font=FONTS["body_base"],
            corner_radius=CORNER_RADIUS["input"],
            fg_color=COLORS["surface_high"],
            border_color=COLORS["outline_variant"],
        )
        self.txt_busqueda.grid(row=0, column=1, padx=20, pady=12, sticky="")

        # Panel usuario
        user_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        user_frame.grid(row=0, column=2, padx=20, sticky="e")

        nombre = getattr(self.usuario, "nombre_completo", None) or getattr(self.usuario, "nombre_usuario", "Usuario")
        iniciales = "".join(p[0].upper() for p in nombre.split()[:2])

        ctk.CTkLabel(
            user_frame, text=iniciales,
            font=FONTS["body_bold"],
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            width=36, height=36, corner_radius=18,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            user_frame, text=nombre,
            font=FONTS["body_bold"], text_color=COLORS["neutral"],
        ).pack(side="left")

        # Separador inferior
        ctk.CTkFrame(
            self.topbar, height=1, fg_color=COLORS["outline_variant"]
        ).place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

    # ─── Área de contenido ───────────────────────────────────────────────────
    def _build_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["surface"],
            corner_radius=0,
        )
        self.content.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

    # ─── Navegación ──────────────────────────────────────────────────────────
    def navegar(self, key: str):
        if key == self.modulo_activo:
            return

        self.modulo_activo = key
        self.lbl_modulo.configure(text=key)

        # Resaltar botón activo
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["on_primary"],
                    font=FONTS["body_bold"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["sidebar_text"],
                    font=FONTS["body_base"],
                )

        # Limpiar contenido
        for w in self.content.winfo_children():
            w.destroy()

        if key == "Dashboard":
            from panel.dashboard_vista import DashboardVista
            DashboardVista(self.content)
            return

        if key in MODULE_MAP:
            mod_path, class_name = MODULE_MAP[key]
            try:
                mod = importlib.import_module(mod_path)
                clase = getattr(mod, class_name)
                clase(self.content)
            except Exception as exc:
                self._mostrar_error(str(exc))
        else:
            self._mostrar_error(f"Módulo '{key}' no encontrado.")

    def _mostrar_error(self, msg: str):
        ctk.CTkLabel(
            self.content, text=f"Error: {msg}",
            text_color=COLORS["error"], font=FONTS["body_base"],
        ).pack(expand=True, pady=40)

    # ─── Sesión / cierre ─────────────────────────────────────────────────────
    def _cerrar_sesion(self):
        AuthSession.clear()
        self.destroy()
        self.login_window.deiconify()

    def _cerrar_app(self):
        self.destroy()
        self.login_window.destroy()

    # Alias compat
    cerrar_sesion = _cerrar_sesion
    cerrar_app    = _cerrar_app
