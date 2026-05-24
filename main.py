import customtkinter as ctk
from config.database import init_db
from config.style import configurar_tema
from autenticacion.login_vista import LoginVista

def main():
    configurar_tema()
    
    # Inicializar Base de Datos SQLAlchemy
    init_db()
    
    app = LoginVista()
    app.mainloop()

if __name__ == "__main__":
    main()