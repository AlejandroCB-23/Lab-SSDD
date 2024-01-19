
class AdministracionPersistencia:
    """Clase que se encarga de administrar la persistencia de los usuarios."""

    def __init__(self, persistencia_usuarios="Nombres_Contrasenas.txt"):
            self.persistencia_usuarios = persistencia_usuarios

    #Metodo utilizado para guardar el usuario en el archivo de texto
    def guardar_usuario_en_archivo(self, username: str, password: str):
        """Guardar el usuario en el archivo de texto."""
        
        #Abrimos el archivo y escribimos el nombre de usuario y la contraseña
        with open(self.persistencia_usuarios, "a") as file:
            file.write(f"{username},{password}\n")
    
    def verificar_usuario_en_archivo(self, username: str, password: str = None) -> bool:
        """Verificar si el usuario existe en el archivo."""
        with open(self.persistencia_usuarios, "r") as fichero:
            for linea in fichero:
                # Ignorar líneas en blanco
                if not linea.strip():
                    continue

                # Dividir la línea en elementos
                elementos = linea.strip().split(',')

                # Verificar si hay al menos un elemento (nombre de usuario)
                if elementos and elementos[0] == username:
                    # Si no se proporciona una contraseña, solo verificamos el nombre de usuario
                    if password is None:
                        return True

                    # Si se proporciona una contraseña, también verificamos la contraseña
                    if password is not None and len(elementos) > 1 and elementos[1] == password:
                        return True

        return False
    
    #Metodo utilizado para eliminar el usuario del archivo de texto
    def eliminar_usuario_del_archivo(self, username: str, uuid: str = None):
        """Eliminar el nombre del usuario del archivo de usuarios."""

        with open(self.persistencia_usuarios, "r+") as fichero:
            #Leemos las lineas del fichero
            lineas = fichero.readlines()
            
            #Nos ponemos al principio del fichero
            fichero.seek(0)
            
            #Escribimos las lineas que no contengan el nombre de usuario
            fichero.writelines(line for line in lineas if not (line.startswith(username + ',')))
            
            #Truncamos el fichero
            fichero.truncate()

