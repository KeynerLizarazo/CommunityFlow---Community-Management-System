from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, SessionLocal
from datetime import datetime, date
from bitacora.bitacora_modelo import BitacoraModelo

class Habitante(Base):
    __tablename__ = 'habitantes'
    
    id_habitante = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(20), unique=True, nullable=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date)
    sexo = Column(String(10))
    telefono = Column(String(20))
    direccion = Column(String(200))
    activo = Column(Boolean, default=True)
    parentesco = Column(String(50))
    
    familia_id = Column(Integer, ForeignKey('familias.id_familia'))
    familia = relationship("Familia", back_populates="habitantes", foreign_keys=[familia_id])

class HabitantesModelo:
    def parse_fecha(self, f_str):
        if not f_str:
            return None
        if isinstance(f_str, (date, datetime)):
            return f_str
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(f_str, fmt).date()
            except ValueError:
                continue
        raise ValueError("Fecha inválida. Use DD/MM/AAAA")

    def validar_edad(self, f_date):
        if not f_date:
            return True
        today = date.today()
        edad = today.year - f_date.year - ((today.month, today.day) < (f_date.month, f_date.day))
        return 0 <= edad <= 120

    def obtener_todos(self, busqueda=None, familia_id=None):
        db = SessionLocal()
        try:
            query = db.query(Habitante).filter(Habitante.activo == True)
            if familia_id:
                query = query.filter(Habitante.familia_id == familia_id)
            if busqueda:
                busqueda = f"%{busqueda}%"
                query = query.filter(
                    (Habitante.cedula.like(busqueda)) |
                    (Habitante.nombres.like(busqueda)) |
                    (Habitante.apellidos.like(busqueda))
                )
            
            res = query.all()
            # Devolver formato tabular (lista de diccionarios)
            return [
                {
                    "id_habitante": h.id_habitante,
                    "cedula": h.cedula or "",
                    "nombres": h.nombres,
                    "apellidos": h.apellidos,
                    "fecha_nacimiento": h.fecha_nacimiento.strftime("%d/%m/%Y") if h.fecha_nacimiento else "",
                    "sexo": h.sexo or "",
                    "telefono": h.telefono or "",
                    "direccion": h.direccion or "",
                    "parentesco": h.parentesco or "",
                    "familia_id": h.familia_id
                }
                for h in res
            ]
        finally:
            db.close()

    def insertar(self, cedula, nombres, apellidos, fecha_nacimiento, sexo, telefono, direccion, parentesco, familia_id, usuario_id):
        db = SessionLocal()
        try:
            # Validar cédula única si se ingresa
            if cedula:
                ex = db.query(Habitante).filter(Habitante.cedula == cedula, Habitante.activo == True).first()
                if ex:
                    return False, "La cédula ingresada ya está registrada y activa."
            
            try:
                f_date = self.parse_fecha(fecha_nacimiento)
            except ValueError as e:
                return False, str(e)

            if not self.validar_edad(f_date):
                return False, "La edad del habitante debe estar entre 0 y 120 años."

            # Heredar dirección y teléfono de la familia si no se especifican
            if familia_id:
                from familias.familias_modelo import Familia
                fam = db.query(Familia).filter(Familia.id_familia == familia_id).first()
                if fam:
                    if not direccion:
                        direccion = fam.direccion
                    if not telefono:
                        telefono = fam.telefono

            nuevo = Habitante(
                cedula=cedula or None,
                nombres=nombres,
                apellidos=apellidos,
                fecha_nacimiento=f_date,
                sexo=sexo,
                telefono=telefono,
                direccion=direccion,
                parentesco=parentesco,
                familia_id=familia_id,
                activo=True
            )
            db.add(nuevo)
            db.commit()
            
            # Registrar auditoría
            BitacoraModelo.registrar_accion(
                usuario_id=usuario_id,
                modulo="Habitantes",
                accion="crear",
                registro_id=str(nuevo.id_habitante),
                datos_nuevos={"cedula": cedula, "nombre_completo": f"{nombres} {apellidos}"}
            )
            return True, "Habitante registrado con éxito."
        except Exception as e:
            db.rollback()
            return False, f"Error: {e}"
        finally:
            db.close()

    def actualizar(self, id_habitante, cedula, nombres, apellidos, fecha_nacimiento, sexo, telefono, direccion, parentesco, familia_id, usuario_id):
        db = SessionLocal()
        try:
            h = db.query(Habitante).filter(Habitante.id_habitante == id_habitante).first()
            if not h:
                return False, "Habitante no encontrado."

            if cedula and cedula != h.cedula:
                ex = db.query(Habitante).filter(Habitante.cedula == cedula, Habitante.activo == True).first()
                if ex:
                    return False, "La cédula ingresada ya está registrada y activa."

            try:
                f_date = self.parse_fecha(fecha_nacimiento)
            except ValueError as e:
                return False, str(e)

            if not self.validar_edad(f_date):
                return False, "La edad del habitante debe estar entre 0 y 120 años."

            datos_previos = {"cedula": h.cedula, "nombre_completo": f"{h.nombres} {h.apellidos}"}

            h.cedula = cedula or None
            h.nombres = nombres
            h.apellidos = apellidos
            h.fecha_nacimiento = f_date
            h.sexo = sexo
            h.telefono = telefono
            h.direccion = direccion
            h.parentesco = parentesco
            h.familia_id = familia_id
            db.commit()

            BitacoraModelo.registrar_accion(
                usuario_id=usuario_id,
                modulo="Habitantes",
                accion="editar",
                registro_id=str(id_habitante),
                datos_previos=datos_previos,
                datos_nuevos={"cedula": cedula, "nombre_completo": f"{nombres} {apellidos}"}
            )
            return True, "Habitante actualizado con éxito."
        except Exception as e:
            db.rollback()
            return False, f"Error: {e}"
        finally:
            db.close()

    def eliminar(self, id_habitante, usuario_id):
        db = SessionLocal()
        try:
            h = db.query(Habitante).filter(Habitante.id_habitante == id_habitante).first()
            if not h:
                return False, "Habitante no encontrado."
            
            datos_previos = {"cedula": h.cedula, "nombre_completo": f"{h.nombres} {h.apellidos}"}
            h.activo = False
            db.commit()

            BitacoraModelo.registrar_accion(
                usuario_id=usuario_id,
                modulo="Habitantes",
                accion="eliminar",
                registro_id=str(id_habitante),
                datos_previos=datos_previos
            )
            return True, "Habitante eliminado con éxito (borrado lógico)."
        except Exception as e:
            db.rollback()
            return False, f"Error: {e}"
        finally:
            db.close()
