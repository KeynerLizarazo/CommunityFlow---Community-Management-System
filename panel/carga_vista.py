import customtkinter as ctk
from config.style import *
from panel.panel_vista import PanelVista

class CargaVista(ctk.CTkToplevel):
    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        self.parent = parent
        self.usuario_data = usuario_data
        
        self.geometry("300x150")
        self.overrideredirect(True) # Sin bordes
        self.configure(fg_color=COLOR_CONTENIDO)
        
        # Center window
        self.update_idletasks()
        width = 300
        height = 150
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure((0,1,2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(self, text="Cargando...", font=("Inter", 18, "bold"), text_color=COLOR_ACENTO)
        lbl.grid(row=1, column=0)

        self.progress = ctk.CTkProgressBar(self, fg_color=COLOR_SIDEBAR, progress_color=COLOR_ACENTO, mode="indeterminado")
        self.progress.grid(row=2, column=0, padx=20, sticky="ew")

    def iniciar(self):
        self.progress.start()
        # Simular carga de 1.5 segundos
        self.after(1500, self.finalizar_carga)

    def finalizar_carga(self):
        self.progress.stop()
        self.destroy()
        self.parent.destroy() # Destruir login
        panel = PanelVista(self.usuario_data)
        panel.show()
