from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# Configuracion de SQLite con SQLAlchemy
# timeout=15 evita "database is locked" al esperar hasta 15s por el desbloqueo
engine = create_engine(
    'sqlite:///comunidad.db',
    echo=False,
    connect_args={
        "check_same_thread": False,
        "timeout": 15
    },
    pool_pre_ping=True
)

# Activar WAL (Write-Ahead Logging) para permitir lecturas concurrentes con escrituras
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

# scoped_session garantiza una sesión por hilo y evita conflictos de bloqueo
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

Base = declarative_base()

def remove_db():
    """Cierra y libera la sesión del hilo actual. Llamar siempre al terminar una operación."""
    SessionLocal.remove()

def init_db():
    # Importar todos los modelos para que metadata los reconozca
    import autenticacion.usuario_modelo
    import bitacora.bitacora_modelo
    import habitantes.habitantes_modelo
    import familias.familias_modelo
    import voceros.voceros_modelo
    import proyectos.proyectos_modelo
    import documentos.documentos_modelo
    import finanzas.finanzas_modelo
    
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario admin inicial si no existe
    db = SessionLocal()
    try:
        from autenticacion.usuario_modelo import Usuario
        import bcrypt
        if not db.query(Usuario).first():
            hashed_pw = bcrypt.hashpw('123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = Usuario(
                nombre_usuario='admin',
                contrasena_hash=hashed_pw,
                nombre_completo='Administrador del Sistema',
                cambio_password_obligatorio=True,
                activo=True,
                rol='Admin'
            )
            db.add(admin)
            
            # Seed default cargos
            from voceros.voceros_modelo import Cargo
            cargos_defecto = ["Vocero Principal", "Vocero Suplente", "Presidente", "Tesorero", "Secretario", "Contralor"]
            for nombre_cargo in cargos_defecto:
                if not db.query(Cargo).filter(Cargo.nombre == nombre_cargo).first():
                    db.add(Cargo(nombre=nombre_cargo))
                    
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error en init_db: {e}")
    finally:
        remove_db()
