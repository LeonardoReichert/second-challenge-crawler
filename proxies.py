
"""

Modulo que se usara para leer y probar las proxies si funcionan

"""


from requests import Session
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config



# lineas en archivo proxies.txt son ip:port
_proxylines = [line.strip() for line in open("proxies.txt", "r").readlines() if line.strip()]

proxies = [{"https":ip_port} for ip_port in _proxylines if ip_port[0] != "#"]



class ProxyTester:
    """ Clase que testea las proxies al principio del programa,
        para filtrar las que respondan en una conexion
    """
    def __init__(self, proxies, max_threads, user_agent, url_test, timeout, max_retrys):
        """ Inicia el tester de proxies, con los parametros de 
                la conexion a probar, hilos maximos, y tiempo de respuesta """
        if not proxies:
            raise Exception("El argumento 'proxies' no es una coleccion de proxies")
        
        self.proxies = proxies
        self.user_agent = user_agent
        self.url_test = url_test
        self.timeout = timeout
        self.max_threads = max_threads
        self.max_retrys = max_retrys

    def filter_by_test(self):
        """ inicia un test para cada proxy y devuelve 
            una lista de proxies que pasaron el test
        """

        print(f"=== Testing proxies  {len(self.proxies)} === ")

        pthreads = ThreadPoolExecutor(self.max_threads)
        
        self._results = []

        count = 0
        tasks = [pthreads.submit(self._thread_test_proxy, proxy) for proxy in self.proxies]
        for _tsk in as_completed(tasks):
            count += 1
            print(f"\r completed {count}/{len(self.proxies)}", end="")
        
        print("\nproxies on:", len(self._results))

        return self._results
    

    def _thread_test_proxy(self, proxy_address):

        bw = Session()
        bw.headers["User-Agent"] = self.user_agent
        bw.proxies = proxy_address

        try:
            resp = bw.get(self.url_test, timeout=self.timeout)
            resp.raise_for_status()
            #success
            self._results.append(proxy_address)
            return
        except:
            pass




#testear proxies:
#las proxies se someteran a prueba si se establece la opcion de hacerlo:
if config["_proxies_need_prevtest"]:

    proxies = ProxyTester(proxies, max_threads = config["max_threads_connections"],
                                   user_agent = config["user_agent"],
                                   url_test = open("target_site.txt", "r").read(),
                                   #timeout=config["timeouts"],
                                   timeout = 10,
                                   max_retrys = config["max_retrys"],
                        ).filter_by_test()
    

    #for proxy in proxies:
    #    print(proxy["https"])
    

