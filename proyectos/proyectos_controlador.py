from proyectos.proyectos_modelo import ProyectosModelo

class ProyectosControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = ProyectosModelo()

    def cargar_datos(self, busqueda=""):
        datos = self.modelo.obtener_todos(busqueda)
        self.vista.mostrar_datos(datos)

    def guardar(self, id_proyecto, codigo, nombre, descripcion, estado, fecha_inicio, fecha_fin):
        if not codigo or not nombre:
            self.vista.mostrar_mensaje("Error", "Código y Nombre son obligatorios.")
            return

        if id_proyecto:
            exito, msj = self.modelo.actualizar(id_proyecto, codigo, nombre, descripcion, estado, fecha_inicio, fecha_fin)
        else:
            exito, msj = self.modelo.insertar(codigo, nombre, descripcion, estado, fecha_inicio, fecha_fin)

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al guardar: {msj}")

    def eliminar(self, id_proyecto):
        exito, msj = self.modelo.eliminar(id_proyecto)
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos()
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", f"Error al eliminar: {msj}")
