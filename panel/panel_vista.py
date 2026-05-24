import customtkinter as ctk
from config.style import *
from config.auth_session import AuthSession
from config.database import SessionLocal
import threading

class PanelVista(ctk.CTkToplevel):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.title("Consejo Comunal La Pedregosa")
        self.geometry("1920x1080")
        self.state('zoomed')
        self.configure(fg_color=COLOR_CONTENIDO)
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar_app)
        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COLOR_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        
        lbl_titulo = ctk.CTkLabel(self.sidebar, text="La Pedregosa", font=FUENTE_TITULO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=20)

        # Todos los módulos visibles para el administrador
        modulos = ["Dashboard", "Censo", "Voceros", "Proyectos", "Documentos", "Finanzas", "Bitácora"]
        self.botones_nav = []
        
        for mod in modulos:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=mod,
                fg_color="transparent",
                text_color=COLOR_TEXTO,
                hover_color=COLOR_ACENTO,
                font=FUENTE_CUERPO,
                anchor="w",
                command=lambda m=mod: self.navegar(m)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.botones_nav.append((mod, btn))

        self.btn_salir = ctk.CTkButton(
            self.sidebar, 
            text="Cerrar sesión",
            fg_color=COLOR_ERROR,
            text_color="#FFFFFF",
            hover_color="#B71C1C",
            font=FUENTE_CUERPO,
            anchor="w",
            command=self.cerrar_sesion
        )
        self.btn_salir.pack(side="bottom", fill="x", padx=10, pady=20)

        # Área de contenido
        self.area_contenido = ctk.CTkFrame(self, fg_color=COLOR_CONTENIDO, corner_radius=0)
        self.area_contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.navegar("Dashboard")

    def navegar(self, modulo_nombre):
        for nombre, btn in self.botones_nav:
            if nombre == modulo_nombre:
                btn.configure(fg_color=COLOR_ACENTO, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXTO)
                
        for widget in self.area_contenido.winfo_children():
            widget.destroy()
            
        if modulo_nombre == "Dashboard":
            self.mostrar_dashboard()
            return
            
        mapa_modulos = {
            "Censo": ("familias.familias_vista", "FamiliasVista"), # Por defecto mostramos familias
            "Voceros": ("voceros.voceros_vista", "VocerosVista"),
            "Proyectos": ("proyectos.proyectos_vista", "ProyectosVista"),
            "Documentos": ("documentos.documentos_vista", "DocumentosVista"),
            "Finanzas": ("finanzas.finanzas_vista", "FinanzasVista"),
            "Bitácora": ("bitacora.bitacora_vista", "BitacoraVista")
        }

        try:
            mod_path, class_name = mapa_modulos[modulo_nombre]
            import importlib
            modulo = importlib.import_module(mod_path)
            clase_vista = getattr(modulo, class_name)
            clase_vista(self.area_contenido)
        except Exception as e:
            lbl = ctk.CTkLabel(self.area_contenido, text=f"Módulo en construcción o error: {e}", text_color=COLOR_ERROR)
            lbl.pack(expand=True)

    def mostrar_dashboard(self):
        lbl = ctk.CTkLabel(self.area_contenido, text="Dashboard Principal", font=("Inter", 32, "bold"), text_color=COLOR_TEXTO)
        lbl.pack(pady=20, anchor="w")

        # Tarjetas
        frame_tarjetas = ctk.CTkFrame(self.area_contenido, fg_color="transparent")
        frame_tarjetas.pack(fill="x", pady=20)
        
        self.lbl_tot_familias = self.crear_tarjeta(frame_tarjetas, "Familias", "0")
        self.lbl_tot_habitantes = self.crear_tarjeta(frame_tarjetas, "Habitantes", "0")
        self.lbl_tot_voceros = self.crear_tarjeta(frame_tarjetas, "Voceros/Miembros", "0")
        self.lbl_saldo = self.crear_tarjeta(frame_tarjetas, "Saldo Actual", "0.00")

        self.actualizar_dashboard_async()

    def crear_tarjeta(self, parent, titulo, valor_inicial):
        tarjeta = ctk.CTkFrame(parent, fg_color=COLOR_CONTENIDO, corner_radius=10, border_width=1, border_color=COLOR_HOVER)
        tarjeta.pack(side="left", fill="both", expand=True, padx=10)
        
        lbl_titulo = ctk.CTkLabel(tarjeta, text=titulo, font=FUENTE_CUERPO, text_color=COLOR_TEXTO)
        lbl_titulo.pack(pady=(10, 0))
        
        lbl_valor = ctk.CTkLabel(tarjeta, text=valor_inicial, font=("Inter", 24, "bold"), text_color=COLOR_ACENTO)
        lbl_valor.pack(pady=(0, 10))
        
        return lbl_valor

    def actualizar_dashboard_async(self):
        # Esta función calculará los totales. Por ahora es un placeholder estructurado.
        def tarea():
            try:
                db = SessionLocal()
                # En un futuro, importaremos los modelos aquí para hacer las consultas
                # fam_count = db.query(Familia).filter_by(activo=True).count()
                # etc.
                db.close()
                # self.lbl_tot_familias.configure(text=str(fam_count))
            except Exception as e:
                print(f"Error actualizando dashboard: {e}")

        t = threading.Thread(target=tarea)
        t.start()

    def cerrar_sesion(self):
        AuthSession.clear()
        self.destroy()
        self.login_window.deiconify()

    def cerrar_app(self):
        self.destroy()
        self.login_window.destroy()
