import customtkinter as ctk
from controllers.main_controller import MainController

# Configuración básica de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # Temas por defecto: "blue", "dark-blue", "green"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión Comunitaria")
        self.geometry("1000x600")
        self.minsize(800, 500)
        
        # Inicializar el controlador principal
        self.controller = MainController(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()
