"""
voceros/voceros_vista.py – Vocería y Representantes.
Tabla con filtros y modal de registro de representante.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from voceros.voceros_modelo import VocerosModelo, Representante, Cargo
from config.database import SessionLocal, remove_db
from config.auth_session import AuthSession
from bitacora.bitacora_modelo import BitacoraModelo


class VocerosVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self.modelo = VocerosModelo()
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # Encabezado
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(hdr, text="Voceria y Representantes",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Registrar Representante",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=40, corner_radius=CORNER_RADIUS["button"],
            command=self._abrir_modal,
        ).pack(side="right")

        # KPIs rápidos
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, PADDING["md"]))
        self._lbl_activos = self._kpi_chip(kpi_row, "Voceros Activos", "0", COLORS["tertiary"])
        self._lbl_inactivos = self._kpi_chip(kpi_row, "Inactivos", "0", COLORS["on_surface_variant"])

        # Filtro
        filtro = ctk.CTkFrame(self, fg_color=COLORS["surface_high"],
                              corner_radius=CORNER_RADIUS["input"])
        filtro.pack(fill="x", pady=(0, PADDING["md"]))

        self.txt_busqueda = ctk.CTkEntry(
            filtro, placeholder_text="Buscar por nombre o cargo...",
            height=40, font=FONTS["body_base"], fg_color="transparent", border_width=0,
        )
        self.txt_busqueda.pack(side="left", fill="x", expand=True, padx=12)
        self.txt_busqueda.bind("<Return>", lambda e: self._cargar_datos())

        ctk.CTkLabel(filtro, text="Estado:", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(side="left", padx=(0, 4))
        self.opt_estado = ctk.CTkOptionMenu(
            filtro, values=["Todos", "activo", "inactivo"],
            width=120, font=FONTS["body_base"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            command=lambda _: self._cargar_datos(),
        )
        self.opt_estado.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            filtro, text="Buscar", width=90, height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"], font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._cargar_datos,
        ).pack(side="right", padx=8)

        # Tabla
        card = ctk.CTkFrame(
            self, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        card.pack(fill="both", expand=True)

        hdr2 = ctk.CTkFrame(card, fg_color="transparent")
        hdr2.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(hdr2, text="Directiva Comunal",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(side="left")
        self.lbl_conteo = ctk.CTkLabel(hdr2, text="",
                                       font=FONTS["helper_text"],
                                       text_color=COLORS["on_surface_variant"])
        self.lbl_conteo.pack(side="right")

        ctk.CTkFrame(card, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x")

        cols = ("ID", "Nombre Completo", "Cargo", "Tipo", "F. Inicio", "F. Fin", "Estado")
        self.tabla = ttk.Treeview(card, columns=cols, show="headings", style="CF.Treeview")
        anchos = {"ID": 50, "Nombre Completo": 220, "Cargo": 180,
                  "Tipo": 90, "F. Inicio": 100, "F. Fin": 100, "Estado": 90}
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col,
                             anchor="w" if col == "Nombre Completo" else "center",
                             width=anchos[col])

        sb = ttk.Scrollbar(card, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self.tabla.tag_configure("activo",   foreground=COLORS["tertiary"])
        self.tabla.tag_configure("inactivo", foreground=COLORS["on_surface_variant"])

    def _kpi_chip(self, parent, titulo, valor, color):
        chip = ctk.CTkFrame(parent, fg_color=COLORS["surface_lowest"],
                            corner_radius=CORNER_RADIUS["card"],
                            border_width=1, border_color=COLORS["outline_variant"])
        chip.pack(side="left", padx=(0, 10), ipadx=12, ipady=6)
        ctk.CTkLabel(chip, text=titulo, font=FONTS["label_caps"],
                     text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(10, 6))
        lbl = ctk.CTkLabel(chip, text=valor, font=FONTS["body_bold"], text_color=color)
        lbl.pack(side="left", padx=(0, 10))
        return lbl

    def _cargar_datos(self):
        busqueda  = self.txt_busqueda.get().strip().lower()
        estado_f  = self.opt_estado.get()

        db = SessionLocal()
        try:
            query = db.query(Representante)
            if estado_f != "Todos":
                query = query.filter(Representante.estado == estado_f)
            reps = query.limit(500).all()

            data = []
            for r in reps:
                nombre = f"{r.habitante.nombres} {r.habitante.apellidos}" if r.habitante else "—"
                cargo  = r.cargo.nombre if r.cargo else "—"
                data.append({
                    "id":      r.id_representante,
                    "nombre":  nombre,
                    "cargo":   cargo,
                    "tipo":    r.tipo or "—",
                    "inicio":  str(r.fecha_inicio) if r.fecha_inicio else "—",
                    "fin":     str(r.fecha_fin) if r.fecha_fin else "—",
                    "estado":  r.estado,
                })
        finally:
            remove_db()

        if busqueda:
            data = [d for d in data if
                    busqueda in d["nombre"].lower() or
                    busqueda in d["cargo"].lower()]

        activos   = sum(1 for d in data if d["estado"] == "activo")
        inactivos = sum(1 for d in data if d["estado"] == "inactivo")
        self._lbl_activos.configure(text=str(activos))
        self._lbl_inactivos.configure(text=str(inactivos))
        self.lbl_conteo.configure(text=f"{len(data)} registros")

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for d in data:
            tag = d["estado"]
            self.tabla.insert("", "end", values=(
                d["id"], d["nombre"], d["cargo"], d["tipo"],
                d["inicio"], d["fin"], d["estado"],
            ), tags=(tag,))

    def _abrir_modal(self):
        dlg = _ModalRepresentante(self, on_guardar=self._cargar_datos)
        dlg.grab_set()


# ─── Modal Representante ──────────────────────────────────────────────────────
class _ModalRepresentante(ctk.CTkToplevel):
    def __init__(self, parent, on_guardar=None):
        super().__init__(parent)
        self.title("Registrar Representante")
        self.geometry("540x540")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.on_guardar = on_guardar
        self.modelo = VocerosModelo()
        self._habitante_id = None
        self._cargos: list[Cargo] = []
        self._build_ui()
        self._cargar_cargos()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Nuevo Representante",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 20))

        # Buscar habitante
        ctk.CTkLabel(inner, text="Buscar Habitante (nombre o cedula) *",
                     font=FONTS["body_bold"], text_color=COLORS["neutral"]).pack(anchor="w")
        row_h = ctk.CTkFrame(inner, fg_color="transparent")
        row_h.pack(fill="x", pady=(4, 4))

        self.txt_habitante = ctk.CTkEntry(row_h, height=40, font=FONTS["body_base"],
                                          corner_radius=CORNER_RADIUS["input"],
                                          border_color=COLORS["outline_variant"])
        self.txt_habitante.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            row_h, text="Buscar", width=80, height=40,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"], font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._buscar_habitante,
        ).pack(side="right", padx=(8, 0))

        self.lbl_habitante_sel = ctk.CTkLabel(
            inner, text="Ninguno seleccionado",
            font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
        )
        self.lbl_habitante_sel.pack(anchor="w", pady=(2, 12))

        # Cargo
        ctk.CTkLabel(inner, text="Cargo *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.opt_cargo = ctk.CTkOptionMenu(
            inner, values=["Cargando..."],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_base"],
        )
        self.opt_cargo.pack(fill="x", pady=(4, 12))

        # Tipo
        ctk.CTkLabel(inner, text="Tipo *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.opt_tipo = ctk.CTkOptionMenu(
            inner, values=["Vocero", "Miembro"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_base"],
        )
        self.opt_tipo.pack(fill="x", pady=(4, 12))

        # Fecha inicio
        ctk.CTkLabel(inner, text="Fecha Inicio (AAAA-MM-DD) *",
                     font=FONTS["body_bold"], text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_inicio = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                                       corner_radius=CORNER_RADIUS["input"],
                                       border_color=COLORS["outline_variant"])
        self.txt_inicio.insert(0, str(date.today()))
        self.txt_inicio.pack(fill="x", pady=(4, 12))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Registrar",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _cargar_cargos(self):
        db = SessionLocal()
        try:
            self._cargos = db.query(Cargo).all()
            nombres = [c.nombre for c in self._cargos] or ["Sin cargos"]
            self._cargos_map = {c.nombre: c.id_cargo for c in self._cargos}
        finally:
            remove_db()
        self.opt_cargo.configure(values=nombres)
        if nombres:
            self.opt_cargo.set(nombres[0])

    def _buscar_habitante(self):
        busqueda = self.txt_habitante.get().strip()
        if not busqueda:
            return
        from habitantes.habitantes_modelo import HabitantesModelo
        modelo = HabitantesModelo()
        res = modelo.obtener_todos(busqueda=busqueda)
        if not res:
            self.lbl_habitante_sel.configure(
                text="No encontrado.", text_color=COLORS["error"])
            return
        h = res[0]
        self._habitante_id = h["id_habitante"]
        self.lbl_habitante_sel.configure(
            text=f"✓ {h['nombres']} {h['apellidos']} (CI: {h['cedula'] or '—'})",
            text_color=COLORS["tertiary"],
        )

    def _guardar(self):
        if not self._habitante_id:
            self.lbl_err.configure(text="Debe seleccionar un habitante.")
            return
        cargo_nombre = self.opt_cargo.get()
        cargo_id = self._cargos_map.get(cargo_nombre)
        if not cargo_id:
            self.lbl_err.configure(text="Cargo no valido.")
            return
        try:
            f_inicio = date.fromisoformat(self.txt_inicio.get().strip())
        except ValueError:
            self.lbl_err.configure(text="Fecha invalida (AAAA-MM-DD).")
            return

        datos = {
            "habitante_id": self._habitante_id,
            "cargo_id":     cargo_id,
            "tipo":         self.opt_tipo.get(),
            "fecha_inicio": f_inicio,
            "estado":       "activo",
        }
        ok, msg = self.modelo.crear_representante(datos)
        if ok:
            if self.on_guardar:
                self.on_guardar()
            self.destroy()
        else:
            self.lbl_err.configure(text=msg)
