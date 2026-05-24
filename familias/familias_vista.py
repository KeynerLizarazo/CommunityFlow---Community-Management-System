"""
familias/familias_vista.py – Módulo de Censo Familiar.
Tabla de familias con búsqueda, KPIs y panel lateral de habitantes.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from config.auth_session import AuthSession
from familias.familias_modelo import FamiliaModelo, Familia
from habitantes.habitantes_modelo import HabitantesModelo
from config.database import SessionLocal, remove_db


class FamiliasVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()

        self.modelo_familia  = FamiliaModelo()
        self.modelo_habitante = HabitantesModelo()
        self._panel_lateral_visible = False

        self._build_ui()
        self._cargar_datos()

    # ─── Layout ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Encabezado
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(hdr, text="Censo Familiar",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Nueva Familia",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=40, corner_radius=CORNER_RADIUS["button"],
            command=self._abrir_modal_familia,
        ).pack(side="right")

        # KPIs
        self._kpis_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._kpis_frame.pack(fill="x", pady=(0, PADDING["md"]))
        self._kpi_labels = {}
        for i, (key, titulo, color) in enumerate([
            ("familias",   "Total Familias",         COLORS["primary"]),
            ("habitantes", "Total Habitantes",        COLORS["secondary"]),
            ("promedio",   "Prom. Hab/Familia",       COLORS["tertiary"]),
            ("completos",  "Registros con Jefe",      COLORS["warning"]),
        ]):
            self._kpis_frame.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(
                self._kpis_frame, fg_color=COLORS["surface_lowest"],
                corner_radius=CORNER_RADIUS["card"],
                border_width=1, border_color=COLORS["outline_variant"],
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0), ipady=6)
            ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0).pack(fill="x")
            ctk.CTkLabel(card, text=titulo, font=FONTS["label_caps"],
                         text_color=COLORS["on_surface_variant"]).pack(pady=(10, 2))
            lbl = ctk.CTkLabel(card, text="—", font=FONTS["headline_md"],
                               text_color=color)
            lbl.pack(pady=(0, 10))
            self._kpi_labels[key] = lbl

        # Barra de búsqueda
        search_bar = ctk.CTkFrame(self, fg_color=COLORS["surface_high"],
                                  corner_radius=CORNER_RADIUS["input"])
        search_bar.pack(fill="x", pady=(0, PADDING["md"]))

        self.txt_busqueda = ctk.CTkEntry(
            search_bar, placeholder_text="Buscar por código, dirección o jefe...",
            height=40, font=FONTS["body_base"], fg_color="transparent",
            border_width=0,
        )
        self.txt_busqueda.pack(side="left", fill="x", expand=True, padx=12)
        self.txt_busqueda.bind("<Return>", lambda e: self._cargar_datos())

        ctk.CTkButton(
            search_bar, text="Buscar", width=90, height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"], font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._cargar_datos,
        ).pack(side="right", padx=8, pady=4)

        # Área principal (tabla + panel lateral)
        self._main_area = ctk.CTkFrame(self, fg_color="transparent")
        self._main_area.pack(fill="both", expand=True)
        self._main_area.grid_columnconfigure(0, weight=1)
        self._main_area.grid_rowconfigure(0, weight=1)

        self._build_tabla()

    def _build_tabla(self):
        tabla_frame = ctk.CTkFrame(
            self._main_area, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        tabla_frame.grid(row=0, column=0, sticky="nsew")

        # Encabezado tabla
        hdr = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(hdr, text="Familias Registradas", font=FONTS["headline_sm"],
                     text_color=COLORS["neutral"]).pack(side="left")

        self.lbl_conteo = ctk.CTkLabel(hdr, text="",
                                       font=FONTS["helper_text"],
                                       text_color=COLORS["on_surface_variant"])
        self.lbl_conteo.pack(side="right")

        ctk.CTkFrame(tabla_frame, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x")

        cols = ("ID", "Codigo", "Jefe de Familia", "Direccion", "Telefono", "Habitantes")
        self.tabla = ttk.Treeview(tabla_frame, columns=cols, show="headings",
                                  style="CF.Treeview")
        anchos = {"ID": 50, "Codigo": 120, "Jefe de Familia": 200,
                  "Direccion": 240, "Telefono": 120, "Habitantes": 90}
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center" if col not in ("Jefe de Familia", "Direccion") else "w",
                             width=anchos[col])

        sb = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self.tabla.bind("<Double-1>", self._on_doble_clic)
        self.tabla.bind("<Button-3>", self._menu_contextual)

    # ─── Datos ───────────────────────────────────────────────────────────────
    def _cargar_datos(self):
        busqueda = self.txt_busqueda.get().strip().lower()

        db = SessionLocal()
        try:
            query = db.query(Familia).filter_by(activo=True)
            familias_raw = query.all()

            # Serializar para no mantener sesión abierta
            familias = []
            total_hab = 0
            con_jefe = 0
            for f in familias_raw:
                jefe = f"{f.jefe.nombres} {f.jefe.apellidos}" if f.jefe else "Sin asignar"
                n_hab = len(f.habitantes)
                total_hab += n_hab
                if f.jefe:
                    con_jefe += 1
                familias.append({
                    "id": f.id_familia,
                    "codigo": f.codigo_familia,
                    "jefe": jefe,
                    "direccion": f.direccion or "",
                    "telefono": f.telefono or "",
                    "n_hab": n_hab,
                })
        finally:
            remove_db()

        # Filtro local
        if busqueda:
            familias = [f for f in familias if
                        busqueda in f["codigo"].lower() or
                        busqueda in f["jefe"].lower() or
                        busqueda in f["direccion"].lower()]

        # KPIs
        n = len(familias)
        promedio = round(total_hab / len(familias_raw), 1) if familias_raw else 0
        self._kpi_labels["familias"].configure(text=str(n))
        self._kpi_labels["habitantes"].configure(text=str(total_hab))
        self._kpi_labels["promedio"].configure(text=str(promedio))
        self._kpi_labels["completos"].configure(text=str(con_jefe))
        self.lbl_conteo.configure(text=f"{n} registros")

        # Tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for f in familias:
            tag = "par" if f["id"] % 2 == 0 else "impar"
            self.tabla.insert("", "end", iid=str(f["id"]),
                              values=(f["id"], f["codigo"], f["jefe"],
                                      f["direccion"], f["telefono"], f["n_hab"]),
                              tags=(tag,))
        self.tabla.tag_configure("par", background=COLORS["surface"])
        self.tabla.tag_configure("impar", background=COLORS["surface_lowest"])

    def _on_doble_clic(self, event):
        sel = self.tabla.selection()
        if not sel:
            return
        id_familia = int(sel[0])
        self._mostrar_panel_habitantes(id_familia)

    def _menu_contextual(self, event):
        item = self.tabla.identify_row(event.y)
        if not item:
            return
        self.tabla.selection_set(item)
        id_familia = int(item)
        menu = ctk.CTkFrame(self)  # placeholder; usamos tk.Menu en su lugar
        from tkinter import Menu as TkMenu
        m = TkMenu(self, tearoff=0)
        m.add_command(label="Ver Habitantes", command=lambda: self._mostrar_panel_habitantes(id_familia))
        m.add_command(label="Editar Familia", command=lambda: self._abrir_modal_familia(id_familia))
        m.add_separator()
        m.add_command(label="Desactivar", command=lambda: self._desactivar(id_familia))
        m.tk_popup(event.x_root, event.y_root)

    # ─── Panel lateral de habitantes ─────────────────────────────────────────
    def _mostrar_panel_habitantes(self, id_familia: int):
        # Crear o reusar panel lateral
        if hasattr(self, "_panel_lat"):
            self._panel_lat.destroy()

        self._main_area.grid_columnconfigure(1, weight=0, minsize=340)
        panel = ctk.CTkFrame(
            self._main_area, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
            width=320,
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        panel.grid_propagate(False)
        self._panel_lat = panel

        # Header del panel
        ph = ctk.CTkFrame(panel, fg_color=COLORS["primary"], corner_radius=0)
        ph.pack(fill="x")

        ctk.CTkLabel(ph, text=f"Familia #{id_familia}",
                     font=FONTS["headline_sm"], text_color=COLORS["on_primary"]).pack(
            side="left", padx=16, pady=12)

        ctk.CTkButton(
            ph, text="✕", width=32, height=32, fg_color="transparent",
            hover_color=COLORS["primary_container"], text_color=COLORS["on_primary"],
            font=FONTS["body_bold"], corner_radius=CORNER_RADIUS["button"],
            command=self._cerrar_panel_lat,
        ).pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            panel, text="+ Agregar Habitante",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=36, corner_radius=CORNER_RADIUS["button"],
            command=lambda: self._abrir_modal_habitante(id_familia),
        ).pack(fill="x", padx=12, pady=8)

        # Lista de habitantes
        lista = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        lista.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        habitantes = self.modelo_habitante.obtener_todos(familia_id=id_familia)

        if not habitantes:
            ctk.CTkLabel(lista, text="Sin habitantes registrados.",
                         font=FONTS["helper_text"],
                         text_color=COLORS["on_surface_variant"]).pack(pady=20)
        else:
            for h in habitantes:
                card = ctk.CTkFrame(lista, fg_color=COLORS["surface"],
                                    corner_radius=8)
                card.pack(fill="x", pady=3)

                ctk.CTkLabel(
                    card,
                    text=f"{h['nombres']} {h['apellidos']}",
                    font=FONTS["body_bold"], text_color=COLORS["neutral"],
                    anchor="w",
                ).pack(anchor="w", padx=12, pady=(8, 2))

                info = f"CI: {h['cedula'] or '—'}  |  {h['parentesco'] or '—'}  |  {h['sexo'] or '—'}"
                ctk.CTkLabel(
                    card, text=info,
                    font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
                    anchor="w",
                ).pack(anchor="w", padx=12, pady=(0, 8))

    def _cerrar_panel_lat(self):
        if hasattr(self, "_panel_lat"):
            self._panel_lat.destroy()
            del self._panel_lat
        self._main_area.grid_columnconfigure(1, weight=0, minsize=0)

    # ─── Modal Nueva Familia ─────────────────────────────────────────────────
    def _abrir_modal_familia(self, id_familia=None):
        dlg = _ModalFamilia(self, id_familia, on_guardar=self._cargar_datos)
        dlg.grab_set()

    def _abrir_modal_habitante(self, id_familia: int):
        dlg = _ModalHabitante(self, id_familia,
                              on_guardar=lambda: self._mostrar_panel_habitantes(id_familia))
        dlg.grab_set()

    def _desactivar(self, id_familia: int):
        if messagebox.askyesno("Confirmar",
                               f"¿Desactivar la familia #{id_familia} y todos sus habitantes?"):
            self.modelo_familia.desactivar_familia(id_familia)
            self._cargar_datos()


# ─── Modal Familia ────────────────────────────────────────────────────────────
class _ModalFamilia(ctk.CTkToplevel):
    def __init__(self, parent, id_familia=None, on_guardar=None):
        super().__init__(parent)
        self.title("Nueva Familia" if id_familia is None else "Editar Familia")
        self.geometry("520x380")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.on_guardar = on_guardar
        self.modelo = FamiliaModelo()

        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Registrar Nueva Familia",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 20))

        fields = [("Codigo de Familia *", "txt_codigo"),
                  ("Direccion",           "txt_direccion"),
                  ("Telefono",            "txt_telefono")]
        self._entries = {}
        for label, key in fields:
            ctk.CTkLabel(inner, text=label, font=FONTS["body_bold"],
                         text_color=COLORS["neutral"]).pack(anchor="w")
            ent = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                               corner_radius=CORNER_RADIUS["input"],
                               border_color=COLORS["outline_variant"])
            ent.pack(fill="x", pady=(4, 12))
            self._entries[key] = ent

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Guardar Familia",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        codigo = self._entries["txt_codigo"].get().strip()
        if not codigo:
            self.lbl_err.configure(text="El codigo es obligatorio.")
            return
        datos = {
            "codigo_familia": codigo,
            "direccion": self._entries["txt_direccion"].get().strip() or None,
            "telefono":  self._entries["txt_telefono"].get().strip() or None,
        }
        ok = self.modelo.crear_familia(datos)
        if ok:
            if self.on_guardar:
                self.on_guardar()
            self.destroy()
        else:
            self.lbl_err.configure(text="Error: el codigo ya existe o hubo un problema.")


# ─── Modal Habitante ──────────────────────────────────────────────────────────
class _ModalHabitante(ctk.CTkToplevel):
    def __init__(self, parent, familia_id: int, on_guardar=None):
        super().__init__(parent)
        self.title("Agregar Habitante")
        self.geometry("540x560")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.familia_id = familia_id
        self.on_guardar = on_guardar
        self.modelo = HabitantesModelo()
        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Agregar Habitante",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 16))

        def campo(lbl, key):
            ctk.CTkLabel(inner, text=lbl, font=FONTS["body_bold"],
                         text_color=COLORS["neutral"]).pack(anchor="w")
            e = ctk.CTkEntry(inner, height=38, font=FONTS["body_base"],
                             corner_radius=CORNER_RADIUS["input"],
                             border_color=COLORS["outline_variant"])
            e.pack(fill="x", pady=(2, 8))
            return e

        self.txt_nombres  = campo("Nombres *", "nombres")
        self.txt_apellidos= campo("Apellidos *", "apellidos")
        self.txt_cedula   = campo("Cedula (opcional)", "cedula")
        self.txt_fnac     = campo("Fecha Nacimiento (DD/MM/AAAA)", "fnac")
        self.txt_telefono = campo("Telefono", "tel")

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 8))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row2, text="Sexo", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row2, text="Parentesco", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.opt_sexo = ctk.CTkOptionMenu(row2, values=["Masculino", "Femenino", "Otro"],
                                          fg_color=COLORS["surface_high"],
                                          button_color=COLORS["primary"],
                                          text_color=COLORS["neutral"])
        self.opt_sexo.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.opt_parentesco = ctk.CTkOptionMenu(
            row2, values=["Jefe/a", "Cónyuge", "Hijo/a", "Padre/Madre", "Otro"],
            fg_color=COLORS["surface_high"],
            button_color=COLORS["primary"],
            text_color=COLORS["neutral"],
        )
        self.opt_parentesco.grid(row=1, column=1, sticky="ew", pady=(4, 0), padx=(12, 0))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack(pady=(4, 0))

        ctk.CTkButton(
            inner, text="Registrar Habitante",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        nombres   = self.txt_nombres.get().strip()
        apellidos = self.txt_apellidos.get().strip()
        if not nombres or not apellidos:
            self.lbl_err.configure(text="Nombres y Apellidos son obligatorios.")
            return

        usuario = AuthSession.get_usuario()
        uid = usuario.id_usuario if usuario else 0

        ok, msg = self.modelo.insertar(
            cedula          = self.txt_cedula.get().strip() or None,
            nombres         = nombres,
            apellidos       = apellidos,
            fecha_nacimiento= self.txt_fnac.get().strip(),
            sexo            = self.opt_sexo.get(),
            telefono        = self.txt_telefono.get().strip(),
            direccion       = "",
            parentesco      = self.opt_parentesco.get(),
            familia_id      = self.familia_id,
            usuario_id      = uid,
        )
        if ok:
            if self.on_guardar:
                self.on_guardar()
            self.destroy()
        else:
            self.lbl_err.configure(text=msg)
