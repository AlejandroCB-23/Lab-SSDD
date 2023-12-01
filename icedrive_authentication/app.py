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

        #Ahora vamos a añadir un usuario
        user = authentication.newUser("Alejandro", "123")
        logging.info("User: %s", user)
        
        time.sleep(60)
        if user.isAlive():
            logging.info("El usuario esta vivo")
        time.sleep(61)
        if not user.isAlive():
            logging.info("El usuario no esta vivo")

        user.refresh()
        time.sleep(60)
        if user.isAlive():
            logging.info("El usuario esta vivo 2")

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

        authentication.removeUser("Alejandro", "123")
        logging.info("El usuario fue eliminado")
        


        

       

       

        


      
    

   
