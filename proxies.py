
"""

Modulo que se usara para leer y probar las proxies si funcionan

"""


from requests import Session;
from pool_threads import PoolThreads;


# lineas en archivo proxys.txt son ip:port
_proxylines = [line.strip() for line in open("proxies.txt", "r").readlines() if line.strip()];

proxies = \
[
    {"https":ip_port}       #{clave "https": valor "ip:port"}
    for ip_port in 
    _proxylines
    if ip_port[0] != "#"
];


def testProxies(proxies, maxthreads, user_agent, url, timeout):
    """ testeo opcional por si queremos proxies que funcionen bien,
        > borra las proxies de la lista que fallen un intento
    """

    threads = PoolThreads(maxthreads);

    def _threadTestProxy(proxy):
        bw = Session();
        bw.headers["User-Agent"] = user_agent;
        bw.proxies = proxy;
        try:
            resp = bw.get(url, timeout=timeout);
            resp.raise_for_status();
        except:
            proxies.remove(proxy); #por referencia borra


    print("Initial proxies:", len(proxies));

    for proxy in proxies:
        threads.startNewThread(_threadTestProxy, proxy);

    threads.waitThreads(wait_all=True);

    print("proxies Online:", len(proxies));



