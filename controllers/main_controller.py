from models.user import UserModel
from models.family import FamilyModel
from models.spokesperson import SpokespersonModel
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.family_view import FamilyView
from views.spokesperson_view import SpokespersonView

class MainController:
    def __init__(self, root):
        self.root = root
        self.user_model = UserModel()
        self.family_model = FamilyModel()
        self.spokesperson_model = SpokespersonModel()
        
        self.current_view = None
        self.show_login()

    def set_main_view(self, view_class, **kwargs):
        if self.current_view is not None:
            self.current_view.destroy()
        
        self.current_view = view_class(self.root, self, **kwargs)
        self.current_view.pack(fill="both", expand=True)

    def show_login(self):
        self.set_main_view(LoginView)

    def handle_login(self, username, password):
        if self.user_model.authenticate(username, password):
            self.set_main_view(DashboardView)
        else:
            self.current_view.show_error("Usuario o contraseña incorrectos")

    def handle_logout(self):
        self.show_login()

    # Métodos para el Dashboard
    def show_families(self):
        # Actualiza el panel central del dashboard
        if isinstance(self.current_view, DashboardView):
            family_view = FamilyView(self.current_view.main_content, self)
            self.current_view.set_content(family_view)

    def show_spokespersons(self):
        if isinstance(self.current_view, DashboardView):
            sp_view = SpokespersonView(self.current_view.main_content, self)
            self.current_view.set_content(sp_view)

    # Interfaz con Modelos
    def get_total_families(self):
        return self.family_model.get_total_families()

    def get_total_spokespersons(self):
        return self.spokesperson_model.get_total_spokespersons()

    def get_all_families(self):
        return self.family_model.get_all_families()

    def add_family(self, rep, cant, dir, tel):
        return self.family_model.add_family(rep, cant, dir, tel)

    def get_all_spokespersons(self):
        return self.spokesperson_model.get_all_spokespersons()

    def add_spokesperson(self, nombre, cargo, tel, correo):
        return self.spokesperson_model.add_spokesperson(nombre, cargo, tel, correo)
