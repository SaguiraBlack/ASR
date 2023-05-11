import rrdtool
import os

ret = rrdtool.create(os.path.join(os.getcwd(), "p3", "rendimiento.rrd"),
    "--start",'N',
    "--step",'60',
    "DS:cpu:GAUGE:60:0:100",
    "DS:ram:GAUGE:60:0:100",
    "DS:disk:GAUGE:60:0:100",
    "RRA:AVERAGE:0.5:1:2400",
)

if ret:
    print (rrdtool.error())