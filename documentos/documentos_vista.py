import customtkinter as ctk
from config.style import *
from componentes.barra_busqueda import BarraBusquedaFiltros
from documentos.documentos_modelo import DocumentosModelo

class DocumentosVista(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLOR_CONTENIDO, **kwargs)
        self.pack(fill="both", expand=True)
        self.modelo = DocumentosModelo()
        self.setup_ui()

    def setup_ui(self):
        lbl_titulo = ctk.CTkLabel(self, text="Constancias y Documentos", font=("Inter", 24, "bold"), text_color=COLOR_TEXTO)
        lbl_titulo.pack(anchor="w", pady=(0, 20))

        frame_controles = ctk.CTkFrame(self, fg_color="transparent")
        frame_controles.pack(fill="x", pady=10)

        lbl_tipo = ctk.CTkLabel(frame_controles, text="Tipo de Constancia:", font=FUENTE_SUBTITULO)
        lbl_tipo.pack(side="left", padx=(0, 10))

        self.combo_tipo = ctk.CTkComboBox(frame_controles, values=["Residencia", "Buena Conducta", "Bajos Recursos"], width=200, font=FUENTE_CUERPO)
        self.combo_tipo.pack(side="left")

        self.btn_generar = ctk.CTkButton(frame_controles, text="Previsualizar", fg_color=COLOR_ACENTO, hover_color=COLOR_HOVER, command=self.previsualizar)
        self.btn_generar.pack(side="left", padx=20)

        self.textbox_vista_previa = ctk.CTkTextbox(self, font=FUENTE_CUERPO, wrap="word")
        self.textbox_vista_previa.pack(fill="both", expand=True, pady=20)

        self.btn_imprimir = ctk.CTkButton(self, text="Imprimir", fg_color=COLOR_EXITO, hover_color="#2E7D32", command=self.imprimir)
        self.btn_imprimir.pack(anchor="e")

    def previsualizar(self):
        tipo = self.combo_tipo.get()
        texto = f"CONSTANCIA DE {tipo.upper()}\n\nEl Consejo Comunal La Pedregosa hace constar que..."
        self.textbox_vista_previa.delete("0.0", "end")
        self.textbox_vista_previa.insert("0.0", texto)

    def imprimir(self):
        # Lógica de impresión OS (placeholder)
        pass
