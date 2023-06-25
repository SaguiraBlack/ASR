import rrdtool
import os

if not os.path.exists(os.path.join(os.getcwd(), "RRD")):
    os.mkdir(os.path.join(os.getcwd(), "RRD"))

# Leer el archivo de dispositivos
with open("dispositivos.txt", "r") as f:
    lineas = f.readlines()

# Iterar sobre las líneas del archivo de dispositivos
for linea in lineas:
    # Dividir la línea en los campos separados por comas
    campos = linea.strip().split(",")

    # Extraer los valores de los campos
    nombre = campos[0]
    comunidad = campos[1]
    version = campos[2]
    puerto = campos[3]
    direccion = campos[4]

    # Generar el nombre del archivo RRD basado en el nombre del dispositivo
    nombre_rrd = nombre + ".rrd"

    ret = rrdtool.create(os.path.join(os.getcwd(), "RRD", nombre_rrd),
                     "--start", "N", "--step", "60",
                     "DS:ifInMulticastPkts:COUNTER:120:U:U",
                     "DS:ipInReceives:COUNTER:120:U:U",
                     "DS:icmpOutEchoReps:COUNTER:120:U:U",
                     "DS:tcpOutSegs:COUNTER:120:U:U",
                     "DS:udpInOverflows:COUNTER:120:U:U",
                     "RRA:AVERAGE:0.5:1:60",
                     "RRA:AVERAGE:0.5:5:24",
                     "RRA:AVERAGE:0.5:10:18")

    if ret:
        print("Error al crear el archivo RRD para el dispositivo: " + nombre)
    else:
        print("Archivo RRD creado exitosamente para el dispositivo: " + nombre)