"""Authentication service application."""

import logging
import sys
from typing import List
import time

import Ice
import IceDrive

#import authentication
from .authentication import Authentication

class AuthenticationApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        adapter = self.communicator().createObjectAdapter("AuthenticationAdapter")
        adapter.activate()

        servant = Authentication()
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0



class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the Client."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the ClientApp class."""
        proxy = self.communicator().stringToProxy(args[1])
        authentication = IceDrive.AuthenticationPrx.checkedCast(proxy)

        if not authentication:
            raise RuntimeError("Invalid proxy")
        
        print("Has Conectado")

        #Ahora vamos a añadir dos usuarios
        user = authentication.newUser("Alejandro", "123")
        logging.info("User: %s", user)

        user2 = authentication.newUser("Alejandro2", "123")
        logging.info("User: %s", user2)

        user3 = authentication.newUser("Alejandro3", "123")
        logging.info("User: %s", user3)
        
        #Coprobamos que esta vivo a los 60 segundos 
        time.sleep(60)
        if user.isAlive():
            logging.info("El usuario esta vivo")
        
        if user2.isAlive():
            logging.info("El usuario2 esta vivo")

        if user3.isAlive():
            logging.info("El usuario3 esta vivo")

        #Le añadimos al usuario 3 120 segundos mas de vida
        user3.refresh()

        #Comprobamos que esta vivo pasado los 120 segundos
        time.sleep(61)
        if not user.isAlive():
            logging.info("El usuario no esta vivo")
        
        if not user2.isAlive():
            logging.info("El usuario2 no esta vivo")

        if user3.isAlive():
            logging.info("El usuario3 esta vivo")
        
        time.sleep(181)

        if not user3.isAlive():
            logging.info("El usuario3 no esta vivo")

        #Ahora vamos a hacer login
        user4 = authentication.login("Alejandro", "123")
        logging.info("User: %s", user4)
        logging.info("Usuario logeado")

        if user4.isAlive():
            logging.info("El usuario esta vivo 1 (logueado)")
        time.sleep(121)
        
        if not user3.isAlive():
            logging.info("El usuario no esta vivo 1 (logueado)")

        if authentication.verifyUser(user4):
            logging.info("El usuario fue verificado 1 (logueado)")


        #Eliminamos el usuario
        authentication.removeUser("Alejandro", "123")
        logging.info("El usuario fue eliminado")

        authentication.removeUser("Alejandro2", "123")
        logging.info("El usuario2 fue eliminado")

        authentication.removeUser("Alejandro3", "123")
        logging.info("El usuario3 fue eliminado")
        
        #Comprobamos que no esta en el servicio
        if not authentication.verifyUser(user):
            logging.info("El usuario no fue verificado 1")


        

       

       

        


      
    

   
