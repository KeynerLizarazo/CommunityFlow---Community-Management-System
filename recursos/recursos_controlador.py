from recursos.recursos_modelo import RecursosModelo

class RecursosControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = RecursosModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_recurso, codigo, descripcion, tipo, cantidad):
        if not codigo or not descripcion:
            self.vista.mostrar_mensaje("Error", "Código y Descripción son obligatorios.")
            return

        if id_recurso:
            exito, msj = self.modelo.actualizar(id_recurso, codigo, descripcion, tipo, cantidad)
        else:
            exito, msj = self.modelo.insertar(codigo, descripcion, tipo, cantidad)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_recurso):
        exito, msj = self.modelo.eliminar(id_recurso)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
