# IceDrive Authentication service template

This repository contains the project template for the Authentication service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Updating `pyproject.toml`

One of the first things that you need to setup when you clone this branch is to take a look into
`pyproject.toml` file and update the needed values:

- Project authors
- Project dependencies
- Projects URL humepage


A la hora de implementar la practica he tenido en cuenta que cada usuario solo puede tener un proxy activo del mismo, de este modo simularia que si tu inicias sesión en un ordenador a la hora de hacerlo en otro ordenador este cerraria la conexión con el primero y se conectaría al segundo. 

Para lograr esto hay que tener en cuenta que cada vez que un usuario hace login(), significa que se inicia una nueva conexión y por tanto se crea un nuevo proxy, por tanto en esta función habria que sacar el nuevo UUID del proxy y eliminar el proxy antiguo.

La implementación consise en un archivo con las correspondientes clases Usuario y Autentificación y una tercera añadida por mi "administracion_persistencia" esta clase permite manejar todo aquello que tiene que ver con leer del archivo de persistencia, borrar o actualizarlo.

Luego tenemos el archivo app en el cual se encuentra la clase Servidor y Clase Cliente que sirve para poder probar que funciona el programa 

Tambien contamos con una carpeta en la que guardamos los diferentes test que se han ido haciendo a la aplicacion con el fin de saber si se han realizado correctamente las funciones 