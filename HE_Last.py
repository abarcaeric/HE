import requests
import threading
import time
from flask import Flask
from bs4 import BeautifulSoup
import json
import os

TOKEN = "7539406137:AAEKVhg1M65H6Birs-RpCYObYeOAr6Yfq8g" #token acceso @BotFather 
#chat_id = "@hechosesencialeschile" #id grupo
chat_id = "6697147223" #id bot
timer = 30
fecha_old = ''

# Cargar el archivo JSON de empresas a tomar en cuenta
with open("empresas.json", "r") as archivo:
    Empresas = json.load(archivo)

app = Flask(__name__)

def scraping_loop():
    global fecha_old
    
    while True:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = "https://www.cmfchile.cl/institucional/hechos/hechos_portada.php"
        respuesta = requests.get(url, headers=headers)
        if respuesta.status_code == 200:
            print ("iniciando...")
            soup = BeautifulSoup(respuesta.text, "html.parser")

            hechos = soup.find_all("tr")[3]

            fecha = hechos.find_all("td")[0].text.strip()    
            documento  = hechos.find_all("td")[1]
            link = str(documento.find_all("a")[0])
            archivo = 'https://www.cmfchile.cl' + link.split('"')[3].replace('amp;','')
            entidad = hechos.find_all("td")[2].text.strip()
            materia = hechos.find_all("td")[3].text.strip()

            # Recorrer de las empresas
            for valor in Empresas:
                #if fecha_old != fecha and str(valor) == str(entidad):
                    mensaje = 'NUEVO HECHO ESENCIAL\n\nFecha : ' + str(fecha) + '\nEmpresa : ' + str(entidad) + '\nMateria : ' + str(materia) +  '\nDocumento : ' + str(archivo) 
                    
                    requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
                        data={"chat_id": chat_id, "text": mensaje})
                    fecha_old = fecha
        
            time.sleep(timer)
        else:
            print('Hubo un error en la peticion')
            time.sleep(timer)

# Iniciar el bucle de scraping en un hilo separado
threading.Thread(target=scraping_loop, daemon=True).start()

# Ruta de ejemplo para Flask
@app.route('/')
def home():
    return "Servicio de scraping en ejecución."

# Ejecutar Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))  # Usa el puerto de Render o 8081 por defecto
    app.run(host='0.0.0.0', port=port)