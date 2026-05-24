import customtkinter as ctk
from tkinter import ttk
from config.style import *
from voceros.voceros_controlador import VocerosControlador

class VocerosVista(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.controlador = VocerosControlador(self)
        self.id_seleccionado = None
        
        self.setup_ui()
        self.controlador.cargar_datos()

    def setup_ui(self):
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="Gestión de Voceros", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=(0, 20), anchor="w")

        # Top bar (Búsqueda y Formulario)
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        # Formulario
        form_frame = ctk.CTkFrame(top_frame, fg_color=COLOR_SIDEBAR)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.txt_id_habitante = ctk.CTkEntry(form_frame, placeholder_text="ID Habitante", font=FUENTE_CUERPO)
        self.txt_id_habitante.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.txt_id_cargo = ctk.CTkEntry(form_frame, placeholder_text="ID Cargo", font=FUENTE_CUERPO)
        self.txt_id_cargo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.cmb_tipo = ctk.CTkComboBox(form_frame, values=["P", "S"], font=FUENTE_CUERPO) # P=Principal, S=Suplente
        self.cmb_tipo.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.txt_fecha_inicio = ctk.CTkEntry(form_frame, placeholder_text="Fecha Inicio (DD/MM/AAAA)", font=FUENTE_CUERPO)
        self.txt_fecha_inicio.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.txt_fecha_fin = ctk.CTkEntry(form_frame, placeholder_text="Fecha Fin (DD/MM/AAAA)", font=FUENTE_CUERPO)
        self.txt_fecha_fin.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        for i in range(3):
            form_frame.grid_columnconfigure(i, weight=1)

        # Botones Formulario
        btn_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        btn_frame.pack(side="right", fill="y")

        self.btn_guardar = ctk.CTkButton(btn_frame, text="Guardar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, command=self.guardar)
        self.btn_guardar.pack(pady=(0, 10))

        self.btn_eliminar = ctk.CTkButton(btn_frame, text="Eliminar", fg_color=COLOR_ERROR, hover_color="#B71C1C", command=self.eliminar, state="disabled")
        self.btn_eliminar.pack(pady=(0, 10))

        self.btn_limpiar = ctk.CTkButton(btn_frame, text="Limpiar", fg_color="#757575", hover_color="#616161", command=self.limpiar_formulario)
        self.btn_limpiar.pack()

        # Barra de búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        self.txt_buscar = ctk.CTkEntry(search_frame, placeholder_text="Buscar por Habitante o Cargo...", font=FUENTE_CUERPO)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(search_frame, text="Buscar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, width=100, command=lambda: self.controlador.cargar_datos(self.txt_buscar.get()))
        btn_buscar.pack(side="right")

        # Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=FUENTE_SUBTITULO, background=COLOR_SIDEBAR, foreground=COLOR_TEXTO)
        style.configure("Treeview", font=FUENTE_CUERPO, rowheight=30, background=COLOR_CONTENIDO, foreground=COLOR_TEXTO, fieldbackground=COLOR_CONTENIDO)
        style.map("Treeview", background=[("selected", COLOR_ACENTO)])

        columns = ("ID", "Habitante", "Cargo", "Tipo", "Fecha Inicio", "Fecha Fin", "ID Hab", "ID Car")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")
        self.tree.column("ID", width=30)
        self.tree.column("ID Hab", width=0, stretch=False)
        self.tree.column("ID Car", width=0, stretch=False)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=FUENTE_CUERPO)
        self.lbl_mensaje.pack(pady=5)

    def mostrar_datos(self, datos):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in datos:
            self.tree.insert("", "end", values=row)

    def seleccionar_registro(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])['values']
            self.id_seleccionado = item[0]
            self.limpiar_entradas()
            self.txt_id_habitante.insert(0, item[6] if item[6] != "None" else "")
            self.txt_id_cargo.insert(0, item[7] if item[7] != "None" else "")
            self.cmb_tipo.set(item[3] if item[3] != "None" else "P")
            self.txt_fecha_inicio.insert(0, item[4] if item[4] != "None" else "")
            self.txt_fecha_fin.insert(0, item[5] if item[5] != "None" else "")
            self.btn_eliminar.configure(state="normal")

    def limpiar_entradas(self):
        self.txt_id_habitante.delete(0, 'end')
        self.txt_id_cargo.delete(0, 'end')
        self.txt_fecha_inicio.delete(0, 'end')
        self.txt_fecha_fin.delete(0, 'end')

    def limpiar_formulario(self):
        self.id_seleccionado = None
        self.limpiar_entradas()
        self.btn_eliminar.configure(state="disabled")
        self.txt_buscar.delete(0, 'end')
        self.lbl_mensaje.configure(text="")
        self.controlador.cargar_datos()

    def guardar(self):
        id_hab = self.txt_id_habitante.get()
        id_car = self.txt_id_cargo.get()
        if not id_hab.isdigit() or not id_car.isdigit():
            self.mostrar_mensaje("Error", "IDs deben ser numéricos")
            return

        self.controlador.guardar(
            self.id_seleccionado,
            int(id_hab),
            int(id_car),
            self.cmb_tipo.get(),
            self.txt_fecha_inicio.get(),
            self.txt_fecha_fin.get()
        )

    def eliminar(self):
        if self.id_seleccionado:
            self.controlador.eliminar(self.id_seleccionado)

    def mostrar_mensaje(self, titulo, mensaje):
        color = COLOR_EXITO if titulo == "Éxito" else COLOR_ERROR
        self.lbl_mensaje.configure(text=mensaje, text_color=color)
