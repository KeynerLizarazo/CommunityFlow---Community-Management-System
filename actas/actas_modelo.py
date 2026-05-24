from config.database import Database

class ActasModelo:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self, busqueda=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT id_acta, numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones FROM actas"
        params = ()
        if busqueda:
            query += " WHERE numero_acta LIKE ? OR asunto LIKE ?"
            params = (f"%{busqueda}%", f"%{busqueda}%")
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    def insertar(self, numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO actas (numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones))
            conn.commit()
            return True, "Insertado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def actualizar(self, id_acta, numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE actas 
                SET numero_acta=?, fecha_reunion=?, lugar=?, tipo_reunion=?, asunto=?, conclusiones=?
                WHERE id_acta=?
            ''', (numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones, id_acta))
            conn.commit()
            return True, "Actualizado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def eliminar(self, id_acta):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM actas WHERE id_acta=?", (id_acta,))
            conn.commit()
            return True, "Eliminado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
