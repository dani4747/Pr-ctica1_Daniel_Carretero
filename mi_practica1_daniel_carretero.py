'''Daniel Carretero'''

'''
Implementar un merge concurrente:
- Tenemos NPROD procesos que producen números no negativos de forma
creciente. Cuando un proceso acaba de producir, produce un -1

- Hay un proceso merge que debe tomar los números y almacenarlos de
forma creciente en una única lista (o array). El proceso debe esperar a que
los productores tengan listo un elemento e introducir el menor de
ellos.

- Se debe crear listas de semáforos. Cada productor solo maneja los
sus semáforos para sus datos. El proceso merge debe manejar todos los
semáforos.

- OPCIONAL: mente se puede hacer un búffer de tamaño fijo de forma que
los productores ponen valores en el búffer.
'''

'''
notas:
[Lock()]*n

consumidor:
    wait 'todas prducido'
    loop -todos los prod han producido-
        [procesar el minimo] -> pos
        signal al pos, espero que produzca (wait pos)
    
consumidor:
    wait 'todas prducido'
    running = [True, True, ... True]
    while alguno de los valores sea True
    loop -todos los prod han producido-
        [procesar el minimo] -> pos
        signal al pos, espero que produzca (wait pos)

'''

#importo todas las librerías necesarias
from multiprocessing import  Process, Value, Array, current_process, Semaphore, BoundedSemaphore, Lock
from time import sleep
from random import random,randint

N=4
NPROD=15
NCONS=3

def delay(factor=3):
    sleep(random()/factor)
    
def producer(indice, buf, l): # Parámetros de entrada: indices, buffer y lista
    val=0
    i=0
    while (i<N): 
        val+=randint(0,6)
        print('Producer num -> ',indice,'Value -> ',val)
        l[2*indice].acquire() 
        buf[indice]=val
        l[2*indice+1].release()
        i+=1
    val=-1
    l[2*indice].acquire() 
    buf[indice]=val
    l[2*indice+1].release() 

def consumer(buf, l):  # buffer y lista
    lnum=[]
    k=0
    while (k<NPROD):
        l[2*k+1].acquire()
        k+=1    
    while (list(buf)!=[-1]*NPROD):
        delay()
        val, indice=toma_mins(buf)
        print('New value:',val, 'By producer',indice)
        lnum.append(val)
        print(lnum)
        l[2*indice].release()
        l[1+2*indice].acquire()
    print ('List values:',lnum)
    
def toma_mins(l): # Toma la lista como entrada
    l2=[0]*len(l)
    m=max(l) # Tomo el máximo de la lista
    for i in range(len(l)):
        if l[i] == -1: 
            l2[i]=m+1
        else:
            l2[i]=l[i]        
    mi=l2[0] #minimo 
    indice=0 
    #Busco el elemento mas pequeño
    for i in range(1, len(l2)):
        if l2[i] != -1 and mi>l2[i]:
            mi=l2[i]
            indice=i        
    return mi, indice  
  
# Implementamos el main
def main():
    sem=[]
    buf=Array('i', NPROD)
    
    k=0
    while k<NPROD:
        sem.append(BoundedSemaphore(1))
        sem.append(Semaphore(0)) 
        k+=1
    
    procesos=[]  
    for indice in range(NPROD):
        procesos.append(Process(target=producer, args=(sem, buf, indice)))
    procesos.append(Process(target=consumer, args=(sem, buf)))    
    for proceso in procesos:
        proceso.start()
    for proceso in procesos:
        proceso.join()

if __name__ == "__main__":
    main()    
           


    
