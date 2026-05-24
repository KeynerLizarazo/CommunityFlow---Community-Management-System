from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from config.database import Base, SessionLocal
from datetime import date
from sqlalchemy import func

class MovimientoFinanciero(Base):
    __tablename__ = 'movimientos_financieros'
    
    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(10), nullable=False) # 'Ingreso' o 'Egreso'
    monto = Column(Numeric(10, 2), nullable=False)
    concepto = Column(String(200), nullable=False)
    observaciones = Column(String(500))
    fecha = Column(Date, default=date.today)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id_proyecto'), nullable=True)

class FinanzasModelo:
    def obtener_balance(self):
        db = SessionLocal()
        try:
            balance = db.query(
                func.sum(
                    func.case(
                        (MovimientoFinanciero.tipo == 'Ingreso', MovimientoFinanciero.monto),
                        else_=-MovimientoFinanciero.monto
                    )
                )
            ).scalar()
            return balance or 0.0
        finally:
            db.close()

    def obtener_movimientos(self, limite=1000):
        db = SessionLocal()
        try:
            return db.query(MovimientoFinanciero).order_by(MovimientoFinanciero.fecha.desc()).limit(limite).all()
        finally:
            db.close()
