from threading import Thread
from agentes import agregar, eliminar
from resumen import obtenerResumen, consultaSNMP

""" Main """
# Se ejecuta en segundo plano proceso de graficas

# Menu Principal
while True:
  print "Que desea hacer?\n1. Resumen\n2. Agregar agente"
  print "3. Eliminar agente\n4. Detalle de agente"  
  opcion = input("Opcion: ") 
  if (opcion == 1):
    obtenerResumen()
  elif (opcion == 2):
    agregar()
  elif (opcion == 3):
    eliminar()
  else:
    print consultaSNMP('localhost', 1, 161, 'public', "1.3.6.1.2.1.2.2.1.8.1")

