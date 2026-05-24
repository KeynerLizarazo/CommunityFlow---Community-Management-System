"""
autenticacion/usuarios_admin_vista.py – Gestión de Usuarios (solo Admin).
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from config.style import COLORS, FONTS, PADDING, CORNER_RADIUS, aplicar_estilo_tabla
from autenticacion.usuario_modelo import UsuarioModelo, Usuario
from config.database import SessionLocal, remove_db
from config.auth_session import AuthSession
from bitacora.bitacora_modelo import BitacoraModelo


class UsuariosAdminVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True, padx=PADDING["lg"], pady=PADDING["lg"])
        aplicar_estilo_tabla()
        self.modelo = UsuarioModelo()
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # Encabezado
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, PADDING["lg"]))

        ctk.CTkLabel(hdr, text="Gestion de Usuarios",
                     font=FONTS["display_lg"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Nuevo Usuario",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=40, corner_radius=CORNER_RADIUS["button"],
            command=self._abrir_modal_crear,
        ).pack(side="right")

        # Tabla
        card = ctk.CTkFrame(
            self, fg_color=COLORS["surface_lowest"],
            corner_radius=CORNER_RADIUS["card"],
            border_width=1, border_color=COLORS["outline_variant"],
        )
        card.pack(fill="both", expand=True)

        hdr2 = ctk.CTkFrame(card, fg_color="transparent")
        hdr2.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(hdr2, text="Usuarios del Sistema",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(side="left")

        ctk.CTkFrame(card, height=1, fg_color=COLORS["outline_variant"]).pack(fill="x")

        cols = ("ID", "Usuario", "Nombre Completo", "Rol", "Estado", "Cambio PW")
        self.tabla = ttk.Treeview(card, columns=cols, show="headings",
                                  style="CF.Treeview")
        anchos = {"ID": 50, "Usuario": 140, "Nombre Completo": 220,
                  "Rol": 100, "Estado": 90, "Cambio PW": 100}
        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center" if col != "Nombre Completo" else "w",
                             width=anchos[col])

        sb = ttk.Scrollbar(card, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 8))

        self.tabla.tag_configure("activo",   foreground=COLORS["tertiary"])
        self.tabla.tag_configure("inactivo", foreground=COLORS["on_surface_variant"])

        # Botones de acción
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", pady=(PADDING["md"], 0))

        for texto, color, hover, cmd in [
            ("Editar Usuario",      COLORS["secondary"],   COLORS["on_secondary_container"], self._editar),
            ("Restablecer Password",COLORS["warning"],     "#E65100",                        self._restablecer_pw),
            ("Desactivar",          COLORS["error"],       "#B71C1C",                        self._desactivar),
        ]:
            ctk.CTkButton(
                acciones, text=texto,
                fg_color=color, hover_color=hover,
                text_color=COLORS["on_primary"], font=FONTS["body_bold"],
                height=38, corner_radius=CORNER_RADIUS["button"],
                command=cmd,
            ).pack(side="left", padx=(0, 10))

    def _cargar_datos(self):
        usuarios = self.modelo.obtener_todos()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for u in usuarios:
            tag = "activo" if u["activo"] else "inactivo"
            self.tabla.insert("", "end", iid=str(u["id_usuario"]), values=(
                u["id_usuario"],
                u["nombre_usuario"],
                u["nombre_completo"] or "—",
                u["rol"],
                "Activo" if u["activo"] else "Inactivo",
                "Si" if u["cambio_password_obligatorio"] else "No",
            ), tags=(tag,))

    def _sel_id(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Seleccion", "Seleccione un usuario de la tabla.")
            return None
        return int(sel[0])

    def _abrir_modal_crear(self):
        dlg = _ModalUsuario(self, on_guardar=self._cargar_datos)
        dlg.grab_set()

    def _editar(self):
        uid = self._sel_id()
        if uid is None:
            return
        # Obtener datos actuales
        todos = self.modelo.obtener_todos()
        user_data = next((u for u in todos if u["id_usuario"] == uid), None)
        if not user_data:
            return
        dlg = _ModalUsuario(self, on_guardar=self._cargar_datos, user_data=user_data)
        dlg.grab_set()

    def _restablecer_pw(self):
        uid = self._sel_id()
        if uid is None:
            return
        dlg = _ModalResetPW(self, uid, on_guardar=self._cargar_datos)
        dlg.grab_set()

    def _desactivar(self):
        uid = self._sel_id()
        if uid is None:
            return
        me = AuthSession.get_usuario()
        if me and me.id_usuario == uid:
            messagebox.showerror("Error", "No puedes desactivar tu propia cuenta.")
            return
        if messagebox.askyesno("Confirmar", f"¿Desactivar el usuario #{uid}?"):
            ok, msg = self.modelo.actualizar_usuario(uid, *[
                u[k] for u in self.modelo.obtener_todos() if u["id_usuario"] == uid
                for k in ["nombre_usuario", "nombre_completo", "rol"]
            ] + [False])
            self._cargar_datos()


# ─── Modal Crear/Editar Usuario ───────────────────────────────────────────────
class _ModalUsuario(ctk.CTkToplevel):
    def __init__(self, parent, on_guardar=None, user_data=None):
        super().__init__(parent)
        self.title("Nuevo Usuario" if user_data is None else "Editar Usuario")
        self.geometry("480x520")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.on_guardar = on_guardar
        self.user_data  = user_data
        self.modelo     = UsuarioModelo()
        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        titulo = "Crear Usuario" if self.user_data is None else "Editar Usuario"
        ctk.CTkLabel(inner, text=titulo,
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 20))

        def campo(lbl, key, placeholder=""):
            ctk.CTkLabel(inner, text=lbl, font=FONTS["body_bold"],
                         text_color=COLORS["neutral"]).pack(anchor="w")
            e = ctk.CTkEntry(inner, height=40, font=FONTS["body_base"],
                             placeholder_text=placeholder,
                             corner_radius=CORNER_RADIUS["input"],
                             border_color=COLORS["outline_variant"])
            e.pack(fill="x", pady=(4, 12))
            return e

        self.txt_usuario  = campo("Nombre de Usuario *")
        self.txt_nombre   = campo("Nombre Completo")
        if self.user_data is None:
            self.txt_pw = campo("Contraseña *")
        else:
            self.txt_pw = None

        ctk.CTkLabel(inner, text="Rol *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.opt_rol = ctk.CTkOptionMenu(
            inner, values=["Admin", "Operador", "Lectura"],
            fg_color=COLORS["primary"], button_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_base"],
        )
        self.opt_rol.pack(fill="x", pady=(4, 12))

        if self.user_data:
            self.txt_usuario.insert(0, self.user_data.get("nombre_usuario", ""))
            self.txt_nombre.insert(0, self.user_data.get("nombre_completo", "") or "")
            self.opt_rol.set(self.user_data.get("rol", "Admin"))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Guardar",
            fg_color=COLORS["primary"], hover_color=COLORS["primary_container"],
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        usuario = self.txt_usuario.get().strip()
        nombre  = self.txt_nombre.get().strip()
        rol     = self.opt_rol.get()

        if not usuario:
            self.lbl_err.configure(text="El nombre de usuario es obligatorio.")
            return

        if self.user_data is None:
            # Crear
            pw = self.txt_pw.get()
            if not pw or len(pw) < 6:
                self.lbl_err.configure(text="La contraseña debe tener al menos 6 caracteres.")
                return
            ok, msg = self.modelo.crear_usuario(usuario, pw, nombre, rol)
        else:
            # Editar
            ok, msg = self.modelo.actualizar_usuario(
                self.user_data["id_usuario"], usuario, nombre, rol,
                self.user_data.get("activo", True),
            )
        if ok:
            if self.on_guardar:
                self.on_guardar()
            self.destroy()
        else:
            self.lbl_err.configure(text=msg)


# ─── Modal Reset Password ─────────────────────────────────────────────────────
class _ModalResetPW(ctk.CTkToplevel):
    def __init__(self, parent, id_usuario: int, on_guardar=None):
        super().__init__(parent)
        self.title("Restablecer Contraseña")
        self.geometry("420x340")
        self.configure(fg_color=COLORS["surface_lowest"])
        self.id_usuario = id_usuario
        self.on_guardar = on_guardar
        self.modelo     = UsuarioModelo()
        self._build_ui()

    def _build_ui(self):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(inner, text="Restablecer Contraseña",
                     font=FONTS["headline_sm"], text_color=COLORS["neutral"]).pack(pady=(0, 8))
        ctk.CTkLabel(
            inner,
            text=f"Usuario #{self.id_usuario}\nEl usuario debera cambiar la contrasena al iniciar sesion.",
            font=FONTS["helper_text"], text_color=COLORS["on_surface_variant"],
            justify="center",
        ).pack(pady=(0, 20))

        ctk.CTkLabel(inner, text="Nueva Contraseña *", font=FONTS["body_bold"],
                     text_color=COLORS["neutral"]).pack(anchor="w")
        self.txt_pw = ctk.CTkEntry(inner, show="*", height=44, font=FONTS["body_base"],
                                   corner_radius=CORNER_RADIUS["input"],
                                   border_color=COLORS["outline_variant"])
        self.txt_pw.pack(fill="x", pady=(4, 12))

        self.lbl_err = ctk.CTkLabel(inner, text="", text_color=COLORS["error"],
                                    font=FONTS["helper_text"])
        self.lbl_err.pack()

        ctk.CTkButton(
            inner, text="Restablecer",
            fg_color=COLORS["error"], hover_color="#B71C1C",
            text_color=COLORS["on_primary"], font=FONTS["body_bold"],
            height=44, corner_radius=CORNER_RADIUS["button"],
            command=self._guardar,
        ).pack(fill="x", pady=(12, 0))

    def _guardar(self):
        pw = self.txt_pw.get()
        if len(pw) < 6:
            self.lbl_err.configure(text="Minimo 6 caracteres.")
            return
        ok, msg = self.modelo.admin_cambiar_contrasena(self.id_usuario, pw)
        if ok:
            if self.on_guardar:
                self.on_guardar()
            self.destroy()
        else:
            self.lbl_err.configure(text=msg)
