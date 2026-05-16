from database.db_manager import DBManager

class SpokespersonModel:
    def __init__(self):
        self.db = DBManager()

    def add_spokesperson(self, nombre, cargo, telefono, correo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voceros (nombre, cargo, telefono, correo)
            VALUES (?, ?, ?, ?)
        ''', (nombre, cargo, telefono, correo))
        
        conn.commit()
        conn.close()
        return True

    def get_all_spokespersons(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nombre, cargo, telefono, correo FROM voceros")
        spokespersons = cursor.fetchall()
        
        conn.close()
        return spokespersons

    def get_total_spokespersons(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM voceros")
        total = cursor.fetchone()[0]
        
        conn.close()
        return total
