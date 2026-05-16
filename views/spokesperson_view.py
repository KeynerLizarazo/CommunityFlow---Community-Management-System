import customtkinter as ctk
from views.style import *

class SpokespersonView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=BG_DARK)
        self.controller = controller

        # Título
        self.title = ctk.CTkLabel(self, text="Gestión de Voceros", font=FONT_TITLE, text_color=TEXT_MAIN)
        self.title.pack(anchor="w", pady=(0, 20))

        # Panel superior (Formulario)
        self.form_panel = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=10)
        self.form_panel.pack(fill="x", pady=(0, 20), ipady=10)

        # Campos del formulario (2x2 grid)
        self.form_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.nombre_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Nombre completo", font=FONT_NORMAL, height=35)
        self.nombre_entry.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="ew")

        self.cargo_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Cargo (ej. Finanzas, Contraloría)", font=FONT_NORMAL, height=35)
        self.cargo_entry.grid(row=0, column=2, columnspan=2, padx=15, pady=15, sticky="ew")

        self.tel_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Teléfono", font=FONT_NORMAL, height=35)
        self.tel_entry.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        self.correo_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Correo Electrónico", font=FONT_NORMAL, height=35)
        self.correo_entry.grid(row=1, column=2, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        # Botón guardar
        self.save_btn = ctk.CTkButton(self.form_panel, text="Registrar Vocero", font=FONT_NORMAL_BOLD, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, height=35, command=self.save_spokesperson)
        self.save_btn.grid(row=2, column=0, columnspan=4, padx=15, pady=(0, 10))
        
        self.msg_label = ctk.CTkLabel(self.form_panel, text="", font=FONT_SMALL)
        self.msg_label.grid(row=3, column=0, columnspan=4)

        # Panel inferior (Lista)
        self.list_panel = ctk.CTkScrollableFrame(self, fg_color=BG_PANEL, corner_radius=10)
        self.list_panel.pack(fill="both", expand=True)

        self.load_list()

    def load_list(self):
        # Limpiar lista actual
        for widget in self.list_panel.winfo_children():
            widget.destroy()

        # Encabezados
        headers = ["ID", "Nombre", "Cargo", "Teléfono", "Correo"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.list_panel, text=h, font=FONT_NORMAL_BOLD, text_color=PRIMARY_COLOR)
            lbl.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            self.list_panel.grid_columnconfigure(i, weight=1)

        # Datos
        spokespersons = self.controller.get_all_spokespersons()
        for row_idx, sp in enumerate(spokespersons, start=1):
            for col_idx, value in enumerate(sp):
                lbl = ctk.CTkLabel(self.list_panel, text=str(value), font=FONT_NORMAL, text_color=TEXT_MAIN)
                lbl.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")

    def save_spokesperson(self):
        nombre = self.nombre_entry.get()
        cargo = self.cargo_entry.get()
        tel = self.tel_entry.get()
        correo = self.correo_entry.get()

        if not all([nombre, cargo, tel, correo]):
            self.show_message("Todos los campos son requeridos.", ERROR_COLOR)
            return

        success = self.controller.add_spokesperson(nombre, cargo, tel, correo)
        if success:
            self.show_message("Vocero registrado exitosamente.", PRIMARY_COLOR)
            self.clear_form()
            self.load_list()
        else:
            self.show_message("Error al registrar vocero.", ERROR_COLOR)

    def show_message(self, msg, color):
        self.msg_label.configure(text=msg, text_color=color)

    def clear_form(self):
        self.nombre_entry.delete(0, 'end')
        self.cargo_entry.delete(0, 'end')
        self.tel_entry.delete(0, 'end')
        self.correo_entry.delete(0, 'end')
