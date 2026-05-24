"""
bitacora/bitacora_vista.py – Historial de actividad del sistema.
"""
import customtkinter as ctk
from tkinter import ttk
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from bitacora.bitacora_modelo import BitacoraModelo


ACCION_COLOR = {
    "crear":    COLORS["tertiary"],
    "editar":   COLORS["warning"],
    "eliminar": COLORS["error"],
}


class BitacoraVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self.modelo = BitacoraModelo()
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # Encabezado
        ctk.CTkLabel(self, text="Historial de Actividad",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(
            anchor="w", pady=(0, PADDING["lg"]))

        # Filtros
        filtro = ctk.CTkFrame(self, fg_color=COLORS["surface_high"],
                              corner_radius=CORNER_RADIUS["input"])
        filtro.pack(fill="x", pady=(0, PADDING["md"]))

        ctk.CTkLabel(filtro, text="Modulo:", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(side="left", padx=(12, 4))
        self.opt_modulo = ctk.CTkOptionMenu(
            filtro,
            values=["Todos", "Habitantes", "Familias", "Finanzas",
                    "Proyectos", "Voceros", "Mi Cuenta"],
            width=150, font=FONTS["body_base"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            command=lambda _: self._cargar_datos(),
        )
        self.opt_modulo.pack(side="left", padx=8, pady=8)

        ctk.CTkLabel(filtro, text="Accion:", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(side="left", padx=(8, 4))
        self.opt_accion = ctk.CTkOptionMenu(
            filtro, values=["Todas", "crear", "editar", "eliminar"],
            width=120, font=FONTS["body_base"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            command=lambda _: self._cargar_datos(),
        )
        self.opt_accion.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            filtro, text="Actualizar", width=100, height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"], font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._cargar_datos,
        ).pack(side="right", padx=12, pady=8)

        # Tabla
        card = ctk.CTkFrame(
            self, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        card.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(hdr, text="Registro de Actividad",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(side="left")
        self.lbl_conteo = ctk.CTkLabel(hdr, text="", font=FONTS["helper_text"],
                                       text_color=COLORS["on_surface_variant"])
        self.lbl_conteo.pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x")

        cols = ("Fecha/Hora", "Usuario", "Modulo", "Accion", "Registro")
        self.tabla = ttk.Treeview(card, columns=cols, show="headings",
                                  style="CF.Treeview")
        anchos = {"Fecha/Hora": 160, "Usuario": 150, "Modulo": 140,
                  "Accion": 90, "Registro": 100}
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=anchos[col])

        for accion, color in ACCION_COLOR.items():
            self.tabla.tag_configure(accion, foreground=color)

        sb = ttk.Scrollbar(card, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))

    def _cargar_datos(self):
        modulo = self.opt_modulo.get()
        accion = self.opt_accion.get()
        registros = self.modelo.obtener_registros(
            modulo=None if modulo == "Todos" else modulo,
            accion=None if accion == "Todas" else accion,
            limite=500,
        )
        self.lbl_conteo.configure(text=f"{len(registros)} registros")
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for r in registros:
            tag = r.get("accion", "")
            self.tabla.insert("", "end", values=(
                r.get("fecha_hora", ""),
                r.get("usuario_nombre", ""),
                r.get("modulo", ""),
                r.get("accion", ""),
                r.get("registro_id", "—"),
            ), tags=(tag,))
