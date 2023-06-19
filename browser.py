
"""

Aqui la construccion del cuerpo del browser

"""


from requests import Session;

from urllib.robotparser import RobotFileParser;
import time;
from config import config;


class Browser(Session):
    def __init__(self, hostname, proxy, use_robots=config["read_robots"],
                                        debug_errors = config["debug_errors_conn"]):
        super().__init__();
        self.headers["User-Agent"] = config["user_agent"];
        self.hostname = hostname;
        self.proxies = proxy;

        self._useRobots = use_robots;
        if use_robots:
            self.robotParser = RobotFileParser(url=self.hostname+"/robots.txt");
            self.robotParser.read();
    
        self._debugErrors = debug_errors;

    def debugErrors(self, *obj, **kwargs):
        if self._debugErrors:
            print(*obj, **kwargs);
        
    def rbCanFetch(self, url):
        """ Revisa los permisos del archivo /robots.txt del sitio para una url """
        if self._useRobots:
            return self.robotParser.can_fetch(useragent=self.headers["User-Agent"], url=url);
        else:
            return True;
            
    def post(self, url, **kwargs):
        """ POST con reintentos y uso de politica de /robots.txt del sitio """
        url = self.hostname+url;
        
        if not self.rbCanFetch(url):
            self.debugErrors("No se puede hacer acceso a la url", url);
            return -1;
    
        for _retry in range(config["max_retrys"]):
            try:
                kwargs["timeout"] = config["timeouts"];
                resp = super().post(url, **kwargs);
                resp.raise_for_status();
                return resp.content.decode("utf-8");
            except Exception as msg:
                self.debugErrors(f"url {url} fallo, esperando 5 segundos.. {msg}");
                time.sleep(config["retry_wait_seconds"]); 
               
        return -1;

    def get(self, url):
        """ GET con reintentos y uso de politica de /robots.txt del sitio """
        url = self.hostname+url;

        if not self.rbCanFetch(url):
            print("No se puede acceder a la url", url);
            return -1;
    
        for _retry in range(3):
            try:
                resp = super().get(url, timeout=config["timeouts"]);
                resp.raise_for_status();
                return resp.content.decode("utf-8");
            except:
                self.debugErrors(f"url {url} fail, waitin 5 seconds..");
                time.sleep(5);
        
        return -1;



