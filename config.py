"""

La configuracion de todo el programa

"""

import logging

#configuracion de los logs:
logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="a", force=True,
    format="%(asctime)s - %(levelname)s - module:%(module)s - function:%(funcName)s message: %(message)s")




config = {
    #el user agent:
    "user_agent": "",

    #tiempo de espera por solicitud, numero entero positivo o None:
    "timeouts": 10,

    #N proxies conexiones en paralelo a la vez:
    "max_threads_connections": 3,

    #numero de segundos a esperar por consulta en una conexion:
    "wait_seconds_by_query": 3,

    #numero de veces que reintentamos acceder a una solicitud:
    "max_retrys": 3,
    #segundos a esperar despues de un reintento:
    "retry_wait_seconds": 3,

    #debug de los errores al no poder acceder a una url (suele ser molesto)
    "debug_errors_conn": False,
    
    #codificacion con la que se decodifcicaran y codificaran
    "encoding": "utf-8",

    #carpeta donde se guardaran los archivos de resultados:
    "dir_saves": "saves/",
    #nombre de archivo de resultados:
    "filename_saves": "result.json",

    #para testear opcionalmente los proxies antes de empezar:
    "_proxies_need_prevtest": False,
    #para indicar que el testeo previo de proxies se usara de manera vaga (sin reintentos)
    # o se usaran el valor de max_retrys para cantidad de reintentos:
    "_proxies_prevtest_islazy": True,
}


