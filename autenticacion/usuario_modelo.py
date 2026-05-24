from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import make_transient
from config.database import Base, SessionLocal, remove_db
import bcrypt


class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    contrasena_hash = Column(String(200), nullable=False)   # 200 chars por seguridad
    nombre_completo = Column(String(100))
    activo = Column(Boolean, default=True)
    cambio_password_obligatorio = Column(Boolean, default=False)
    rol = Column(String(20), default='Admin')


class UsuarioModelo:

    # ── Autenticación ─────────────────────────────────────────────────────────
    def autenticar(self, usuario: str, contrasena: str):
        """
        Autentica al usuario.
        - Captura ValueError (hash inválido) y retorna None sin romper la app.
        - Retorna un objeto Usuario desacoplado de la sesión.
        """
        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(
                Usuario.nombre_usuario == usuario,
                Usuario.activo == True,
            ).first()

            if user is None:
                return None

            try:
                ok = bcrypt.checkpw(
                    contrasena.encode('utf-8'),
                    user.contrasena_hash.encode('utf-8'),
                )
            except ValueError:
                # Hash corrupto en BD: lo informamos y devolvemos None
                print(
                    f"[autenticar][WARN] Hash invalido para '{usuario}'. "
                    "Ejecute init_db() o el script de reparacion para corregirlo."
                )
                return None
            except Exception as exc:
                print(f"[autenticar] Error inesperado en bcrypt: {exc}")
                return None

            if ok:
                # Desacoplar el objeto de la sesión antes de devolverlo
                db.expunge(user)
                make_transient(user)
                return user

            return None

        finally:
            remove_db()

    def usuario_existe(self, nombre_usuario: str) -> bool:
        """Verifica si el nombre de usuario existe en la BD."""
        db = SessionLocal()
        try:
            return db.query(Usuario).filter(
                Usuario.nombre_usuario == nombre_usuario
            ).first() is not None
        finally:
            remove_db()

    # ── Cambios de contraseña ─────────────────────────────────────────────────
    def cambiar_usuario(self, id_usuario: int, nuevo_usuario: str) -> bool:
        db = SessionLocal()
        try:
            user = db.query(Usuario).get(id_usuario)
            if user:
                user.nombre_usuario = nuevo_usuario
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            remove_db()

    def cambiar_contrasena(self, id_usuario: int, actual: str, nueva: str) -> bool:
        db = SessionLocal()
        try:
            user = db.query(Usuario).get(id_usuario)
            if not user:
                return False
            try:
                ok = bcrypt.checkpw(
                    actual.encode('utf-8'),
                    user.contrasena_hash.encode('utf-8'),
                )
            except ValueError:
                return False
            if ok:
                nuevo_hash = bcrypt.hashpw(
                    nueva.encode('utf-8'), bcrypt.gensalt()
                ).decode('utf-8')
                user.contrasena_hash = nuevo_hash
                user.cambio_password_obligatorio = False
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            remove_db()

    def forzar_cambio_contrasena(self, id_usuario: int, nueva: str) -> bool:
        """Cambio forzado de contraseña en el primer inicio de sesión."""
        db = SessionLocal()
        try:
            user = db.query(Usuario).get(id_usuario)
            if user:
                nuevo_hash = bcrypt.hashpw(
                    nueva.encode('utf-8'), bcrypt.gensalt()
                ).decode('utf-8')
                user.contrasena_hash = nuevo_hash
                user.cambio_password_obligatorio = False
                db.commit()
                return True
            return False
        except Exception as exc:
            db.rollback()
            print(f"[forzar_cambio_contrasena] Error: {exc}")
            return False
        finally:
            remove_db()

    # ── CRUD de usuarios (panel admin) ────────────────────────────────────────
    def obtener_todos(self) -> list:
        db = SessionLocal()
        try:
            usuarios = db.query(Usuario).all()
            return [
                {
                    "id_usuario": u.id_usuario,
                    "nombre_usuario": u.nombre_usuario,
                    "nombre_completo": u.nombre_completo,
                    "activo": u.activo,
                    "cambio_password_obligatorio": u.cambio_password_obligatorio,
                    "rol": u.rol,
                }
                for u in usuarios
            ]
        finally:
            remove_db()

    def crear_usuario(self, nombre_usuario: str, contrasena: str,
                      nombre_completo: str, rol: str):
        db = SessionLocal()
        try:
            if db.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first():
                return False, "El nombre de usuario ya existe."
            hashed = bcrypt.hashpw(
                contrasena.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            db.add(Usuario(
                nombre_usuario=nombre_usuario,
                contrasena_hash=hashed,
                nombre_completo=nombre_completo,
                rol=rol,
                activo=True,
                cambio_password_obligatorio=True,
            ))
            db.commit()
            return True, "Usuario creado con éxito."
        except Exception as exc:
            db.rollback()
            return False, str(exc)
        finally:
            remove_db()

    def actualizar_usuario(self, id_usuario: int, nombre_usuario: str,
                           nombre_completo: str, rol: str, activo: bool):
        db = SessionLocal()
        try:
            if db.query(Usuario).filter(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.id_usuario != id_usuario,
            ).first():
                return False, "El nombre de usuario ya está en uso."
            user = db.query(Usuario).get(id_usuario)
            if user:
                user.nombre_usuario = nombre_usuario
                user.nombre_completo = nombre_completo
                user.rol = rol
                user.activo = activo
                db.commit()
                return True, "Usuario actualizado con éxito."
            return False, "Usuario no encontrado."
        except Exception as exc:
            db.rollback()
            return False, str(exc)
        finally:
            remove_db()

    def admin_cambiar_contrasena(self, id_usuario: int, nueva_contrasena: str):
        db = SessionLocal()
        try:
            user = db.query(Usuario).get(id_usuario)
            if user:
                hashed = bcrypt.hashpw(
                    nueva_contrasena.encode('utf-8'), bcrypt.gensalt()
                ).decode('utf-8')
                user.contrasena_hash = hashed
                user.cambio_password_obligatorio = True
                db.commit()
                return True, "Contraseña restablecida con éxito."
            return False, "Usuario no encontrado."
        except Exception as exc:
            db.rollback()
            return False, str(exc)
        finally:
            remove_db()
