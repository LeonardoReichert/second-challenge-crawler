
"""

Aqui se desarrolla las acciones del desafio, scrap

"""



from browser import Browser;

import re;
import json;
import time;



class Scrap(Browser):

    def searchByMark(self, num_mark):
        """
        Busca, obtiene mediante Requests y por marcas lo necesario
        """

        url = "/Marca/BuscarMarca.aspx";
        
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
        
        data = {"LastNumSol":0,
                "Hash":hashes[0], "IDW":hashes[1], "responseCaptcha":"",
                "param1":num_mark,"param17":"1"};
        data |= {f"param{n}":"" for n in range(2,17)}; #<-llenamos de datos iguales
        
        resp = self.post(url+"/FindMarcas",json=data,headers={"Content-Type":"application/json"});
        if resp == -1:
            print("No se ha podido hacer efectivamente el POST.");
            return -1;
        resp = json.loads(resp);
        print(resp)

        data2 = {"IDW": hashes[1], "Hash": json.loads(resp["d"])["Hash"],
                    "numeroSolicitud": str(num_mark)};

        print("\n\n")
        
        #tocar en la lista de resultados:
        resp2 = self.post(url+"/FindMarcaByNumeroSolicitud",
                         json=data2, headers={"Content-Type": "application/json"});
        
        resp2 = json.loads(resp2);
        print(resp2)


hostname = open("target_site.txt", "r").read().strip(); #localhost:443
num = open("regs.txt", "r").read().strip(); #123


b = Scrap(hostname);
print(b.searchByMark(num)); #123
b.close();


