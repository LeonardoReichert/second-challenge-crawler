# second-challenge-crawler
Cumpliendo con un challenge de scraping midd

## Requisitos:
 * Usado **Python** 3.11 aunque podria andar en otras versiones 3.x
 * Usado **requests** como libreria para web.
    Se necesita ejecutar el comando **"pip install requests"**
 * Crear o modificar los archivos .txt que este mini-tutorial señala.
 * Configurar con los valores adecuados config.py como este tutorial y los comentarios en el codigo señalan.
 * El ultimo paso ejecutar "scrap.py"

## Funcionamiento
Cumple con lo requerido, busca por **numeros de marca** en el sitio y por manejo de threads y proxies logra cumplir con las requests.<br>
Lanza la cantidad de Threads especificada por config.py, y cada Thread continuamente establece una nueva la conexion inicial, y luego toma del monton un numero siguiente para consultarlo.<br>
Los threads tienen vida indeterminada o mejor dicho hasta completar el trabajo total, finalmente se guardan los resultados requeridos en un archivo .json como el challenge.

## Archivos necesarios
 Se debe crear los siguientes archivos en la carpeta del programa:
 * **target_site.txt**: El archivo que contiene la **dirección del sitio** al que apuntar, tal asi: https://localhost por ejemplo (siempre con https://). Este archivo no puede tener otra cosa que el host, no puede tener comentarios o otra cosa.
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
 El archivo **config.py** tiene las **configuraciones necesarias** para poner a punto y dar una correcta y personalizada ejecución, tiene solo una variable **config (diccionario)** el cual agrupa toda la **configuracion del programa**. Este mismo archivo esta repleto de comentarios que guian para que sirve cada cosa.
 
 Las **opciones** son:

  * **user_agent**: Una cadena de texto, Nombre de usuario agente que se usara.
    
  * **timeouts**: Tiempo o lapso que se espera por cada solicitud, un entero o None.

  * **max_threads_connections**: Numero de threads o conexiones proxies en paralelo a la vez.
  Obviamente este numero debe ser menor a la cantidad de proxies existente, si se ingresa mayor a la cantidad de proxies entonces se iguala a la cantidad de proxies...
    
  * **wait_seconds_by_query**: Numero de segundos a esperar por cada consulta en una conexion

  * **max_retrys**: Numero de veces que reintentamos acceder a una solicitud.

  * **retry_wait_seconds**: Segundos a esperar despues de un reintento o intento fallido.

  * **debug_errors_conn**: Muestra los errores al no poder acceder a una url mediante (suele ser molesto).
    
  * **encoding**: Codificacion con la que se decodifcicaran y codificaran, por ejemplo cuando se guarda un archivo de resultado se elige el encoding, por defecto "utf-8"

  * **dir_saves**: Carpeta donde se guardaran los archivos de resultados, por defecto "saves/"
    
  * **filename_saves**: Nombre del archivo de resultados por defecto "result.json"
    <br>
  * **_proxies_need_prevtest**: True/False para testear opcionalmente los proxies antes de empezar y seguir solo con los que respondan.
  * **_threads_prevtest_proxy**: Cantidad de threads de prueba a usar para testear los proxies.


<br>

## Otras indicaciones y aclaraciones

  Por logica, no permite ejecutar el programa sin proxies, se necesita proxies en el archivo **proxies.txt** para poder tener exito.
 De esta manera el programa se basa en crear los **threads** y que cada thread se encargue de seleccionar proxies para crear una conexion y cada conexion se encarga de los numeros que pueda, asi se repite hasta terminar la cantidad de numeros ingresados en **target_regs.txt**
 
Gracias :D
