
#own modules:
from proxies import proxies, testProxies;


config = {
    #el user agent:
    "user_agent": "",

    #cantidad de n-registros limite a consultarse por conexion:
    "max_registros_by_conn":3,
    #numero de segundos a esperar por consulta en una conexion:
    "wait_seconds_by_query":3,
    #numero de conexiones paralelas de proxy o normal a la vez:

    #numero de veces que reintentamos acceder a una solicitud:
    "max_retrys": 3,
    #segundos a esperar despues de un reintento:
    "retry_wait_seconds": 5,
    
    #codificacion con la que se decodifcicaran y codificaran
    #   la informacion obtenida y guardada:
    "encoding": "utf-8",

    "proxies": proxies,
    "_proxies_need_prev_test": False,
    "_threads_prevtest_proxy": 1,      #threads a usar para testear las proxies
}




#las proxies se someteran a prueba si se establece la opcion de hacerlo:
if config["_proxies_need_prev_test"]:
    testProxies(proxies, config["_threads_prevtest_proxy"],
                         config["user_agent"],
                         open("target_site.txt", "r").read(),
                         timeout=10,
                        );
    
    #for proxy in proxies:
    #    print(proxy["https"]);
    
