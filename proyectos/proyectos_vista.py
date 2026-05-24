import customtkinter as ctk
from tkinter import ttk
from config.style import *
from componentes.barra_busqueda import BarraBusquedaFiltros
from proyectos.proyectos_modelo import ProyectosModelo

class ProyectosVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CONTENIDO, **kwargs)
        self.pack(fill="both", expand=True)
        self.modelo = ProyectosModelo()
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        lbl_titulo = ctk.CTkLabel(self, text="Gestión de Proyectos", font=("Inter", 24, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(anchor="w", pady=(0, 20))

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("Activos")
        self.tabview.add("Pendientes")
        self.tabview.add("Finalizados")

        # Configurar cada pestaña (por simplicidad aquí mostramos cómo sería en una)
        for tab in ["Activos", "Pendientes", "Finalizados"]:
            frame = self.tabview.tab(tab)
            barra = BarraBusquedaFiltros(frame)
            barra.pack(fill="x", pady=10)
            
            lbl = ctk.CTkLabel(frame, text=f"Proyectos {tab}", font=FUENTE_SUBTITULO)
            lbl.pack(pady=20)

    def cargar_datos(self):
        pass
