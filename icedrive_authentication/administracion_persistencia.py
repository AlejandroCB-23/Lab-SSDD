
class AdministracionPersistencia:
    """Clase que se encarga de administrar la persistencia de los usuarios."""

    def __init__(self, persistencia_usuarios="Nombres_Contrasenas.txt"):
            self.persistencia_usuarios = persistencia_usuarios

    def guardar_usuario_en_archivo(self, username: str, password: str, uuid: str):
        """Guardar el usuario en el archivo de texto."""
        with open(self.persistencia_usuarios, "a") as file:
            file.write(f"{username},{password},{uuid}\n")
    
    def verificar_usuario_en_archivo(self, username: str, password: str = None, uuid: str = None) -> bool:
        """Verificar si el usuario existe en el archivo."""
        with open(self.persistencia_usuarios, "r") as fichero:
            for linea in fichero:
                # Dividir la línea en elementos
                elementos = linea.strip().split(',')

                # Verificar si hay al menos un elemento (nombre de usuario)
                if elementos and elementos[0] == username:
                    # Si no se proporciona una contraseña o un UUID, solo verificamos el nombre de usuario
                    if password is None and uuid is None:
                        return True

                    # Si se proporciona una contraseña, también verificamos la contraseña
                    if password is not None and len(elementos) > 1 and elementos[1] == password:
                        return True

                    # Si se proporciona un UUID, también verificamos el UUID
                    if uuid is not None and len(elementos) > 2 and elementos[2] == uuid:
                        return True

        return False
    
    def eliminar_usuario_del_archivo(self, username: str, uuid: str = None):
        """Eliminar el nombre del usuario del archivo de usuarios."""
        with open(self.persistencia_usuarios, "r+") as fichero:
            lineas = fichero.readlines()
            fichero.seek(0)
            fichero.writelines(line for line in lineas if not (line.startswith(username + ',') and (uuid is None or line.endswith(',' + uuid + '\n'))))
            fichero.truncate()

    def obtener_uuid_de_archivo(self, username: str, password: str = None) -> str:
        """Obtener el UUID del usuario del archivo."""
            
        # Abrir el archivo en modo lectura
        with open(self.persistencia_usuarios, 'r') as fichero:
            # Leer todas las líneas del archivo
            lineas = fichero.readlines()

        # Recorrer cada línea del archivo
        for linea in lineas:
            # Dividir la línea por comas y eliminar espacios en blanco al principio y al final
            partes = linea.strip().split(',')

            # Verificar que la línea tiene al menos dos partes (nombre de usuario y contraseña)
            if len(partes) < 2:
                continue

            user, passw, uuid = partes

            # Verificar si el usuario coincide
            if user == username:
                # Si se proporciona una contraseña, también verificarla
                if password is not None and passw == password:
                    return uuid
                # Si no se proporciona una contraseña, devolver el UUID encontrado
                elif password is None:
                    return uuid

        # Si no se encontró el usuario, devolver None
        return None
        
    def actualizar_uuid_en_archivo(self, username: str, password: str, new_uuid: str):
        """Actualizar el tercer parámetro (UUID) en el archivo de texto."""
        with open(self.persistencia_usuarios, "r") as fichero:
            lineas = fichero.readlines()

        with open(self.persistencia_usuarios, "w") as file:
            for linea in lineas:
                elements = linea.strip().split(',')
                if elements and elements[0] == username and len(elements) > 1 and elements[1] == password:
                    # Actualizar el tercer parámetro (UUID) con el nuevo UUID
                    linea = f"{elements[0]},{elements[1]},{new_uuid}\n"
                file.write(linea)