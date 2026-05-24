"""
panel/dashboard_vista.py – Dashboard principal de CommunityFlow.
Muestra KPIs, actividad reciente y proyectos activos.
"""
import threading
import customtkinter as ctk
from tkinter import ttk
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from config.database import SessionLocal, remove_db
from config.auth_session import AuthSession


class DashboardVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self._kpi_labels: dict = {}
        self._build_ui()
        self._cargar_datos_async()

    # ─── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Encabezado ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(
            header, text="Dashboard", font=FONTS["display_lg"],
            text_color=COLORS["neutral"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Vista general del sistema",
            font=FONTS["body_base"],
            text_color=COLORS["on_surface_variant"],
        ).pack(side="left", padx=16, pady=(8, 0))

        # ── Fila de KPIs ──
        self._kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        self._kpi_row.pack(fill="x", pady=(0, PADDING["lg"]))

        kpis = [
            ("Total Familias",    "0",      COLORS["primary"],             "familias"),
            ("Habitantes",        "0",      COLORS["secondary"],           "habitantes"),
            ("Voceros Activos",   "0",      COLORS["tertiary"],            "voceros"),
            ("Saldo en Caja",     "Bs 0",   COLORS["warning"],             "saldo"),
            ("Proyectos Activos", "0",      COLORS["on_secondary_container"], "proyectos"),
        ]
        for i, (titulo, valor, color, key) in enumerate(kpis):
            self._kpi_row.grid_columnconfigure(i, weight=1)
            lbl = self._crear_tarjeta_kpi(self._kpi_row, titulo, valor, color, i)
            self._kpi_labels[key] = lbl

        # ── Sección inferior: Actividad + Proyectos ──
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True)
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_rowconfigure(0, weight=1)

        self._build_actividad(bottom)
        self._build_proyectos(bottom)

    def _crear_tarjeta_kpi(self, parent, titulo, valor, color, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1,
            border_color=COLORS["outline_variant"],
        )
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0), ipady=10)

        # Barra de color superior
        ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0).pack(fill="x")

        ctk.CTkLabel(
            card, text=titulo,
            font=FONTS["label_caps"], text_color=COLORS["on_surface_variant"],
        ).pack(pady=(14, 2))

        lbl_valor = ctk.CTkLabel(
            card, text=valor,
            font=FONTS["display_lg"], text_color=color,
        )
        lbl_valor.pack(pady=(0, 14))

        return lbl_valor

    def _build_actividad(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1,
            border_color=COLORS["outline_variant"],
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            frame, text="Actividad Reciente",
            font=FONTS["headline_sm"], text_color=COLORS["neutral"],
        ).pack(anchor="w", padx=16, pady=(16, 8))

        ctk.CTkFrame(frame, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x", padx=16)

        self._actividad_frame = ctk.CTkScrollableFrame(
            frame, fg_color="transparent", height=280
        )
        self._actividad_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Placeholder inicial
        ctk.CTkLabel(
            self._actividad_frame,
            text="Cargando actividad...",
            font=FONTS["helper_text"],
            text_color=COLORS["on_surface_variant"],
        ).pack(pady=20)

    def _build_proyectos(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1,
            border_color=COLORS["outline_variant"],
        )
        frame.grid(row=0, column=1, sticky="nsew")

        header_f = ctk.CTkFrame(frame, fg_color="transparent")
        header_f.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            header_f, text="Proyectos Activos",
            font=FONTS["headline_sm"], text_color=COLORS["neutral"],
        ).pack(side="left")

        ctk.CTkFrame(frame, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x", padx=16)

        # Tabla de proyectos
        cols = ("Proyecto", "Estado", "Inicio", "Fin")
        self._tree_proyectos = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="CF.Treeview", height=8,
        )
        for col in cols:
            self._tree_proyectos.heading(col, text=col)
            self._tree_proyectos.column(col, anchor="center", width=160)
        self._tree_proyectos.column("Proyecto", anchor="w", width=220)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self._tree_proyectos.yview)
        self._tree_proyectos.configure(yscrollcommand=sb.set)

        self._tree_proyectos.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=12)
        sb.pack(side="right", fill="y", pady=12, padx=(0, 8))

    # ─── Datos ───────────────────────────────────────────────────────────────
    def _cargar_datos_async(self):
        threading.Thread(target=self._fetch_datos, daemon=True).start()

    def _fetch_datos(self):
        try:
            from familias.familias_modelo import Familia
            from habitantes.habitantes_modelo import Habitante
            from voceros.voceros_modelo import Representante
            from finanzas.finanzas_modelo import FinanzasModelo
            from proyectos.proyectos_modelo import Proyecto
            from bitacora.bitacora_modelo import BitacoraModelo

            db = SessionLocal()
            try:
                n_familias  = db.query(Familia).filter_by(activo=True).count()
                n_habitantes= db.query(Habitante).filter_by(activo=True).count()
                n_voceros   = db.query(Representante).filter_by(estado="activo").count()
                n_proyectos = db.query(Proyecto).filter_by(estado="Activo", activo=True).count()
                proyectos   = db.query(Proyecto).filter_by(activo=True).limit(20).all()
                proy_data   = [
                    (p.nombre, p.estado, str(p.fecha_inicio or "—"), str(p.fecha_fin or "—"))
                    for p in proyectos
                ]
            finally:
                remove_db()

            balance = FinanzasModelo().obtener_balance()
            actividad = BitacoraModelo().obtener_registros(limite=10)

            # Actualizar UI en hilo principal
            self.after(0, lambda: self._actualizar_ui(
                n_familias, n_habitantes, n_voceros, balance, n_proyectos,
                proy_data, actividad
            ))
        except Exception as exc:
            print(f"[Dashboard] Error cargando datos: {exc}")

    def _actualizar_ui(self, familias, habitantes, voceros, saldo, proyectos_n,
                       proy_data, actividad):
        self._kpi_labels["familias"].configure(text=str(familias))
        self._kpi_labels["habitantes"].configure(text=str(habitantes))
        self._kpi_labels["voceros"].configure(text=str(voceros))
        self._kpi_labels["saldo"].configure(text=f"Bs {saldo:,.2f}")
        self._kpi_labels["proyectos"].configure(text=str(proyectos_n))

        # Actividad
        for w in self._actividad_frame.winfo_children():
            w.destroy()

        if not actividad:
            ctk.CTkLabel(
                self._actividad_frame,
                text="Sin actividad reciente.",
                font=FONTS["helper_text"],
                text_color=COLORS["on_surface_variant"],
            ).pack(pady=20)
        else:
            accion_colores = {
                "crear": COLORS["tertiary"],
                "editar": COLORS["warning"],
                "eliminar": COLORS["error"],
            }
            for reg in actividad:
                row = ctk.CTkFrame(
                    self._actividad_frame, fg_color=COLORS["surface"],
                    corner_radius=8,
                )
                row.pack(fill="x", pady=3, padx=4)

                color = accion_colores.get(reg.get("accion",""), COLORS["primary"])
                ctk.CTkFrame(row, width=4, fg_color=color, corner_radius=2).pack(side="left", fill="y", padx=(0, 8))

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, pady=8)

                ctk.CTkLabel(
                    info,
                    text=f"{reg.get('modulo','?')} · {reg.get('accion','?')}",
                    font=FONTS["body_bold"], text_color=COLORS["neutral"],
                    anchor="w",
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info,
                    text=f"{reg.get('usuario_nombre','?')} — {reg.get('fecha_hora','')}",
                    font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
                    anchor="w",
                ).pack(anchor="w")

        # Proyectos
        for row in self._tree_proyectos.get_children():
            self._tree_proyectos.delete(row)
        for p in proy_data:
            self._tree_proyectos.insert("", "end", values=p)
