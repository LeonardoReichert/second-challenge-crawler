
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



import re
import json
import time
import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

#own modules:
from config import config
from proxies import proxies
from browser import Browser




class Scrap:

    def __init__(self, hostname,
                 concurrent_proxies = proxies,
                 max_threads = config["max_threads_connections"],
                 debug_errors = config["debug_errors_conn"],
                 ):
        
        if max_threads > len(concurrent_proxies):
            # si los proxies son menos, se usaran menos threads, por obviedad
            max_threads = len(concurrent_proxies)

        self.hostname = hostname
        self.concurrent_proxies = concurrent_proxies
        self._debug_errors = debug_errors
        self.max_threads = max_threads

        self.lock_debug = Lock()


    def _print_progress(self, allnumbers, completeds):
        """ solo para Mostrar el progreso """
        with self.lock_debug:
            # - sincronizado -
            progress = len(completeds) / len(allnumbers) * 100.0
            print(f"\r {progress:.02f}% {len(completeds)}:{len(allnumbers)} progreso completado...", end="")


    def debug_errors(self, *objs, **kwargs):
        #aun me falta mejorar esta funcionalidad con logs
        if self._debug_errors:
            print(*objs, **kwargs)
        
    
    def find_form_first_hashes(self, browser, sub_url):
        """ Primer paso, visitar link, obtener primeros hashes """
        
        html = browser.get(sub_url)
        if html == -1:
            return -1

        form = re.findall("<form id=\"frmBuscarMarca\" action=\"\">(.+)</form>", html, flags=re.DOTALL)

        hashes = re.findall("setHash\('([a-z0-9]+)','([0-9]+)'\)", html, flags=re.DOTALL)
        
        have_txt = form and "name=\"txtSolicitud\"" in form[0]

        if not (hashes and form and have_txt):
            # esto no paso nunca
            print("Faltan partes en el form")
            return -1

        hashes = hashes[0]
        
        #a este punto no hay faltantes en el form (esto no es una variante)
        return hashes


    def search_nmarks(self, num_marks, exclude_invalid_numbers=True):
        """
        Busca, obtiene mediante Requests y por numeros lo necesario,
        devuelve un diccionario de claves numero con valores resultado solicitad.
        """

        #bien los parametros antes de comenzar:
        if not type(num_marks) in (list, tuple):
            raise Exception("Error -num_marks is not a tuple or list")
        
        #hacemos una copia y exceptuamos los repetidos:
        first_length = len(num_marks)
        num_marks = list(set(num_marks))
        repeateds = len(num_marks) - first_length
        if repeateds > 0:
            print(f"Repetidos: {repeateds}.")

        #el resultado:
        completeds = {}


        def task_thread_connections():
            """ threads que se encargan por medio de conexiones y proxies, de los numeros.
                Varias veces elige un nuevo proxy, y una porcion de numeros para ese proxy,
                para cada numero intenta un resultado.
            """

            sub_url = "/Marca/BuscarMarca.aspx"
        
            while (len(completeds) < len(num_marks)):

                #elegimos el siguiente proxy:
                with lockvars:
                    # - sincronizado -
                    use_proxy = next(proxies_cycle)

                #conexion con o sin proxy, independiente del resto:
                browser = Browser(self.hostname, use_proxy)
                #visitamos la pagina, lo primero:
                hashes = self.find_form_first_hashes(browser, sub_url)

                if hashes == -1:
                    self.debug_errors("Fallo la primer visita")
                    continue
                    
                last_hash, idw = hashes
                
                while len(completeds) <= len(num_marks):

                    #esperar un poco por consulta?:
                    if config["wait_seconds_by_query"]:
                        time.sleep(config["wait_seconds_by_query"])
                    
                    #elegimos siguiente numero del ciclo, si no fue completado:
                    with lockvars:
                        # - sincronizado -
                        num = next(numb_cycle)
                        while num in completeds:
                            num = next(numb_cycle)
                            if len(completeds) >= len(num_marks):
                                #thread off, evitamos bucle infinito si estan todos completados
                                return
                    
                    #preparar campo numero:
                    data = {"LastNumSol":0,
                            "Hash":last_hash, "IDW":idw, "responseCaptcha":"",
                            "param1":num,"param17":"1"}
                    #llenamos de datos iguales:
                    data |= {f"param{n}":"" for n in range(2,17)}
                    
                    #enviar numero:
                    resp = browser.post(sub_url+"/FindMarcas",json=data,
                            headers={"Content-Type":"application/json"})
                    if resp == -1:
                        self.debug_errors("No se ha podido hacer efectivamente el POST.")
                        break #<- siguiente conexion
                    resp = json.loads(resp)

                    if not resp or not "d" in resp:
                        #posiblemente la conexion actual ya no funciona como queremos
                        self.debug_errors("Error json1", json.loads(resp["d"]))
                        #siguiente conexion:
                        break

                    resp["d"] = json.loads(resp["d"])

                    if not "Marcas" in resp["d"] or not resp["d"]["Marcas"]:
                        #no existe la busqueda...
                        completeds[num] = None
                        self._print_progress(num_marks, completeds)
                        #siguiente numero:
                        continue

                    last_hash = resp["d"]["Hash"]

                    #preparamos segunda solicitud:
                    data2 = {"IDW": idw, "Hash": last_hash,
                                "numeroSolicitud": str(num)}
                    
                    #segunda solicitud, tocar en la lista de resultados:
                    resp2 = browser.post(sub_url+"/FindMarcaByNumeroSolicitud",
                                    json=data2, headers={"Content-Type": "application/json"})
                    if resp2 == -1:
                        self.debug_errors("No se ha podido hacer efectivamente el POST.")
                        #siguiente conexion:
                        break

                    resp2 = json.loads(resp2)
                    if not "d" in resp2:
                        #siguiente conexion, posiblemente esta conexion no funciona bien
                        break
                    
                    resp2["d"] = json.loads(resp2["d"])

                    if "ErrorMessage" in resp2["d"]:
                        #print("resp2 err", resp2)
                        msg = resp2["d"]["ErrorMessage"]
                        if "no existe" in msg:
                            #continuamos, no existe el num:
                            completeds[num] = None
                            self._print_progress(num_marks, completeds)
                            #siguiente numero:
                            continue
                        #elif re.search("excedido el l.mite", msg, flags=re.DOTALL):
                            #mensaje desde el servidor que se ha caido la solicitud
                            #break # <- siguiente conexion  #return 0
                        #siguiente conexion:
                        break
                    
                    last_hash = resp2["d"]["Hash"]

                    completeds[num] = self._filter_result(resp2)

                    self._print_progress(num_marks, completeds)

            #final de thread
            return
        
        # se usara los proxies de manera ciclica:
        # para (a,b,c) toma a>b>c>a>b>c
        proxies_cycle = itertools.cycle(self.concurrent_proxies)
        #tambien los numeros:
        numb_cycle = itertools.cycle(num_marks)
        
        #para sincronizar el uso de proxies_cycle y numb_cycle cuando usar item = next(cycle)
        #solo por seguridad:
        lockvars = Lock()

        pool_threads = ThreadPoolExecutor(self.max_threads)

        #lanzar la cantidad de hilos con vida indeterminada a encargarse continuamente de
        # los proxies y de numeros:
        for i in range(self.max_threads):
            pool_threads.submit(task_thread_connections)
            print(f"\r {i+1} threads lanzados", end="")
        print("")

        #esperar todos los threads:
        pool_threads.shutdown()
        
        print("\nterminados", len(completeds), "resultados.")

        #quitamos los invalidos, si es necesario:
        if exclude_invalid_numbers:
            count_invalids = 0
            for num in list(completeds.keys()):
                if completeds[num] == None:
                    #remove invalid number
                    del completeds[num]
                    count_invalids += 1
            
            if count_invalids:
                print(f"{count_invalids} invalidos. Resultado: {len(completeds)} validos.")
        
        return completeds


    def _filter_result(self, item_json):
        """ Devuelve lo necesario para cada resultado, segun la interpretacion de los requisitos """

        try:
            instancias = item_json["d"]["Marca"]["Instancias"]
        except KeyError as _msg:
            #nunca paso
            open("warnings.log", "a").write("\n"+str(_msg)+"\n"+str(item_json)+"\n")

        result = {"Observada_de_Fondo": False,
                  "Fecha_Observada_Fondo": None,
                  "Apelaciones": False,
                  "IPT": False,
                   }

        for dict_inst in instancias:
            if dict_inst["EstadoDescripcion"] == "Resoluci\u00f3n de observaciones de fondo de marca":
                result["Observada_de_Fondo"] = True
                result["Fecha_Observada_Fondo"] = dict_inst["Fecha"]
                continue
            
            if "Recurso de apelacion" in dict_inst["EstadoDescripcion"]:
                result["Apelaciones"] = True

            if "IPT" in dict_inst["EstadoDescripcion"] or "IPTV" in dict_inst["EstadoDescripcion"]:
                result["IPT"] = True
        
        return result
            
    def save_result(self, filename, results, encoding=config["encoding"]):
        
        try:
            with open(filename, "w", encoding=encoding, errors="replace") as fp:
                #fp.write(str(res) + "\n\n")
                json.dump(results,fp)
            return True
        except Exception as msg:
            print(f"Error {msg}")
        
        return False


def main():

    print(
        """

    === Iniciado ===

        """
    )

    if not os.path.exists(config["dir_saves"]):
        try:
            os.makedirs(config["dir_saves"])
        except Exception as msg:
            print(f"Error al crear la carpeta de resultados: {msg}")
            return

    #############

    if not os.path.exists("target_site.txt"):
        print("Error: El archivo target_site.txt no existe.")
        return

    try:
        fp = open("target_site.txt", "r")
        hostname = fp.read().strip() #localhost:443
        fp.close()
    except Exception as msg:
        print("Error al abrir el archivo target_site.txt")
        return
    
    ##############

    if not os.path.exists("target_regs.txt"):
        print("Error: El archivo target_regs.txt no existe.")
        return

    try:
        fp = open("target_regs.txt", "r")
        args = fp.read()
        fp.close()
    except:
        print("Error al leer el archivo target_regs.txt")
        return
    
    #convertimos el archivo cada linea a un numero valido, en una lista:
    arg_nums = [n.strip() for n in args.strip().splitlines() if n.strip().isdigit()]
    del args
    if not arg_nums:
        print("Sin numeros en target regs.txt")
        return

    print(f"Cargados desde target_regs.txt {len(arg_nums)} numeros. ")

    filename_save = f"{config['dir_saves']}{config['filename_saves']}"

    #creamos el objeto principal:

    sc = Scrap(hostname)
    
    results = sc.search_nmarks(arg_nums)

    succes = sc.save_result(filename_save, results)

    if succes:
        print(f"Los {len(results)} se guardaron en {filename_save} exitosamente")
    else:
        print("Los resultados no se guardaron bien.")
        return

    return True #fin


if __name__ == "__main__":
    main()
    input("Pause")

