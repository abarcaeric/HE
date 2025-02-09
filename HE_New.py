import requests
import threading
import time
import sched

from bs4 import BeautifulSoup
#from telegram import Update
#from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

scheduler = sched.scheduler(time.time, time.sleep)

TOKEN = "7539406137:AAEKVhg1M65H6Birs-RpCYObYeOAr6Yfq8g"
#chat_id = "6697147223"
chat_id = "@hechosesencialeschile"
timer = 60
fecha_old = ''

def getHE():
    global fecha_old
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = "https://www.cmfchile.cl/institucional/hechos/hechos_portada.php"
    respuesta = requests.get(url, headers=headers)
    if respuesta.status_code == 200:
        soup = BeautifulSoup(respuesta.text, "html.parser")

        hechos = soup.find_all("tr")[3]

        fecha = hechos.find_all("td")[0].text.strip()    
        documento  = hechos.find_all("td")[1]
        link = str(documento.find_all("a")[0])
        archivo = 'https://www.cmfchile.cl' + link.split('"')[3].replace('amp;','')
        entidad = hechos.find_all("td")[2].text.strip()
        materia = hechos.find_all("td")[3].text.strip()
        #print (fecha)
        #print (fecha_old)
        if fecha_old != fecha:
            mensaje = 'NUEVO HECHO ESENCIAL\n\nFecha : ' + str(fecha) + '\nEmpresa : ' + str(entidad) + '\nMateria : ' + str(materia) +  '\nDocumento : ' + str(archivo) 
                 
            requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
                data = {"chat_id": chat_id, "text": mensaje})
            fecha_old = fecha
            print ('ENVIO')
            scheduler.enter(timer, 1, getHE)  # Vuelve a ejecutar en los segundos que este definido en la variabke timer
    
        else: 
            print ('NO ENVIO')
            scheduler.enter(timer, 1, getHE)

    else:
        print ('Hubo un error en la peticion')
        scheduler.enter(timer, 1, getHE)

scheduler.enter(1, 1, getHE)  # Primera ejecución en 1 segundos
scheduler.run()
