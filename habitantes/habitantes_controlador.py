from habitantes.habitantes_modelo import HabitantesModelo
from config.auth_session import AuthSession

class HabitantesControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = HabitantesModelo()

    def obtener_rol_usuario(self):
        usuario = AuthSession.get_usuario()
        return usuario.rol if usuario else "Consulta"

    def obtener_id_usuario(self):
        usuario = AuthSession.get_usuario()
        return usuario.id_usuario if usuario else 1

    def cargar_datos(self, busqueda="", familia_id=None):
        # El modelo devuelve una lista de diccionarios
        lista_dicts = self.modelo.obtener_todos(busqueda=busqueda, familia_id=familia_id)
        
        # Mapeamos a lista de tuplas para la visualización del Treeview
        datos_tabla = []
        for h in lista_dicts:
            datos_tabla.append((
                h["id_habitante"],
                h["cedula"],
                h["nombres"],
                h["apellidos"],
                h["fecha_nacimiento"],
                h["sexo"],
                h["telefono"],
                h["direccion"],
                h["parentesco"],
                h["familia_id"]
            ))
        
        self.vista.mostrar_datos(datos_tabla)

    def guardar(self, id_habitante, cedula, nombres, apellidos, fecha_nacimiento, sexo, telefono, direccion, parentesco, familia_id):
        # Verificar permisos (NF18)
        if self.obtener_rol_usuario() == "Consulta":
            self.vista.mostrar_mensaje("Error", "Permisos insuficientes. El rol de Consulta no permite modificaciones.")
            return

        usuario_id = self.obtener_id_usuario()

        if id_habitante:
            exito, msj = self.modelo.actualizar(
                id_habitante, cedula, nombres, apellidos, fecha_nacimiento, 
                sexo, telefono, direccion, parentesco, familia_id, usuario_id
            )
        else:
            exito, msj = self.modelo.insertar(
                cedula, nombres, apellidos, fecha_nacimiento, 
                sexo, telefono, direccion, parentesco, familia_id, usuario_id
            )

        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos(familia_id=familia_id)
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", msj)

    def eliminar(self, id_habitante, familia_id=None):
        # Verificar permisos (NF18)
        if self.obtener_rol_usuario() == "Consulta":
            self.vista.mostrar_mensaje("Error", "Permisos insuficientes. El rol de Consulta no permite realizar eliminaciones.")
            return

        usuario_id = self.obtener_id_usuario()
        exito, msj = self.modelo.eliminar(id_habitante, usuario_id)
        
        if exito:
            self.vista.mostrar_mensaje("Éxito", msj)
            self.cargar_datos(familia_id=familia_id)
            self.vista.limpiar_formulario()
        else:
            self.vista.mostrar_mensaje("Error", msj)
