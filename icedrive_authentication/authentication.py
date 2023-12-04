"""Module for servants implementations."""

import Ice
import time
import IceDrive
from .administracion_persistencia import AdministracionPersistencia

class User(IceDrive.User):
    """Implementation of an IceDrive.User interface."""

    def __init__(self, username, password):
        self.persistencia = AdministracionPersistencia()
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

        if not self.persistencia.verificar_usuario_en_archivo(self.username):
            raise IceDrive.UserNotExist
        
        if not self.persistencia.verificar_usuario_en_archivo(self.username, self.password):
            raise IceDrive.Unauthorized
        
        self.creation_time += 120 


class Authentication(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""

    def __init__(self):
        self.persistencia = AdministracionPersistencia()


    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Authenticate an user by username and password and return its User. Comprobando que esten en el txt tambien"""
            
        # Verificar si el usuario existe en el archivo y validar la contraseña
        if not self.persistencia.verificar_usuario_en_archivo(username, password):
            raise IceDrive.UserNotFound

        try:
            # Verificar si el usuario existe en el archivo y obtener el UUID
            uuid = self.persistencia.obtener_uuid_de_archivo(username, password)

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
        self.persistencia.actualizar_uuid_en_archivo(username, password, usuario_proxy.ice_getIdentity().name)

        return usuario_proxy



    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Create an user with username and the given password."""
        
        if self.persistencia.verificar_usuario_en_archivo(username):
                raise IceDrive.UserAlreadyExists

        #Creamos el usuario con el nombre y la contraseña
        usuario = User(username, password)
        #Creamos el proxy del usuario y lo añadiomos al adapter
        usuario_proxy = IceDrive.UserPrx.uncheckedCast(current.adapter.addWithUUID(usuario).ice_timeout(120).ice_twoway().ice_secure(False))

        # Guardar el UUID del usuario en el archivo
        self.persistencia.guardar_usuario_en_archivo(username, password, usuario_proxy.ice_getIdentity().name)

        return usuario_proxy


    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""

        #Verificamos que la contraseña y el nombre son correctos
        if not self.persistencia.verificar_usuario_en_archivo(username, password):
            raise IceDrive.Unauthorized

        try:
            # Obtenemos los UUID
            uuid = self.persistencia.obtener_uuid_de_archivo(username, password)

            if uuid is None:
                raise IceDrive.Unauthorized

            # Crear la identidad con el UUID
            usuario_identidad = Ice.Identity(uuid, "")

            # Intentar eliminar el usuario
            current.adapter.remove(usuario_identidad)
            self.persistencia.eliminar_usuario_del_archivo(username)

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



   
