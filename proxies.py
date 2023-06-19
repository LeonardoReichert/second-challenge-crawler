
"""

Modulo que se usara para leer y probar las proxies si funcionan

"""


from requests import Session;
from pool_threads import PoolThreads;
from config import config;


# lineas en archivo proxys.txt son ip:port
_proxylines = [line.strip() for line in open("proxies.txt", "r").readlines() if line.strip()];

proxies = \
[
    {"https":ip_port}       #{clave "https": valor "ip:port"}
    for ip_port in 
    _proxylines
    if ip_port[0] != "#"
];


def _testProxies(proxies, maxthreads, user_agent, url, timeout):
    """ testeo opcional por si queremos proxies que funcionen bien,
        > borra las proxies de la lista que fallen un intento
    """

    threads = PoolThreads(maxthreads);

    countProxies = len(proxies);
    countTested = 0;
    def _threadTestProxy(proxy):
        nonlocal countTested;

        bw = Session();
        bw.headers["User-Agent"] = user_agent;
        bw.proxies = proxy;
        try:
            resp = bw.get(url, timeout=timeout);
            resp.raise_for_status();
        except:
            proxies.remove(proxy); #por referencia borra

        countTested += 1;
        print(f"\r testing proxies {countTested}/{countProxies}", end="");

    print("=== Testing proxies === ");
    print("initial proxies:", len(proxies));

    for proxy in proxies:
        threads.startNewThread(_threadTestProxy, proxy);

    threads.waitThreads(wait_all=True);

    print("\nproxies on:", len(proxies));




#descargar proxies:
#las proxies se someteran a prueba si se establece la opcion de hacerlo:
if config["_proxies_need_prevtest"]:
    _testProxies(proxies, config["_threads_prevtest_proxy"],
                         config["user_agent"],
                         open("target_site.txt", "r").read(),
                         timeout=10,
                        );
    

    #for proxy in proxies:
    #    print(proxy["https"]);
    

