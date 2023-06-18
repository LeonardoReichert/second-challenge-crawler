
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



import re;
import json;
import time;
import itertools;
from threading import Thread;

#own modules:
from config import config;
from browser import Browser;
from pool_threads import PoolThreads;




class Scrap:

    def __init__(self, hostname,
                 concurrent_proxies = config["proxies"],
                 ):

        self.hostname = hostname;
        self.connThreads = PoolThreads(len(concurrent_proxies));
        self.concurrentProxies = concurrent_proxies;
        
    
    def findFormFirstHashes(self, browser, url):
        """ Primer paso, visitar link """
        
        html = browser.get(url);
        if html == -1:
            return -1;

        form = re.findall("<form id=\"frmBuscarMarca\" action=\"\">(.+)</form>", html, flags=re.DOTALL);

        hashes = re.findall("setHash\('([a-z0-9]+)','([0-9]+)'\);", html, flags=re.DOTALL);
        
        hasTx = form and "name=\"txtSolicitud\"" in form[0];

        if not (hashes and form and hasTx):
            print("Faltan partes en el form")
            return -1;

        hashes = hashes[0];
        
        #a este punto no hay faltantes en el form (esto no es una variante)
        return hashes;


    def searchByMark(self, num_marks):
        """
        Busca, obtiene mediante Requests y por marcas lo necesario
        """

        #bien los parametros antes de comenzar:
        if not type(num_marks) in (list, tuple):
            raise Exception("Error-num_marks is not a tuple or list")

        #guardamos los proxies que fallan:
        failedProxies = [];
        numsCompleted = [];
        result = [];


        def _connectionThreadProxy(nmarks, use_proxy):
            """ Conexion, proxy y thread que se encarga de una porcion de numeros solicitados """

            url = "/Marca/BuscarMarca.aspx";
        
            #conexion con o sin proxy, independiente del resto:
            browser = Browser(self.hostname, use_proxy);

            #visitamos la pagina, lo primero:
            hashes = self.findFormFirstHashes(browser, url);
            if hashes == -1:
                print("Fallo la primer visita")
                failedProxies.append(use_proxy);
                return -1;
                
            lastHash, idw = hashes;

            for num in nmarks:

                #esperar un poco por consulta?:
                if num: time.sleep(config["wait_seconds_by_query"]);
                
                #preparar 1ra solicitud:
                data = {"LastNumSol":0,
                        "Hash":lastHash, "IDW":idw, "responseCaptcha":"",
                        "param1":num,"param17":"1"};
                #llenamos de datos iguales:
                data |= {f"param{n}":"" for n in range(2,17)};
                
                #primera valor poner numero en textinput:
                resp = browser.post(url+"/FindMarcas",json=data,
                        headers={"Content-Type":"application/json"});
                if resp == -1:
                    print("No se ha podido hacer efectivamente el POST.");
                    return -1;
                resp = json.loads(resp);
                if not "d" in resp or "ErrorMessage" in resp["d"]:
                    print("Error json1", json.loads(resp["d"])["ErrorMessage"]);
                    return 0;
                
                lastHash2 = json.loads(resp["d"])["Hash"];

                #print("resp1",resp)
                #preparamos segunda solicitud:
                data2 = {"IDW": idw, "Hash": lastHash2,
                            "numeroSolicitud": str(num)};

                print("\n\n")
                
                #segunda solicitud, tocar en la lista de resultados:
                resp2 = browser.post(url+"/FindMarcaByNumeroSolicitud",
                                json=data2, headers={"Content-Type": "application/json"});
                
                resp2 = json.loads(resp2);
                #{'d': '{"ErrorMessage":"Información:\\n\\n Lo sentimos, ha excedido el límite de consultas. Vuelva a intentarlo más tarde."}'}
                if not "d" in resp2 or "ErrorMessage" in resp2["d"]:
                    print("Error json2", json.loads(resp2["d"])["ErrorMessage"]);
                    #posiblemente el proxy dado esta fallando:
                    failedProxies.append(use_proxy);
                    return 0;
                
                #print("resp2",resp2);
                print("-resultado");
        
        # se usara los proxies de manera ciclica
        # para (a,b,c) tomar a>b>c>a>b>c
        proxiesCycle = itertools.cycle(self.concurrentProxies);

        maxRegByThread = config["max_registros_by_conn"];

        for fromIndex in range(0, len(num_marks), maxRegByThread):
            # tomando desde numeros fromIndex hasta fromIndex+maxRegByThread indices:
            partNums = num_marks[fromIndex : fromIndex+maxRegByThread]; #slice de numeros

            #elegir un proxy y si esta en la lista de fallados seguir eligiendo siguiente:
            _firstProxy = nextProxy = next(proxiesCycle);
            while nextProxy in failedProxies:
                nextProxy = next(proxiesCycle);
                if nextProxy == _firstProxy:
                    print("Posiblemetne todos los proxies tienen fallas.")
                    break; #<- dio toda la vuelta al ciclo y no encontro sin fallos
            
            #lanzar numero limitado de conexiones en hilos a encargarse de la porcion de numeros:
            self.connThreads.startNewThread(_connectionThreadProxy, partNums, nextProxy);
            print("-nuevo thread", self.connThreads.count, "threads");



if __name__ == "__main__":

    hostname = open("target_site.txt", "r").read().strip(); #localhost:443
    args = open("regs.txt", "r").read().strip(); #123

    b = Scrap(hostname);

    print(b.searchByMark( args.splitlines() )); #123

    b.close();

