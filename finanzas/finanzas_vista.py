"""
finanzas/finanzas_vista.py – Módulo de Finanzas.
Tarjetas de balance, tabla de movimientos con badges, modal de registro.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from finanzas.finanzas_modelo import FinanzasModelo, MovimientoFinanciero
from config.database import SessionLocal, remove_db
from config.auth_session import AuthSession
from bitacora.bitacora_modelo import BitacoraModelo


class FinanzasVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self.modelo = FinanzasModelo()
        self._filtro_tipo = "Todos"
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # ── Encabezado ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(hdr, text="Finanzas",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Registrar Movimiento",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=40, corner_radius=CORNER_RADIUS["button"],
            command=self._abrir_modal,
        ).pack(side="right")

        # ── Tarjetas balance ──
        bal_row = ctk.CTkFrame(self, fg_color="transparent")
        bal_row.pack(fill="x", pady=(0, PADDING["md"]))
        for i in range(3):
            bal_row.grid_columnconfigure(i, weight=1)

        self._lbl_ingresos = self._tarjeta_balance(bal_row, "Total Ingresos",
                                                    COLORS["tertiary"], 0)
        self._lbl_egresos  = self._tarjeta_balance(bal_row, "Total Egresos",
                                                    COLORS["error"], 1)
        self._lbl_balance  = self._tarjeta_balance(bal_row, "Balance Neto",
                                                    COLORS["primary"], 2)

        # ── Filtros ──
        filtros = ctk.CTkFrame(self, fg_color=COLORS["surface_high"],
                               corner_radius=CORNER_RADIUS["input"])
        filtros.pack(fill="x", pady=(0, PADDING["md"]))

        self.txt_busqueda = ctk.CTkEntry(
            filtros, placeholder_text="Buscar concepto...",
            height=40, font=FONTS["body_base"], fg_color="transparent", border_width=0,
        )
        self.txt_busqueda.pack(side="left", fill="x", expand=True, padx=12)
        self.txt_busqueda.bind("<Return>", lambda e: self._cargar_datos())

        ctk.CTkLabel(filtros, text="Tipo:", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(side="left", padx=(0, 4))

        self.opt_tipo = ctk.CTkOptionMenu(
            filtros, values=["Todos", "Ingreso", "Egreso"],
            width=120, font=FONTS["body_base"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"],
            command=lambda v: setattr(self, "_filtro_tipo", v) or self._cargar_datos(),
        )
        self.opt_tipo.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            filtros, text="Buscar", width=90, height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"], font=FONTS["body_bold"],
            corner_radius=CORNER_RADIUS["button"],
            command=self._cargar_datos,
        ).pack(side="right", padx=8)

        # ── Tabla ──
        tabla_card = ctk.CTkFrame(
            self, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        tabla_card.pack(fill="both", expand=True)

        hdr2 = ctk.CTkFrame(tabla_card, fg_color="transparent")
        hdr2.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(hdr2, text="Movimientos Financieros",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(side="left")
        self.lbl_conteo = ctk.CTkLabel(hdr2, text="",
                                       font=FONTS["helper_text"],
                                       text_color=COLORS["on_surface_variant"])
        self.lbl_conteo.pack(side="right")

        ctk.CTkFrame(tabla_card, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x")

        cols = ("Fecha", "Tipo", "Concepto", "Monto", "Proyecto")
        self.tabla = ttk.Treeview(tabla_card, columns=cols, show="headings",
                                  style="CF.Treeview")
        anchos = {"Fecha": 100, "Tipo": 90, "Concepto": 300, "Monto": 120, "Proyecto": 140}
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center" if col != "Concepto" else "w",
                             width=anchos[col])

        sb = ttk.Scrollbar(tabla_card, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))

        # Tags de color por tipo
        self.tabla.tag_configure("ingreso",  foreground=COLORS["tertiary"])
        self.tabla.tag_configure("egreso",   foreground=COLORS["error"])

    def _tarjeta_balance(self, parent, titulo, color, col):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0), ipady=10)
        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(card, text=titulo, font=FONTS["label_caps"],
                     text_color=COLORS["on_surface_variant"]).pack(pady=(10, 2))
        lbl = ctk.CTkLabel(card, text="Bs 0.00", font=FONTS["headline_md"], text_color=color)
        lbl.pack(pady=(0, 10))
        return lbl

    def _cargar_datos(self):
        from sqlalchemy import func
        db = SessionLocal()
        try:
            query = db.query(MovimientoFinanciero)
            busqueda = self.txt_busqueda.get().strip()
            if busqueda:
                query = query.filter(MovimientoFinanciero.concepto.ilike(f"%{busqueda}%"))
            if self._filtro_tipo != "Todos":
                query = query.filter(MovimientoFinanciero.tipo == self._filtro_tipo)

            movs = query.order_by(MovimientoFinanciero.fecha.desc()).limit(500).all()

            # Totales
            ing = db.query(func.sum(MovimientoFinanciero.monto)).filter(
                MovimientoFinanciero.tipo == "Ingreso").scalar() or 0
            egr = db.query(func.sum(MovimientoFinanciero.monto)).filter(
                MovimientoFinanciero.tipo == "Egreso").scalar() or 0

            mov_data = [
                (m.fecha.strftime("%d/%m/%Y") if m.fecha else "—",
                 m.tipo, m.concepto,
                 f"Bs {m.monto:,.2f}",
                 str(m.proyecto_id) if m.proyecto_id else "—")
                for m in movs
            ]
            tipos = [m.tipo for m in movs]
        finally:
            remove_db()

        self._lbl_ingresos.configure(text=f"Bs {float(ing):,.2f}")
        self._lbl_egresos.configure(text=f"Bs {float(egr):,.2f}")
        neto = float(ing) - float(egr)
        color_neto = COLORS["tertiary"] if neto >= 0 else COLORS["error"]
        self._lbl_balance.configure(text=f"Bs {neto:,.2f}", text_color=color_neto)
        self.lbl_conteo.configure(text=f"{len(mov_data)} registros")

        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for datos, tipo in zip(mov_data, tipos):
            tag = "ingreso" if tipo == "Ingreso" else "egreso"
            self.tabla.insert("", "end", values=datos, tags=(tag,))

    def _abrir_modal(self):
        dlg = _ModalMovimiento(self, on_guardar=self._cargar_datos)
        dlg.grab_set()


# ─── Modal Movimiento ─────────────────────────────────────────────────────────
class _ModalMovimiento(ctk.CTkToplevel):
    def __init__(self, parent, on_guardar=None):
        super().__init__(parent)
        self.title("Registrar Movimiento")
        self.geometry("500x500")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.on_guardar = on_guardar
        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Nuevo Movimiento Financiero",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 20))

        # Tipo
        ctk.CTkLabel(inner, text="Tipo *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.opt_tipo = ctk.CTkOptionMenu(
            inner, values=["Ingreso", "Egreso"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_base"],
        )
        self.opt_tipo.pack(fill="x", pady=(4, 12))

        # Monto
        ctk.CTkLabel(inner, text="Monto (Bs) *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_monto = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                                      corner_radius=CORNER_RADIUS["input"],
                                      border_color=COLORS["outline_variant"])
        self.txt_monto.pack(fill="x", pady=(4, 12))

        # Concepto
        ctk.CTkLabel(inner, text="Concepto *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_concepto = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                                         corner_radius=CORNER_RADIUS["input"],
                                         border_color=COLORS["outline_variant"])
        self.txt_concepto.pack(fill="x", pady=(4, 12))

        # Observaciones
        ctk.CTkLabel(inner, text="Observaciones", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_obs = ctk.CTkTextbox(inner, height=80, font=FONTS["body_base"],
                                      corner_radius=CORNER_RADIUS["input"],
                                      border_width=1,
                                      border_color=COLORS["outline_variant"])
        self.txt_obs.pack(fill="x", pady=(4, 12))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Guardar Movimiento",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        tipo     = self.opt_tipo.get()
        concepto = self.txt_concepto.get().strip()
        obs      = self.txt_obs.get("1.0", "end").strip()
        monto_str= self.txt_monto.get().strip()

        if not concepto or not monto_str:
            self.lbl_err.configure(text="Tipo, Monto y Concepto son obligatorios.")
            return
        try:
            monto = float(monto_str.replace(",", "."))
            if monto <= 0:
                raise ValueError
        except ValueError:
            self.lbl_err.configure(text="El monto debe ser un número positivo.")
            return

        from config.database import SessionLocal, remove_db
        db = SessionLocal()
        try:
            from finanzas.finanzas_modelo import MovimientoFinanciero
            db.add(MovimientoFinanciero(
                tipo=tipo, monto=monto, concepto=concepto,
                observaciones=obs or None, fecha=date.today(),
            ))
            db.commit()

            usuario = AuthSession.get_usuario()
            BitacoraModelo.registrar_accion(
                usuario_id=usuario.id_usuario if usuario else 0,
                modulo="Finanzas", accion="crear",
                datos_nuevos={"tipo": tipo, "monto": monto, "concepto": concepto},
            )
        except Exception as exc:
            db.rollback()
            self.lbl_err.configure(text=f"Error: {exc}")
            return
        finally:
            remove_db()

        if self.on_guardar:
            self.on_guardar()
        self.destroy()
