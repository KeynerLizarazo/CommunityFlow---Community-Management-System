from voceros.voceros_modelo import VocerosModelo

class VocerosControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = VocerosModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_vocero, id_habitante, id_cargo, tipo, fecha_inicio, fecha_fin):
        if not id_habitante or not id_cargo or not fecha_inicio:
            self.vista.mostrar_mensaje("Error", "ID Habitante, ID Cargo y Fecha Inicio son obligatorios.")
            return

        if id_vocero:
            exito, msj = self.modelo.actualizar(id_vocero, id_habitante, id_cargo, tipo, fecha_inicio, fecha_fin)
        else:
            exito, msj = self.modelo.insertar(id_habitante, id_cargo, tipo, fecha_inicio, fecha_fin)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_vocero):
        exito, msj = self.modelo.eliminar(id_vocero)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
