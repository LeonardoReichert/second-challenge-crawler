
"""

modulo que contruye el manejo de threads encapsulado

"""


import time;
from threading import Thread;


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
    
    @property
    def count(self):
        return len(self.activeThreads);
    



