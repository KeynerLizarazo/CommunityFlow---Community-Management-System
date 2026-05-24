import customtkinter as ctk
from tkinter import ttk
from config.style import *
from actas.actas_controlador import ActasControlador

class ActasVista(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.controlador = ActasControlador(self)
        self.id_seleccionado = None
        
        self.setup_ui()
        self.controlador.cargar_datos()

    def setup_ui(self):
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="Gestión de Actas", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=(0, 20), anchor="w")

        # Top bar (Búsqueda y Formulario)
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        # Formulario
        form_frame = ctk.CTkFrame(top_frame, fg_color=COLOR_SIDEBAR)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.txt_numero = ctk.CTkEntry(form_frame, placeholder_text="Número de Acta", font=FUENTE_CUERPO)
        self.txt_numero.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.txt_fecha = ctk.CTkEntry(form_frame, placeholder_text="Fecha Reunión (DD/MM/AAAA)", font=FUENTE_CUERPO)
        self.txt_fecha.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.txt_lugar = ctk.CTkEntry(form_frame, placeholder_text="Lugar", font=FUENTE_CUERPO)
        self.txt_lugar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.cmb_tipo = ctk.CTkComboBox(form_frame, values=["Ordinaria", "Extraordinaria", "Asamblea"], font=FUENTE_CUERPO)
        self.cmb_tipo.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.txt_asunto = ctk.CTkEntry(form_frame, placeholder_text="Asunto", font=FUENTE_CUERPO)
        self.txt_asunto.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.txt_conclusiones = ctk.CTkEntry(form_frame, placeholder_text="Conclusiones", font=FUENTE_CUERPO)
        self.txt_conclusiones.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

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
        
        self.txt_buscar = ctk.CTkEntry(search_frame, placeholder_text="Buscar por Número o Asunto...", font=FUENTE_CUERPO)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(search_frame, text="Buscar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, width=100, command=lambda: self.controlador.cargar_datos(self.txt_buscar.get()))
        btn_buscar.pack(side="right")

        # Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=FUENTE_SUBTITULO, background=COLOR_SIDEBAR, foreground=COLOR_TEXTO)
        style.configure("Treeview", font=FUENTE_CUERPO, rowheight=30, background=COLOR_CONTENIDO, foreground=COLOR_TEXTO, fieldbackground=COLOR_CONTENIDO)
        style.map("Treeview", background=[("selected", COLOR_ACENTO)])

        columns = ("ID", "Nro Acta", "Fecha", "Lugar", "Tipo", "Asunto", "Conclusiones")
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
            self.txt_numero.insert(0, item[1])
            self.txt_fecha.insert(0, item[2] if item[2] != "None" else "")
            self.txt_lugar.insert(0, item[3] if item[3] != "None" else "")
            self.cmb_tipo.set(item[4] if item[4] != "None" else "Ordinaria")
            self.txt_asunto.insert(0, item[5] if item[5] != "None" else "")
            self.txt_conclusiones.insert(0, item[6] if item[6] != "None" else "")
            self.btn_eliminar.configure(state="normal")

    def limpiar_entradas(self):
        self.txt_numero.delete(0, 'end')
        self.txt_fecha.delete(0, 'end')
        self.txt_lugar.delete(0, 'end')
        self.txt_asunto.delete(0, 'end')
        self.txt_conclusiones.delete(0, 'end')

    def limpiar_formulario(self):
        self.id_seleccionado = None
        self.limpiar_entradas()
        self.btn_eliminar.configure(state="disabled")
        self.txt_buscar.delete(0, 'end')
        self.lbl_mensaje.configure(text="")
        self.controlador.cargar_datos()

    def guardar(self):
        self.controlador.guardar(
            self.id_seleccionado,
            self.txt_numero.get(),
            self.txt_fecha.get(),
            self.txt_lugar.get(),
            self.cmb_tipo.get(),
            self.txt_asunto.get(),
            self.txt_conclusiones.get()
        )

    def eliminar(self):
        if self.id_seleccionado:
            self.controlador.eliminar(self.id_seleccionado)

    def mostrar_mensaje(self, titulo, mensaje):
        color = COLOR_EXITO if titulo == "Éxito" else COLOR_ERROR
        self.lbl_mensaje.configure(text=mensaje, text_color=color)
