# second-challenge-crawler
Cumpliendo con un challenge de scraping midd

## Requisitos:
 * Usado **Python** 3.11 aunque podria andar en otras versiones 3.x
 * Usado **requests** como libreria para web.
    Se necesita ejecutar el comando **"pip install requests"**
 * Crear o modificar los archivos .txt que este mini-tutorial readme señala.
 * Configurar con los valores adecuados config.py como este tutorial y los comentarios en el codigo señalan.


## Funcionamiento
Cumple con lo requerido, busca por **numeros de marca** en el sitio y por manejo de threads y proxies logra cumplir con las requests.
Cada proxy sera un thread que toma una porción del trabajo, se usaran varios proxies-threads hasta completar el trabajo, finalmente se guarda el resultado requerido en un archivo .json como el challenge lo propuso.

## Archivos necesarios
 Se debe crear los siguientes archivos en la carpeta del programa:
 * **target_site.txt**: El archivo que contiene la **dirección del sitio** al que apuntar, tal asi: https://localhost (siempre con https://). Este archivo no puede tener otra cosa que el host, no puede tener comentarios o otra cosa.
 * **target_regs.txt**: El archivo con todos los **numeros de marca** a consultar uno debajo del otro, uno por linea, un ejemplo para tres numeros:

```
1111111111111111111
2222222222222222222
3333333333333333333
```

 * **proxies.txt**: El archivo que contiene las **proxies** a usarse, una por linea debajo de la otra, por ejemplo:

```
ip1:puerto
ip2:puerto
ip3:puerto
```

<br>

## Configuración
----------------
 El archivo **config.py** tiene las **configuraciones necesarias** para poner a punto y dar una correcta y personalizada ejecución, tiene una variable config **como diccionario** que es el diccionario que agrupa toda la **configuración del programa**. Este mismo archivo esta repleto de comentarios que guian para que sirve cada cosa.
 
 Las **opciones** son:


  * **user_agent**: Una cadena de texto, Nombre de usuario agente que se usara.
    
  * **timeouts**: Tiempo o lapso que se espera por cada solicitud, un entero o None.

  * **max_threads_proxy**: Numero de proxies o conexiones en paralelo a la vez mediante threads

  * **maxregistros_peer_conn**: Un entero **cantidad de numeros** a consultarse por conexion, o la **porción de numeros** que tomará cada hilo para consultar.
    
  * **wait_seconds_by_query**: Numero de segundos a esperar por cada consulta en una conexion

  * **max_retrys**: Numero de veces que reintentamos acceder a una solicitud.

  * **retry_wait_seconds**: Segundos a esperar despues de un reintento o intento fallido.
    
  * **read_robots**: Decidir si leer robots.txt o no True/False:

  * **debug_errors_conn**: Muestra los errores al no poder acceder a una url mediante (suele ser molesto).
    
  * **encoding**: Codificacion con la que se decodifcicaran y codificaran, por ejemplo cuando se guarda un archivo de resultado se elige el encoding, por defecto "utf-8"

  * **dir_saves**: Carpeta donde se guardaran los archivos de resultados, por defecto "saves/"
    
  * **filename_saves**: Nombre del archivo de resultados por defecto "result.json"
    <br>
  * **_proxies_need_prevtest**: True/False para testear opcionalmente los proxies antes de empezar y seguir solo con los que respondan.
  * **_threads_prevtest_proxy**: Cantidad de threads de prueba a usar para testear los proxies.


<br>

## Otras indicaciones y aclaraciones
-------------------------------------

  Por logica, no permite ejecutar el programa sin proxies, se necesita proxies en el archivo **proxies.txt** para poder tener exito.
 De esta manera el programa se basa en crear un **thread a cada conexion proxy**, un thread independiente. El algoritmo usa threads de manera ciclica, crea threads y le asigna una **porcion de numeros**, hace lo mismo para un limite de threads y cuando terminan esos threads mientras hallan mas numeros sigue lanzando de esta manera threads hasta terminar, es como una rueda de threads o conexiones hasta terminar.

Gracias :D
