import folium 
import numpy as np 
import matplotlib.pyplot as plt
import random as rd 
import requests
import json 
from folium import plugins
from folium.plugins import HeatMap
import time 
from networkx import DiGraph
from vrpy import VehicleRoutingProblem
import random as rd 
from time import * 


def dist(u,v):
    return ((v[0]-u[0])**2 + (u[1]-v[1])**2)**0.5


def distanceGPS(A,B):
    """Retourne la distance en mètres entre les 2 points A et B connus grâce à
       leurs coordonnées GPS (en radians).
    """
    # Rayon de la terre en mètres (sphère IAG-GRS80)
    latA = 2*np.pi*A[0]/360
    longA = 2*np.pi*A[1]/360
    latB = 2*np.pi*B[0]/360
    longB = 2*np.pi*B[1]/360
    RT = 6378137
    # angle en radians entre les 2 points
    S = 2*np.sqrt(np.sin((latB-latA)/2)**2+np.cos(latA)*np.cos(latB)*np.sin((longB-longA)/2)**2)
    # S = np.arccos(np.sin(latA)*np.sin(latB) + np.cos(latA)*np.cos(latB)*np.cos(abs(longB-longA)))
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT

    
def change(way, dmax, dmin, h): #
    """
    dmax c'est la distance maximale autorisée entre deux points : si est dépassé, on en crée de nouveaux
    dmin c'est l'inverse : on détruit un point. h c'est la distance optimale, entre les deux.   
    """
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


def route_dect(itineraire): 
    """
    Cette fonction nous permet de connaître toutes les routes de notre itinéraire. 
    Chacun de ces éléments correspond à une liste qui définit une route : noeud de début, noeud d'arrivée (en coordonnées)
    """
    theta = 0 
    N = len(itineraire)
    routes = [[itineraire[0]]] # Chaque élément de routes est une route, avec un point de départ, et un point d'arrivée. 
    for k in range(N-2):
        a = distanceGPS(itineraire[k+2], itineraire[k+1])
        b = distanceGPS(itineraire[k+2], itineraire[k])
        c = distanceGPS(itineraire[k], itineraire[k+1]) 
        try :
            theta = round(np.arccos((a**2 - b**2 - c**2)/(-2*b*c))*360/(2*np.pi))

        except ValueError:
            theta = 0
        if theta >= 35 : #cela signifie que le prochain point est le départ d'une nouvelle route. 
            routes.append([])
            routes[-1].append(itineraire[k+1]) #On ouvre une nouvelle route 
            routes[-2].append(itineraire[k]) #Et on ferme l'ancienne 
    return routes


def construction_matrices(nodes):
    """
    Cette fonction prend en entrée la liste des noeuds qui ont été prédéfinis. 
    Elle renvoie d'une part la matrice des itinéraires entre les noeuds et d'autre part la matrice des temps de trajet entre les noeuds. 
    """
    N_nodes = len(nodes)
    matrix_durations = np.zeros((N_nodes,N_nodes))
    liste_itineraires = []

    i = 0 
    for node_start in nodes :
        liste_itineraires.append([])
        start_x = nodes[node_start][1] 
        start_y = nodes[node_start][0]
        print(f'i = {i}')
        j = 0
        for node_end in nodes :
            end_x = nodes[node_end][1] 
            end_y = nodes[node_end][0]
            texte = requests.get("https://wxs.ign.fr/essentiels/geoportail/itineraire/rest/1.0.0/route?resource=bdtopo-osrm&start=" + f'{str(start_x)},{str(start_y)}&end={str(end_x)},{str(end_y)}&timeUnit=second')
            texte = json.loads(texte.text)
            itineraire = texte['geometry']['coordinates']
            duration = texte['duration']
            matrix_durations[i,j] = duration 
            for element in itineraire: 
                if round(element[0]) == 2 : 
                    p = element[0]
                    element[0] = element[1]
                    element[1] = p 
            itineraire_points = change(itineraire,  0.00025, 0.0002, 0.000225)

            #il va maintenant falloir modifier cela en liste de noeuds. 
            itineraire_noeuds = []
            for point in itineraire_points :
                for node in nodes : 
                    if node not in itineraire_noeuds and dist(point, nodes[node]) <= 0.00045 : 
                        itineraire_noeuds.append(node)
            liste_itineraires[i].append(itineraire_noeuds)  #Donc liste_itineraires[i][j] c'est l'itineraire pour aller de i vers j en parlant en noeud. 
            j+=1
        i+=1 
    return liste_itineraires, matrix_durations