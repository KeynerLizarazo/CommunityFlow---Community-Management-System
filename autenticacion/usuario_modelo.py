from sqlalchemy import Column, Integer, String, Boolean
from config.database import Base, SessionLocal, remove_db
from sqlalchemy.orm import make_transient
import bcrypt

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    contrasena_hash = Column(String(200), nullable=False)
    nombre_completo = Column(String(100))
    activo = Column(Boolean, default=True)
    cambio_password_obligatorio = Column(Boolean, default=False)
    rol = Column(String(20), default='Admin')

class UsuarioModelo:
    def autenticar(self, usuario, contrasena):
        """
        Autentica al usuario y devuelve un objeto desacoplado de la sesión.
        Esto evita que la sesión quede abierta con un objeto atado a ella.
        """
        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(
                Usuario.nombre_usuario == usuario,
                Usuario.activo == True
            ).first()
            if user and bcrypt.checkpw(
                contrasena.encode('utf-8'),
                user.contrasena_hash.encode('utf-8')
            ):
                # Expulsar el objeto de la sesión para que sea independiente
                db.expunge(user)
                make_transient(user)
                return user
            return None
        finally:
            remove_db()

    def usuario_existe(self, nombre_usuario):
        """Verifica si el nombre de usuario existe (para mensajes de error en login)."""
        db = SessionLocal()
        try:
            return db.query(Usuario).filter(
                Usuario.nombre_usuario == nombre_usuario
            ).first() is not None
        finally:
            remove_db()
    
    def cambiar_usuario(self, id_usuario, nuevo_usuario):
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

    def cambiar_contrasena(self, id_usuario, actual, nueva):
        db = SessionLocal()
        try:
            user = db.query(Usuario).get(id_usuario)
            if user and bcrypt.checkpw(
                actual.encode('utf-8'),
                user.contrasena_hash.encode('utf-8')
            ):
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

    def forzar_cambio_contrasena(self, id_usuario, nueva):
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
        except Exception as e:
            db.rollback()
            print(f"Error en forzar_cambio_contrasena: {e}")
            return False
        finally:
            remove_db()

    def obtener_todos(self):
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
                    "rol": u.rol
                }
                for u in usuarios
            ]
        finally:
            remove_db()

    def crear_usuario(self, nombre_usuario, contrasena, nombre_completo, rol):
        db = SessionLocal()
        try:
            existe = db.query(Usuario).filter(
                Usuario.nombre_usuario == nombre_usuario
            ).first()
            if existe:
                return False, "El nombre de usuario ya existe."
            hashed = bcrypt.hashpw(
                contrasena.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            nuevo = Usuario(
                nombre_usuario=nombre_usuario,
                contrasena_hash=hashed,
                nombre_completo=nombre_completo,
                rol=rol,
                activo=True,
                cambio_password_obligatorio=True
            )
            db.add(nuevo)
            db.commit()
            return True, "Usuario creado con éxito."
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            remove_db()

    def actualizar_usuario(self, id_usuario, nombre_usuario, nombre_completo, rol, activo):
        db = SessionLocal()
        try:
            existe = db.query(Usuario).filter(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.id_usuario != id_usuario
            ).first()
            if existe:
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
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            remove_db()

    def admin_cambiar_contrasena(self, id_usuario, nueva_contrasena):
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
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            remove_db()
