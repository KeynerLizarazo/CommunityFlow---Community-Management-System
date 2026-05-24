from config.database import Database

class RecursosModelo:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self, busqueda=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = "SELECT id_recurso, codigo, descripcion, tipo, cantidad FROM recursos"
        params = ()
        if busqueda:
            query += " WHERE codigo LIKE ? OR descripcion LIKE ?"
            params = (f"%{busqueda}%", f"%{busqueda}%")
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    def insertar(self, codigo, descripcion, tipo, cantidad):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO recursos (codigo, descripcion, tipo, cantidad)
                VALUES (?, ?, ?, ?)
            ''', (codigo, descripcion, tipo, cantidad))
            conn.commit()
            return True, "Insertado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def actualizar(self, id_recurso, codigo, descripcion, tipo, cantidad):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE recursos 
                SET codigo=?, descripcion=?, tipo=?, cantidad=?
                WHERE id_recurso=?
            ''', (codigo, descripcion, tipo, cantidad, id_recurso))
            conn.commit()
            return True, "Actualizado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def eliminar(self, id_recurso):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM recursos WHERE id_recurso=?", (id_recurso,))
            conn.commit()
            return True, "Eliminado correctamente."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
