# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

class Lego :

    def __init__(self, taille, couleur):
        self.taille = taille
        self.couleur = couleur
        self.modèle = (taille*2, couleur)

    def __repr__(self) -> str:
        print("ce lego est de couleur ")



Lego(4, 'bleue')
Lego(6, 'rouge')

print(Lego(4, 'bleue').modèle)


{1: ['Source', '2', 'Sink'],
 2: ['Source', '31', 'Sink'],
 3: ['Source', '1', 'Sink'],
 4: ['Source', '23', '11', '12', '16', 'Sink'],
 5: ['Source', '14', '15', '6', '38', 'Sink'],
 6: ['Source', '34', '33', 'Sink'],
 7: ['Source', '40', '32', 'Sink'],
 8: ['Source', '8', '30', '5', 'Sink']}


import time
import random

def profit():
    l = []
    for i in range(100000):
        l.append(i**2)
    return l

def loss():
    l = []
    for i in range(100000) :
        l.append(i*2)
    return l

def total(l1, l2):
    l = []
    for i in range(100000) :
        l.append(l1[i] + l2[i])
    return l



a = time.time()
x = profit()
y = loss()
z = total(x, y)
print("z=", z[9999])
b = time.time()
print(b-a)

import dask
profit = dask.delayed(profit)
loss = dask.delayed(loss)
total = dask.delayed(total)

# +
a = time.time()
print("a", a)
x = profit()
y = loss()
z = total(x, y)
b = time.time()
print("b", b)

print(z.compute()[9999])
c = time.time()
print("temps d'execution", b-a)
print("temps d'execution", c-a)
# z.visualize(rankdir='LR')

# +
# z.visualize()
# -

def profit(x, y):
    time.sleep(3)
    return x+y


def loss(x, y):
    time.sleep(3)
    return x-y


def total(x, y):
    time.sleep(3)
    return x+y


a = time.time()
print("a", a)
x = profit(15, 20)
y = loss(25, 10)
z = total(x, y)
b = time.time()
print("b", b)
print("temps d'execution", b-a)

profit = dask.delayed(profit)
loss = dask.delayed(loss)
total = dask.delayed(total)

a = time.time()
print("a", a)
x = profit(15, 20)
y = loss(25, 10)
z = total(x, y)
b = time.time()
print("b", b)
print(z.compute())
c = time.time()
print("temps d'execution", b-a)
print("temps d'execution", c-a)
# z.visualize(rankdir='LR')


