
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



import re
import json
import time
import itertools
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import logging



#own modules:
from config import config
from proxies import proxies
from browser import Browser




class Scrap:
    """
        Clase donde se implementa la idea principal
        Ejemplo:
        >>> s = Scrap(hostname)
        >>> result = s.search_nmarks(numbers)
        >>> s.save_result("result.json", result)
    """
    def __init__(self, hostname,
                        concurrent_proxies = proxies.copy(),
                        max_threads = config["max_threads_connections"],
                        debug_conn_errors = config["debug_errors_conn"],
                        ):
        
        if len(concurrent_proxies) == 0:
            # no se especificaron proxies..
            logging.error("Sin proxies el programa no puede correr, configurar proxies.txt")
            raise Exception("program need proxies")
        
        if max_threads > len(concurrent_proxies):
            # si los proxies son menos, se usaran menos threads
            max_threads = len(concurrent_proxies)
            logging.warning("Configuracion de threads totales es superior a los proxies, se usaran menos")

        self.hostname = hostname
        self.concurrent_proxies = concurrent_proxies
        self._debug_conn_errors = debug_conn_errors
        self.max_threads = max_threads

        self.lock_debug = Lock()


    def _print_progress(self, allnumbers, completeds):
        """ solo para Mostrar el progreso """
        with self.lock_debug:
            # - sincronizado -
            progress = len(completeds) / len(allnumbers) * 100.0
            print(f"\r {progress:.02f}% {len(completeds)}:{len(allnumbers)} progreso completado...", end="")


    def debug_conn_errors(self, message):
        """ Se encarga de los logs de errores de conexion molestos """
        if self._debug_conn_errors:
            # solo si se desea se captar estos errores
            with self.lock_debug:
                # - sincronizado -
                logging.error(message)

    
    def _find_form_first_hashes(self, browser, sub_url):
        """ Primer paso, visitar link, obtener primeros hashes """
        
        html = browser.get(sub_url)
        if html == -1:
            return -1

        form = re.findall("<form id=\"frmBuscarMarca\" action=\"\">(.+)</form>", html, flags=re.DOTALL)

        hashes = re.findall("setHash\('([a-z0-9]+)','([0-9]+)'\)", html, flags=re.DOTALL)
        
        have_txt = form and "name=\"txtSolicitud\"" in form[0]

        if not (hashes and form and have_txt):
            # esto no paso nunca
            logging.warning("Faltan partes en el form")
            return -1

        hashes = hashes[0]
        
        #a este punto no hay faltantes en el form (esto no es una variante)
        return hashes


    def search_nmarks(self, num_marks, exclude_invalid_numbers=True):
        """
         Busca, obtiene mediante Requests y por numeros lo necesario,
        devuelve un diccionario de claves numero con valores resultado solicitad.
        Parametros:
            - num_marks: lista de numeros.
            - exclude_invalid_numbers: boleano, excluir del resultado los
                                        numeros que no existan.
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
            """ Threads que se encargan por medio de conexiones y proxies, de los numeros.
                Continuamente: elige un nuevo proxy y establece una conexion, y para esa
                conexion elige numeros, para cada numero intenta un resultado.
            """

            sub_url = "/Marca/BuscarMarca.aspx"
        
            while (len(completeds) < len(num_marks)):

                #elegimos el siguiente proxy:
                with lockvars:
                    # - sincronizado -
                    use_proxy = next(proxies_cycle)

                #browser con proxy:
                browser = Browser(self.hostname, use_proxy)

                #visitamos la pagina, lo primero:
                hashes = self._find_form_first_hashes(browser, sub_url)

                if hashes == -1:
                    #fallo la primera visita, siguiente proxy:
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
                    #lo llenamos de datos iguales:
                    data |= {f"param{n}":"" for n in range(2,17)}
                    
                    #consultar numero:
                    resp = browser.post(sub_url+"/FindMarcas",json=data,
                            headers={"Content-Type":"application/json"})
                    if resp == -1:
                        self.debug_conn_errors(f"No se ha podido hacer el 1er POST.")
                        #siguiente conexion:
                        break
                    resp = json.loads(resp)

                    if not resp or not "d" in resp:
                        #posiblemente la conexion actual ya no funciona como queremos
                        self.debug_conn_errors(f"Error json de numero {num}, no hay clave 'd' en json")
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
                        self.debug_conn_errors("No ha podido hacer efectivamente el 2do POST.")
                        #siguiente conexion:
                        break

                    resp2 = json.loads(resp2)
                    if not "d" in resp2:
                        #siguiente conexion, posiblemente esta conexion no funciona bien
                        break
                    
                    resp2["d"] = json.loads(resp2["d"])

                    if "ErrorMessage" in resp2["d"]:
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

        print("terminados", len(completeds), "resultados.")

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
        except KeyError:
            #nunca paso
            logging.warning(f'error de tipo KeyError en json "{item_json}"')

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
        """ Guarda el resultado de la busqueda en un archivo .json """

        try:
            with open(filename, "w", encoding=encoding, errors="replace") as fp:
                json.dump(results,fp)
            return True
        except Exception as msg:
            logging.error(f"No se ha podido guardar {filename}, mensaje: {msg}")
        
        return False

