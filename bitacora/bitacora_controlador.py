from bitacora.bitacora_modelo import BitacoraModelo

class BitacoraControlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = BitacoraModelo()

    def cargar_datos(self, texto="", filtros=None):
        modulo = filtros.get("Módulo") if filtros else None
        accion = filtros.get("Acción") if filtros else None
        
        registros = self.modelo.obtener_registros(modulo=modulo, accion=accion)
        
        datos = []
        for r in registros:
            # Filtrado por texto en el cliente (simple)
            coincide_texto = True
            if texto:
                coincide_texto = (texto.lower() in str(r.modulo).lower() or 
                                  texto.lower() in str(r.accion).lower() or
                                  texto.lower() in str(r.registro_id).lower() or
                                  texto.lower() in str(r.fecha_hora).lower())
            
            if coincide_texto:
                usuario_nombre = r.usuario.nombre_usuario if r.usuario else "Desconocido"
                datos.append([
                    r.id_bitacora,
                    usuario_nombre,
                    r.modulo,
                    r.accion,
                    r.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                    r.registro_id or "-"
                ])
                
        self.vista.mostrar_datos(datos)
