import customtkinter as ctk

def configurar_tema():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")  # We'll override specific colors in the views

# Paleta de colores globales
COLOR_ACENTO = "#00BCD4"
COLOR_HOVER = "#0097A7"
COLOR_SIDEBAR = "#F5F5F5"
COLOR_CONTENIDO = "#FFFFFF"
COLOR_TEXTO = "#212121"
COLOR_ERROR = "#E53935"
COLOR_EXITO = "#43A047"

# Fuentes
FUENTE_CUERPO = ("Inter", 14)
FUENTE_TITULO = ("Inter", 20, "bold")
FUENTE_SUBTITULO = ("Inter", 16, "bold")
