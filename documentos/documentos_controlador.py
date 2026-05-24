from documentos.documentos_modelo import DocumentosModelo

class DocumentosControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = DocumentosModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_documento, numero_control, tipo_documento, id_solicitante, fecha_emision, contenido):
        if not numero_control:
            self.vista.mostrar_mensaje("Error", "El número de control es obligatorio.")
            return

        if id_documento:
            exito, msj = self.modelo.actualizar(id_documento, numero_control, tipo_documento, id_solicitante, fecha_emision, contenido)
        else:
            exito, msj = self.modelo.insertar(numero_control, tipo_documento, id_solicitante, fecha_emision, contenido)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_documento):
        exito, msj = self.modelo.eliminar(id_documento)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
