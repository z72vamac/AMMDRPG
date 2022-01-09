# Incluimos primero los paquetes
import gurobipy as gp
import pdb
from gurobipy import GRB
import numpy as np
from itertools import product
import random
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
from data import *
import entorno as e
import copy
import estimacion_M as eM
import networkx as nx
# from AMMDRPGST import AMMDRPGST
from synchronous_version_withoutd import SYNCHRONOUS

data = []

for i in range(1, 7):
    puntos = pd.read_excel('./case_study/patios_breakpoints.xlsx', sheet_name='Ruta'+str(i))
    
    puntos['y'] = 200 - puntos['y']

    V = copy.copy(puntos.to_numpy())
    
    m = V.shape[0]
    
    Ar = np.zeros((m+1, m+1))
    
    if i == 1 or i == 2 or i == 5:
        for j in range(m):
            Ar[j, j+1] = 1
        
    if i == 3:
        for j in range(15):
            Ar[j, j+1] = 1
        
        Ar[2, 16] = 1
        Ar[16, 17] = 1
        Ar[9, 18] = 1
    
    if i == 4:
        for j in range(24):
            Ar[j, j+1] = 1
        
        Ar[6, 25] = 1
        Ar[20, 26] = 1
        Ar[21, 27] = 1
    
    if i == 6:
        for j in range(23):
            Ar[j, j+1] = 1
        
        Ar[2, 24] = 1
        Ar[24, 25] = 1
        Ar[13, 26] = 1
        Ar[14, 27] = 1
        
    
    data.append(e.Grafo(V, Ar, 1))



datos = Data(data, m=6, grid = True, tmax=60, alpha = False, nD = 2, capacity = 0.123672786,
        init=False,
        show=True,
        vC = 30,
        vD = 43,
        orig = [0, 0],
        dest = [0, 0],
        seed=2)

print(sum([grafo.longitud for grafo in data])*14000/1e6)

# velocities = np.linspace(1.5, 3, 16)

# for n in range(1, 4):
#     for cap in range(200, 205, 5):
#         for v in range(len(velocities)):
#             datos = Data(data, m=6, grid = True, tmax=1, alpha = False, nD = n, capacity = cap,
#                         init=False,
#                         show=True,
#                         vD = velocities[v],
#                         orig = [0, 0],
#                         dest = [0, 0],
#                         seed=2)
#
#             fig, ax = plt.subplots()
#
#             grafos = datos.data
            
            # colors = ['blue', 'purple', 'cyan', 'orange', 'red', 'green']
            # for g in range(1, 7):
                # grafo = grafos[g-1]
                # centroide = np.mean(grafo.V, axis = 0)
                # nx.draw(grafo.G, grafo.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
                # ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
                # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)
            

SYNCHRONOUS(datos)

# plt.show()