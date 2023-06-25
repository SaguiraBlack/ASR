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

# Email vars
mailsender = "josefina10969@gmail.com"
mailreceip = "josefina10969@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = 'hhsjqmzngogigntc'

async def enableEmail():
    await asyncio.sleep(60*5)  # Espera 5 segundos
    canSendEmail = True
    print("El tiempo ha pasado")


def sendEmail(nombre, tipo, valor):
    global canSendEmail
    if canSendEmail:
        canSendEmail = False
        asyncio.gather(enableEmail())
        msg = MIMEMultipart()
        msg['Subject'] = "Alerta de rendimiento"
        msg['From'] = mailsender
        msg['To'] = mailreceip
        body = f'El dispositivo {nombre} ha superado el umbral de {tipo} con un valor de {valor}'
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

    else:
        print("No se puede enviar el correo")

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

while 1:
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
            
            if cargaCPU > 30 or cargaCPU > 50 or cargaCPU > 80:
                sendEmail(nombre, "CPU", cargaCPU)
            if memoryUsage > 30 or memoryUsage > 50 or memoryUsage > 80:
                sendEmail(nombre, "RAM", memoryUsage)
            if diskUsage > 30 or diskUsage > 50 or diskUsage > 90:
                sendEmail(nombre, "Disco", diskUsage)

            valor = "N:" + str(cargaCPU) + ":" + str(memoryUsage)+ ":" +str(diskUsage)

            # Actualizar la base de datos RRD correspondiente con el valor obtenido
            rrdtool.update(rrdpath, valor)
            rrdtool.dump(rrdpath, xmlpath)

            print(nombre + " - " + valor)
            time.sleep(5)

        except Exception as e:
            if e == KeyboardInterrupt:
                raise Exception("Se canceló la ejecución del programa...")
            print("Error: " + str(e))
