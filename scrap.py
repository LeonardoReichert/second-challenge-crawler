
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



import re;
import json;
import time;
import itertools;
import os;

#own modules:
from config import config;
from proxies import proxies;
from browser import Browser;
from pool_threads import PoolThreads;




class Scrap:

    def __init__(self, hostname,
                 concurrent_proxies = proxies,
                 max_threads = config["max_threads_proxy"],
                 debugErrors = config["debug_errors_conn"],
                 maxregistros_peer_conn = config["maxregistros_peer_conn"]
                 ):

        self.hostname = hostname;
        self.connThreads = PoolThreads(max_threads);
        self.concurrentProxies = concurrent_proxies;
        self.maxregistros_peer_conn = maxregistros_peer_conn;
        self._debugErrors = debugErrors;

    
    def debugErrors(self, *objs, **kwargs):
        if self._debugErrors:
            print(*objs, **kwargs);
        
    
    def findFormFirstHashes(self, browser, url):
        """ Primer paso, visitar link """
        
        html = browser.get(url);
        if html == -1:
            return -1;

        form = re.findall("<form id=\"frmBuscarMarca\" action=\"\">(.+)</form>", html, flags=re.DOTALL);

        hashes = re.findall("setHash\('([a-z0-9]+)','([0-9]+)'\);", html, flags=re.DOTALL);
        
        hasTx = form and "name=\"txtSolicitud\"" in form[0];

        if not (hashes and form and hasTx):
            print("Faltan partes en el form");
            return -1;

        hashes = hashes[0];
        
        #a este punto no hay faltantes en el form (esto no es una variante)
        return hashes;


    def searchByMark(self, _num_marks, excludeInvalidNumbers=True):
        """
        Busca, obtiene mediante Requests y por numeros lo necesario,
        devuelve un diccionario de claves numero con valores resultado solicitad.
        """

        #bien los parametros antes de comenzar:
        if not type(_num_marks) in (list, tuple):
            raise Exception("Error-num_marks is not a tuple or list")
        
        #hacemos una copia y exceptuamos los repetidos:
        num_marks = list(set(_num_marks));
        repetidos = len(_num_marks) - len(num_marks);
        if repetidos > 0:
            print(f"Repetidos: {repetidos}")

        #el resultado:
        numsCompleteds = {};


        def _connectionThreadProxy(use_proxy):
            """ Conexion, proxy y thread que se encarga de una porcion de numeros solicitados """

            url = "/Marca/BuscarMarca.aspx";
        
            #conexion con o sin proxy, independiente del resto:
            browser = Browser(self.hostname, use_proxy);

            #visitamos la pagina, lo primero:
            hashes = self.findFormFirstHashes(browser, url);
            if hashes == -1:
                self.debugErrors("Fallo la primer visita");
                return -1;
                
            lastHash, idw = hashes;

            for _ in range(self.maxregistros_peer_conn):
                #tomamos siguiente numero del ciclo, si no fue completado:
                num = next(numbCycle);
                if num in numsCompleteds:
                    continue;

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
                    self.debugErrors("No se ha podido hacer efectivamente el POST.");
                    return -1;
                resp = json.loads(resp);

                if not resp or not "d" in resp:
                    #in resp or "ErrorMessage" in resp["d"]:
                    
                    #posiblemente la conexion actual ya no funciona como queremos
                    self.debugErrors("Error json1", json.loads(resp["d"]));
                    return 0;

                resp["d"] = json.loads(resp["d"]);

                if not "Marcas" in resp["d"] or not resp["d"]["Marcas"]:
                    #no existe la busqueda...
                    numsCompleteds[num] = None;
                    continue;

                lastHash = resp["d"]["Hash"];

                #preparamos segunda solicitud:
                data2 = {"IDW": idw, "Hash": lastHash,
                            "numeroSolicitud": str(num)};
                
                #segunda solicitud, tocar en la lista de resultados:
                resp2 = browser.post(url+"/FindMarcaByNumeroSolicitud",
                                json=data2, headers={"Content-Type": "application/json"});
                if resp2 == -1:
                    self.debugErrors("No se ha podido hacer efectivamente el POST.");
                    return -1;

                resp2 = json.loads(resp2);
                if not "d" in resp2:
                    #posiblemente esta conexion no funciona bien
                    return -1;
                
                resp2["d"] = json.loads(resp2["d"]);

                if "ErrorMessage" in resp2["d"]:
                    #print("resp2 err", resp2)
                    msg = resp2["d"]["ErrorMessage"];
                    if "no existe" in msg:
                        #continuamos, no existe el num, pero contiuamos con los demas
                        numsCompleteds[num] = None;
                        #print("no exite el registro");
                        continue;
                    elif re.search("excedido el l.mite", msg, flags=re.DOTALL):
                        #mensaje desde el servidor que se ha caido la solicitud
                        #print("se ha caido la solicitud en una conexion");
                        return 0;

                    #print("Error json2", resp2["d"]["ErrorMessage"]);
                    #posiblemente el proxy dado esta fallando:
                    return 0;
            
                lastHash = resp2["d"]["Hash"];
                #print("hash termina en ",lastHash)

                numsCompleteds[num] = self.getResult(resp2);

                progress = len(numsCompleteds) / len(num_marks) * 100.0;
                print(f"\r {progress:.02f}% {len(numsCompleteds)}:{len(num_marks)} resultados x{self.connThreads.count} proxys-threads.",
                                end="");
        
        # se usara los proxies de manera ciclica
        # para (a,b,c) tomar a>b>c>a>b>c
        proxiesCycle = itertools.cycle(self.concurrentProxies);
        numbCycle = itertools.cycle(num_marks);

        #mientras los completados sean menos que los solicitados:
        while len(numsCompleteds) < len(num_marks):
            
            #elegir un proxy siguiente:
            nextProxy = next(proxiesCycle);
                
            #lanzar numero limitado de conexiones en hilos a encargarse de la porcion de numeros:
            self.connThreads.startNewThread(_connectionThreadProxy, nextProxy);
                
            #print(f"\nhay {self.connThreads.count} threads\n");
        
        print(f"\nfinalizando {self.connThreads.count} threads...\n");
        self.connThreads.waitThreads(wait_all=True);
        print("terminados", len(numsCompleteds), "resultados");

        if excludeInvalidNumbers:
            countNunInvalids = 0;
            for num in list(numsCompleteds.keys()):
                if numsCompleteds[num] == None:
                    del numsCompleteds[num]; #remove invalid number
                    countNunInvalids += 1;
            
            if countNunInvalids:
                print(f"{countNunInvalids} invalidos. Resultado: {len(numsCompleteds)} validos.")
        
        return numsCompleteds;


    def getResult(self, item_json):
        """ Devuelve lo necesario para cada resultado, segun requisitos """

        try:
            instancias = item_json["d"]["Marca"]["Instancias"];
        except KeyError as _msg:
            #nunca paso
            open("warnings.log", "a").write("\n"+str(_msg)+"\n"+str(item_json)+"\n");

        result = {"Observada_de_Fondo": False,
                  "Fecha_Observada_Fondo": None,
                  "Apelaciones": False,
                  "IPT": False,
                   };

        for dictInst in instancias:
            if dictInst["EstadoDescripcion"] == "Resoluci\u00f3n de observaciones de fondo de marca":
                result["Observada_de_Fondo"] = True;
                result["Fecha_Observada_Fondo"] = dictInst["Fecha"];
                continue;
            
            if "Recurso de apelacion" in dictInst["EstadoDescripcion"]:
                result["Apelaciones"] = True;

            if "IPT" in dictInst["EstadoDescripcion"] or "IPTV" in dictInst["EstadoDescripcion"]:
                result["IPT"] = True;
        
        return result;
            
    def saveResult(self, filename, results, encoding=config["encoding"]):
        
        try:
            with open(filename, "w", encoding=encoding, errors="replace") as fp:
                #fp.write(str(res) + "\n\n");
                json.dump(results,fp);
            return True;
        except Exception as msg:
            print(f"Error {msg}");
        
        return False;


def main():

    print(
        """

    === Iniciado ===

        """
    );

    if not os.path.exists(config["dir_saves"]):
        try:
            os.makedirs(config["dir_saves"]);
        except Exception as msg:
            print(f"Error al crear la carpeta de resultados: {msg}");
            return;

    #############

    if not os.path.exists("target_site.txt"):
        print("Error: El archivo target_site.txt no existe.");
        return;

    try:
        fp = open("target_site.txt", "r");
        hostname = fp.read().strip(); #localhost:443
        fp.close();
    except Exception as msg:
        print("Error al abrir el archivo target_site.txt");
        return;
    
    ##############

    if not os.path.exists("target_regs.txt"):
        print("Error: El archivo target_regs.txt no existe.");
        return;

    try:
        fp = open("target_regs.txt", "r");
        args = fp.read();
        fp.close();
    except:
        print("Error al leer el archivo target_regs.txt");
        return;
    
    #convertimos el archivo cada linea a un numero valido, en una lista:
    argNums = [n.strip() for n in args.strip().splitlines() if n.strip().isdigit()];
    del args;
    if not argNums:
        print("Sin numeros en target regs.txt")
        return;

    print(f"Cargados desde target_regs.txt {len(argNums)} numeros. ");

    filenameSave = f"{config['dir_saves']}{config['filename_saves']}";

    #creamos el objeto principal:

    sc = Scrap(hostname);

    results = sc.searchByMark(argNums);

    succes = sc.saveResult(filenameSave, results);

    if succes:
        print(f"Los {len(results)} se guardaron en {filenameSave} exitosamente");
    else:
        print("Los resultados no se guardaron bien.")
        return;

    return True; #fin


if __name__ == "__main__":
    main();

