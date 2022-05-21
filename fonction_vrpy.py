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

nodes = {
    "0" : [48.845483, 2.34145],
    "1" : [48.84398, 2.339001],
    "2" : [48.843641, 2.340548], 
    "3" : [48.843384, 2.341554], 
    "4" : [48.844355, 2.342002], 
    "5" : [48.846296, 2.340244], 
    "6" : [48.846057, 2.341126], 
    "7" : [48.845582, 2.342657], 
    "8" : [48.846642, 2.341607],
    "9" : [48.846411, 2.342591], 
    "10" : [48.846105, 2.34298], 
    "11" : [48.84733, 2.340717], 
    "12" : [48.8471, 2.341967], 
    "13" : [48.846896, 2.34282], 
    "14" : [48.846773, 2.343323]
        }

for node in nodes : 
    a = nodes[node][0]
    nodes[node][0] = nodes[node][1]
    nodes[node][1] = a


N_nodes = len(nodes)
matrix_durations = np.zeros((N_nodes,N_nodes))
liste_itineraires = []

i = 0 
for node_start in nodes : 
    liste_itineraires.append([])
    start_x = nodes[node_start][0]
    start_y = nodes[node_start][1]
    print(i)
    j = 0
    for node_end in nodes :
        end_x = nodes[node_end][0]
        end_y = nodes[node_end][1]
        texte = requests.get("https://wxs.ign.fr/essentiels/geoportail/itineraire/rest/1.0.0/route?resource=bdtopo-osrm&start=" + str(start_x) + "," + str(start_y) + "&end=" + str(end_x) + "," + str(end_y) + "&timeUnit=second")
        texte = json.loads(texte.text)
        itineraire = texte['geometry']['coordinates']
        duration = texte['duration']
        matrix_durations[i,j] = duration 
        liste_itineraires[i].append(itineraire)  #Donc liste_itineraires[i][j] c'est l'itineraire pour aller de i vers j. 
        j+=1
    i+=1 


def itinary(noeuds): #dans les noeuds concernés, on ne donne pas le noeud 0 qui est le point de départ toujours.  
    G = DiGraph()

    for noeud in noeuds : # ici on crée les edges entre les noeuds et le début / la fin qui est au noeud 0. 
        G.add_edge('Source', noeud, cost = matrix_durations[0,eval(noeud)])
        G.add_edge(noeud, 'Sink', cost = matrix_durations[eval(noeud),0])
    for start in noeuds: 
        for ending in noeuds:
            G.add_edge(start, ending, cost = matrix_durations[eval(start),eval(ending)])
    
    prob = VehicleRoutingProblem(G, load_capacity=10)
    prob.solve()
    ordre_passage = prob.best_routes[(1)]

    N_points = len(ordre_passage)  - 2 #-2 pour ne pas compter source et sink. 
    c = 1 #indice courant du point que l'on traite 

    best_way = liste_itineraires[0][eval(ordre_passage[c])]
    while c != len(ordre_passage) - 2:
        best_way += liste_itineraires[eval(ordre_passage[c])][eval(ordre_passage[c+1])]
        c += 1 
    best_way += liste_itineraires[eval(ordre_passage[c])][0]
    return best_way