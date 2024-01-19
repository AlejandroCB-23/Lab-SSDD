"""Authentication service application."""

import logging
import sys
from typing import List
import time

import Ice
import IceDrive
import IceStorm
import threading

#import authentication
from .authentication import Authentication
from .delayed_response import AuthenticationQuery, AuthenticationQueryResponse
from .discovery import Discovery
from .administracion_persistencia import AdministracionPersistencia

class AuthenticationApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""



    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        properties = self.communicator().getProperties()
        properties_query = self.communicator().getProperties()

        topic_name = properties.getProperty("Discovery.Topic")
        topic_query = properties_query.getProperty("Authentication.DeferredResolution.Topic")

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        )

        try :
            topic = topic_manager.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name)


        try :
            topic2 = topic_manager.retrieve(topic_query)
        except IceStorm.NoSuchTopic:
            topic2 = topic_manager.create(topic_query)

       
        #Creamos el discovery, lo añadimos al adaptador y lo publicamos
        print("Creamos el discovery")
        discovery_pub = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher())
        query_pub = IceDrive.AuthenticationQueryPrx.uncheckedCast(topic2.getPublisher())

        print("Publisher: " + str(discovery_pub))
        print("Publisher: " + str(query_pub))


   
        
        print("Añadimos el discovery al adaptador")

        adapter = self.communicator().createObjectAdapter("AuthenticationAdapter")
        adapter.activate()

        servant = Discovery()
        authentication_service = Authentication(query_pub)
        authentication_prx = IceDrive.AuthenticationPrx.checkedCast(adapter.addWithUUID(authentication_service))

        #Hacemos el query_servant y le pasamos la instancia del servicio
        #query_servant = AuthenticationQuery(authentication_service)
        query_servant = AuthenticationQuery(AdministracionPersistencia())


        servant_proxy = IceDrive.DiscoveryPrx.checkedCast(adapter.addWithUUID(servant))
        servant_proxy2 = IceDrive.AuthenticationQueryPrx.checkedCast(adapter.addWithUUID(query_servant))
        print("Discovery: " + str(servant_proxy))
        print("Query: " + str(servant_proxy2))

        #Nos subscribimos al topic, obtenemos los subscritores y esperamos a que se conecten
        print("Nos subscribimos al topic")
        topic.subscribeAndGetPublisher({}, servant_proxy)

        #Nos subscribimos al topic2, obtenemos los subscritores y esperamos a que se conecten
        print("Nos subscribimos al topic2")
        topic2.subscribeAndGetPublisher({}, servant_proxy2)



    
        announce_thread = threading.Thread(target=self.run_announce_periodically, args=(authentication_prx, discovery_pub))
        announce_thread.start()

        try:
            self.shutdownOnInterrupt()
            self.communicator().waitForShutdown()
        finally:
            # Asegúrate de detener el hilo al finalizar
            announce_thread.join()


        return 0
     

    def run_announce_periodically(self, authentication_prx, discovery_pub):

    
        while not self.communicator().isShutdown():
            time.sleep(5)
            print("Me anuncio en el topic")
            discovery_pub.announceAuthentication(authentication_prx)




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

        nombre = user.getUsername()
        logging.info("Nombre: %s", nombre)

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
        
        time.sleep(121)

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


        

       

       

        


      
    

   
