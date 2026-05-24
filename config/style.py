# config/style.py – Sistema de diseño CommunityFlow
# Paleta Material Design 3 adaptada
import customtkinter as ctk

# ─── Colores ───────────────────────────────────────────────────────────────────
COLORS = {
    # Primario
    "primary":                  "#00BCD4",
    "primary_container":        "#00ACC1",
    "on_primary":               "#FFFFFF",
    # Secundario
    "secondary":                "#0097A7",
    "secondary_container":      "#80DEEA",
    "on_secondary_container":   "#003545",
    # Terciario
    "tertiary":                 "#43A047",
    "tertiary_container":       "#81C784",
    "on_tertiary_container":    "#003300",
    # Neutros
    "neutral":                  "#212121",
    "on_surface_variant":       "#757575",
    # Superficies
    "surface":                  "#FAFAFA",
    "surface_lowest":           "#FFFFFF",
    "surface_high":             "#EEEEEE",
    # Borde
    "outline_variant":          "#BDBDBD",
    # Estados
    "error":                    "#D32F2F",
    "error_container":          "#FFCDD2",
    "success":                  "#43A047",
    "warning":                  "#F57C00",
    # Sidebar
    "sidebar_bg":               "#006064",
    "sidebar_active":           "#00838F",
    "sidebar_text":             "#E0F7FA",
    "sidebar_text_muted":       "#80DEEA",
}

# Atajos semánticos para backward-compat con código antiguo
COLOR_ACENTO    = COLORS["primary"]
COLOR_HOVER     = COLORS["primary_container"]
COLOR_SIDEBAR   = COLORS["surface_high"]
COLOR_CONTENIDO = COLORS["surface_lowest"]
COLOR_TEXTO     = COLORS["neutral"]
COLOR_ERROR     = COLORS["error"]
COLOR_EXITO     = COLORS["success"]

# ─── Tipografía ────────────────────────────────────────────────────────────────
FONTS = {
    "display_lg":   ("Inter", 32, "bold"),
    "headline_md":  ("Inter", 24, "bold"),
    "headline_sm":  ("Inter", 18, "bold"),
    "body_bold":    ("Inter", 14, "bold"),
    "body_base":    ("Inter", 14),
    "label_caps":   ("Inter", 12, "bold"),
    "helper_text":  ("Inter", 12),
}

# Atajos semánticos
FUENTE_TITULO    = FONTS["headline_md"]
FUENTE_SUBTITULO = FONTS["headline_sm"]
FUENTE_CUERPO    = FONTS["body_base"]

# ─── Espaciado ─────────────────────────────────────────────────────────────────
PADDING = {
    "xs":   4,
    "sm":   8,
    "md":   15,
    "lg":   20,
    "xl":   30,
}

# ─── Radios ────────────────────────────────────────────────────────────────────
CORNER_RADIUS = {
    "card":   12,
    "input":  8,
    "button": 8,
    "chip":   16,
}

# ─── Estilos ttk ──────────────────────────────────────────────────────────────
def aplicar_estilo_tabla():
    """Aplica estilo Material al ttk.Treeview global."""
    from tkinter import ttk
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "CF.Treeview",
        background=COLORS["surface_lowest"],
        foreground=COLORS["neutral"],
        fieldbackground=COLORS["surface_lowest"],
        rowheight=36,
        font=FONTS["body_base"],
        borderwidth=0,
    )
    style.configure(
        "CF.Treeview.Heading",
        background=COLORS["surface_high"],
        foreground=COLORS["neutral"],
        font=FONTS["body_bold"],
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "CF.Treeview",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", COLORS["on_primary"])],
    )

# ─── Tema ──────────────────────────────────────────────────────────────────────
def configurar_tema():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
