import folium 
import numpy as np 
import matplotlib.pyplot as plt
import random as rd 
import requests
import json 
from folium import plugins
from folium.plugins import HeatMap
import time 

green = '#80FF00'
yellow = '#FFFF00'
orange ='#FF8000'
red = '#FF0000'

def center(summits): 
    y1, x1 = summits[0]
    y2, x2 = summits[1]
    y3, x3 = summits[2]
    y_milieu = y1 + (y3-y2)/2
    x_milieu = x1 + (x2-x1)/2
    return [y_milieu, x_milieu]


def fusion(t1,t2):
            if t1==[]:
                return t2
            elif t2==[]:
                return t1
            else:
                if t1[0][0]<t2[0][0]:
                    return [t1[0]] + fusion(t1[1:],t2)
                else:
                    return [t2[0]] + fusion(t1,t2[1:])


def tri_fusion(T):
    if len(T)<=1:
        return T
    else:
        c = len(T)//2
    return fusion(tri_fusion(T[0:c]),tri_fusion(T[c:]))



def tri_insertion(liste):
    L = list(liste) # copie de la liste
    N = len(L)
    for n in range(1,N):
        cle = L[n]
        j = n-1
        while j>=0 and L[j][0] > cle[0]:
            L[j+1] = L[j] # decalage
            j = j-1
        L[j+1] = cle
    return L



def change(way, dmax, dmin, h): #dmax c'est la distance maximale autorisée entre deux points : si est dépassé, on en crée de nouveaux. dmin c'est l'inverse : on détruit un point. h c'est la distance optimale, entre les deux.   
    N = len(way)
    c = 0 #C'est l'indice courant, on se déplace le long du chemin.
    while c+1 != N: 
        D = dist(way[c],way[c+1]) #Distance between start and arrival  
        x1, y1 = way[c]
        x2, y2 = way[c+1]
        if D > dmax: 
            x = (h/D)*(x2 - x1) + x1
            y = (h/D)*(y2 - y1) + y1
            way.insert(c+1, [x,y])
            c += 1
        elif D < dmin : 
            way.pop(c+1)
        else : 
            c += 1
        N = len(way)
    return way 


def dist(u,v):
    return ((v[0]-u[0])**2 + (u[1]-v[1])**2)**0.5



class division : 
    def __init__(self, coordinates, traffic) : 
        self.coordinates = coordinates
        self.traffic = traffic 
        self.summits = [coordinates[0], [coordinates[0][0], coordinates[1][1]], coordinates[1], [coordinates[1][0], coordinates[0][1]]]
        summits = self.summits
        self.edges = [[summits[0], summits[1]], [summits[1], summits[2]]]
        self.center = center(summits)
    
    def draw(self, map): 
        summits = self.summits 
        traffic = self.traffic 
        bounds = [
            [summits[0][0], summits[3][1]],
            [summits[3][0], summits[2][1]]
            ]
        if traffic == 0: 
            color = green 
        elif traffic > 0 and traffic <= 0.33: 
            color = yellow
        elif traffic > 0.33 and traffic < 0.66:    
            color = orange 
        else : 
            color = red
            
            
        rectangle = folium.Rectangle(bounds, stroke = True, color = color, fill = False, fillopacity = 100, fillcolor = color, weight = 7)
        rectangle.add_to(map)
        



class grid : 
    def __init__(self, coordinates, N): 
        Y0, X0 = coordinates[0]
        Y1, X1 = coordinates[1]
        delta_Y = Y1 - Y0
        delta_X = X1 - X0 
        delta_y = delta_Y/N
        delta_x = delta_X/N

        self.delta_x = delta_x
        self.delta_y = delta_y
        self.N = N 
        self.coordinates = coordinates

        matrix = []
        for i in range (N): 
            matrix.append([])
        for i in range(N): 
            for j in range(N): 
                coordiv = [Y0 + i*delta_y, X0 + j*delta_x], [Y0 + i*delta_y + delta_y, X0 + j*delta_x + delta_x]
                matrix[i].append(division(coordinates = coordiv, traffic = 0))
        
        self.matrix = matrix 
        self.cases_avec_traffic = []
    



    def draw(self, map):
        matrix = self.matrix 
        N = self.N
        for i in range(N): 
            for j in range(N): 
                div = matrix[i][j]
                div.draw(map)
                



    def traffic_grow(self, itineraire, h): #h c'est l'aire d'influence d'un point, on a une décroissance linéaire du centre du point jusq'à la distance .  
        coorgrid = self.coordinates
        Y0, X0 = coorgrid[0]
        Y1, X1 = coorgrid[1]
        delta_x = self.delta_x
        delta_y = self.delta_y 
        N = len(self.matrix)
        cases_avec_traffic = []
        for point in itineraire: 
            i = 0
            j = 0
            while Y0 + i*delta_y < point[0]: 
                i+= 1
            i-=1
            I = i #servira plus tard
            while X0 + j*delta_x < point[1]: 
                j+= 1
            j-=1
            J = j #servira plus tard
            if i >= 0 and i < N and j >= 0 and j < N: 
                self.matrix[i][j].traffic += 1 #on colorie déjà la case au centre 
            

            #Avoir le rayon du cercle de changement de couleur 
            #cases à tester vers la droite
            count_y = 0
            dy = delta_y
            while dy <= h :
                count_y += 1
                dy += delta_y 
            
            #cases à tester vers le haut
            count_x = 0 
            dx = delta_x
            while dx <= h: 
                count_x += 1
                dx += delta_x
            
            count = max(count_x, count_y)

            i = I - count
            for a in range(2*count): 
                i += 1
                j = J - count
                for b in range(2*count): 
                    j += 1 
                    if i >= 0 and i < N and j >= 0 and j < N: 
                        point_centre = self.matrix[i][j].center 
                        d = dist(point_centre, point)
                        if d > 0.00000001: #pour éviter que l'on est le point initial
                            if d <= h :
                                self.matrix[i][j].traffic += 1 - d/h
        

    def normalisation_traffic(self): 
        for i in range(len(self.matrix)): 
            for j in range(len(self.matrix)): 
                if self.matrix[i][j].traffic != 0: 
                    self.cases_avec_traffic.append([self.matrix[i][j].traffic, [i,j]])
        self.cases_avec_traffic = tri_insertion(self.cases_avec_traffic)
        N_cases_avec_traffic = len(self.cases_avec_traffic)
        c = 0 #l'indice courant 
        while c/N_cases_avec_traffic < 1/3 : 
            i = self.cases_avec_traffic[c][1][0]
            j = self.cases_avec_traffic[c][1][1]
            self.matrix[i][j].traffic = 0.1 #on met la case en jaune pour le tier où il y a le moins de traffic. 
            c += 1
        while c/N_cases_avec_traffic < 2/3 : 
            i = self.cases_avec_traffic[c][1][0]
            j = self.cases_avec_traffic[c][1][1]
            self.matrix[i][j].traffic = 0.4 #on met la case en orange pour le deuxième tier 
            c += 1
        while c/N_cases_avec_traffic < 1 : 
            i = self.cases_avec_traffic[c][1][0]
            j = self.cases_avec_traffic[c][1][1]
            self.matrix[i][j].traffic = 0.7 #on met la case en rouge pour le dernier tier 
            c += 1
        print('Le traffic est désormais normalisé')



def heatmap(itinaries, boundaries, N, h): 
    # itinaries ce sont tous les itineraires que l'on a eu à partir de vrpy
    # boundaries c'est les coordonnées des deux extrémaux du carré qui définit l'espace dans lequel on trace la heatmap et sont contenus les itinéraires
    # N c'est la taille de la grille finale que l'on souhaite 
    
    N_iti = len(itinaries)
    k = 0 #c'est l'indice courant pour savoir combien d'itinéraire on a déjà fait l'actualisation du traffic 
    
    map = folium.Map(location=boundaries[0],zoom_start= 15)
    grille = grid(boundaries, N)

    for iti in itinaries: #on suppose que l'itinéraire iti a déjà été modifié (les points sont bien régulièrement espacés etc...)
        grille.traffic_grow(iti, h)
        k += 1
        print('vous avez fait', (k/N_iti)*100, 'pourcent des trajets à faire')

    grille.normalisation_traffic()
    grille.draw(map)
    folium.TileLayer('cartodbdark_matter').add_to(map)
    return map