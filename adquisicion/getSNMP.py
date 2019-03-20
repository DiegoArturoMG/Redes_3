"""
SNMPv1
++++++

Send SNMP GET request using the following options:

  * with SNMPv1, community 'public'
  * over IPv4/UDP
  * to an Agent at demo.snmplabs.com:161
  * for two instances of SNMPv2-MIB::sysDescr.0 MIB object,

Functionally similar to:

| $ snmpget -v1 -c public localhost SNMPv2-MIB::sysDescr.0

"""#
from pysnmp.hlapi import *

def consultaSNMP(comunidad,host,oid):
  errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))
  
  resultado = "0"

  if errorIndication:
    pass
    # print(errorIndication)    
  elif errorStatus:
    pass
    # print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
  else:
    for varBind in varBinds:
      varB = (' = '.join([x.prettyPrint() for x in varBind]))
      resultado = varB.split()[2]
  
  return resultado
