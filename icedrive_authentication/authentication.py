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
        self.creation_time += 120 


class Authentication(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""

    def __init__(self):
        self.usuarios = {}
        self.persistencia_usuarios = "Nombres_Contrasenas.txt"
        self.communicator = Ice.initialize()
        properties = self.communicator.getProperties()
        properties.setProperty("AuthenticationAdapter.Endpoints", "default -p 10000")
        self.adapter = self.communicator.createObjectAdapter("AuthenticationAdapter")
        

    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Authenticate an user by username and password and return its User.Comprobando que esten en el txt tambien"""
            
        # Verificar si el usuario existe en el archivo y validar la contraseña
        if not self.verificar_usuario_en_archivo(username, password):
            raise IceDrive.UserNotFound

        # Buscar la identidad del usuario existente en el adaptador
        user_identity = self.communicator.stringToIdentity(username)
        
        # Verificar la existencia de un proxy existente y eliminarlo
        existing_proxy = self.adapter.find(user_identity)
        if existing_proxy is not None:
            # Eliminar el objeto del adaptador
            self.adapter.remove(user_identity)

        # Crear un nuevo proxy de usuario
        user_proxy = IceDrive.UserPrx.uncheckedCast(
            self.adapter.add(User(username, password), user_identity)
        ).ice_timeout(120)  # Establecer un tiempo de espera de 2 minutos

        return user_proxy

    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Create an user with username and the given password."""

        if self.verificar_usuario_en_archivo(username):
            raise IceDrive.UserAlreadyExists

        usuario = User(username, password)
        user_proxy = IceDrive.UserPrx.uncheckedCast(
            self.adapter.add(usuario, self.communicator.stringToIdentity(username))
                .ice_timeout(120).ice_twoway().ice_secure(False)
        )
        self.guardar_usuario_en_archivo(username, password)

        return user_proxy
        

    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""

        if not self.verificar_usuario_en_archivo(username, password):
            raise IceDrive.Unauthorized
        
    
        #Obtenemos la identidad del usuario
        user_identity = self.communicator.stringToIdentity(username)

        # Buscar el usuario en el adaptador
        user_object = self.adapter.find(user_identity)

        # Verificar si se encontró el objeto
        if user_object is not None:
            # Eliminar el objeto del adaptador
            self.adapter.remove(user_identity)
            
            # Eliminar el usuario del archivo
            self.eliminar_usuario_del_archivo(username)
        else:
            # Manejar el caso donde el usuario no fue encontrado en el adaptador
            raise IceDrive.UserNotFound
       

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.

        Don't check anything related to its authentication state or anything else.
        """
        # Verificar si el proxy del usuario está en el adaptador
        user_identity = self.communicator.stringToIdentity(user.getUsername())
        user_object = self.adapter.find(user_identity)
        
        # Devolver True si el objeto del usuario está presente, False en caso contrario
        return user_object is not None
    



    # Metodos auxiliares del manejo de archivos 

    def guardar_usuario_en_archivo(self, username: str, password: str):
        """Guardar el usuario en el archivo de texto."""
        with open(self.persistencia_usuarios, "a") as file:
            file.write(f"{username},{password}\n")

    
    def verificar_usuario_en_archivo(self, username: str, password: str = None) -> bool:
        """Verificar si el usuario existe en el archivo."""
        with open(self.persistencia_usuarios, "r") as file:
            for line in file:
                # Dividir la línea en elementos
                elements = line.strip().split(',')

                # Verificar si hay al menos un elemento (nombre de usuario)
                if elements and elements[0] == username:
                    # Si no se proporciona una contraseña, solo verificamos el nombre de usuario
                    if password is None:
                        return True

                    # Si se proporciona una contraseña, también verificamos la contraseña
                    if len(elements) > 1 and elements[1] == password:
                        return True

        return False

    
    def eliminar_usuario_del_archivo(self, username: str):
        """Eliminar el nombre del usuario del archivo de usuarios."""
        with open(self.persistencia_usuarios, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            file.writelines(line for line in lines if not line.startswith(username + ','))
            file.truncate()
