"""

Modulo para ejecutar y probar el programa

"""

import logging
import os
import time


#own modules:
from scrap import Scrap
from config import config



def main():

    """
     funcion para ejecutar el programa
    """

    logging.info("\n =========== Iniciado ===========")
    
    if not os.path.exists(config["dir_saves"]):
        try:
            os.makedirs(config["dir_saves"])
        except Exception as msg:
            logging.error(f"Error al crear la carpeta de resultados: {msg}")
            return

    #############

    if not os.path.exists("target_site.txt"):
        logging.error("El archivo target_site.txt no existe.")
        return

    try:
        fp = open("target_site.txt", "r")
        hostname = fp.read().strip() #localhost:443
        fp.close()
    except Exception as msg:
        logging.error("Al abrir el archivo target_site.txt")
        return
    
    ##############

    if not os.path.exists("target_regs.txt"):
        logging.error("El archivo target_regs.txt no existe.")
        return

    try:
        fp = open("target_regs.txt", "r")
        args = fp.read()
        fp.close()
    except:
        logging.error("Al leer el archivo target_regs.txt")
        return
    
    #convertimos el archivo cada linea a un numero valido, en una lista:
    arg_nums = [n.strip() for n in args.strip().splitlines() if n.strip().isdigit()]
    del args
    if not arg_nums:
        logging.info("Sin numeros en target regs.txt")
        return

    print(f"Cargados desde target_regs.txt {len(arg_nums)} numeros. ")

    filename_save = f"{config['dir_saves']}{config['filename_saves']}"

    #creamos el objeto principal:

    sc = Scrap(hostname)
    
    #medir el tiempo antes de empezar (solo por debug):
    first_time = time.time()

    results = sc.search_nmarks(arg_nums)

    seconds = time.time() - first_time
    print(f"\ntiempo tardado: {seconds:.01f} segundos.")
        

    succes = sc.save_result(filename_save, results)

    if succes:
        print(f"Los {len(results)} se guardaron en {filename_save} exitosamente")
    else:
        logging.error("Los resultados no se guardaron bien.")
        return

    return True #fin


if __name__ == "__main__":
    main()
    input("Pause")





