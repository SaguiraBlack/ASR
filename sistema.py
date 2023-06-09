## Tovar Espejo Mariana Josefina | 4CM14 | 2019630340 ##
## Practica 1 - Adquisicion de informacion ##

# imports
from pysnmp.hlapi import *
from fpdf import FPDF
import time
import os
from graphRRD import grafica

# Estados de la interfaz
estadosInterfaz = ['Activo', 'Inactivo', 'Prueba', 'Desconocido', 'Dormido', 'NoPresente', 'CapaInferiorInactiva']
datos = [
    ["ifInMulticastPkts", "ifIn.png", "Paquetes multicast de entrada"],
    ["ipInReceives", "ipIn.png", "Tráfico de entrada"],
    ["icmpOutEchoReps", "icmpOut.png", "Respuestas ICMP de salida"],
    ["tcpOutSegs", "tcpOut.png", "Paquetes TCP de salida"],
    ["udpInOverflows", "udpIn.png", "Paquetes UDP de entrada"]
]

# Desplegar menu principal
def menu():
    print("Sistema de Administración de Red")
    print("Tovar Espejo Mariana Josefina | 4CM14 | 2019630340")
    print("*****************************************************")
    print("Practica 1 - Adquisicion de informacion")
    print("1. Agregar dispositivo")
    print("2. Cambiar información de dispositivo")
    print("3. Eliminar dispositivo")
    print("4. Generar reporte")
    print("*****************************************************")
    print("Practica 2 - Administracion de contabilidad")
    print("5. Generar grafica")
    print("*****************************************************")
    print("Practica 3 - Administracion de rendimiento")
    print("6. Generar grafica")
    print("7. Salir")
    opcion = int(input("Ingresa una opcion: "))
    return opcion


# Función main
def main():
    opcion = menu()
    while opcion != 7:
        if opcion == 1:
            agregarDispositivo()
        elif opcion == 2:
            cambiarDispositivo()
        elif opcion == 3:
            eliminarDispositivo()
        elif opcion == 4:
            generarReporte()
        elif opcion == 5:
            for dato in datos:
                # Obtener el timestamp actual
                now = int(time.time())
                # Restar 10 minutos (600 segundos)
                start = now - 600

                grafica(
                    os.path.join(os.getcwd(), "graficas", dato[1]),
                    start, now, dato[2],
                    dato[0],
                    os.path.join(os.getcwd(), "RRD", "1.rrd"),
                    dato[2])
        elif opcion == 6:
            generarGraficaRendimiento()
        else:
            print("Opcion invalida")
        opcion = menu()


# Agregar dispositivo
def agregarDispositivo():
    print("Agregar dispositivo")
    print("********************")
    nombre = input("Nombre del dispositivo: ")
    comunidad = input("Comunidad: ")
    version = input("Version SNMP: ")
    puerto = input("Puerto: ")
    direccion = input("Direccion IP: ")
    archivo = open("dispositivos.txt","a")
    archivo.write(nombre + "," + comunidad + "," + version + "," + puerto + "," + direccion + "\n")
    archivo.close()
    print("Dispositivo agregado")


# Cambiar información de dispositivo
def cambiarDispositivo():
    print("Cambiar información de dispositivo")
    print("***********************************")
    nombre = input("Ingrese el nombre del dispositivo: ")
    comunidad = input("Comunidad: ")
    version = input("Version SNMP: ")
    puerto = input("Puerto: ")
    direccion = input("Direccion IP: ")
    archivo = open("dispositivos.txt","r")
    lineas = archivo.readlines()
    archivo.close()
    archivo = open("dispositivos.txt","w")
    for linea in lineas:
        datos = linea.split(",")
        if nombre == datos[0]:
            archivo.write(nombre + "," + comunidad + "," + version + "," + puerto + "," + direccion)
        else:
            archivo.write(linea)
    archivo.close()
    print("Dispositivo actualizado")


# Eliminar dispositivo
def eliminarDispositivo():
    nombre = input("Ingrese el nombre del dispositivo: ")
    archivo = open("dispositivos.txt","r")
    lineas = archivo.readlines()
    archivo.close()
    archivo = open("dispositivos.txt","w")
    for linea in lineas:
        datos = linea.split(",")
        if nombre != datos[0]:
            archivo.write(linea)
    archivo.close()
    print("Dispositivo eliminado")


# Generar reporte en PDF
def generarReporte():
    archivo = open("dispositivos.txt","r")
    lineas = archivo.read().splitlines()
    archivo.close()
    for linea in lineas:
        print(linea)
    nombre = input("Ingrese el nombre del dispositivo: ")
    for linea in lineas:
        datos = linea.split(",")
        if nombre == datos[0]:
            comunidad = datos[1]
            direccion = datos[4]
            
    sistemaOperativo = consultaSNMP(comunidad,direccion,"1.3.6.1.2.1.1.1.0")
    versionSO = consultaSNMP(comunidad,direccion,"1.3.6.1.2.1.1.1.0",5)
    informacionContacto = consultaSNMP(comunidad,direccion,"1.3.6.1.2.1.1.4.0")
    ubicacion = consultaSNMP(comunidad,direccion,"1.3.6.1.2.1.1.6.0")
    numeroInterfaces = consultaSNMP(comunidad,direccion,"1.3.6.1.2.1.2.1.0")

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size = 14, style = "B")
    pdf.cell(200, 10, txt = "Administración de Servicios en Red", ln = 5, align = "C")
    pdf.cell(200, 10, txt = "Práctica 1", ln = 5, align = "C")
    pdf.cell(200, 10, txt = "Tovar Espejo Mariana Josefina | 4CM14", ln = 5, align = "C")
    pdf.set_font("Arial", size = 12, style = "B")

    pdf.cell(200, 10, txt = "INFORMACIÓN DE INVENTARIO", ln = 5, align="L")
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = "Sistema Operativo: " + sistemaOperativo, ln = 5, align="L")
    if sistemaOperativo == "Linux":
        pdf.image("ubuntu.png", x = 170, y = 40, w = 30, h = 30)
    elif sistemaOperativo == "Windows":
        pdf.image("windows.png", x = 80, y = 20, w = 50, h = 50)
    pdf.cell(200, 10, txt="Versión del SO: " + versionSO, ln=6, align="L")
    pdf.cell(200, 10, txt="Información de contacto: " + informacionContacto, ln=7, align="L")
    pdf.cell(200, 10, txt="Ubicación: " + ubicacion, ln=8, align="L")
    pdf.set_font("Arial", size = 12, style = "B")

    pdf.cell(200, 10, txt="INFORMACIÓN DE INTERFACES", ln=9, align="L")
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt="Numero de interfaces: " + numeroInterfaces, ln=9, align="L")
    for i in range(int(numeroInterfaces)):
        descripcionInterfaz = consultaSNMP(comunidad,direccion, f"1.3.6.1.2.1.2.2.1.2.{i+1}")
        estadoInterfaz = consultaSNMP(comunidad,direccion, f"1.3.6.1.2.1.2.2.1.7.{i+1}")
        pdf.cell(200, 10, txt=f"Descripcion interfaz: {descripcionInterfaz} | Estado interfaz: {estadosInterfaz[int(estadoInterfaz)-1]}", ln=9, align="L")
    pdf.set_font("Arial", size = 12, style = "B")
    
    pdf.add_page()
    pdf.cell(200, 10, txt="INFORMACIÓN DE CONTABILIDAD", ln=9, align="L")
    pdf.image("graficas/ifIn.png", x = 10, y = 130, w = 100, h = 30)
    pdf.image("graficas/ipIn.png", x = 10, y = 160, w = 100, h = 30)
    pdf.image("graficas/icmpOut.png", x = 10, y = 190, w = 100, h = 30)
    pdf.image("graficas/tcpOut.png", x = 10, y = 220, w = 100, h = 30)
    pdf.image("graficas/udpIn.png", x = 10, y = 250, w = 100, h = 30)
    pdf.output("reporte.pdf")

def consultaSNMP(comunidad,host,oid,position=2):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            #print(varB)
            resultado= varB.split()[position]
            return resultado

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

# Inicio del programa
main()
