import os
from snmp import consultaSNMP
import rrdtool
import time

# Nombre del archivo de dispositivos
dispositivos_file = "dispositivos.txt"

# Leer la información de dispositivos desde el archivo
dispositivos = []
with open(dispositivos_file, "r") as file:
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
            ifInMulticastPkts = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.31.1.1.1.2.1")

            ipInReceives = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.4.3.0")

            icmpOutMsgs = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.5.26.0")

            tcpOutSegs = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.6.11.0")

            udpNoPorts = consultaSNMP(comunidad, direccion, "1.3.6.1.2.1.7.3.0")


            # Verificar si se obtuvieron todos los valores exitosamente
            if ifInMulticastPkts == "" or ipInReceives == "" or icmpOutMsgs == "" or tcpOutSegs == "" or udpNoPorts == "":
                raise Exception("Error al hacer las consultas SNMP en el dispositivo: " + nombre)

            # Concatenar los valores en un string con formato N:<valor1>:<valor2>:...:<valorN>
            valor = "N:" + ifInMulticastPkts + ":" + ipInReceives + ":" + icmpOutMsgs + ":" + tcpOutSegs + ":" + udpNoPorts

            # Actualizar la base de datos RRD correspondiente con el valor obtenido
            rrdtool.update(os.path.join(os.getcwd(), "RRD", nombre + ".rrd"), valor)
            rrdtool.dump(os.path.join(os.getcwd(), "RRD", nombre + ".rrd"), os.path.join(os.getcwd(), "RRD", nombre + ".xml"))

            print(nombre + " - " + valor)

            time.sleep(1)

        except Exception as e:
            if e == KeyboardInterrupt:
                raise Exception("Se canceló la ejecución del programa...")
            print("Error: " + str(e))
