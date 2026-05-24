from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# ── Engine ────────────────────────────────────────────────────────────────────
# timeout=15  → espera hasta 15 s antes de lanzar OperationalError por bloqueo
# check_same_thread=False → obligatorio para multi-hilo (Tkinter + SQLAlchemy)
engine = create_engine(
    'sqlite:///comunidad.db',
    echo=False,
    connect_args={
        "check_same_thread": False,
        "timeout": 15,
    },
    pool_pre_ping=True,
)

# ── WAL mode ─────────────────────────────────────────────────────────────────
# Write-Ahead Logging permite lecturas concurrentes durante escrituras.
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

# ── Session ───────────────────────────────────────────────────────────────────
# scoped_session garantiza UNA sesión por hilo; remove_db() la libera.
_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(_session_factory)

Base = declarative_base()


def remove_db():
    """Cierra y libera la sesión del hilo actual. Llamar siempre en el bloque finally."""
    SessionLocal.remove()


# ── Utilidad privada de bcrypt ────────────────────────────────────────────────
def _hash_valido(hash_str: str) -> bool:
    """Devuelve True si hash_str es un hash bcrypt bien formado."""
    try:
        import bcrypt
        bcrypt.checkpw(b"_test_", hash_str.encode("utf-8"))
        return True
    except ValueError:
        return False
    except Exception:
        # p.e. mismatch (wrong password), pero el salt sí era válido
        return True


def _generar_hash(password: str) -> str:
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── init_db ───────────────────────────────────────────────────────────────────
def init_db():
    """
    Crea las tablas si no existen, inserta el usuario admin por defecto
    y repara automáticamente su hash si está corrupto.
    """
    # Registrar todos los modelos antes de create_all
    import autenticacion.usuario_modelo      # noqa: F401
    import bitacora.bitacora_modelo          # noqa: F401
    import habitantes.habitantes_modelo      # noqa: F401
    import familias.familias_modelo          # noqa: F401
    import voceros.voceros_modelo            # noqa: F401
    import proyectos.proyectos_modelo        # noqa: F401
    import documentos.documentos_modelo      # noqa: F401
    import finanzas.finanzas_modelo          # noqa: F401

    Base.metadata.create_all(bind=engine)

    from autenticacion.usuario_modelo import Usuario
    from voceros.voceros_modelo import Cargo

    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter_by(nombre_usuario="admin").first()

        if admin is None:
            # ── Primera ejecución: crear admin ────────────────────────────
            print("[init_db] Creando usuario admin por defecto...")
            hash_pw = _generar_hash("123")
            db.add(Usuario(
                nombre_usuario="admin",
                contrasena_hash=hash_pw,
                nombre_completo="Administrador del Sistema",
                cambio_password_obligatorio=True,
                activo=True,
                rol="Admin",
            ))

            # Cargos por defecto
            cargos_defecto = [
                "Vocero Principal", "Vocero Suplente", "Presidente",
                "Tesorero", "Secretario", "Contralor",
            ]
            for nombre_cargo in cargos_defecto:
                if not db.query(Cargo).filter_by(nombre=nombre_cargo).first():
                    db.add(Cargo(nombre=nombre_cargo))

            db.commit()
            print("[init_db] Usuario admin creado correctamente.")

        else:
            # ── Ejecuciones posteriores: reparar hash si está corrupto ────
            if not _hash_valido(admin.contrasena_hash):
                print("[init_db][WARN] Hash invalido detectado para 'admin'. Regenerando...")
                admin.contrasena_hash = _generar_hash("123")
                admin.cambio_password_obligatorio = True
                db.commit()
                print("[init_db][OK] Hash reparado. Contrasena restablecida a '123'.")

    except Exception as exc:
        db.rollback()
        print(f"[init_db] ERROR: {exc}")
    finally:
        remove_db()
