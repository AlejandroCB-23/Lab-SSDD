"""Servant implementations for service discovery."""

import Ice

import IceDrive

import random

import logging


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self):
        #Creamos las listas para guardar los respectivos proxies
        self.lista_authentication = []
        self.lista_directory = []
        self.lista_blob = []

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.lista_authentication.append(prx)
        #logging.info("SERVICIO Authentication: %s", prx)


    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        self.lista_directory.append(prx)
        #logging.info("SERVICIO Directory: %s", prx)

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.lista_blob.append(prx)
        #logging.info("SERVICIO Blob: %s", prx)  

    #Getters and removers

    def getAuthenticationService(self):
        #Obtener el proxy del servicio de autenticacion aleatoriamente de la lista
        return random.choice(self.lista_authentication)
    
    def getDirectoryService(self): 
        #Obtener el proxy del servicio de directorio aleatoriamente de la lista
        return random.choice(self.lista_directory)
    
    def getBlobService(self):
        #Obtener el proxy del servicio de blob aleatoriamente de la lista
        return random.choice(self.lista_blob)
    
    def removeAuthenticationService(self, prx: IceDrive.AuthenticationPrx):
        #Eliminar el proxy del servicio de autenticacion de la lista
        self.lista_authentication.remove(prx)

    def removeDirectoryService(self, prx: IceDrive.DirectoryServicePrx):
        #Eliminar el proxy del servicio de directorio de la lista
        self.lista_directory.remove(prx)

    def removeBlobService(self, prx: IceDrive.BlobServicePrx):
        #Eliminar el proxy del servicio de blob de la lista
        self.lista_blob.remove(prx)
    
        
        

