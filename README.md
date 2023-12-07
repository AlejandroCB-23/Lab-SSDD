# IceDrive Authentication service template

This repository contains the project template for the Authentication service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Updating `pyproject.toml`

One of the first things that you need to setup when you clone this branch is to take a look into
`pyproject.toml` file and update the needed values:

- Project authors
- Project dependencies
- Projects URL humepage



Contenido del programa:

La implementación consise en un archivo con las correspondientes clases Usuario y Autentificación y una tercera añadida por mi "administracion_persistencia" esta clase permite manejar todo aquello que tiene que ver con leer del archivo de persistencia, borrar o actualizarlo.

La clase usuario consiste en 3 métodos, en el método getUsarname(), consiste en devolver el nombre correspondiente al usuario, el método isAluive(), no proporcionara un True o un False dependiendo de si el usuario sigue vivo o no y el método refresh() comprobara primero que el usuario exista en el archivo de persistencia, posteriormente comprobara que la contraseña sea la correcta y por último si todo lo anterior es correcto le sumara un total de 120 segundos de vida al proxy (2 minutos).

La clase Autentificación consiste en 4 metodos, el método login() comprobará que cada vez que se acceda a él, el usuario se encuentra en la persistencia del sistema, para posteriormente crear un nuevo proxy de dicho usuario simulando que este usaurio se puede haber logeado en diferentes dispositivos al mismo tiempo, una vez creado el proxy se añadirá al adaptador, el método newUser() consiste en comprobar que el usuario no se encuentre en la persistencia del sistema para de esta manera poder añadirlo, ya que un usuario solo puede estar 1 vez en la persistencia, una vez añadido se crea su objetos proxy y se devuelve, el método removeUser() consiste en comprobar que el usuario y la contraseña sean correctos y una vez comprobados eliminar todos los proxies asociados a ese usuario y posteriormente eliminar dicho usuario de la persistencia y por último el metodo verifyUser que comprobará si el usuario se encuentra en el adaptador o por el contrario es un proxy no valido en el sistema 

Luego tenemos el archivo app en el cual se encuentra la clase Servidor y Clase Cliente que sirve para poder probar que funciona el programa 

Tambien contamos con una carpeta en la que guardamos los diferentes test que se han ido haciendo a la aplicacion con el fin de saber si se han realizado correctamente las funciones 