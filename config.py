"""

La configuracion del programa

"""



config = {
    #el user agent:
    "user_agent": "",

    #tiempo de espera por solicitud:
    "timeouts": None,

    #N proxies conexiones en paralelo a la vez:
    "max_threads_proxy": 5,

    #cantidad de n-registros limite a consultarse por conexion:
    "maxregistros_peer_conn": 8,
    #numero de segundos a esperar por consulta en una conexion:
    "wait_seconds_by_query": 3,
    #numero de conexiones paralelas de proxy o normal a la vez:

    #numero de veces que reintentamos acceder a una solicitud:
    "max_retrys": 3,
    #segundos a esperar despues de un reintento:
    "retry_wait_seconds": 3,

    #decidir si leer robots.txt o no True/False:
    "read_robots": True,

    #muestra los errores al no poder acceder a una url (suele ser molesto)
    "debug_errors_conn": False,
    
    #codificacion con la que se decodifcicaran y codificaran
    #   la informacion obtenida y guardada:
    "encoding": "utf-8",

    #carpeta donde se guardaran los archivos de resultados:
    "dir_saves": "saves/",
    #nombre de archivo:
    "filename_saves": "result.json",

    #para testear opcionalmente los proxies antes de empezar
    # y dejar solo los que respondan bien:
    "_proxies_need_prevtest": False,
    "_threads_prevtest_proxy": 10,      #threads a usar para testear los proxies
}


