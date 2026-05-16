import customtkinter as ctk
from views.style import *

class FamilyView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=BG_DARK)
        self.controller = controller

        # Título
        self.title = ctk.CTkLabel(self, text="Gestión de Familias", font=FONT_TITLE, text_color=TEXT_MAIN)
        self.title.pack(anchor="w", pady=(0, 20))

        # Panel superior (Formulario)
        self.form_panel = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=10)
        self.form_panel.pack(fill="x", pady=(0, 20), ipady=10)

        # Campos del formulario (2x2 grid)
        self.form_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.rep_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Representante de la familia", font=FONT_NORMAL, height=35)
        self.rep_entry.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="ew")

        self.cant_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Cantidad de integrantes", font=FONT_NORMAL, height=35)
        self.cant_entry.grid(row=0, column=2, columnspan=2, padx=15, pady=15, sticky="ew")

        self.dir_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Dirección", font=FONT_NORMAL, height=35)
        self.dir_entry.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        self.tel_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Teléfono", font=FONT_NORMAL, height=35)
        self.tel_entry.grid(row=1, column=2, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        # Botón guardar
        self.save_btn = ctk.CTkButton(self.form_panel, text="Registrar Familia", font=FONT_NORMAL_BOLD, fg_color=PRIMARY_COLOR, hover_color=PRIMARY_HOVER, height=35, command=self.save_family)
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
        headers = ["ID", "Representante", "Integrantes", "Dirección", "Teléfono"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.list_panel, text=h, font=FONT_NORMAL_BOLD, text_color=PRIMARY_COLOR)
            lbl.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            self.list_panel.grid_columnconfigure(i, weight=1)

        # Datos
        families = self.controller.get_all_families()
        for row_idx, fam in enumerate(families, start=1):
            for col_idx, value in enumerate(fam):
                lbl = ctk.CTkLabel(self.list_panel, text=str(value), font=FONT_NORMAL, text_color=TEXT_MAIN)
                lbl.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")

    def save_family(self):
        rep = self.rep_entry.get()
        cant = self.cant_entry.get()
        dir = self.dir_entry.get()
        tel = self.tel_entry.get()

        if not all([rep, cant, dir, tel]):
            self.show_message("Todos los campos son requeridos.", ERROR_COLOR)
            return

        if not cant.isdigit():
            self.show_message("La cantidad debe ser un número.", ERROR_COLOR)
            return

        success = self.controller.add_family(rep, int(cant), dir, tel)
        if success:
            self.show_message("Familia registrada exitosamente.", PRIMARY_COLOR)
            self.clear_form()
            self.load_list()
        else:
            self.show_message("Error al registrar familia.", ERROR_COLOR)

    def show_message(self, msg, color):
        self.msg_label.configure(text=msg, text_color=color)

    def clear_form(self):
        self.rep_entry.delete(0, 'end')
        self.cant_entry.delete(0, 'end')
        self.dir_entry.delete(0, 'end')
        self.tel_entry.delete(0, 'end')
