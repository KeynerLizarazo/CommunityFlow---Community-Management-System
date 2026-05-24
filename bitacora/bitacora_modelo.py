from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from config.database import Base, SessionLocal, remove_db
from datetime import datetime

class Bitacora(Base):
    __tablename__ = 'bitacora'
    
    id_bitacora = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    modulo = Column(String(50), nullable=False)
    accion = Column(String(50), nullable=False) # crear, editar, eliminar, imprimir
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    registro_id = Column(String(50))
    datos_previos = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)

    usuario = relationship("Usuario")

class BitacoraModelo:
    @staticmethod
    def registrar_accion(usuario_id, modulo, accion, registro_id=None, datos_previos=None, datos_nuevos=None):
        # Utilizar transacción independiente
        db = SessionLocal()
        try:
            registro = Bitacora(
                usuario_id=usuario_id,
                modulo=modulo,
                accion=accion,
                registro_id=registro_id,
                datos_previos=datos_previos,
                datos_nuevos=datos_nuevos
            )
            db.add(registro)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error registrando bitácora: {e}")
        finally:
            remove_db()

    def obtener_registros(self, modulo=None, accion=None, limite=1000):
        db = SessionLocal()
        try:
            query = db.query(Bitacora).order_by(Bitacora.fecha_hora.desc())
            if modulo:
                query = query.filter(Bitacora.modulo == modulo)
            if accion:
                query = query.filter(Bitacora.accion == accion)
            registros = query.limit(limite).all()
            # Convertir a lista de dicts para desacoplar de la sesión
            resultado = []
            for r in registros:
                usuario_nombre = r.usuario.nombre_usuario if r.usuario else "Desconocido"
                resultado.append({
                    "id_bitacora": r.id_bitacora,
                    "usuario_nombre": usuario_nombre,
                    "modulo": r.modulo,
                    "accion": r.accion,
                    "fecha_hora": r.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_hora else "",
                    "registro_id": r.registro_id or "-"
                })
            return resultado
        finally:
            remove_db()

