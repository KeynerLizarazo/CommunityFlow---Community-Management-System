import customtkinter as ctk
from config.style import *
from bitacora.bitacora_controlador import BitacoraControlador
from componentes.barra_busqueda import BarraBusquedaFiltros
from tkinter import ttk

class BitacoraVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CONTENIDO, **kwargs)
        self.pack(fill="both", expand=True)
        
        self.controlador = BitacoraControlador(self)
        self.setup_ui()
        self.controlador.cargar_datos()

    def setup_ui(self):
        lbl_titulo = ctk.CTkLabel(self, text="Bitácora de Acciones", font=("Inter", 24, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(anchor="w", pady=(0, 20))

        # Barra de búsqueda
        filtros = {
            "Módulo": ["Familias", "Habitantes", "Voceros", "Finanzas", "Proyectos", "Documentos"],
            "Acción": ["crear", "editar", "eliminar", "imprimir"]
        }
        self.barra_busqueda = BarraBusquedaFiltros(self, filtros=filtros, comando_busqueda=self.controlador.cargar_datos)
        self.barra_busqueda.pack(fill="x", pady=(0, 20))

        # Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#FFFFFF", foreground=COLOR_TEXTO, rowheight=30, fieldbackground="#FFFFFF", font=FUENTE_CUERPO)
        style.configure("Treeview.Heading", background=COLOR_SIDEBAR, foreground="#FFFFFF", font=FUENTE_SUBTITULO)
        style.map('Treeview', background=[('selected', COLOR_ACENTO)])

        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("ID", "Usuario", "Módulo", "Acción", "Fecha/Hora", "ID Registro")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mostrar_datos(self, datos):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for fila in datos:
            self.tabla.insert("", "end", values=fila)
