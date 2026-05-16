import customtkinter as ctk
from views.style import *

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=BG_DARK)
        self.controller = controller

        # Layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_header()
        self.create_sidebar()
        self.create_main_area()
        self.show_home()

    def create_header(self):
        self.header = ctk.CTkFrame(self, fg_color=BG_PANEL, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.logo_label = ctk.CTkLabel(self.header, text="Gestión Comunitaria", font=FONT_TITLE, text_color=PRIMARY_COLOR)
        self.logo_label.pack(side="left", padx=20, pady=15)
        
        self.logout_btn = ctk.CTkButton(self.header, text="Cerrar Sesión", font=FONT_NORMAL_BOLD, fg_color="transparent", border_width=1, border_color=PRIMARY_COLOR, text_color=PRIMARY_COLOR, hover_color=BG_DARK, width=120, command=self.controller.handle_logout)
        self.logout_btn.pack(side="right", padx=20, pady=15)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, width=200)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        
        # Botones del menú
        self.btn_home = ctk.CTkButton(self.sidebar, text="Dashboard", font=FONT_NORMAL_BOLD, fg_color="transparent", text_color=TEXT_MAIN, hover_color=PRIMARY_COLOR, anchor="w", height=40, command=self.show_home)
        self.btn_home.pack(fill="x", pady=(20, 5), padx=10)

        self.btn_familias = ctk.CTkButton(self.sidebar, text="Familias", font=FONT_NORMAL_BOLD, fg_color="transparent", text_color=TEXT_MAIN, hover_color=PRIMARY_COLOR, anchor="w", height=40, command=self.controller.show_families)
        self.btn_familias.pack(fill="x", pady=5, padx=10)

        self.btn_voceros = ctk.CTkButton(self.sidebar, text="Gestión de Voceros", font=FONT_NORMAL_BOLD, fg_color="transparent", text_color=TEXT_MAIN, hover_color=PRIMARY_COLOR, anchor="w", height=40, command=self.controller.show_spokespersons)
        self.btn_voceros.pack(fill="x", pady=5, padx=10)

    def create_main_area(self):
        # Contenedor central donde se cambiarán las vistas
        self.main_content = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        
        # Para mantener una referencia a la vista actual
        self.current_view = None

    def set_content(self, view_widget):
        if self.current_view is not None:
            self.current_view.destroy()
        self.current_view = view_widget
        self.current_view.pack(fill="both", expand=True)

    def show_home(self):
        # Crear vista de inicio (cards de resumen)
        home_view = ctk.CTkFrame(self.main_content, fg_color=BG_DARK)
        
        title = ctk.CTkLabel(home_view, text="Resumen General", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 20))

        # Contenedor de cards
        cards_frame = ctk.CTkFrame(home_view, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        # Obtener datos de resumen
        total_familias = self.controller.get_total_families()
        total_voceros = self.controller.get_total_spokespersons()

        # Card Familias
        card1 = ctk.CTkFrame(cards_frame, fg_color=BG_PANEL, corner_radius=10, height=120)
        card1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        card1.pack_propagate(False)
        ctk.CTkLabel(card1, text="Total Familias", font=FONT_NORMAL, text_color=TEXT_MUTED).pack(pady=(20, 5))
        ctk.CTkLabel(card1, text=str(total_familias), font=(FONT_FAMILY, 36, "bold"), text_color=PRIMARY_COLOR).pack()

        # Card Voceros
        card2 = ctk.CTkFrame(cards_frame, fg_color=BG_PANEL, corner_radius=10, height=120)
        card2.pack(side="left", fill="x", expand=True, padx=(10, 0))
        card2.pack_propagate(False)
        ctk.CTkLabel(card2, text="Total Voceros", font=FONT_NORMAL, text_color=TEXT_MUTED).pack(pady=(20, 5))
        ctk.CTkLabel(card2, text=str(total_voceros), font=(FONT_FAMILY, 36, "bold"), text_color=PRIMARY_COLOR).pack()

        self.set_content(home_view)
