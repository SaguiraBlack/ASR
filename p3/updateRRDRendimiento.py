import os
from snmp import consultaSNMP
import rrdtool
import time
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

# Nombre del archivo de dispositivos
dispositivosFile = os.path.join(os.getcwd(), "dispositivos.txt")
rrdpath = os.path.join(os.getcwd(), "p3", "rendimiento.rrd")
xmlpath = os.path.join(os.getcwd(), "p3", "rendimiento.xml")
imgpath = os.path.join(os.getcwd(), "graficas/")
canSendEmail = True
alertSent = False
# Email vars
mailsender = "josefina10969@gmail.com"
mailreceip = "josefina10969@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'vcnrhkigbrsktfyx'

def grafica(filename, time_start, time_end, title, var, db, name):
    if not os.path.exists(os.path.join(os.getcwd(), "graficas")):
        os.mkdir(os.path.join(os.getcwd(), "graficas"))

    try:
        rrdtool.graph(filename, "--start", str(time_start), "--end", str(time_end),
                      "--vertical-label=Porcentaje (%)", 
                      "--lower-limit", "0", 
                      "--upper-limit", "100",
                      "--title=" + title,
                      "--alt-y-grid",
                      "DEF:variable=" + db + ":" + var + ":AVERAGE",
                      "CDEF:escala=variable,1,*",
                      "LINE3:escala#0000FF:" + name)
        return "OK"
    except Exception as e:
        print(e)
        return "Error al generar la grafica :" + e.args[0]
    
def generarGraficaRendimiento ():
    datos = [
        ["cpu", "cpu.png", "Porcentaje de uso de CPU"],
        ["ram", "ram.png", "Porcentaje de uso de RAM"],
        ["disk", "disk.png", "Porcentaje de uso de disco"],
    ]
    for dato in datos:
        # Obtener el timestamp actual
        now = int(time.time())
        # Restar 10 minutos (600 segundos)
        start = now - 600

        grafica(
            os.path.join(os.getcwd(), "graficas", dato[1]),
            start, now, dato[2],
            dato[0],
            os.path.join(os.getcwd(), "p3", "rendimiento.rrd"),
            dato[2])
    print("Generando graficas de rendimiento...")


def sendEmail(nombre, tipo, valor, message):
    global canSendEmail
    global alertSent
    messages = [
        'primer umbral del 30%',
        'segundo umbral de 50%',
        'tercer umbral de 80%'
    ]
    if canSendEmail:
        generarGraficaRendimiento()
        alertSent = True
        # asyncio.gather(enableEmail())
        msg = MIMEMultipart()
        msg['Subject'] = "Alerta de rendimiento"
        msg['From'] = mailsender
        msg['To'] = mailreceip
        body = f'ATENCIÓN. El dispositivo {nombre} ha superado el {messages[message]} de {tipo} con un valor de {valor}'
        msg.attach(MIMEText(body, 'plain'))
        print(imgpath+tipo.lower()+'.png')
        fp = open(imgpath+tipo.lower()+'.png', 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        s = smtplib.SMTP(mailserver)

        s.starttls()
        # Login Credentials for sending the mail
        s.login(mailsender, password)

        s.sendmail(mailsender, mailreceip, msg.as_string())
        s.quit()
        print("Correo Enviado")
    else:
        print("Aun no se puede enviar correo")
 
async def read_info():
    global alertSent
    global canSendEmail
    # Realizar consultas SNMP para cada dispositivo
    for dispositivo_info in dispositivos:
        try:
            # Obtener información del dispositivo
            nombre = dispositivo_info[0]
            comunidad = dispositivo_info[1]
            version = dispositivo_info[2]
            puerto = dispositivo_info[3]
            direccion = dispositivo_info[4]

            # Realizar consultas SNMP para obtener los valores de las variables de interés
            cargaCPU = int(consultaSNMP(comunidad, direccion,'1.3.6.1.2.1.25.3.3.1.2.196608'))

            memoryUsage = int(consultaSNMP(comunidad, direccion,'1.3.6.1.2.1.25.2.3.1.6.1'))
            totalMemory = int(consultaSNMP(comunidad, direccion,'1.3.6.1.4.1.2021.4.5.0'))
            memoryUsage = round((memoryUsage * 100) / totalMemory, 2)

            diskUsage = int(consultaSNMP(comunidad, direccion,'1.3.6.1.2.1.25.2.3.1.6.36'))
            totalDisk = int(consultaSNMP(comunidad, direccion,'1.3.6.1.2.1.25.2.3.1.5.36'))
            diskUsage = round((diskUsage * 100) / totalDisk, 2)
            #ifInMulticastPkts = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.31.1.1.1.2.1")

            # Verificar si se obtuvieron todos los valores exitosamente
            if cargaCPU == "" or memoryUsage == "" or diskUsage == "":
                raise Exception("Error al hacer las consultas SNMP en el dispositivo: " + nombre)
            
            if cargaCPU > 30:
                sendEmail(nombre, "CPU", cargaCPU, 0)
            if cargaCPU > 50:
                sendEmail(nombre, "CPU", cargaCPU, 1)
            if cargaCPU > 80:
                sendEmail(nombre, "CPU", cargaCPU, 2)    
            if memoryUsage > 30:
                sendEmail(nombre, "RAM", memoryUsage, 0)
            if memoryUsage > 50:
                sendEmail(nombre, "RAM", memoryUsage, 1)
            if memoryUsage > 80:
                sendEmail(nombre, "RAM", memoryUsage, 2)
            if diskUsage > 30:
                sendEmail(nombre, "Disco", diskUsage, 0)
            if diskUsage > 50:
                sendEmail(nombre, "Disco", diskUsage, 1)
            if diskUsage > 90:
                sendEmail(nombre, "Disco", diskUsage, 2)
            if alertSent:
                canSendEmail = False

            valor = "N:" + str(cargaCPU) + ":" + str(memoryUsage)+ ":" +str(int(diskUsage))

            # Actualizar la base de datos RRD correspondiente con el valor obtenido
            rrdtool.update(rrdpath, valor)
            rrdtool.dump(rrdpath, xmlpath)

            print(nombre + " - " + valor)
            await asyncio.sleep(5)

        except Exception as e:
            if e == KeyboardInterrupt:
                raise Exception("Se canceló la ejecución del programa...")
            print("Error: " + str(e))


# Leer la información de dispositivos desde el archivo
dispositivos = []
with open(dispositivosFile, "r") as file:
    for line in file:
        # Eliminar el carácter de nueva línea y dividir por comas
        dispositivo_info = line.strip().split(",")
        # Asegurarse de que se hayan proporcionado todos los campos
        if len(dispositivo_info) != 5:
            raise Exception("Error: El archivo de dispositivos tiene un formato incorrecto.")
        dispositivos.append(dispositivo_info)
   
async def periodic():
    print("periodic")
    global canSendEmail
    await asyncio.sleep(60*5)  # Espera 5 minutos
    canSendEmail = True
    print("El tiempo ha pasado")
    #while True:
    #    print('periodic')
    #    await asyncio.sleep(1)


async def handler():
    while True:
        if canSendEmail:
            asyncio.gather(
                periodic(),
            )
        await read_info()


asyncio.run(handler())
