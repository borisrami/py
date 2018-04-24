from tkinter import *
from tkinter import messagebox
import math
import serial
############################## F U N C I O N E S #############################################
#PARA TRANSMISION DE DATOS
def prepEnvio(x,y,dibujar): #Funcion que crea una lista con datos para enviar al PIC
    global dim, dimServo
    data=calcAngulos(x,y)
    
    envio=[]                    #Lista para trasmitir
    chkme=[]
    envio.append(0xBB)          #245 bandera de inicio CAMBIO
    envio.append(0x44)          #245 bandera de inicio CAMBIO
    envio.append(0x11)          # 0x11 es el OPCODE para ABSMOVE
    chkme.append(0x11)
    envio.append(0x01)          # ARGS = 0x01
    chkme.append(0x01)
    envio.append(0x03)          # ARGS = 0x03
    chkme.append(0x03)
    envio.append(data[0])       # El primer argumento para ABSMOVE es alfa
    chkme.append(data[0])
    envio.append(data[1])       # El segundo argumento para ABSMOVE es beta
    chkme.append(data[1])
    if dibujar==1:              # El tercer argumento para ABSMOVE es 0x01 si se va a dibuar
        envio.append(1)
        chkme.append(1)
    else:                       # o 0x00 si no se va a dibujar
        envio.append(0)
        chkme.append(0)
    checksum = 0x00;
    for i in chkme:
        checksum += i
    print("CHECKSUM para la trama: "+format(checksum&0xFF, "#04x"))
    envio.append(checksum&0xFF)
    envio.append(0xAA)
    envio.append(0x55)
    return envio
    
    
def calcAngulos(x, y): #Funcion para obtenr alfa y beta
    a=12                    #Tamano del brazo en cm
    angulos=[]              #Lista con [245,alfa, beta]. 245 bandera de inicio
    a=float(a)
    x=float(x)
    y=float(y)

    print ("\n RESULTADOS")
    theta = math.atan(y/x)         #Calculos
    print ("Theta = "+str(theta)+" rads")
    b= math.sqrt((x*x)+(y*y))
    print ("b = "+str(b)+" cm")
    print ("2a = " +str(2*a)+" cm")
    print ("b/2a = "+str(b/float(2*a))+" cm")
    phi= math.acos(b/float(2*a))
    print ("phi = "+str(phi)+" rads")
    alfa= int(math.degrees(theta+phi))
    print ("alfa = "+str(alfa)+" grados")
    beta=(2*a*a)-b*b
    beta=beta/(2*a*a)
    beta=int(math.degrees(math.acos(beta)))
    print ("beta = "+str(beta)+" grados")
    # Puede ser que venga de 0 a 35 o bien de 35 a 70
    alfa = int(maprange((0, 180), (0, 70), alfa))
    print ("alfa mapea a = "+str(alfa))
    beta = int(maprange((0, 180), (0, 70), beta))
    print ("beta mapea a = "+str(beta))
    angulos.append(alfa)
    angulos.append(beta)
    return angulos

def maprange(a, b, s):
    (a1, a2), (b1, b2) = a, b
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def mapear(dominio, rango): #Funcion para mapear de un dominio a otro
    mapa={}
    mapeo=1
    cont=0
    intervalo=int(dominio/float(rango-1)) #Para obtener el rango
    for i in range (dominio+1):
        if cont==intervalo:
            mapeo=mapeo+1
            cont=0
        mapa[i]=mapeo
        cont=cont+1
    return mapa

def funSerial(val1):#Funcion para enviar datos mediante conexion serial
    #ser = serial.Serial('/dev/tty.usbserial-00000000', baudrate = 50000, parity = serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)
    with serial.Serial('/dev/ttys001') as ser:
        ser.write(val1)
        print ("Escrito byte "+format(val1, "#010x")+" en el puerto "+ser.port+" a "+str(ser.baudrate)+" bps")
        
#PARA DIBUJAR
def main():
    global root
    drawing_area = Canvas(root, bg="white", width=dim, height= dim)
    drawing_area.pack()
    drawing_area.bind("<Motion>", motion)
    drawing_area.bind("<ButtonPress-1>", b1down)
    drawing_area.bind("<ButtonRelease-1>", b1up)
    drawing_area.bind('<Double-1>', sendData)
    messagebox.showinfo("Envio de Datos", "Al terminar su dibujo, enviar los datos con DOBLE CLICK")
    root.mainloop()
def sendData(event):#Doble click
    print ("DOBLE CLICK")
    budprinted = 0
    coordenadas = []
    for i in dibujo:
        if i not in coordenadas:
            coordenadas.append(i)
    print ("Coordenadas del dibujo: "+str(coordenadas))
    paquete=[]
    for i in coordenadas:
        datos=prepEnvio(i[0],i[1],i[2])
        print ("DATOS= "+str(datos))
        paquete.append(datos)

    for i in paquete:
        print ("PAQUETE "+str(i))

    set_auto = [0xBB, 0x44, 0x10, 0x00, 0x10, 0xAA, 0x55]
    print("Trama a enviar "+str([format(i, "#04x") for i in set_auto])+" manual->auto")
    for dato in set_auto:
        funSerial(dato)

    for prueba in paquete:
        print("Trama a enviar "+str([format(i, "#04x") for i in prueba]))
        for dato in prueba:
            funSerial(dato)

    set_manual = [0xBB, 0x44, 0x12, 0x00, 0x12, 0xAA, 0x55]
    print("Trama a enviar "+str([format(i, "#04x") for i in set_manual])+" auto->manual")
    for dato in set_manual:
        funSerial(dato)

    print ("FIN")
    
def b1down(event):#Mouse presionado
    global b1
    b1 = ("down") 

def b1up(event): #Mouse liberado
    global b1, xold, yold, primera
    b1 = ("up")
    primera=True

def motion(event):
    global xold, yold, mapaCanvas, primera, coordenadas, intervalo, prevDib
    punto=[]
    if b1 == ("down"):
        if xold is not None and yold is not None:
            #Dibujando:
            event.widget.create_line(xold,yold,event.x,event.y,smooth=TRUE, width=intervalo)
                    
        xold = event.x
        yold = event.y

        if yold>dim:
            yold=dim
        if xold>dim:
            xold=dim
        if yold<1:
            yold=1
        if xold<1:
            xold=1
            
        equis=mapaCanvas[xold]
        ye=mapaCanvas[yold]

        ynormal=[]
        yinvertida=[]
        mapearY={}
        for c in range (1,17):
            mapearY[c]=17-c

        ye=mapearY[ye]
        
        if primera==True:
            punto=[equis, ye, 0]
            dibujo.append(punto)
            primera=False
        else:
            if prevDib == False:
                punto = [puntotemp[0],puntotemp[1],0]
                dibujo.append(punto)
        punto = [equis,ye,1]
        puntotemp=punto
        dibujo.append(punto)
        prevDib = True
        print ("x: "+str(equis)+" y: "+str(ye))
    else:
        prevDib = False
        try:
            equis=mapaCanvas[xold]
            ye=mapaCanvas[yold]
            punto=[equis, ye, 0]
            #puntotemp=[puntotemp[0], puntotemp[1], 0]
            dibujo.append(punto)
            xold = None     #Se limpian las variables para poder "levantar el lapiz"
            yold = None
        except:
            pass
        
######################### P R O G R A M A   F U E N T E #############################
#Datos
root = Tk()
root.title("PROYECTO 2")
dim=400         #dimensiones de canvas de 320*320
dimServo=16     #dimensiones area dibujo del servo 16*16
intervalo=int(dim/float(dimServo)) #Para obtener el rango
b1 = "up"
primera=True
prevDib = False
xold, yold = None, None
dibujo=[]       #contiene todas las coordenadas del dibujo
coordenadas=[]  #contiene las coordenadas del dibujo sin repeticiones
datos=[]        #[245,alfa, beta, dib, 255]. 245 bandera inic, angulos, dib indicador de dibujo o no, 255 bandera fin.
paquete=[]      #el conjunto de todos los datos a enviar
x=0             #Coordenadas
y=0

mapaCanvas=mapear(dim, dimServo)    #Escalando canvas
print (mapaCanvas)
     
#Se crea el dibujo y se guardan las coordenadas
if __name__ == "__main__":
    main()

