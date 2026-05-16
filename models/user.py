from database.db_manager import DBManager

class UserModel:
    def __init__(self):
        self.db = DBManager()

    def authenticate(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        
        conn.close()
        return user is not None
