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

from multiprocessing import Process, Value, Array, current_process, Semaphore, BoundedSemaphore, Lock
from time import sleep
from random import random,randint

N = 30
K = N
NPROD = 3
NCONS = 1

def delay(factor = 3):
    sleep(random()/factor)


def add_data(storage, index, pid, data, mutex):
    mutex.acquire()
    try:
        storage[index.value] = randint(1,9) + storage[index.value-1]
        delay(6)
        index.value = index.value + 1
    finally:
        print(storage[:])
        mutex.release()


def get_data(storagelst, indexlst, mutex, miLista,indice):
    mutex.acquire()
    try:
        li = []
        for i in range(NPROD):
            if not (storagelst[i][0] == -1):
                li.append(storagelst[i][0])
        minimo = min(li)
        for i in range(NPROD):
            if minimo == storagelst[i][0]:
                indexlst[i].value = indexlst[i].value - 1
                delay()
                for j in range(indexlst[i].value):
                    storagelst[i][j] = storagelst[i][j + 1]
                storagelst[i][indexlst[i].value] = -1
                break
        
        data = minimo
        miLista[indice] = data
    finally:
        mutex.release()
        print(storagelst[0][:],storagelst[1][:],storagelst[2][:])
        print(miLista[:])
    
def producer(storage, index, empty, non_empty, mutex):
    for v in range(N):
        delay(6)
        print(f"producer {current_process().name} produciendo")
        
        empty.acquire()
        add_data(storage, index, int(current_process().name.split('_')[1]),
                 v, mutex)
        non_empty.release()
        print(f"producer {current_process().name} almacenado {v}")


def consumer(storagelst, indexlst, empty, non_empty, mutex, miLista):
    indice = 0
    for v in range(N*NPROD):
        non_empty.acquire()
        contador = 0
        while  (( indexlst[0].value == 0 or indexlst[1].value == 0 or indexlst[2].value == 0) and (N*NPROD-indice)>2) and contador < 10:
            contador += 1
            delay()
        dato = get_data(storagelst, indexlst, mutex,miLista,indice)
        empty.release()
        indice += 1
        print(f"consumer {current_process().name} consumiendo {dato}")
        delay()
        
def ordenar(listas):
    li = []
    while(not menos_unos(listas)):
        li.append(toma_mins(listas))
    return li
        
def toma_mins(listas):
    li = []
    for i in listas:
        if i[0] != -1:
            li.append(i[0])
    minimo = min(li)
    for i in listas:
        if minimo == i[0]:
            i.pop(0)
            break
    return minimo
        
def menos_unos(lista):
    for i in lista:
        for j in i:
            if j!=-1:
                return False
    return True

def main():

    non_empty = Semaphore(0)
    empty = BoundedSemaphore(K)
    mutex = Lock()
    
    indexlst = [Value('i',0) for _ in range(NPROD)]
        
    storagelst = [Array('i',K) for _ in range(NPROD)]
    
    for j in storagelst:
            for i in range(K):
                j[i] = -1
    
    miLista = Array('i',N*3)
    
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storagelst[i], indexlst[i], empty, non_empty, mutex))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name=f"cons_{i}",
                      args=(storagelst, indexlst, empty, non_empty, mutex,miLista))
                for i in range(NCONS) ]

    for p in prodlst:
        p.start()
    
    for p in conslst:
        p.start()

    for p in prodlst:
        p.join()
    
    for p in  conslst:
        p.join()
        
    print(miLista[:],len(miLista[:]))


if __name__ == '__main__':
    main()


        