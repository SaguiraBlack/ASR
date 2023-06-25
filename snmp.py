# imports
from pysnmp.hlapi import *
from fpdf import FPDF

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

def consulta_multicast(comunidad, version, puerto, direccion):
    # Crea la comunidad SNMP
    comunidad_snmp = CommunityData(comunidad, mpModel=version)
    
    # Crea el objeto Target para la dirección multicast
    direccion_multicast = UdpTransportTarget((direccion, puerto), timeout=1, retries=0)
    
    # Define la OID a consultar
    # , "1.3.6.1.2.1.1.1.0"
    #oid = ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
    oid = ObjectType(ObjectIdentity("1.3.6.1.2.1.1.3.0"))
    
    # Realiza la consulta SNMP
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               comunidad_snmp,
               direccion_multicast,
               ContextData(),
               oid)
    )
    
    # Verifica si se recibió una respuesta exitosa
    if errorIndication:
        raise Exception(errorIndication)
    elif errorStatus:
        raise Exception('%s at %s' % (errorStatus.prettyPrint(),
                                      errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    
    # Retorna el valor obtenido
    return varBinds[0][1].prettyPrint()

#ifInUcastPkts = consultaSNMP('comunidadSaguira', 'localhost', "1.3.6.1.2.1.2.2.1.11.1")
#print(ifInUcastPkts)
#multicastTest = consulta_multicast('comunidadASR', 1, 161, 'localhost')
#print(multicastTest)
