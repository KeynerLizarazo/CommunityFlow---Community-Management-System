import customtkinter as ctk
from tkinter import ttk
from config.style import *
from componentes.barra_busqueda import BarraBusquedaFiltros
from finanzas.finanzas_modelo import FinanzasModelo

class FinanzasVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CONTENIDO, **kwargs)
        self.pack(fill="both", expand=True)
        self.modelo = FinanzasModelo()
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        lbl_titulo = ctk.CTkLabel(self, text="Finanzas y Recursos", font=("Inter", 24, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(anchor="w", pady=(0, 20))

        self.barra_busqueda = BarraBusquedaFiltros(self, filtros={"Tipo": ["Ingreso", "Egreso"]}, comando_busqueda=self.buscar)
        self.barra_busqueda.pack(fill="x", pady=(0, 20))
        
        self.lbl_balance = ctk.CTkLabel(self, text="Balance Actual: $0.00", font=("Inter", 20, "bold"), text_color=COLOR_ACENTO)
        self.lbl_balance.pack(anchor="w", pady=(0, 20))

        style = ttk.Style()
        style.configure("Treeview", background="#FFFFFF", foreground=COLOR_TEXTO, rowheight=30, font=FUENTE_CUERPO)
        style.configure("Treeview.Heading", background=COLOR_SIDEBAR, foreground="#FFFFFF", font=FUENTE_SUBTITULO)
        style.map('Treeview', background=[('selected', COLOR_ACENTO)])

        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("ID", "Fecha", "Tipo", "Concepto", "Monto")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargar_datos(self):
        balance = self.modelo.obtener_balance()
        self.lbl_balance.configure(text=f"Balance Actual: ${balance:.2f}")
        
        movs = self.modelo.obtener_movimientos()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for m in movs:
            self.tabla.insert("", "end", values=(m.id_movimiento, m.fecha, m.tipo, m.concepto, f"${m.monto:.2f}"))

    def buscar(self, texto, filtros):
        pass
