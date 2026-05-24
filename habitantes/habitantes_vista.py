import customtkinter as ctk
from tkinter import ttk
from config.style import *
from habitantes.habitantes_controlador import HabitantesControlador
from componentes.barra_busqueda import BarraBusquedaFiltros

class HabitantesVista(ctk.CTkFrame):
    def __init__(self, parent, familia_id=None):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        self.familia_id = familia_id
        self.controlador = HabitantesControlador(self)
        self.id_seleccionado = None
        
        self.setup_ui()
        self.controlador.cargar_datos(familia_id=self.familia_id)
        self.aplicar_permisos()

    def setup_ui(self):
        # Título
        titulo_texto = "Gestión de Habitantes"
        if self.familia_id:
            titulo_texto += f" (Filtrado por Familia ID: {self.familia_id})"
            
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = ctk.CTkLabel(header_frame, text=titulo_texto, font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(side="left", anchor="w")

        if self.familia_id:
            btn_regresar = ctk.CTkButton(
                header_frame, 
                text="← Volver a Familias", 
                fg_color=COLOR_ACENTO, 
                hover_color=COLOR_HOVER, 
                width=150,
                command=self.regresar_a_familias
            )
            btn_regresar.pack(side="right")

        # Top bar (Formulario y Controles)
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        # Formulario
        form_frame = ctk.CTkFrame(top_frame, fg_color=COLOR_SIDEBAR)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.txt_cedula = ctk.CTkEntry(form_frame, placeholder_text="Cédula", font=FUENTE_CUERPO)
        self.txt_cedula.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.txt_nombres = ctk.CTkEntry(form_frame, placeholder_text="Nombres", font=FUENTE_CUERPO)
        self.txt_nombres.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.txt_apellidos = ctk.CTkEntry(form_frame, placeholder_text="Apellidos", font=FUENTE_CUERPO)
        self.txt_apellidos.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.txt_fecha_nac = ctk.CTkEntry(form_frame, placeholder_text="Fecha Nac. (DD/MM/AAAA)", font=FUENTE_CUERPO)
        self.txt_fecha_nac.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.cmb_sexo = ctk.CTkComboBox(form_frame, values=["M", "F"], font=FUENTE_CUERPO)
        self.cmb_sexo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.cmb_sexo.set("M")

        self.txt_telefono = ctk.CTkEntry(form_frame, placeholder_text="Teléfono (Hereda de familia si vacío)", font=FUENTE_CUERPO)
        self.txt_telefono.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.txt_direccion = ctk.CTkEntry(form_frame, placeholder_text="Dirección (Hereda de familia si vacío)", font=FUENTE_CUERPO)
        self.txt_direccion.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.cmb_parentesco = ctk.CTkComboBox(
            form_frame, 
            values=["Jefe de Familia", "Esposo/a", "Hijo/a", "Padre/Madre", "Hermano/a", "Otro"], 
            font=FUENTE_CUERPO
        )
        self.cmb_parentesco.grid(row=2, column=2, padx=10, pady=10, sticky="ew")
        self.cmb_parentesco.set("Jefe de Familia")

        # Campo de Familia ID
        self.txt_familia_id = ctk.CTkEntry(form_frame, placeholder_text="ID Familia", font=FUENTE_CUERPO)
        self.txt_familia_id.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        if self.familia_id:
            self.txt_familia_id.insert(0, str(self.familia_id))

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

        # Barra de búsqueda unificada
        self.barra_busqueda = BarraBusquedaFiltros(
            self, 
            filtros={"Sexo": ["M", "F"]}, 
            comando_busqueda=self.buscar
        )
        self.barra_busqueda.pack(fill="x", pady=(0, 15))

        # Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=FUENTE_SUBTITULO, background=COLOR_SIDEBAR, foreground=COLOR_TEXTO)
        style.configure("Treeview", font=FUENTE_CUERPO, rowheight=30, background=COLOR_CONTENIDO, foreground=COLOR_TEXTO, fieldbackground=COLOR_CONTENIDO)
        style.map("Treeview", background=[("selected", COLOR_ACENTO)])

        self.columns = ("ID", "Cédula", "Nombres", "Apellidos", "F. Nac", "Sexo", "Teléfono", "Dirección", "Parentesco", "Familia ID")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")
        self.tree.column("ID", width=30)
        self.tree.column("Familia ID", width=60)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)
        
        self.lbl_mensaje = ctk.CTkLabel(self, text="", font=FUENTE_CUERPO)
        self.lbl_mensaje.pack(pady=5)

    def aplicar_permisos(self):
        rol = self.controlador.obtener_rol_usuario()
        if rol == "Consulta":
            self.btn_guardar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.btn_limpiar.configure(state="disabled")
            self.txt_cedula.configure(state="disabled")
            self.txt_nombres.configure(state="disabled")
            self.txt_apellidos.configure(state="disabled")
            self.txt_fecha_nac.configure(state="disabled")
            self.cmb_sexo.configure(state="disabled")
            self.txt_telefono.configure(state="disabled")
            self.txt_direccion.configure(state="disabled")
            self.cmb_parentesco.configure(state="disabled")
            self.txt_familia_id.configure(state="disabled")

    def buscar(self, texto, filtros_activos):
        # La barra de búsqueda pasa el texto y filtros
        self.controlador.cargar_datos(busqueda=texto, familia_id=self.familia_id)

    def mostrar_datos(self, datos):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in datos:
            self.tree.insert("", "end", values=row)

    def seleccionar_registro(self, event):
        if self.controlador.obtener_rol_usuario() == "Consulta":
            return
            
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])['values']
            self.id_seleccionado = item[0]
            self.limpiar_entradas()
            self.txt_cedula.insert(0, item[1] if item[1] != "None" else "")
            self.txt_nombres.insert(0, item[2])
            self.txt_apellidos.insert(0, item[3])
            self.txt_fecha_nac.insert(0, item[4] if item[4] != "None" else "")
            self.cmb_sexo.set(item[5] if item[5] != "None" else "M")
            self.txt_telefono.insert(0, item[6] if item[6] != "None" else "")
            self.txt_direccion.insert(0, item[7] if item[7] != "None" else "")
            self.cmb_parentesco.set(item[8] if item[8] != "None" else "Jefe de Familia")
            self.txt_familia_id.insert(0, item[9] if item[9] != "None" else "")
            self.btn_eliminar.configure(state="normal")

    def limpiar_entradas(self):
        self.txt_cedula.delete(0, 'end')
        self.txt_nombres.delete(0, 'end')
        self.txt_apellidos.delete(0, 'end')
        self.txt_fecha_nac.delete(0, 'end')
        self.txt_telefono.delete(0, 'end')
        self.txt_direccion.delete(0, 'end')
        self.txt_familia_id.delete(0, 'end')

    def limpiar_formulario(self):
        self.id_seleccionado = None
        self.limpiar_entradas()
        self.btn_eliminar.configure(state="disabled")
        self.lbl_mensaje.configure(text="")
        if self.familia_id:
            self.txt_familia_id.insert(0, str(self.familia_id))
        self.controlador.cargar_datos(familia_id=self.familia_id)

    def guardar(self):
        fam_id_str = self.txt_familia_id.get().strip()
        fam_id = int(fam_id_str) if fam_id_str.isdigit() else None
        
        self.controlador.guardar(
            self.id_seleccionado,
            self.txt_cedula.get().strip(),
            self.txt_nombres.get().strip(),
            self.txt_apellidos.get().strip(),
            self.txt_fecha_nac.get().strip(),
            self.cmb_sexo.get(),
            self.txt_telefono.get().strip(),
            self.txt_direccion.get().strip(),
            self.cmb_parentesco.get(),
            fam_id
        )

    def eliminar(self):
        if self.id_seleccionado:
            self.controlador.eliminar(self.id_seleccionado, familia_id=self.familia_id)

    def mostrar_mensaje(self, titulo, mensaje):
        color = COLOR_EXITO if titulo == "Éxito" else COLOR_ERROR
        self.lbl_mensaje.configure(text=mensaje, text_color=color)

    def regresar_a_familias(self):
        # Buscamos el PanelVista parent
        parent = self.master
        while parent and not hasattr(parent, 'navegar'):
            parent = parent.master
        if parent:
            parent.navegar("Censo")
