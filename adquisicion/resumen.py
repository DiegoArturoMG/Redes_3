from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool
from pysnmp.hlapi import *
import subprocess

SYS_DSCR = "1.3.6.1.2.1.1.1.0"
IF_NUMBER = "1.3.6.1.2.1.2.1.0"
IF_OPSTATUS = "1.3.6.1.2.1.2.2.1.8."

def consultaSNMP(host, version, puerto, comunidad, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, puerto)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
      # print "Error ->" + str(errorIndication)
      return -1
    elif errorStatus:
      print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
      for varBind in varBinds:        
        items = str(varBind).split("=");
        resultado = items[1].lstrip().strip()
      return resultado

def peticionAgente(datosAgente):
  host = datosAgente[0]
  version = int(datosAgente[1])
  puerto = int(datosAgente[2])
  comunidad = datosAgente[3].strip()  
  retorno = []

  d = subprocess.call("snmpstatus -c " + comunidad + " -v 1 " + host + ":" + str(puerto), shell=True)
  
  if d == 1: # No hubo respuesta
    valor = {}
    valor[host] = 0 # DOWN
    retorno.append(valor)
  else:
    disp = consultaSNMP(host, version, puerto, comunidad, SYS_DSCR)
    valor = {}
    valor[host] = 1 # UP
    retorno.append(valor)

    # Consulta de numero de interfaces 
    numInt = consultaSNMP(host, version, puerto, comunidad, IF_NUMBER)
    intD = {'numInt': numInt}
    retorno.append(intD)

    # Consulta de cada interfaz acerca de su estado    
    intEst = []
    for i in range(1, int(numInt) + 1):
      intEst.append(consultaSNMP(host, version, puerto, comunidad, IF_OPSTATUS + str(i)))

    i = 1
    for estado in intEst:
      retorno.append({'' + str(i): estado})
      i += 1

  return retorno

def peticionConcurrente(datosAgentes):
  # Se crea un pool de conexiones
  pool = ThreadPool(2)

  # Se ejecuta 'peticionAgente' por cada item en 'datosAgente'
  results = pool.map(peticionAgente, datosAgentes)

  # Cierre y espera 
  pool.close()
  pool.join()

  # Se regresa, en forma de lista, los valores de cada hilo ejecutado.
  return results

def obtenerResumen(nada=":D"):
  # Leo los agentes del archivo
  print "mmmm"
  f = open("adquisicion/agentes.txt", "r")
  registros = f.readlines()
  datosAgentes = []
  
  # Se obtienen los datos y se ponen en una lista
  for agente in registros:
    datosAgentes.append(agente.split(" "))

  # Peticiones concurrentes
  resultados = peticionConcurrente(datosAgentes)
  return resultados