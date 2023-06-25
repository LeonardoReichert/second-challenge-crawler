"""

La configuracion del programa

"""



config = {
    #el user agent:
    "user_agent": "",

    #tiempo de espera por solicitud:
    "timeouts": 10,

    #N proxies conexiones en paralelo a la vez:
    "max_threads_connections": 3, #renombrar de proxy a connections

    #numero de segundos a esperar por consulta en una conexion:
    "wait_seconds_by_query": 3,

    #numero de veces que reintentamos acceder a una solicitud:
    "max_retrys": 3,
    #segundos a esperar despues de un reintento:
    "retry_wait_seconds": 3,

    #muestra los errores al no poder acceder a una url (suele ser molesto)
    "debug_errors_conn": False,
    
    #codificacion con la que se decodifcicaran y codificaran
    "encoding": "utf-8",

    #carpeta donde se guardaran los archivos de resultados:
    "dir_saves": "saves/",
    #nombre de archivo de resultados:
    "filename_saves": "result.json",

    #para testear opcionalmente los proxies antes de empezar:
    "_proxies_need_prevtest": False,
}


