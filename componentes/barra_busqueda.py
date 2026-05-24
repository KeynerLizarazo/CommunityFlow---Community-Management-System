import customtkinter as ctk
from config.style import *

class BarraBusquedaFiltros(ctk.CTkFrame):
    def __init__(self, master, filtros=None, comando_busqueda=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.comando_busqueda = comando_busqueda
        self._timer_busqueda = None
        
        # Búsqueda de texto
        self.entry_busqueda = ctk.CTkEntry(
            self, 
            placeholder_text="Buscar...", 
            width=300, 
            height=40,
            font=FUENTE_CUERPO
        )
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", self._on_key_release)
        self.entry_busqueda.bind("<Return>", self._ejecutar_busqueda)
        
        # Filtros adicionales
        self.comboboxes = {}
        if filtros:
            for nombre, opciones in filtros.items():
                combo = ctk.CTkComboBox(
                    self, 
                    values=opciones,
                    width=150,
                    height=40,
                    font=FUENTE_CUERPO,
                    command=self._ejecutar_busqueda
                )
                combo.set(f"Filtrar {nombre}")
                combo.pack(side="left", padx=5)
                self.comboboxes[nombre] = combo
                
        # Botón buscar
        self.btn_buscar = ctk.CTkButton(
            self,
            text="Buscar",
            width=100,
            height=40,
            fg_color=COLOR_ACENTO,
            hover_color=COLOR_HOVER,
            command=self._ejecutar_busqueda
        )
        self.btn_buscar.pack(side="left", padx=10)

    def _on_key_release(self, event):
        # Debounce logic: wait 500ms before executing search
        if self._timer_busqueda is not None:
            self.after_cancel(self._timer_busqueda)
        self._timer_busqueda = self.after(500, self._ejecutar_busqueda)

    def _ejecutar_busqueda(self, *args):
        if self.comando_busqueda:
            texto = self.entry_busqueda.get()
            filtros_activos = {}
            for nombre, combo in self.comboboxes.items():
                val = combo.get()
                if val and not val.startswith("Filtrar"):
                    filtros_activos[nombre] = val
            self.comando_busqueda(texto, filtros_activos)
