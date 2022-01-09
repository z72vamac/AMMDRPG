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


def aglomerativo(datos, paths):
    
    def canLink(list):
        """ Receives a list and print if possible to link having account the capacity constraint
        """
        
        print('Resolviendo el problema de factibilidad para los clusters {0} y {1}'.format(list[0], list[1]))
        
        paths_problem = []
        
        for i in list:
            for g in clusters[i]:
                paths_problem.append(paths[g-1])
                
        
        nPaths = len(paths_problem)
        
        if nPaths > datos.nD:
            print('Drone capacity satisfied')
            print()
            return False
        
        MODEL = gp.Model('Can_Link')
        
        # Centroid
        C = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'C')
        
        dRg = MODEL.addVars(nPaths, vtype = GRB.CONTINUOUS, name = 'dRg')
        difRg = MODEL.addVars(nPaths, 2, vtype = GRB.CONTINUOUS, name = 'difRg')
        
        dLg = MODEL.addVars(nPaths, vtype = GRB.CONTINUOUS, name = 'dLg')
        difLg = MODEL.addVars(nPaths, 2, vtype = GRB.CONTINUOUS, name = 'difLg')
        
        MODEL.update()
        
        MODEL.addConstrs(difLg[g, dim] >=  (paths_problem[g][1][1][dim] - C[dim])*14000/1e6 for g, dim in difLg.keys())
        MODEL.addConstrs(difLg[g, dim] >= (-paths_problem[g][1][1][dim] + C[dim])*14000/1e6 for g, dim in difLg.keys())
        MODEL.addConstrs(gp.quicksum(difLg[g, dim]*difLg[g, dim] for dim in range(2)) <= dLg[g]*dLg[g] for g in dLg.keys())
        
        MODEL.addConstrs(difRg[g, dim] >=  (paths_problem[g][1][0][dim] - C[dim])*14000/1e6 for g, dim in difRg.keys())
        MODEL.addConstrs(difRg[g, dim] >= (-paths_problem[g][1][0][dim] + C[dim])*14000/1e6 for g, dim in difRg.keys())
        MODEL.addConstrs(gp.quicksum(difRg[g, dim]*difRg[g, dim] for dim in range(2)) <= dRg[g]*dRg[g] for g in dLg.keys())
        
        MODEL.addConstrs((dLg[g] + paths_problem[g][2] + dRg[g])/datos.vD <= datos.capacity for g in dLg.keys())
        
        objective = 1
        
        MODEL.setObjective(objective, GRB.MINIMIZE)
        
        MODEL.update()
        MODEL.Params.OutputFlag = 0
        
        MODEL.optimize()
        
        MODEL.update()
        
        if MODEL.Status == GRB.INFEASIBLE:
            return False
        
        if MODEL.Status == GRB.OPTIMAL:
            print('El problema es factible para estos clusters')
            print('Pegamos el cluster {0} y el cluster {1}'.format(list[0], list[1]))
            print()
            return True
        
    
    """
    datos: problem data,
    paths: list of (path_g, points_g, cost_g) associated to the graph g
    """
    nG = datos.m
    
    G_index = range(1, nG+1)
    
    clusters = {}
    
    for g in G_index:
        clusters[g] = [g]
        
    nIter = 15
    
    for i in range(nIter):
        
        if len(list(clusters.keys())) > 2:
            lista = random.sample(list(clusters.keys()), 2)
        else:
            break
        
        representante = min(lista)
        eliminado = max(lista)
        
        # print(lista)
        
        if canLink(lista):
            
            cluster_graphs = []
            
            for i in lista:
                for g in clusters[i]:
                    cluster_graphs.append(g)
                    
            clusters[representante] = cluster_graphs
            
            del clusters[eliminado]
        else:
            print('El problema es infactible para estos clusters')
            print()
                
    # print(clusters)
    
    return clusters
            
    
    


    
    