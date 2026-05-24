"""
proyectos/proyectos_vista.py – Módulo de Proyectos Comunales.
Pestañas Activos/Pendientes/Finalizados, tarjetas de proyecto, modal nuevo proyecto.
"""
import customtkinter as ctk
from tkinter import ttk
from datetime import date
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from proyectos.proyectos_modelo import ProyectosModelo, Proyecto
from config.database import SessionLocal, remove_db
from config.auth_session import AuthSession
from bitacora.bitacora_modelo import BitacoraModelo


ESTADO_COLORES = {
    "Activo":     COLORS["tertiary"],
    "Pendiente":  COLORS["warning"],
    "Finalizado": COLORS["on_surface_variant"],
}


class ProyectosVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self.modelo = ProyectosModelo()
        self._build_ui()

    def _build_ui(self):
        # Encabezado
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(hdr, text="Proyectos Comunales",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Nuevo Proyecto",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=40, corner_radius=CORNER_RADIUS["button"],
            command=self._abrir_modal,
        ).pack(side="right")

        # Pestañas
        self.tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["surface_lowest"],
            segmented_button_fg_color=COLORS["surface_high"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_container"],
            segmented_button_unselected_color=COLORS["surface_high"],
            segmented_button_unselected_hover_color=COLORS["surface_high"],
            text_color=COLORS["neutral"],
            corner_radius=CORNER_RADIUS["card"],
        )
        self.tabs.pack(fill="both", expand=True)

        for estado in ["Activo", "Pendiente", "Finalizado"]:
            tab = self.tabs.add(estado)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            self._build_tab(tab, estado)

    def _build_tab(self, tab: ctk.CTkFrame, estado: str):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure((0, 1, 2), weight=1)

        proyectos = self.modelo.obtener_por_estado(estado)

        if not proyectos:
            ctk.CTkLabel(
                scroll,
                text=f"No hay proyectos {estado.lower()}s.",
                font=FONTS["body_base"], text_color=COLORS["on_surface_variant"],
            ).pack(pady=40)
            return

        for idx, p in enumerate(proyectos):
            col = idx % 3
            row = idx // 3
            self._tarjeta_proyecto(scroll, p, row, col)

    def _tarjeta_proyecto(self, parent, p: Proyecto, row: int, col: int):
        color = ESTADO_COLORES.get(p.estado, COLORS["primary"])
        card = ctk.CTkFrame(
            parent, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6, ipady=4)

        # Barra de estado
        ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        # Badge estado
        badge = ctk.CTkLabel(
            body, text=f"  {p.estado}  ",
            font=FONTS["label_caps"],
            fg_color=color, text_color=COLORS["on_primary"],
            corner_radius=CORNER_RADIUS["chip"],
        )
        badge.pack(anchor="e", pady=(0, 6))

        ctk.CTkLabel(
            body, text=p.nombre,
            font=FONTS["body_bold"], text_color=COLORS["neutral"],
            anchor="w", wraplength=240,
        ).pack(anchor="w")

        ctk.CTkLabel(
            body, text=f"Cod: {p.codigo}",
            font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 6))

        if p.descripcion:
            ctk.CTkLabel(
                body, text=p.descripcion,
                font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
                anchor="w", wraplength=240,
            ).pack(anchor="w", pady=(0, 8))

        fechas = f"{p.fecha_inicio or '—'} → {p.fecha_fin or '—'}"
        ctk.CTkLabel(
            body, text=fechas,
            font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        # Cambiar estado
        estados_disponibles = [e for e in ["Activo", "Pendiente", "Finalizado"] if e != p.estado]
        opt = ctk.CTkOptionMenu(
            body, values=estados_disponibles,
            width=180, font=FONTS["helper_text"],
            fg_color=COLORS["surface_high"],
            button_color=COLORS["primary"],
            text_color=COLORS["neutral"],
            command=lambda v, pid=p.id_proyecto: self._cambiar_estado(pid, v),
        )
        opt.set("Cambiar estado...")
        opt.pack(fill="x")

    def _cambiar_estado(self, id_proyecto: int, nuevo_estado: str):
        self.modelo.cambiar_estado(id_proyecto, nuevo_estado)
        usuario = AuthSession.get_usuario()
        BitacoraModelo.registrar_accion(
            usuario_id=usuario.id_usuario if usuario else 0,
            modulo="Proyectos", accion="editar",
            registro_id=str(id_proyecto),
            datos_nuevos={"estado": nuevo_estado},
        )
        # Recargar la pestaña activa
        self._refrescar()

    def _refrescar(self):
        tab_activa = self.tabs.get()
        for estado in ["Activo", "Pendiente", "Finalizado"]:
            tab = self.tabs.tab(estado)
            for w in tab.winfo_children():
                w.destroy()
            self._build_tab(tab, estado)

    def _abrir_modal(self):
        dlg = _ModalProyecto(self, on_guardar=self._refrescar)
        dlg.grab_set()


# ─── Modal Proyecto ───────────────────────────────────────────────────────────
class _ModalProyecto(ctk.CTkToplevel):
    def __init__(self, parent, on_guardar=None):
        super().__init__(parent)
        self.title("Nuevo Proyecto")
        self.geometry("520x560")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.on_guardar = on_guardar
        self.modelo = ProyectosModelo()
        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Nuevo Proyecto Comunal",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 20))

        def campo(lbl, ph=""):
            ctk.CTkLabel(inner, text=lbl, font=FONTS["body_bold"],
                         text_color=COLORS["neutral"]).pack(anchor="w")
            e = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                             placeholder_text=ph,
                             corner_radius=CORNER_RADIUS["input"],
                             border_color=COLORS["outline_variant"])
            e.pack(fill="x", pady=(4, 12))
            return e

        self.txt_codigo      = campo("Codigo Unico *", "PROY-001")
        self.txt_nombre      = campo("Nombre del Proyecto *")
        self.txt_descripcion = campo("Descripcion")
        self.txt_inicio      = campo("Fecha Inicio (AAAA-MM-DD)", str(date.today()))
        self.txt_fin         = campo("Fecha Fin (AAAA-MM-DD)")

        ctk.CTkLabel(inner, text="Estado inicial", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.opt_estado = ctk.CTkOptionMenu(
            inner, values=["Pendiente", "Activo"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_base"],
        )
        self.opt_estado.pack(fill="x", pady=(4, 12))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Crear Proyecto",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        codigo  = self.txt_codigo.get().strip()
        nombre  = self.txt_nombre.get().strip()
        if not codigo or not nombre:
            self.lbl_err.configure(text="Codigo y Nombre son obligatorios.")
            return

        def _parse_fecha(s):
            s = s.strip()
            if not s:
                return None
            try:
                return date.fromisoformat(s)
            except ValueError:
                return None

        datos = {
            "codigo":      codigo,
            "nombre":      nombre,
            "descripcion": self.txt_descripcion.get().strip() or None,
            "estado":      self.opt_estado.get(),
            "fecha_inicio":_parse_fecha(self.txt_inicio.get()),
            "fecha_fin":   _parse_fecha(self.txt_fin.get()),
            "activo":      True,
        }

        db = SessionLocal()
        try:
            existe = db.query(Proyecto).filter_by(codigo=codigo).first()
            if existe:
                self.lbl_err.configure(text="Ya existe un proyecto con ese codigo.")
                return
            db.add(Proyecto(**datos))
            db.commit()
        except Exception as exc:
            db.rollback()
            self.lbl_err.configure(text=f"Error: {exc}")
            return
        finally:
            remove_db()

        usuario = AuthSession.get_usuario()
        BitacoraModelo.registrar_accion(
            usuario_id=usuario.id_usuario if usuario else 0,
            modulo="Proyectos", accion="crear",
            datos_nuevos={"codigo": codigo, "nombre": nombre},
        )
        if self.on_guardar:
            self.on_guardar()
        self.destroy()
