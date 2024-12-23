"""Module for servants implementations."""

import Ice
import threading
import time
import IceDrive
from .administracion_persistencia import AdministracionPersistencia
from .delayed_response import AuthenticationQueryResponse, AuthenticationQuery


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


        if not self.persistencia.verificar_usuario_en_archivo(self.username, self.password):
            return False
        
        return time.time() - self.creation_time < self.lifetime
 

    def refresh(self, current: Ice.Current = None) -> None:
        """Renew the authentication for 1 more period of time."""

        
        #Comprobamos que el usuario exista en el txt
        if not self.persistencia.verificar_usuario_en_archivo(self.username, self.password):
            raise IceDrive.UserNotExist
        
        #Si el usuario no esta vivo lanzamos la excepcion Unauthorized
        if not self.isAlive():
            raise IceDrive.Unauthorized
        
        self.creation_time = time.time() + 120 


class Authentication(IceDrive.Authentication):
    """Implementation of an IceDrive.Authentication interface."""

    def __init__(self, query_pub: IceDrive.AuthenticationQueryPrx):
        self.persistencia = AdministracionPersistencia()
        self.diccionario_proxy = {}
        self.query = query_pub 


    def login(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Authenticate an user by username and password and return its User. Comprobando que esten en el txt tambien"""

            
        # Verificar si el usuario existe en el archivo y validar la contraseña. En caso de que no este, lanzamos la excepcion Unauthorized
        if not self.persistencia.verificar_usuario_en_archivo(username, password):
            #Si no esta en la persistencia se consulta a los demas servicios, si en 5 segundos no nos contestan, se lanza la excepcion Unauthorized
            #Le pasamos el usuario y la contraseña al delayed_response
            
            #Creamos el future
            future = Ice.Future()
            #Creamos el objeto de respuesta y la instancia de user
            respuesta = AuthenticationQueryResponse(future)
            #Creamos el proxy de respuesta
            respuesta_proxy = IceDrive.AuthenticationQueryResponsePrx.uncheckedCast(current.adapter.add(respuesta, current.id))

            #Enviamos la peticion a los demas servicios
            self.query.login(username, password, respuesta_proxy)

            threading.Timer(5, future.set_exception, [IceDrive.Unauthorized]).start()
           
            

        # Crear un nuevo proxy de usuario
        usuario = User(username, password)

        #Creamos el proxy del usuario y lo añadimos al adapter
        usuario_proxy = IceDrive.UserPrx.uncheckedCast( current.adapter.addWithUUID(usuario)).ice_timeout(120)

        #Guardar el proxy en el diccionario
        self.diccionario_proxy.setdefault(username, []).append(usuario_proxy)

        # Devolver el proxy del usuario
        return usuario_proxy



    def newUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> IceDrive.UserPrx:
        """Create an user with username and the given password."""

        
        #Verificamos que el usuario no este en el txt y si este se encuentra en el, lanzamos la excepcion UserAlreadyExists
        if self.persistencia.verificar_usuario_en_archivo(username):
                #Se consulta la existencia del mismo a traves del topic, donde otras instancias del servicio pueden responder
                #Si el usuario existe, se lanza la excepcion UserAlreadyExists
                
                #Creamos el future
                future = Ice.Future()
                #Creamos el objeto de respuesta y la instancia de user
                respuesta = AuthenticationQueryResponse(future)
                #Creamos el proxy de respuesta
                respuesta_proxy = IceDrive.AuthenticationQueryResponsePrx.uncheckedCast(current.adapter.add(respuesta, current.id))

                #Enviamos la peticion a los demas servicios
                self.query.doUserExist(username, respuesta_proxy)

                threading.Timer(5, future.set_exception, [IceDrive.UserAlreadyExists]).start()

                
        

        #Creamos el usuario con el nombre y la contraseña
        usuario = User(username, password)

        #Creamos el proxy del usuario y lo añadiomos al adapter
        usuario_proxy = IceDrive.UserPrx.uncheckedCast(current.adapter.addWithUUID(usuario).ice_timeout(120))

        #Guardamos el proxy en el diccionario
        self.diccionario_proxy.setdefault(username, []).append(usuario_proxy)

        # Guardar el usuario en el archivo
        self.persistencia.guardar_usuario_en_archivo(username, password)

        # Devolver el proxy del usuario
        return usuario_proxy


    def removeUser(
        self, username: str, password: str, current: Ice.Current = None
    ) -> None:
        """Remove the user "username" if the "password" is correct."""


        #Verificamos que la contraseña y el nombre son correctos. Si no lo son lanzamos la excepcion Unauthorized 
        if not self.persistencia.verificar_usuario_en_archivo(username, password):

            #Creamos el future
            future = Ice.Future()
            #Creamos el objeto de respuesta y la instancia de user
            respuesta = AuthenticationQueryResponse(future)
            #Creamos el proxy de respuesta
            respuesta_proxy = IceDrive.AuthenticationQueryResponsePrx.uncheckedCast(current.adapter.add(respuesta, current.id))

            #Enviamos la peticion a los demas servicios
            self.query.removeUser(username, password, respuesta_proxy)

            threading.Timer(5, future.set_exception, [IceDrive.Unauthorized]).start()
            


        try:
            #Verificar si el usuario tiene proxies en el diccionario, en caso de que no tenga, lanzamos la excepcion UserNotExist
            if username in self.diccionario_proxy:
                
                #Recorremos la lista de proxies asoiada al usuario
                for usuario_proxy in self.diccionario_proxy[username]:

                    #Eliminamos el proxy del adapter
                    current.adapter.remove(usuario_proxy.ice_getIdentity())

                #Limpiamos la lista de proxies del usuario
                del self.diccionario_proxy[username]
            
            #Eliminar el usuario del archivo
            self.persistencia.eliminar_usuario_del_archivo(username, password)
        
        except Ice.ObjectNotExistException:
            raise IceDrive.UserNotExist
                

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        """Check if the user belongs to this service.
        Don't check anything related to its authentication state or anything else."""


        #Obtenemos el uuid del usuario
        uuid = user.ice_getIdentity().name

        #Obtenemos la identidad del usuario
        usuario_identidad = Ice.Identity(uuid, "")

        #Obtenemos el objeto del usuario a traves del uuid y si no esta preguntar al topic
        objeto_usuario = current.adapter.find(usuario_identidad)
        if objeto_usuario is None:
            #Creamos el future
            future = Ice.Future()
            #Creamos el objeto de respuesta y la instancia de user
            respuesta = AuthenticationQueryResponse(future)
            #Creamos el proxy de respuesta
            respuesta_proxy = IceDrive.AuthenticationQueryResponsePrx.uncheckedCast(current.adapter.add(respuesta, current.id))

            #Enviamos la peticion a los demas servicios
            self.query.verifyUser(user, respuesta_proxy)

            threading.Timer(5, future.set_exception, [IceDrive.UserNotExist]).start()

        
        # Devolver True si el objeto del usuario está presente, False en caso contrario
        return objeto_usuario is not None



   
