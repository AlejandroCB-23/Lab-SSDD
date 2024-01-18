"""Servant implementation for the delayed response mechanism."""

import Ice

import IceDrive
from .administracion_persistencia import AdministracionPersistencia
from .authentication import Authentication, User


class AuthenticationQueryResponse(IceDrive.AuthenticationQueryResponse): #Respondes a otros
    """Query response receiver."""
    def __init__(self, instance: Authentication, persistencia: AdministracionPersistencia, future: Ice.Future):
        self.persistencia = persistencia
        self.instance = instance
        self.future = future

    def loginResponse(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> None:
        """Receive an User when other service instance knows about it and credentials are correct."""
        "El servicio recibe la llamada al método “loginResponse” de esta interfaz con el proxy del usuario y comprueba que ese usuario este en el diccionario."
        "Si esta invoca una respuesta enviando el nombre de usuario y contraseña y adjunta un objeto User en caso de credenciales correctas o uno nulo en caso de incorrectas"

        self.future.set(user)
        current.adapter.remove(current.id)


    def userRemoved(self, current: Ice.Current = None) -> None:
        """Receive an invocation when other service instance knows the user and removed it."""
        "El servicio recibe la llamada al método “userRemoved” de esta interfaz y elimina el usuario del diccionario"
        

    def verifyUserResponse(self, result: bool, current: Ice.Current = None) -> None:
        """Receive a boolean when other service instance is owner of the `user`."""
        "El servicio recibe la llamada al método “verifyUserResponse” de esta interfaz con el resultado de la verificación. Si el resultado es “True”, se enviará una llamada al método “userExists” de la interfaz AuthenticationQueryResponse con el proxy del usuario. Si el resultado es “False”, se enviará una llamada al método “userRemoved” de la interfaz AuthenticationQueryResponse."


    def userExists(self, current: Ice.Current = None) -> None:
        """Receive an invocation when other service instance knows about the user."""


class AuthenticationQuery(IceDrive.AuthenticationQuery): #Para que otros me ayuden
    """Query receiver."""
    def __init__(self, instance: Authentication):
        self.instance = instance

    def login(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user login."""
        "El servicio recibe la llamada al método “login” de esta interfaz con las credenciales de usuario. Si no son correctas, se ignorarán. Si el usuario existe, se enviará la respuesta a través del proxy de tipo AuthenticationQueryResponse recibido."

        usuario = User(username, password)
        response.loginResponse(usuario)
        
        
    def removeUser(self, username: str, password: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an user to be removed."""
        "El servicio recibe la llamada al método “removeUser” de esta interfaz con las credenciales de usuario. Si no son correctas, se ignorarán. Si el usuario existe, se enviará la respuesta a través del proxy de tipo AuthenticationQueryResponse recibido."

        usuario = User(username, password)
        response.userRemoved(usuario)

    def verifyUser(self, user: IceDrive.UserPrx, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an `User` to be verified."""
        "El servicio recibe la llamada al método “verifyUser” de esta interfaz con el proxy del usuario. Si el usuario existe, se enviará la respuesta a través del proxy de tipo AuthenticationQueryResponse recibido. Si el usuario no existe, se enviará la respuesta a través del proxy de tipo AuthenticationQueryResponse recibido."

        response.verifyUserResponse(user)

    def doesUserExists(self, username: str, response: IceDrive.AuthenticationQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about an `User` to be verified."""

        response.userExists(username)

