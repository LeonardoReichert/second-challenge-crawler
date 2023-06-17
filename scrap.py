
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



import re;
import json;
import time;
from threading import Thread;

#own modules:
from config import config;
from browser import Browser;



class PoolThreads:
    def __init__(self, maxthreads):
        self.maxThreads = maxthreads;
        self.activeThreads = [];

    def waitThreads(self, wait_all=False):
        """ Espera mientras la cantidad de threads este al limite o espera todos """
        while (len(self.activeThreads) >= self.maxThreads) or (wait_all and self.activeThreads):
            for thread in self.activeThreads:
                if not thread.is_alive():
                    self.activeThreads.remove(thread);
            time.sleep(0.01); #10ms no estresa cpu

    def startNewThread(self, func, *args):
        """ Inicia un thread y lo pone en la lista de threads, pero espera si la lista esta en tope """
        self.waitThreads();
        thread = Thread(target=func, args=args);
        thread.start();
        self.activeThreads.append(thread);
    


class Scrap(Browser, PoolThreads):

    def __init__(self, hostname, maxthreads = config["max_threads"]):
        super().__init__(hostname);
        PoolThreads.__init__(self, maxthreads);

    def findFormFirstHashes(self, url):
        """ Primer paso, visitar link """
        
        html = self.get(url);
        if html == -1:
            return -1;

        form = re.findall("<form id=\"frmBuscarMarca\" action=\"\">(.+)</form>", html, flags=re.DOTALL);

        hashes = re.findall("setHash\('([a-z0-9]+)','([0-9]+)'\);", html, flags=re.DOTALL);
        
        hasTx = form and "name=\"txtSolicitud\"" in form[0];

        if not (hashes and form and hasTx):
            print("Faltan partes en el form")
            return -1;
    
        form = form[0];
        hashes = hashes[0];
        
        #a este punto no hay faltantes en el form (no es una variante)

        return hashes;

    def searchByMark(self, num_marks):
        """
        Busca, obtiene mediante Requests y por marcas lo necesario
        """
        
        url = "/Marca/BuscarMarca.aspx";
        hashes = self.findFormFirstHashes(url);
        if hashes == -1:
            print("Fallo la primer visita")
            return -1;

        lastHash = hashes[0];
        idw = hashes[1];
        #nota, pensar en cada cuanto renovar un hash

        def workThread(nmarks):
            """ El thread que se encargara de un num de consultas """
            
            for num in nmarks:
                
                data = {"LastNumSol":0,
                        "Hash":lastHash, "IDW":idw, "responseCaptcha":"",
                        "param1":num,"param17":"1"};
                data |= {f"param{n}":"" for n in range(2,17)}; #<-llenamos de datos iguales
                
                #primera valor poner numero en textinput:
                resp = self.post(url+"/FindMarcas",json=data,
                        headers={"Content-Type":"application/json"});
                if resp == -1:
                    print("No se ha podido hacer efectivamente el POST.");
                    return -1;
                resp = json.loads(resp);
                if not "d" in resp or "ErrorMessage" in resp["d"]:
                    print("Error json");
                    return 0;
            
                lastHash2 = json.loads(resp["d"])["Hash"];

        #        if len(resp) > 1:
        #           print(" SON MAS?")
        #          input("PAUSA")

                print(resp)

                data2 = {"IDW": idw, "Hash": lastHash2,
                            "numeroSolicitud": str(num)};

                print("\n\n")
                
                #tocar en la lista de resultados:
                resp2 = self.post(url+"/FindMarcaByNumeroSolicitud",
                                json=data2, headers={"Content-Type": "application/json"});
                
                resp2 = json.loads(resp2);
                print(resp2)

        #probando una ejecucion:
        
        self.startNewThread(workThread, num_marks);



hostname = open("target_site.txt", "r").read().strip(); #localhost:443
args = open("regs.txt", "r").read().strip(); #123


b = Scrap(hostname);

print(b.searchByMark( args.splitlines() )); #123

b.close();



