from actas.actas_modelo import ActasModelo

class ActasControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ActasModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_acta, numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones):
        if not numero_acta or not fecha_reunion:
            self.vista.mostrar_mensaje("Error", "El número de acta y la fecha son obligatorios.")
            return

        if id_acta:
            exito, msj = self.modelo.actualizar(id_acta, numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones)
        else:
            exito, msj = self.modelo.insertar(numero_acta, fecha_reunion, lugar, tipo_reunion, asunto, conclusiones)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_acta):
        exito, msj = self.modelo.eliminar(id_acta)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
