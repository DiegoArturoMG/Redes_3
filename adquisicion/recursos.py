import rrdtool
import subprocess
import random
import time

from getSNMP import consultaSNMP
from notify import enviaAlerta

OID_PROCESSOR_TABLE = '1.3.6.1.2.1.25.3.3.1.2'

OID_DESC_STORAGE_TABLE = '1.3.6.1.2.1.25.2.3.1.3' # Con este oid se obtienen los nombres de los recursos tipo storage
OID_INDEX_STORAGE_TABLE ='1.3.6.1.2.1.25.2.3.1.1' # Con este oid se obtienen los indices de los recursos tipo storage
OID_USED_STORAGE_TABLE = '1.3.6.1.2.1.25.2.3.1.6' # OID para el espacio usado 
OID_TOTAL_STORAGE_TABLE ='1.3.6.1.2.1.25.2.3.1.5' # OID para el espacio total 

OID_MEM_SIZE = '1.3.6.1.2.1.25.2.3.1.5'
OID_MEM_USED = '1.3.6.1.2.1.25.2.3.1.6'

CONTRATO_PROCESADORES = [30, 60, 90]
CONTRATO_HDD = [60, 75, 85]
CONTRATO_RAM = [69, 78, 87]
CONTRATO_COLORES = ['#e8eb00', '#e86600', '#c00000']

def creacionBaseRecursos(directorio, num_procs):
  # Se procede a crear la base de datos round-robin
  datasources = []
  rra = []

  # Se generan los datasources de los procesadores
  for i in range(num_procs):
    dataStr = "DS:CPU" + str(i + 1) + "load:GAUGE:600:U:U" 
    datasources.append(dataStr)
    rraStr = "RRA:AVERAGE:0.5:1:600"
    rra.append(rraStr)

  ret = rrdtool.create(directorio + "/recursos.rrd",
                     "--start",'N',
                     "--step",'15',
                     datasources, rra)

def creacionBaseMemoria(directorio, indices):    #funcion que crea la base del uso de memoria y disco duro
  # Se procede a crear la base de datos round-robin
  datasources = []
  rra = []

  # Se generan los datasources de los procesadores
  for ind in indices:
    dataStr = "DS:strg" + ind+ "load:GAUGE:600:U:U" 
    datasources.append(dataStr)
    rraStr = "RRA:AVERAGE:0.5:1:600"
    rra.append(rraStr)    

  ret = rrdtool.create(directorio + "/memoria.rrd",
                     "--start",'N',
                     "--step",'15',
                     datasources, rra)

def obtenerProcesadores(comunidad, ipAddr):
  comunidad = comunidad.strip().lstrip()    
  snmpWalk = 'snmpwalk -v2c -c ' + comunidad + ' ' + ipAddr + ':161 ' + OID_PROCESSOR_TABLE

  # Se realiza la consulta
  try:
    retorno = subprocess.check_output(snmpWalk, shell=True)
    #retorno = ["hrProcessorLoad.1026 = INTEGER: 60"]
    #retorno = ['HOST-RESOURCES-MIB::hrProcessorLoad.1026 = INTEGER: 60']
    cargas = retorno.split('\n')
    cargas = cargas[:-1]

    print '------>'+str(cargas)+'<------'

    return cargas
  except subprocess.CalledProcessError, e:
    return []

#funcion que devuelve en un array los nombres de los storage dada una ip y comunidad
def obtenerStorageNames(comunidad, ipAddr):
  comunidad = comunidad.strip().lstrip()    
  snmpWalk = 'snmpwalk -v2c -c ' + comunidad + ' ' + ipAddr + ' ' + OID_DESC_STORAGE_TABLE
  nombres = []
  # Se realiza la consulta
  try:
    retorno = subprocess.check_output(snmpWalk, shell=True)
    cargas = retorno.split('\n')
    cargas = cargas[:-1]    
    
    for cr in cargas:
      aux=cr.split("STRING:")[-1]
      nombres.append(aux.strip())

    return nombres
  except subprocess.CalledProcessError, e:
    return []

#funcion que devuelve en un array los indices de los storage dada una ip y comunidad
def obtenerStorageIndices(comunidad, ipAddr):
  comunidad = comunidad.strip().lstrip()    
  snmpWalk = 'snmpwalk -v2c -c ' + comunidad + ' ' + ipAddr + ' ' + OID_INDEX_STORAGE_TABLE
  nombres = []
  # Se realiza la consulta
  try:
    retorno = subprocess.check_output(snmpWalk, shell=True)
    cargas = retorno.split('\n')
    cargas = cargas[:-1]    
    
    for cr in cargas:
      aux=cr.split("INTEGER:")[-1]
      nombres.append(aux.strip())

    return nombres
  except subprocess.CalledProcessError, e:
    return []

def adicionInfoProcesadoresAgente(directorio, identificadores, comunidad, ipAddr):
  valores = "N:"

  # Parte de informacion de procesadores
  for ide in identificadores: 
    ide = ide.replace('\n', '')       
    carga_CPU = int(consultaSNMP(comunidad, ipAddr, OID_PROCESSOR_TABLE + "." + ide))
    valores += str(carga_CPU) + ":"
  
  valores = valores[:-1]
  
  rrdtool.update(directorio + '/recursos.rrd', valores)

def adicionInfoStorageAgente(directorio, indices, comunidad, ipAddr):
  valores = "N:"

  # Parte de informacion de procesadores
  for ide in indices: 
    ide = ide.replace('\n', '')       
    usado = int(consultaSNMP(comunidad, ipAddr, OID_USED_STORAGE_TABLE + "." + ide))
    total = int(consultaSNMP(comunidad, ipAddr, OID_TOTAL_STORAGE_TABLE + "." + ide))
    
    if(total == 0):
      total = 0.001;

    if(usado == 0):
      usado = 0.001;
    
    percent = int((float(usado)/float(total))*100)
    valores += str(percent) + ":"
  
  valores = valores[:-1]  
  rrdtool.update(directorio + '/memoria.rrd', valores)
  rrdtool.dump(directorio +'/memoria.rrd',directorio +'/memoria.xml')

def graficaRecursosAgente(directorio, tiempo_inicio, num_procs, no_spam):  
  # Se generan las propiedades de las graficas
  propiedades_recursos = []  

  # Primero los procesadores
  for i in range(num_procs):
    propiedades_recursos.append(generacionPropiedadesProcesadorGrafica(directorio, i, tiempo_inicio))
  
  # Se grafican todos los recursos
  num_proc = 1
  for propiedad in propiedades_recursos:
    graficaProcesador(propiedad, directorio, num_proc, no_spam[num_proc - 1])
    num_proc += 1

def graficaStorageAgente(directorio, tiempo_inicio, no_spam):
  # Se lee el archivo, para saber cuantas graficas se haran
  proc_arch = open(directorio + "/storages.txt", "r")
  lineasLeidas = proc_arch.readlines()
  nombres = []
  indices = []
  for linea in lineasLeidas:
    nombres.append(linea.split("<<-->>")[1])
    indices.append(linea.split("<<-->>")[0])
  
  numOfStorages = len(lineasLeidas)
  # Se generan las propiedades de las graficas
  propiedades_recursos = []  

  # Primero los procesadores
  for i in range(numOfStorages):
    propiedades_recursos.append(generacionPropiedadesStorageGrafica(directorio, tiempo_inicio, nombres[i], indices[i]))

  # Se grafican todos los recursos
  i = 0
  for propiedad in propiedades_recursos:
    graficaMemoria(propiedad, directorio, nombres[i], no_spam)
    i += 1

def generacionPropiedadesProcesadorGrafica(directorio, numProcesador, tiempo_inicio):
  propiedades = []
  grafica = directorio + "/recursos.rrd"

  # Cadenas relativas a la grafica de la linea
  definicion = "DEF:carga" + str(numProcesador + 1) + "=" + grafica + ":CPU" + str(numProcesador + 1) + "load:AVERAGE"
  color = "AREA:carga" + str(numProcesador + 1) + hex_code_colors() + ":CPU" + str(numProcesador + 1) + " load"
  baselines = []
  i = 0
  for linea in CONTRATO_PROCESADORES:
    baselines.append("LINE2:" + str(linea) + CONTRATO_COLORES[i])
    i += 1

  # Se llena el arreglo con las propiedades
  propiedades.append(directorio + "/procesador" + str(numProcesador + 1) + ".png")
  propiedades.append("--start")
  propiedades.append(tiempo_inicio)  
  propiedades.append("--vertical-label=Carga CPU" + str(numProcesador + 1))  
  propiedades.append('--vertical-label')
  propiedades.append("Uso de CPU (%)")
  propiedades.append('--lower-limit=0')  
  propiedades.append('--upper-limit=100')
  propiedades.append('--rigid')
  propiedades.append(definicion)
  propiedades.append(color)
  
  for baseline in baselines:
    propiedades.append(baseline)

  propiedades.append("VDEF:entradaLAST=carga" + str(numProcesador + 1) + ",LAST")
  propiedades.append("PRINT:entradaLAST:%6.2le")

  return propiedades

def generacionPropiedadesStorageGrafica(directorio, tiempo_inicio, nombre, index):
  propiedades = []
  grafica = directorio + "/memoria.rrd"

  # Cadenas relativas a la grafica de la linea
  definicion = "DEF:Memory_Used=" + grafica + ":strg" + index + "load:AVERAGE"
  color = "AREA:Memory_Used" + hex_code_colors() + ":Memory_Used"
  
  # Se llena el arreglo con las propiedades
  nombre = nombre.replace("/","_")
  nombre = nombre.replace("\\","_")
  nombre = nombre.lstrip().rstrip()
    
  propiedades.append(directorio + "/" + nombre + ".png")
  propiedades.append("--start")
  propiedades.append(tiempo_inicio)  
  propiedades.append("--vertical-label=Uso de Memoria")  
  propiedades.append('--vertical-label')
  propiedades.append("Espacio usado: (%)")
  propiedades.append('--lower-limit=0')  
  propiedades.append('--upper-limit=100')
  propiedades.append('--rigid')
  propiedades.append(definicion)
  propiedades.append(color)

  # Se verifica si es la memoria RAM, ya que entra en el contrato
  if "Physical" in nombre:    
    baselines = []
    i = 0
    
    for linea in CONTRATO_RAM:
      baselines.append("LINE2:" + str(linea) + CONTRATO_COLORES[i])
      i += 1

    for baseline in baselines:
      propiedades.append(baseline)
    
    propiedades.append("VDEF:entradaLAST=Memory_Used,LAST")
    propiedades.append("PRINT:entradaLAST:%6.2le")    
  else:       #se trata de un storage
    baselines = []
    i = 0
    for linea in CONTRATO_HDD:
      baselines.append("LINE2:" + str(linea) + CONTRATO_COLORES[i])
      i += 1

    for baseline in baselines:
      propiedades.append(baseline)
     

  return propiedades

def graficaMemoria(propiedad, directorio, nombre, no_spam):  
  ret = rrdtool.graph(propiedad)
  nombre = nombre.lstrip().rstrip()

  if "Physical" in nombre:    
    ultima_carga = procesarCadenaRetorno(ret[2][0])
    tipo_linea = comparacionValoresContrato(ultima_carga, CONTRATO_RAM)
    mensajeCorreo = seleccionMensajeCorreoProcesador(tipo_linea)
    
    if mensajeCorreo != "" and no_spam == True: # Se enviara correo
      enviaAlerta('Memoria RAM: ' + mensajeCorreo, \
      directorio + '/' + nombre + '.png')

def graficaProcesador(propiedad, directorio, num_proc, no_spam):
  ret = rrdtool.graph(propiedad)
  ultima_carga = procesarCadenaRetorno(ret[2][0])
  tipo_linea = comparacionValoresContrato(ultima_carga, CONTRATO_PROCESADORES)
  mensajeCorreo = seleccionMensajeCorreoProcesador(tipo_linea)

  if mensajeCorreo != "" and no_spam == True:  # Se enviara correo
    procesador = 'procesador' + str(num_proc)
    enviaAlerta(procesador, directorio + '/' + procesador + '.png')

def comparacionValoresContrato(valor, valores_contrato):
  # Primero se compara con el mayor, para que sea el de mayor peso
  comparadores = list(reversed(valores_contrato))
  i = 0

  for comparador in comparadores:    
    if (valor >= comparador):
      return i # 0 -> mayor peso, 2 -> menor peso
    i += 1

  return -1 # no ha pasado ningun limite

def seleccionMensajeCorreoProcesador(tipo):
  mensajeCorreo = ""

  if tipo != -1: # Se debe de notificar!!
    if tipo == 0:
      mensajeCorreo = 'Se ha sobrepasado el limite GO. Actue lo antes posible.'
    elif tipo == 1:
      mensajeCorreo = 'Se ha sobrepasado el limite SET. Mantengase al pendiente.'
    elif tipo == 2:
      mensajeCorreo = 'Se ha sobrepasado el limite READY.'

  return mensajeCorreo

def procesarCadenaRetorno(cadena):
  # Primero, se limpia la cadena
  cadena = cadena.lstrip()
  valor = cadena.split(" ")

  try:
    # Se convierte a un float
    float(valor[0])    
    return float(valor[0])
  except ValueError:    
    return 0

def hex_code_colors():
  a = hex(random.randrange(0,256))
  b = hex(random.randrange(0,256))
  c = hex(random.randrange(0,256))
  a = a[2:]
  b = b[2:]
  c = c[2:]
  if len(a) < 2:
      a = "0" + a
  if len(b) < 2:
      b = "0" + b
  if len(c) < 2:
      c = "0" + c
  z = a + b + c
  return "#" + z.upper()
