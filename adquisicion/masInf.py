from Tkinter import *
from threading import Thread

from resumen import consultaSNMP

SYS_DSCR = "1.3.6.1.2.1.1.1.0"
SYS_UP_TIME = "1.3.6.1.2.1.1.3.0"
SYS_CONTACT = "1.3.6.1.2.1.1.4.0"
SYS_LOCATION = "1.3.6.1.2.1.1.6.0"
IF_NUMBER = "1.3.6.1.2.1.2.1.0"

tkimg = [None]

def muestraGrafica(carpeta, nombre, ventanaMI):
  path = carpeta.replace(".", "_") + "/" + nombre 
  visor = Toplevel()
  visor.title("Grafica de " + carpeta + " -> " + nombre)

  # Parte de imagen
  imagen = PhotoImage(file=path)
  grafica = Label(visor, image=imagen)
  grafica.image = imagen
  grafica.pack()

  subproceso = Thread(target=cambiaAfter, args=(grafica, path, ventanaMI,))
  subproceso.start()

  # cambiaAfter(grafica, path, ventanaMI)

def cambiaAfter(panel, path, ventanaMI):
    # print "me -> " + path
    tkimg[0] = PhotoImage(file=path)
    panel.configure(image=tkimg[0])
    panel.image = tkimg[0]
    # ventanaMI.update_idletasks()
    ventanaMI.after(5000, lambda: cambiaAfter(panel, path, ventanaMI))    

def mostrarMasInfo(host, root):
  ventanaMI = Toplevel()
  ventanaMI.title("Informacion de: " + host)
  datosAgentes = []

  # Obtengo los datos del archivo
  f = open("adquisicion/agentes.txt", "r")
  registros = f.readlines()
  f.close()

  # Se obtienen los datos y se ponen en una lista
  for agente in registros:
    datosAgentes.append(agente.split(" "))

  i = 0
  for dato in datosAgentes:
    if (host == dato[0]):
      break
    i += 1
  
  datosAgente = datosAgentes[i]
  host = datosAgente[0]
  version = int(datosAgente[1])
  puerto = int(datosAgente[2])
  comunidad = datosAgente[3].strip()  

  # Se obtiene la informacion de la MIB del agente en cuestion
  descr = consultaSNMP(host, version, puerto, comunidad, SYS_DSCR)
  upTime = consultaSNMP(host, version, puerto, comunidad, SYS_UP_TIME)
  contact = consultaSNMP(host, version, puerto, comunidad, SYS_CONTACT)
  location = consultaSNMP(host, version, puerto, comunidad, SYS_LOCATION)

  txtDescrL = ""

  if "Windows" in descr: # SO Windows
    txtDescrL = "Windows" 
  elif "Linux" in descr: # SO Linux
    txtDescrL = "Linux"
  else:
    txtDescrL = "Desconocido"

  upTimeS = int(upTime) / 100
  upTimeM = upTimeS / 60

  dL = Label(ventanaMI, text="Sistema Operativo: " + txtDescrL)
  utL = Label(ventanaMI, text="Ultimo reinicio hace " + str(upTimeS) + " segundos (" + str(upTimeM) + " min)")
  cL = Label(ventanaMI, text="Contacto: " + contact)
  lL = Label(ventanaMI, text="Ubicacion: " + location)
  img = PhotoImage(file="imagenes/" + txtDescrL + ".png")
  logo = Label(ventanaMI, image=img)
  logo.image = img

  btnICMP = Button(ventanaMI, text="Ver grafica ICMP", command=lambda: muestraGrafica(host, "netICMP.png", ventanaMI))
  btnPING = Button(ventanaMI, text="Ver grafica PING", command=lambda: muestraGrafica(host, "netPING.png", ventanaMI) )
  btnTCP = Button(ventanaMI, text="Ver grafica TCP", command=lambda: muestraGrafica(host, "netTCP.png", ventanaMI)) 
  btnUDP = Button(ventanaMI, text="Ver grafica UDP", command=lambda: muestraGrafica(host, "netUDP.png", ventanaMI))
  btnTCPc = Button(ventanaMI, text="Ver grafica TCPc", command=lambda: muestraGrafica(host, "netTCPc.png", ventanaMI))

  logo.grid(row=0, column=0)
  dL.grid(row=0, column=2)
  utL.grid(row=1, column=0)
  cL.grid(row=2, column=0)
  lL.grid(row=3, column=0)
  btnICMP.grid(row=2, column=2)
  btnPING.grid(row=2, column=3)
  btnTCP.grid(row=3, column=2)
  btnUDP.grid(row=3, column=3)
  btnTCPc.grid(row=4, column=2)
