# -*- coding: utf-8 -*-

import sys
"import serial"
import math
from tkinter import *
from math import *
import time
click_mouse= ""                    #Nos indica el estado del boton del mouse, arriba, abaja
coordenadaX= None                    #Variable que nos indica la coordenada en x
coordenadaY= None                    #cordenada en y
global x
global y
x=[]                                #Vector que va almacenando coordenadas en x
y=[]                                #Vector que va alamacenado coordenadas en y
vector_coordenadas_x = []                        #En cada casilla almacena el vector de coordenas x, se usa para diferenciar lineas no continuas
vector_coordenadas_y = []                        #En cada casilla almacena el vector de coordenas y, se usa para diferenciar lineas no continuas

#######################################################################################################################################################
def main():
    domain = Tk()
    position = Frame(domain)
    position.pack()
    draw_space = Canvas(position, width = 300, height = 300,bg="blue")
    draw_space.pack()
    draw_space.bind("<Motion>", drag)
    draw_space.bind("<ButtonPress-1>", contact)
    draw_space.bind("<ButtonRelease-1>", lift_mouse)
    space_button = Button(position, text="Dibujar", command=mandar, activeforeground="RED", padx=20)
    space_button.pack(padx=5,side=LEFT)  
    domain.mainloop()

#######################################################################################################################################################
def contact(event):
    global click_mouse
    click_mouse = "clik"       #funcion para detectar cuando el mouse esta presionado

#######################################################################################################################################################
def drag(event):
    global click_mouse
    global coordenadaX
    global coordenadaY  
    if click_mouse=="clik":
        if coordenadaX is not None and coordenadaY is not None:
            event.widget.create_line(coordenadaX,coordenadaY, event.x, event.y, smooth=TRUE)  #Se crea una line entre las dos posiciones
        coordenadaX= event.x               #se guardan las coordenadas nuevas 
        coordenadaY= event.y
        x.append(coordenadaX)              #Se guardan las corrdenadas
        y.append(coordenadaY)
       
       #print(y)

#######################################################################################################################################################
        
def lift_mouse(event):                  #Cuando se levanta el botton del mouse se alamacena el vector de coordenas en el vector global
    global click_mouse
    global coordenadaX 
    global coordenadaY
    global vector_coordenadas_x
    global vector_coordenadas_y  
    click_mouse= "no-click"
    vector_coordenadas_x.append(x[:])    #se almacenan las coordenas en la matriz de vectores
    vector_coordenadas_y.append(y[:])
    del x[:]                   #se limpia el vector de coordenadas de esta linea
    del y[:]
    coordenadaX=None             #Se borran las coordenadas
    coordenadaY=None
  
#######################################################################################################################################################
def mandar():
    global vector_coordenadas_x
    global vector_coordenadas_y    
    
    cord_x=[]
    cord_y=[]
    for i in vector_coordenadas_x: # Se trabajan con los porcentajes de las coordenadas
        cord_x.append(111)
        for j in i:    
            if int(j)<=300 and int(j)>=0:
                cord_x.append((int(j))/3)
                
    for i in vector_coordenadas_y:
        cord_y.append(111)
        for j in i:
            if int(j)<=300 and int(j)>=0:
                cord_y.append((int(j))/3)

  # print(y)

             
#######################################################################################################################################################
    beta=[]
    alfa=[]
    alfa1=[]
    beta1=[]
    angulos=[]
    brazo_medi=float((100**2+100**2)**(0.5))*0.5         #largo de un brazo
    bandera_marcador=0
    m=0
    for k in range(len(cord_x)):                           #calculo el angulo para la base y el codo en grados
        try:

            theta = math.degrees(math.atan(cord_y[k]/cord_x[k]))    #Calculo de los angulos de los servos
            b=float((cord_x[k]**2+cord_y[k]**2)**(0.5))    
            fi=math.degrees(math.acos(b/(2*brazo_medi)))
            beta.append(180-int(2*fi))
            alfa.append(int(fi+theta))
            conversion1=bin(int((180-int(2*fi))/(float(180)/63))).lstrip("0b")
            conversion2=bin(int(int(fi+theta)/(float(180)/63))).lstrip("0b")
            #while len(conversion1)<6:
             #   conversion1="0"+conversion1
            #while len(conversion2)<6:
             #   conversion2="0"+conversion2# Se rellenan de ceros cuando sea necesario para que siempre sea una cadena de 6 bits
            #if bandera_marcador==1:
             #   for x in range(10): #Se coloca estos bits para levantar el brazo cuando haya una linea discontinua
              #      angulos.append("00"+conversion1)
               #     angulos.append("10"+conversion2) 
                #bandera_marcador=0
            angulos.append("01"+conversion1)
            angulos.append("11"+conversion2)
            alfa1.append(int(int(fi+theta)/(float(180)/63)))      #Angulos de los servos definitivos
            beta1.append(int((180-int(2*fi))/(float(180)/63)))
            
        except:
            bandera_marcador=1 #Bandera para levantar el marcador
            beta.append(-1)
            alfa.append(-1)

            
            print(angulos)
            
#######################################################################################################################################################            
    #Mandar los datos
    puerto=serial.Serial("COM3",9600,timeout=1)     
   
    for j in range(len(angulos)): 
        one_byte = int(angulos[j], 2)
        single_byte = one_byte.to_bytes(1, byteorder='big', signed=False)
       
        puerto.write(single_byte)
        time.sleep(0.05)
    puerto.close()
            
    print (beta)
    print (alfa)
    print (beta1)
    print (alfa1)
    print (angulos)
                      
    del vector_coordenadas_x[:]         #se borran las coordenadas anteriores
    del vector_coordenadas_y[:]  

#######################################################################################################################################################
    
if __name__ == "__main__":
    main()



