import sqlite3
import os

class DBManager:
    def __init__(self, db_name="database/comunidad.db"):
        # Asegurarse de que el directorio database exista
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla Usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin'
            )
        ''')

        # Tabla Familias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS familias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                representante TEXT NOT NULL,
                cantidad_integrantes INTEGER NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL
            )
        ''')

        # Tabla Voceros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voceros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cargo TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo TEXT NOT NULL
            )
        ''')

        # Crear usuario admin por defecto si no existe ninguno
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES ('admin', 'admin')")

        conn.commit()
        conn.close()
