from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from config.database import Base, SessionLocal, remove_db
from datetime import date


class Constancia(Base):
    __tablename__ = 'constancias'

    id_constancia = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), nullable=False)  # enum
    habitante_id = Column(Integer, ForeignKey('habitantes.id_habitante'), nullable=True)
    texto = Column(Text, nullable=False)
    fecha_emision = Column(Date, default=date.today)


class DocumentosModelo:
    def registrar_emision(self, datos: dict) -> bool:
        db = SessionLocal()
        try:
            nueva = Constancia(**datos)
            db.add(nueva)
            db.commit()
            return True
        except Exception as exc:
            db.rollback()
            print(f"[DocumentosModelo] Error al registrar emision: {exc}")
            return False
        finally:
            remove_db()
