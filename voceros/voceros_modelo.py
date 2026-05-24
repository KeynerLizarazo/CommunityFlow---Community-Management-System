from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, SessionLocal

class Cargo(Base):
    __tablename__ = 'cargos'
    id_cargo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)

class Representante(Base):
    __tablename__ = 'representantes' # Antes voceros
    
    id_representante = Column(Integer, primary_key=True, autoincrement=True)
    habitante_id = Column(Integer, ForeignKey('habitantes.id_habitante'), nullable=False)
    cargo_id = Column(Integer, ForeignKey('cargos.id_cargo'), nullable=False)
    tipo = Column(String(20)) # 'Vocero', 'Miembro'
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    estado = Column(String(20), default='activo') # 'activo', 'inactivo'
    
    habitante = relationship("Habitante")
    cargo = relationship("Cargo")

class VocerosModelo:
    def obtener_activos(self, limite=1000):
        db = SessionLocal()
        try:
            return db.query(Representante).filter(Representante.estado == 'activo').limit(limite).all()
        finally:
            db.close()
    
    def crear_representante(self, datos):
        db = SessionLocal()
        try:
            # Validar unicidad activa
            existe = db.query(Representante).filter(
                Representante.habitante_id == datos['habitante_id'],
                Representante.cargo_id == datos['cargo_id'],
                Representante.tipo == datos['tipo'],
                Representante.estado == 'activo'
            ).first()
            if existe:
                return False, "El habitante ya tiene este cargo activo."
            
            nuevo = Representante(**datos)
            db.add(nuevo)
            db.commit()
            return True, "Guardado exitosamente."
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()
