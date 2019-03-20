import os
import sys
import rrdtool
from datetime import date
from time import mktime
from adquisicion.notify import enviaAlerta

ONE_HR_POSIX = 86400 / 24
ONE_MIN_POSIX = ONE_HR_POSIX / 60
TIEMPO_EXTRA = 900

def realizar_prediccion(fecha_inicio, hora_inicio, fecha_termino, hora_termino, agente, baseRRD, variable, limInf, limSup):
  dirSinPuntos = agente.replace(".","_")			# Se quitan los puntos de la IP y se ponen _
  directorio = os.getcwd() + "/" + dirSinPuntos		# Se obtiene el directorio en el que deben guardarse las graficas .png
  baseRRD = directorio + "/" + baseRRD

  rrdtool.dump(baseRRD, baseRRD + "Test.xml")       # NO borrar, sirve para depurar esta funcion

  propiedades = []  
  posix_inicio = calculo_fecha_posix(fecha_inicio, hora_inicio)
  posix_termino = calculo_fecha_posix(fecha_termino, hora_termino)
  
  print 'Hr inicial: -> ' + str(posix_inicio)
  print 'Hr termino: -> ' + str(posix_termino)

  definicion = "DEF:" + variable + "=" + baseRRD + ":" + variable + ":AVERAGE"		#de la tarea 'procesadores' de Cesar
  color = "AREA:" + variable+"#CC99FF" + ":"+ variable

  # Se llena el arreglo con las propiedades
  if (posix_inicio < rrdtool.first(baseRRD)): # Se valida que los tiempos dados esten entre los tiempos que tiene la RRD    
    posix_inicio = rrdtool.first(baseRRD)

  #if(posix_termino>rrdtool.last(baseRRD)):
   # print "el dato mas actual de "+baseRRD+ "es del momento"+str(rrdtool.last(baseRRD)), "usare ese"
    #posix_termino=rrdtool.last(baseRRD)

  # Verificacion de limites, para mostrarlos en la grafica
  linea_lim_inf = ""
  linea_lim_sup = ""

  if (limInf != -1): # Se trazara la linea inferior
    linea_lim_inf = "LINE1:" + str(limInf) + "#6600CC"

  if (limSup != -1): # Se traza la linea superior
    linea_lim_sup = "LINE1:" + str(limSup) + "#006666"
  
  ret = rrdtool.graph("grafica" + variable + ".png",
                      "--start",
                      str(int(posix_inicio)),
                      "--end",
                      str(int(posix_termino) + TIEMPO_EXTRA),
                      "--vertical-label=" + variable,
                      "--vertical-label=" + "Uso de " + variable,
                      "--lower-limit=0",
                      "--upper-limit=100",
                      "--rigid",
                      definicion, color,
                      linea_lim_inf, linea_lim_sup,
                      "VDEF:a=" + variable + ",LSLSLOPE",
                      "VDEF:b=" + variable + ",LSLINT",
                      "CDEF:avg2=" + variable + ",POP,a,COUNT,*,b,+",
                      "CDEF:pred=avg2,0," + limSup + ",LIMIT",
                      "VDEF:maxpred=pred,MAXIMUM",
                      "GPRINT:maxpred:%c:strftime",
                      "GPRINT:maxpred:%5.4lf",
                      "PRINT:maxpred:%c:strftime",  #se imprime la variable en ret para usarse a nivel de python
                      "PRINT:maxpred:%5.4lf",
                      "CDEF:predB=avg2,0," + limInf + ",LIMIT",
                      "VDEF:minpred=predB,MINIMUM",
                      "GPRINT:minpred:%c:strftime",
                      "GPRINT:minpred:%5.4lf",
                      "PRINT:minpred:%c:strftime",
                      "PRINT:minpred:%5.4lf",
                      "LINE2:avg2#99FF33")
  print ret
  
  momentoSUP = ret[2][0]
  valorSUP = ret[2][1]
  momentoINF = ret[2][2]
  valorINF = ret[2][3]
  
  # enviaAlerta("Prediccion lim.superior: "+momentoSUP+" Valor:"+valorSUP+
               #"Prediccion lim.inferior: "+momentoINF+" Valor:"+valorINF, "grafica"+ variable + ".png")
  
  print momentoSUP + valorSUP + momentoINF + valorINF

def calculo_fecha_posix(fecha, hora):
  posix_fecha = mktime(fecha.timetuple())
  hr, mins = hora.split(":")
  posix_hora = (ONE_HR_POSIX * float(hr)) + (ONE_MIN_POSIX * float(mins))
  return posix_fecha + posix_hora 
  
