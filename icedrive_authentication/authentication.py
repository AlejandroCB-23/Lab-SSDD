"""Module for servants implementations."""

import Ice
import time
import IceDrive

class User(IceDrive.User):
    """Implementation of an IceDrive.User interface."""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.creation_time = time.time()
        self.lifetime = 120  # Vida útil de 2 minutos en segundos

    def getUsername(self, current: Ice.Current = None) -> str:
        """Return the username for the User object."""
        return self.username

    def isAlive(self, current: Ice.Current = None) -> bool:
        """Check if the authentication is still valid or not."""
        return time.time() - self.creation_time < self.lifetime
 

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""
        #Comprobamos que el usuario siga en el txt
        #if not self.verificar_usuario_en_archivo(self.username, self.password):
            #raise IceDrive.Unauthorized
        
        self.creation_time += 120 


class Authentication(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""

    def __init__(self):
        self.persistencia_usuarios = "Nombres_Contrasenas.txt"
        

    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Authenticate an user by username and password and return its User.Comprobando que esten en el txt tambien"""
            
        # Verificar si el usuario existe en el archivo y validar la contraseña
        if not self.verificar_usuario_en_archivo(username, password):
            raise IceDrive.UserNotFound

        try:
            # Verificar si el usuario existe en el archivo y obtener el UUID
            uuid = self.obtener_uuid_de_archivo(username, password)

            if uuid is None:
                raise IceDrive.Unauthorized

            # Crear la identidad con el UUID
            usuario_identidad = Ice.Identity(uuid, "")

            # Intentar eliminar el usuario
            current.adapter.remove(usuario_identidad)

        except Ice.ObjectNotExistException:
            raise IceDrive.UserNotFound

        # Crear un nuevo proxy de usuario
        usuario = User(username, password)
        usuario_proxy = IceDrive.UserPrx.uncheckedCast( current.adapter.addWithUUID(usuario)).ice_timeout(120)  # Establecer un tiempo de espera de 2 minutos

        # Guardar el UUID del usuario en el archivo
        self.actualizar_uuid_en_archivo(username, password, usuario_proxy.ice_getIdentity().name)

        return usuario_proxy

    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Create an user with username and the given password."""
        
        if self.verificar_usuario_en_archivo(username):
                raise IceDrive.UserAlreadyExists

        usuario = User(username, password)
        usuario_proxy = IceDrive.UserPrx.uncheckedCast( current.adapter.addWithUUID(usuario).ice_timeout(120).ice_twoway().ice_secure(False))

        # Guardar el UUID del usuario en el archivo
        self.guardar_usuario_en_archivo(username, password, usuario_proxy.ice_getIdentity().name)

        return usuario_proxy


    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""

        if not self.verificar_usuario_en_archivo(username, password):
            raise IceDrive.Unauthorized

        try:
            # Verificar si el usuario existe en el archivo y obtener el UUID
            uuid = self.obtener_uuid_de_archivo(username, password)

            if uuid is None:
                raise IceDrive.Unauthorized

            # Crear la identidad con el UUID
            usuario_identidad = Ice.Identity(uuid, "")

            # Intentar eliminar el usuario
            current.adapter.remove(usuario_identidad)
            self.eliminar_usuario_del_archivo(username)

        except Ice.ObjectNotExistException:
            raise IceDrive.UserNotFound




    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.

        Don't check anything related to its authentication state or anything else."""

        uuid = user.ice_getIdentity().name
        usuario_identidad = Ice.Identity(uuid, "")
        objeto_usuario = current.adapter.find(usuario_identidad)
        
        # Devolver True si el objeto del usuario está presente, False en caso contrario
        return objeto_usuario is not None
    



    # Metodos auxiliares del manejo de archivos 

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

