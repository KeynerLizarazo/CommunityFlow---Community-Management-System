from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base, SessionLocal
from datetime import date
from habitantes.habitantes_modelo import Habitante

class Familia(Base):
    __tablename__ = 'familias'
    
    id_familia = Column(Integer, primary_key=True, autoincrement=True)
    codigo_familia = Column(String(50), unique=True, nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20))
    id_jefe = Column(Integer, ForeignKey('habitantes.id_habitante'), nullable=True)
    fecha_registro = Column(Date, default=date.today)
    activo = Column(Boolean, default=True)
    
    jefe = relationship("Habitante", foreign_keys=[id_jefe])
    habitantes = relationship("Habitante", back_populates="familia", foreign_keys="[Habitante.familia_id]", cascade="all, delete-orphan")

class FamiliaModelo:
    def obtener_todas(self, limite=1000, offset=0):
        db = SessionLocal()
        try:
            query = db.query(Familia).filter(Familia.activo == True)
            return query.limit(limite).offset(offset).all()
        finally:
            db.close()
    
    def crear_familia(self, datos):
        db = SessionLocal()
        try:
            nueva = Familia(**datos)
            db.add(nueva)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    
    def desactivar_familia(self, id_familia):
        db = SessionLocal()
        try:
            fam = db.query(Familia).get(id_familia)
            if fam:
                fam.activo = False
                for hab in fam.habitantes:
                    hab.activo = False
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
