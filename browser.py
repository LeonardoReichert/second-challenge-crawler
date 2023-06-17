
"""

Aqui la construccion del cuerpo del browser

"""


from requests import Session;

from urllib.robotparser import RobotFileParser;
import time;


class Browser(Session):
    def __init__(self, hostname):
        super().__init__();
        self.headers["User-Agent"] = "Cr"
        self.hostname = hostname;

        self.robotParser = RobotFileParser(url=self.hostname+"/robots.txt");
        self.robotParser.read();
    
    def rbCanFetch(self, url):
        """ Revisa los permisos del archivo /robots.txt del sitio para una url """
        return self.robotParser.can_fetch(useragent=self.headers["User-Agent"], url=url);
            
    def post(self, url, **kwargs):
        """ POST con reintentos y uso de politica de /robots.txt del sitio """
        url = self.hostname+url;
        
        if not self.rbCanFetch(url):
            print("No se puede hacer acceso a la url", url);
            return -1;
    
        for _retry in range(3):
            try:
                resp = super().post(url, **kwargs);
                resp.raise_for_status();
                return resp.content.decode("utf-8");
            except:
                print(f"url {url} fallo, esperando 5 segundos..");
                time.sleep(5); 
               
        return -1;

    def get(self, url):
        """ GET con reintentos y uso de politica de /robots.txt del sitio """
        url = self.hostname+url;

        if not self.rbCanFetch(url):
            print("No se puede acceder a la url", url);
            return -1;
    
        for _retry in range(3):
            try:
                resp = super().get(url);
                resp.raise_for_status();
                return resp.content.decode("utf-8");
            except:
                print(f"url {url} fail, waitin 5 seconds..");
                time.sleep(5);
        
        return -1;






