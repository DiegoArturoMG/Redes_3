import threading
import rrdtool
import thread
from utilidadesRR import *
from Tkinter import *
import tkMessageBox
import Tkinter

def hiloParaBaseRR(nombre,direccionIP,comunidad):
	creaBaseRRD(nombre)
	time.sleep(1)
	llenaBaseRRD(nombre,direccionIP,comunidad)
	return

def hiloParaGrafica(nombre,direccionIP):
	print("ya esta graficando-------------------<>>>")
	graficaRR(nombre,direccionIP)
	return

def worker(nombre,direccionIP,comunidad):
	threads = []
	thread.start_new_thread( hiloParaBaseRR, (nombre,direccionIP,comunidad,) )
	time.sleep(3);
	thread.start_new_thread( hiloParaGrafica, (nombre,direccionIP,))	
	return

def obtenerResumen():
	# Leo los agentes del archivo
	f = open("agentes.txt", "r")
	registros = f.readlines()
	datosAgentes = []
  
	# Se obtienen los datos y se ponen en una lista
	for agente in registros:
		datosAgentes.append(agente.split(" "))

	print datosAgentes
	return datosAgentes

# void main(?)
threads = []
i=0
datosNec=obtenerResumen()
for aux in datosNec:
	i=i+1
	print(i)
	print(aux[0]+"->"+aux[3])
	t = threading.Thread(target=worker, args=(str(i),aux[0],aux[3]))
	threads.append(t)
	t.start()
	
root = Tk()
scrollbar = Scrollbar(root)
scrollbar.pack( side = RIGHT, fill = Y )

mylist = Listbox(root, yscrollcommand = scrollbar.set )
for line in range(100):
	mylist.insert(END, "This is line number " + str(line))

mylist.pack( side = LEFT, fill = BOTH )
scrollbar.config( command = mylist.yview )

mainloop()