
"""

Aqui la construccion del cuerpo del browser

"""


from requests import Session
from threading import Lock
import time
import logging

from config import config




class Browser(Session):
    def __init__(self, hostname, proxy,
                                        user_agent = config["user_agent"],
                                        debug_errors = config["debug_errors_conn"],
                                        ):
        super().__init__()
        self.headers["User-Agent"] = user_agent
        self.hostname = hostname
        self.proxies = proxy
        self._debug_errors = debug_errors

        self.lock_debug = Lock()


    def debug_errors(self, message):
        """ Se encarga de los logs de errores de conexion molestos """
        if self._debug_errors:
            # solo si se desea se captar estos errores
            with self.lock_debug:
                # - sincronizado -
                logging.error(message)
            
            
    def post(self, suburl, **kwargs):
        """ POST con reintentos a la sub url, por ejemplo /index.html"""

        url = self.hostname + suburl
    
        for _retry in range(config["max_retrys"]+1):
            try:
                kwargs["timeout"] = config["timeouts"]
                resp = super().post(url, **kwargs)
                resp.raise_for_status()
                return resp.content.decode(config["encoding"])
            except Exception as msg:
                self.debug_errors(f"url {suburl} fallo en metodo POST {msg}")
                time.sleep(config["retry_wait_seconds"]) 
               
        return -1

    def get(self, suburl):
        """ GET con reintentos de la sub url, por ejemplo /index.html"""

        url = self.hostname + suburl
        
        for _retry in range(config["max_retrys"]+1):
            try:
                resp = super().get(url, timeout=config["timeouts"])
                resp.raise_for_status()
                return resp.content.decode(config["encoding"])
            except Exception as msg:
                self.debug_errors(f"url {suburl} fallo en metodo GET {msg}")
                time.sleep(config["retry_wait_seconds"])
        
        return -1



