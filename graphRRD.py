import rrdtool
import os
import time

def grafica(filename, time_start, time_end, title, var, db, name):
    if not os.path.exists(os.path.join(os.getcwd(), "graficas")):
        os.mkdir(os.path.join(os.getcwd(), "graficas"))

    try:
        rrdtool.graph(filename, "--start", str(time_start), "--end", str(time_end),
                      "--vertical-label=Bytes/s", "--title=" + title,
                      "DEF:variable=" + db + ":" + var + ":AVERAGE",
                      "CDEF:escala=variable,8,*",
                      "LINE3:escala#0000FF:" + name)
        return "OK"
    except Exception as e:
        print(e)
        return "Error al generar la grafica :" + e.args[0]

datos = [
    ["ifInMulticastPkts", "ifIn.png", "Paquetes multicast de entrada"],
    ["ipInReceives", "ipIn.png", "Tráfico de entrada"],
    ["icmpOutEchoReps", "icmpOut.png", "Respuestas ICMP de salida"],
    ["tcpOutSegs", "tcpOut.png", "Paquetes TCP de salida"],
    ["udpInOverflows", "udpIn.png", "Paquetes UDP de entrada"]
]

#for dato in datos:
#    # Obtener el timestamp actual
#    now = int(time.time())
#    # Restar 10 minutos (600 segundos)
#    start = now - 600#

#    grafica(
#        os.path.join(os.getcwd(), "graficas", dato[1]),
#        start, now, datos,
#        dato[0],
#        os.path.join(os.getcwd(), "RRD", "1.rrd"),
#        dato[2])
