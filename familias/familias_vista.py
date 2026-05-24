import customtkinter as ctk
from tkinter import ttk
from config.style import *
from componentes.barra_busqueda import BarraBusquedaFiltros
from familias.familias_modelo import FamiliaModelo

class FamiliasVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CONTENIDO, **kwargs)
        self.pack(fill="both", expand=True)
        self.modelo = FamiliaModelo()
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        lbl_titulo = ctk.CTkLabel(self, text="Gestión de Familias", font=("Inter", 24, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(anchor="w", pady=(0, 20))

        self.barra_busqueda = BarraBusquedaFiltros(self, comando_busqueda=self.buscar)
        self.barra_busqueda.pack(fill="x", pady=(0, 20))

        style = ttk.Style()
        style.configure("Treeview", background="#FFFFFF", foreground=COLOR_TEXTO, rowheight=30, font=FUENTE_CUERPO)
        style.configure("Treeview.Heading", background=COLOR_SIDEBAR, foreground="#FFFFFF", font=FUENTE_SUBTITULO)
        style.map('Treeview', background=[('selected', COLOR_ACENTO)])

        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("ID", "Código", "Jefe de Familia", "Dirección", "Teléfono")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tabla.bind("<Double-1>", self.on_doble_clic)

    def cargar_datos(self):
        familias = self.modelo.obtener_todas()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for f in familias:
            jefe_nombre = f"{f.jefe.nombres} {f.jefe.apellidos}" if f.jefe else "Sin asignar"
            self.tabla.insert("", "end", values=(f.id_familia, f.codigo_familia, jefe_nombre, f.direccion, f.telefono))

    def buscar(self, texto, filtros):
        # Implementar filtro local para demostración
        pass

    def on_doble_clic(self, event):
        item = self.tabla.selection()[0]
        id_familia = self.tabla.item(item, "values")[0]
        # Aquí se cargaría la vista de habitantes filtrada por familia_id
        # Ejemplo:
        # from habitantes.habitantes_vista import HabitantesVista
        # self.pack_forget()
        # HabitantesVista(self.master, familia_id=id_familia)
