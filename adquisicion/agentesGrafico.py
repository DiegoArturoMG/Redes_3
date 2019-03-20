from Tkinter import *
import ttk
import tkMessageBox

from agentes import agregarAlArchivo, quitarDeArchivo

def agregarAgente(root):
	# Entrada de texto para host o direccion IP
	hostT = Label(root, text="Host o direccion IP")
	hostE = Entry(root)

	# Seleccion con ComboBox para la version del protocolo
	verL = Label(root, text="\nVersion SNMP:")
	verC = ttk.Combobox(root, values=['1', '2'], state='readonly')
	verC.set('1')

	# Entrada de texto para el numero de puerto
	ptoT = Label(root, text="\nNumero de puerto:")
	ptoE = Entry(root)

	# Entrada de texto para el nombre de la comunidad
	comT = Label(root, text="\nNombre de comunidad:")
	comE = Entry(root)

	# Salto de linea grafico
	salto = Label(root, text="\n")

	# Boton para la adicion del agente
	addB = Button(root, text="Agregar Agente", command=lambda: verificaDatos(hostE, verC, ptoE, comE))

	# Se insertan los componentes en la ventana
	hostT.pack()
	hostE.pack()
	verL.pack()
	verC.pack()
	ptoT.pack()
	ptoE.pack()
	comT.pack()
	comE.pack()
	salto.pack()
	addB.pack()

def verificaDatos(hostE, verC, ptoE, comE):
	# Se obtienen los datos de las entradas de texto
	host = hostE.get()
	version = verC.current() + 1	
	puerto = ptoE.get()

	if (host == '' or comE.get() == ''):
		tkMessageBox.showerror("Error", "Faltan datos")
		return 

	# Se verifica que sea un digito el puerto
	if puerto.isdigit() == True:
		# Se obtienen los datos restantes
		puerto = int(puerto)
		comunidad = comE.get()

		# Se agrega al archivo y se notifica al usuario que se realizo la adicion satisfactoriamente
		agregarAlArchivo(host, version, puerto, comunidad)
		tkMessageBox.showinfo("Exito", "Se agrego el agente satisfactoriamente")		
	else:
		# Notificacion al usuario acerca del error
		tkMessageBox.showerror("Error", "El puerto debe de ser un numero")		

def eliminarAgente(root):
	# Entrada de texto para host o direccion IP
	hostT = Label(root, text="Host o direccion IP")
	hostE = Entry(root)

	# Boton para la adicion del agente
	remB = Button(root, text="Eliminar Agente", command=lambda: elimina(hostE))

	# Se insertan los componentes a la ventana
	hostT.pack()
	hostE.pack()
	remB.pack()
	
def elimina(hostE):
	host = hostE.get()
	
	if (host == ''):
		tkMessageBox.showerror("Error", "Faltan datos")
		return

	exito = quitarDeArchivo(host)

	if exito:
		tkMessageBox.showinfo("Exito", "Se removio el agente satisfactoriamente")		
	else:
		tkMessageBox.showerror("Error", "No se encontro host en los registros")
