from sqlalchemy import Column, Integer, String, Date, Boolean
from config.database import Base, SessionLocal

class Proyecto(Base):
    __tablename__ = 'proyectos'
    
    id_proyecto = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500))
    estado = Column(String(20), default='Pendiente') # 'Activo', 'Finalizado', 'Pendiente'
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    activo = Column(Boolean, default=True)

class ProyectosModelo:
    def obtener_por_estado(self, estado):
        db = SessionLocal()
        try:
            return db.query(Proyecto).filter(Proyecto.estado == estado, Proyecto.activo == True).all()
        finally:
            db.close()
    
    def cambiar_estado(self, id_proyecto, nuevo_estado):
        db = SessionLocal()
        try:
            proy = db.query(Proyecto).get(id_proyecto)
            if proy:
                proy.estado = nuevo_estado
                db.commit()
                return True
            return False
        finally:
            db.close()
