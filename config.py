



config = {
    #el user agent:
    "user_agent": "yo",

    #cantidad de threads a usarse a la vez:
    "max_threads": 1,
    #cantidad de n-registros a consultarse por thread:
    "max_threads_registros": 10, #sincronos a cada thread
    #numero de segundos a esperar por consulta:
    "wait_seconds_query": 0,

    #numero de veces que reintentamos acceder a una solicitud:
    "max_retrys": 3,
    #segundos a esperar despues de un reintento:
    "retry_wait_seconds": 5,
    
    #codificacion con la que se decodifcicaran y codificaran
    #   la informacion obtenida y guardada:
    "encoding": "utf-8",
}



