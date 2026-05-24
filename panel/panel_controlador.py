import importlib

class PanelControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modulo_actual = None

    def cargar_modulo(self, nombre_modulo):
        # Limpiar área de contenido
        for widget in self.vista.area_contenido.winfo_children():
            widget.destroy()

        if nombre_modulo == "Panel":
            from customtkinter import CTkLabel
            from config.style import FUENTE_TITULO, COLOR_TEXTO
            lbl = CTkLabel(self.vista.area_contenido, text="Bienvenido al Panel de Control", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
            lbl.pack(expand=True)
            return

        if nombre_modulo == "Mi cuenta":
            from autenticacion.mi_cuenta_vista import MiCuentaVista
            MiCuentaVista(self.vista)
            return

        try:
            # Importación dinámica del módulo
            modulo = importlib.import_module(f"{nombre_modulo.lower()}.{nombre_modulo.lower()}_vista")
            clase_vista = getattr(modulo, f"{nombre_modulo.capitalize()}Vista")
            # Instanciar la vista del módulo, pasándole el frame contenedor
            clase_vista(self.vista.area_contenido)
        except Exception as e:
            from customtkinter import CTkLabel
            from config.style import COLOR_ERROR
            print(e)
            lbl = CTkLabel(self.vista.area_contenido, text=f"Error cargando módulo {nombre_modulo}", text_color=COLOR_ERROR)
            lbl.pack(expand=True)

    def cerrar_sesion(self):
        self.vista.destroy()
        from autenticacion.login_vista import LoginVista
        login = LoginVista()
        login.mainloop()
