import requests
import time
import json
import os
from flask import Flask
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

TOKEN = "7539406137:AAEKVhg1M65H6Birs-RpCYObYeOAr6Yfq8g" #token acceso @BotFather 
chat_id = "@hechosesencialeschile"  # ID del grupo de Telegram
#chat_id = "6697147223" #id bot
timer = 30
fecha_old = ''

# Cargar empresas desde JSON
with open("empresas.json", "r") as archivo:
    Empresas = json.load(archivo)

app = Flask(__name__)

def scraping_loop():
    global fecha_old

    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            url = "https://www.cmfchile.cl/institucional/hechos/hechos_portada.php"
            respuesta = requests.get(url, headers=headers, timeout=10)

            if respuesta.status_code == 200:
                print("Iniciando scraping...")
                soup = BeautifulSoup(respuesta.text, "html.parser")
                hechos = soup.find_all("tr")[3]

                fecha = hechos.find_all("td")[0].text.strip()    
                documento = hechos.find_all("td")[1]
                link = str(documento.find_all("a")[0])
                archivo = 'https://www.cmfchile.cl' + link.split('"')[3].replace('amp;', '')
                entidad = hechos.find_all("td")[2].text.strip()
                materia = hechos.find_all("td")[3].text.strip()

                # Verificar si la empresa está en la lista y si es un hecho nuevo
                for valor in Empresas:
                    if fecha_old != fecha and str(valor) == str(entidad):
                        mensaje = f'NUEVO HECHO ESENCIAL\n\nFecha: {fecha}\nEmpresa: {entidad}\nMateria: {materia}\nDocumento: {archivo}'

                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                        data={"chat_id": chat_id, "text": mensaje})
                #response = requests.post(
                #        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                #        data={"chat_id": chat_id, "text": mensaje}
                #    )
                #print("Respuesta de Telegram:", response.status_code, response.text)
                print ("envio mensaje a telegram")
                fecha_old = fecha

            else:
                print('Error en la petición:', respuesta.status_code)

        except requests.RequestException as e:
            print(f"Error de conexión: {e}")

        time.sleep(timer)

def keep_awake():
    """ Envía un ping cada 5 minutos para evitar que Render apague la app. """
    while True:
        try:
            requests.get("https://he-ry71.onrender.com", timeout=5)
            print("Ping enviado para mantener la app activa")
        except requests.RequestException:
            print("Error al enviar el ping")
        time.sleep(300)  # 5 minutos

# Iniciar tareas en segundo plano
executor = ThreadPoolExecutor(max_workers=2)
executor.submit(scraping_loop)
executor.submit(keep_awake)
@app.route('/')
def home():
    return "Servicio de scraping en ejecución."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8082))  # Usa el puerto de Render o 8081 por defecto
    app.run(host='0.0.0.0', port=port)