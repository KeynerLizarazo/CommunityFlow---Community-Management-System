import customtkinter as ctk
from tkinter import ttk
from config.style import *
from recursos.recursos_controlador import RecursosControlador

class RecursosVista(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.controlador = RecursosControlador(self)
        self.id_seleccionado = None
        
        self.setup_ui()
        self.controlador.cargar_datos()

    def setup_ui(self):
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="Gestión de Recursos", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=(0, 20), anchor="w")

        # Top bar (Búsqueda y Formulario)
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        # Formulario
        form_frame = ctk.CTkFrame(top_frame, fg_color=COLOR_SIDEBAR)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.txt_codigo = ctk.CTkEntry(form_frame, placeholder_text="Código", font=FUENTE_CUERPO)
        self.txt_codigo.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.txt_descripcion = ctk.CTkEntry(form_frame, placeholder_text="Descripción", font=FUENTE_CUERPO)
        self.txt_descripcion.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.cmb_tipo = ctk.CTkComboBox(form_frame, values=["Financiero", "Material", "Tecnológico", "Humano"], font=FUENTE_CUERPO)
        self.cmb_tipo.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.txt_cantidad = ctk.CTkEntry(form_frame, placeholder_text="Cantidad", font=FUENTE_CUERPO)
        self.txt_cantidad.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        for i in range(2):
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
        
        self.txt_buscar = ctk.CTkEntry(search_frame, placeholder_text="Buscar por Código o Descripción...", font=FUENTE_CUERPO)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(search_frame, text="Buscar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, width=100, command=lambda: self.controlador.cargar_datos(self.txt_buscar.get()))
        btn_buscar.pack(side="right")

        # Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=FUENTE_SUBTITULO, background=COLOR_SIDEBAR, foreground=COLOR_TEXTO)
        style.configure("Treeview", font=FUENTE_CUERPO, rowheight=30, background=COLOR_CONTENIDO, foreground=COLOR_TEXTO, fieldbackground=COLOR_CONTENIDO)
        style.map("Treeview", background=[("selected", COLOR_ACENTO)])

        columns = ("ID", "Código", "Descripción", "Tipo", "Cantidad")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")
        self.tree.column("ID", width=30)
        
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
            self.txt_codigo.insert(0, item[1])
            self.txt_descripcion.insert(0, item[2])
            self.cmb_tipo.set(item[3] if item[3] != "None" else "Material")
            self.txt_cantidad.insert(0, item[4] if item[4] != "None" else "")
            self.btn_eliminar.configure(state="normal")

    def limpiar_entradas(self):
        self.txt_codigo.delete(0, 'end')
        self.txt_descripcion.delete(0, 'end')
        self.txt_cantidad.delete(0, 'end')

    def limpiar_formulario(self):
        self.id_seleccionado = None
        self.limpiar_entradas()
        self.btn_eliminar.configure(state="disabled")
        self.txt_buscar.delete(0, 'end')
        self.lbl_mensaje.configure(text="")
        self.controlador.cargar_datos()

    def guardar(self):
        cant = self.txt_cantidad.get()
        try:
            cant_float = float(cant) if cant else 0.0
        except ValueError:
            self.mostrar_mensaje("Error", "Cantidad debe ser numérico")
            return

        self.controlador.guardar(
            self.id_seleccionado,
            self.txt_codigo.get(),
            self.txt_descripcion.get(),
            self.cmb_tipo.get(),
            cant_float
        )

    def eliminar(self):
        if self.id_seleccionado:
            self.controlador.eliminar(self.id_seleccionado)

    def mostrar_mensaje(self, titulo, mensaje):
        color = COLOR_EXITO if titulo == "Éxito" else COLOR_ERROR
        self.lbl_mensaje.configure(text=mensaje, text_color=color)
