from database.db_manager import DBManager

class FamilyModel:
    def __init__(self):
        self.db = DBManager()

    def add_family(self, representante, cantidad_integrantes, direccion, telefono):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO familias (representante, cantidad_integrantes, direccion, telefono)
            VALUES (?, ?, ?, ?)
        ''', (representante, cantidad_integrantes, direccion, telefono))
        
        conn.commit()
        conn.close()
        return True

    def get_all_families(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, representante, cantidad_integrantes, direccion, telefono FROM familias")
        families = cursor.fetchall()
        
        conn.close()
        return families

    def get_total_families(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM familias")
        total = cursor.fetchone()[0]
        
        conn.close()
        return total
