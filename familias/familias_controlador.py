from familias.familias_modelo import FamiliasModelo

class FamiliasControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = FamiliasModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_familia, codigo_familia, direccion, id_jefe, fecha_registro):
        if not codigo_familia:
            self.vista.mostrar_mensaje("Error", "El código de familia es obligatorio.")
            return

        if id_familia:
            exito, msj = self.modelo.actualizar(id_familia, codigo_familia, direccion, id_jefe, fecha_registro)
        else:
            exito, msj = self.modelo.insertar(codigo_familia, direccion, id_jefe, fecha_registro)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_familia):
        exito, msj = self.modelo.eliminar(id_familia)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
