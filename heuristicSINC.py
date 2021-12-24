import gurobipy as gp
import pdb
from gurobipy import GRB
import numpy as np
from itertools import product
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
from data import *
from entorno import *
import copy
import estimacion_M as eM
import networkx as nx
import auxiliar_functions as af
from vns import *
import time
from grafo_problem import grafo_problem
from clustering_easy import clustering_easy
from tsp import tsp
from aglomerativo import aglomerativo
from AMMDRPGSTSINCPARTIAL import AMMDRPGSTSINCPARTIAL


# # Primer paso: Generamos datos
# np.random.seed(5)
#
# lista = list(4*np.ones(10, int))
#
# nG = len(lista)
# datos = Data([], m=nG, grid = True, tmax=60, alpha = True, nD = 4, capacity = 30,
             # init=False,
             # show=True,
             # seed=2)
             #
# datos.generar_grid() 
# datos.generar_grafos(lista)

def heuristicSINC(datos):
    # Segundo paso: Resolvemos utilizando grafo problem 
    
    nG = datos.m
    
    paths = []
    
    for g in range(1, nG+1):
        path = grafo_problem(datos.data[g-1], datos.alpha)
        paths.append(path)
        
    print()
    print(paths)
    print()
    
    seeds = 20
    
    best_clusters = {}
    # best_Ck = {}
    best_uigtd = {}
    best_vigtd = {}
    best_objval = 100000
    best_path = []
    
    for i in range(seeds):
        np.random.seed(i)
        
        # Tercer paso: Algoritmo aglomerativo para clustering_hard
        clusters = aglomerativo(datos, paths)
        
        
        objVal, uigtd, vigtd = AMMDRPGSTSINCPARTIAL(datos, clusters)
        
        
        # # Cuarto paso: Resolvemos la localizacion de los puntos una vez formado el clustering_hard
        # Ck = clustering_easy(datos, paths, clusters)
        #
        # path, objVal = tsp(Ck)
        #
        if objVal <= best_objval:
            best_clusters = clusters
            best_objval = objVal
            # best_Ck = Ck
            best_uigtd = uigtd
            best_vigtd = vigtd
            best_path = path
    
    
    uigtd_sol = best_uigtd
    vigtd_sol = best_vigtd
    
    
    # for i, t in zip(best_path, range(1, len(best_path)+1)):
        # for g, d in zip(best_clusters[i], range(len(best_clusters[i]))):
            # e1 = paths[g-1][0][0]
            # e2 = paths[g-1][0][-1]
            # uigtd_sol.append((e1, g, t, d))
            # vigtd_sol.append((e2, g, t, d))
            #
    # print(uigtd_sol)
    # print(vigtd_sol)
    
    
    print()
    print(best_clusters)
    print(best_objval)
    print(uigtd_sol)
    print(vigtd_sol)
    
    # print(best_path)
    
    # fig, ax = plt.subplots()
    #
    # for g in range(1, datos.m+1):
        # grafo = datos.data[g-1]
        # centroide = np.mean(grafo.V, axis = 0)
        # nx.draw(grafo.G, grafo.pos, node_size=100, node_color='black', alpha=1, width = 1, edge_color='black')
        # ax.annotate(g, xy = (centroide[0], centroide[1]))
        # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=9)
        #
    # colores = ['blue', 'green', 'red', 'purple', 'black', 'yellow', 'brown']
    #
    # for (k, i) in zip(best_clusters.keys(), range(len(best_clusters.keys()))):
        # plt.plot(best_Ck[(k, 0)], best_Ck[(k, 1)], 'ko', color = colores[i])
        # ax.annotate(k, xy = (best_Ck[(k, 0)], best_Ck[(k, 1)]))
        #
    # plt.show()        
    

    return uigtd_sol, vigtd_sol

