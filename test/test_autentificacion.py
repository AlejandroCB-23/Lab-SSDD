from icedrive_authentication.authentication import User 
from icedrive_authentication.authentication import Authentication
import os
import pytest
import time
import Ice

#Creamos una instancia de la clase Authentication, para poder destruirla despues y que no haya problemas
@pytest.fixture
def auth_instance():
    auth = Authentication()
    yield auth
    # Asegurarse de que el comunicador de Ice se cierre al finalizar la prueba
    auth.communicator.destroy()

#Test para comprobar que se crea un usuario correctamente
def test_usr_creation(auth_instance):            
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    assert user.getUsername() == "Alejandro"
    authentication.removeUser("Alejandro", "123")

#Test para verificar si un ususario se encuentra en el sistema
def test_verificar_usuario(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    assert authentication.verifyUser(user) == True
    authentication.removeUser("Alejandro", "123")

#Test para verificar si un ususario no se encuentra en el sistema
def test_verficar_usuario_no_esta(auth_instance):
    user_no_esta = User("Eustaquio", "123")
    assert not auth_instance.verifyUser(user_no_esta)

#Test para comprobar que se verifica bien o no despues de borrar un usuario
def test_verificar_usuario_depues_de_borrar(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    assert authentication.verifyUser(user) == True
    authentication.removeUser("Alejandro", "123")
    user_comprobacion=User("Alejandro", "123")
    assert not authentication.verifyUser(user_comprobacion)

#Test para comprobar que un usuario se a logeado correctamente y que se encuentra vivo
def test_login(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    user_proxy = authentication.login("Alejandro", "123")
    assert user_proxy.getUsername() == "Alejandro"
    assert user_proxy.isAlive() == True
    authentication.removeUser("Alejandro", "123")

#Test para comprobar un login de contraseña incorrecta el cual revocara en una excepcion
def test_login_contrasena_incorrecta(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    authentication.login("Alejandro", "1234")
    authentication.removeUser("Alejandro", "123")

#Test para comprobar que se ha hecho correctamente el refresh()
def test_aumento_de_vida(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    assert user.isAlive() == True
    user.refresh()
    time.sleep(140)
    assert user.isAlive() == True
    authentication.removeUser("Alejandro", "123")

#Test para conprobar que un usuario muere depsues de 120 segundos
def test_usuario_con_vida_despues_120s(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    time.sleep(121)
    assert user.isAlive() == False
    authentication.removeUser("Alejandro", "123")

#Test para comprobar la vida de un usuario
def test_usuario_con_vida(auth_instance):
    authentication = auth_instance
    user = authentication.newUser("Alejandro", "123")
    time.sleep(60)
    assert user.isAlive() == True
    user_proxy = authentication.login("Alejandro", "123")
    assert user_proxy.isAlive() == True
    time.sleep(60)
    assert user.isAlive() == True
    time.sleep(59)
    assert user.isAlive() == True
    time.sleep(5)
    assert user.isAlive() == False
    authentication.removeUser("Alejandro", "123")
    



