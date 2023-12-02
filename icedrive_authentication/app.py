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
        
        #Coprobamos que esta vivo a los 60 segundos 
        time.sleep(60)
        if user.isAlive():
            logging.info("El usuario esta vivo")

        #Comprobamos que esta vivo pasado los 120 segundos
        time.sleep(61)
        if not user.isAlive():
            logging.info("El usuario no esta vivo")

        #Una vez comprobado que no esta vivo, vamos a refrescarlo y comprobamos que este vico
        user.refresh()
        time.sleep(60)
        if user.isAlive():
            logging.info("El usuario esta vivo 2")

        #Comprobamos que no esta vivo pasado los 120 segundos
        time.sleep(61)
        if not user.isAlive():
            logging.info("El usuario no esta vivo 2")

        #Ahora vamos a hacer login
        user = authentication.login("Alejandro", "123")
        logging.info("User: %s", user)
        logging.info("Usuario logeado")

        if user.isAlive():
            logging.info("El usuario esta vivo 3")
        time.sleep(121)
        if not user.isAlive():
            logging.info("El usuario no esta vivo 3")

        if authentication.verifyUser(user):
            logging.info("El usuario fue verificado")


        #Eliminamos el usuario
        authentication.removeUser("Alejandro", "123")
        logging.info("El usuario fue eliminado")

        authentication.removeUser("Alejandro2", "123")
        logging.info("El usuario2 fue eliminado")
        


        

       

       

        


      
    

   
