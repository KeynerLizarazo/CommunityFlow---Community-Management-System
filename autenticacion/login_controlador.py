from autenticacion.usuario_modelo import UsuarioModelo

class LoginControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = UsuarioModelo()
        self.intentos_fallidos = 0

    def intentar_login(self, usuario, contrasena):
        if not usuario:
            self.vista.mostrar_error_usuario("El campo usuario no puede estar vacío.")
            return
        if not contrasena:
            self.vista.mostrar_error_contrasena("El campo contraseña no puede estar vacío.")
            return

        usuario_data = self.modelo.autenticar(usuario, contrasena)
        
        if usuario_data:
            self.intentos_fallidos = 0
            self.vista.mostrar_carga(usuario_data)
        else:
            self.intentos_fallidos += 1
            
            # Verificar si el usuario existe (usando el modelo, no SQL directo)
            if not self.modelo.usuario_existe(usuario):
                self.vista.mostrar_error_usuario("Usuario no encontrado.")
                self.vista.limpiar_campos_fallo_usuario()
            else:
                self.vista.mostrar_error_contrasena("Contraseña incorrecta.")
                self.vista.limpiar_campos_fallo_contrasena()

            if self.intentos_fallidos >= 3:
                self.vista.bloquear_boton(30)
