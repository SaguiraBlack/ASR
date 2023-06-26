import rrdtool
import os

path = os.path.join(os.getcwd(), "p3", "rendimiento.rrd")
print(path)
ret = rrdtool.create(os.path.join(os.getcwd(), "p3", "rendimiento.rrd"),
    "--start",'N',
    "--step",'10',
    "DS:cpu:GAUGE:10:0:100",
    "DS:ram:GAUGE:10:0:100",
    "DS:disk:GAUGE:10:0:100",
    "RRA:AVERAGE:0.5:1:2400",
)

if ret:
    print (rrdtool.error())