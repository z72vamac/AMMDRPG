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



def clustering_easy(datos, paths, clusters):
    
    """
    datos: problem data,
    paths: list of (path_g, points_g, cost_g) associated to the graph g
    """
    
    nD = datos.nD
    nG = datos.m
    vD = datos.vD
    vC = datos.vC
    orig = datos.orig
    capacity = datos.capacity
    
    
    K_index = list(clusters.keys())
    G_index = range(1, nG + 1)
    
    
    MODEL = gp.Model('Clustering')
    
    ykg = MODEL.addVars(K_index, G_index, vtype = GRB.BINARY, name = 'ykg')
    
    dkg = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'dkg')
    difkg = MODEL.addVars(K_index, G_index, 2, vtype = GRB.CONTINUOUS, name = 'dkg')
    # pkg = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'pkg')
    
    
    dkg_prima = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'dkg_prima')
    difkg_prima = MODEL.addVars(K_index, G_index, 2, vtype = GRB.CONTINUOUS, name = 'dkg_prima')
    # pkg_prima = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'pkg_prima')
    
    
    dkk = MODEL.addVars(K_index, K_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dkk')
    difkk = MODEL.addVars(K_index, K_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difkk')
    # zkk = MODEL.addVars(K_index, K_index, vtype = GRB.BINARY, name = 'zkk')
    # pkk = MODEL.addVars(K_index, K_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pkk')
    
    dk = MODEL.addVars(K_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dk')
    difk = MODEL.addVars(K_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difk')
    
    
    Ck = MODEL.addVars(K_index, 2, vtype = GRB.CONTINUOUS, name = 'Ck')
    
    MODEL.update()
        
    # MODEL.addConstrs(ykg.sum(k, '*') <= nD for k in K_index)
    # MODEL.addConstrs(ykg.sum('*', g) == 1 for g in G_index)
    
    for k in clusters.keys():
        for g in clusters[k]:
            MODEL.addConstr(ykg[k, g] >= 0.5)
    # MODEL.addConstrs((pkg[k, g] <= BigM * ykg[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg[k, g] <= dkg[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg[k, g] >= SmallM * ykg[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg[k, g] >= dkg[k, g] - BigM * (1 - ykg[k, g])) for k, g in ykg.keys())
    
    # MODEL.addConstrs((pkg_prima[k, g] <= BigM * ykg[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg_prima[k, g] <= dkg_prima[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg_prima[k, g] >= SmallM * ykg[k, g]) for k, g in ykg.keys())
    # MODEL.addConstrs((pkg_prima[k, g] >= dkg_prima[k, g] - BigM * (1 - ykg[k, g])) for k, g in ykg.keys())
    
        
    MODEL.addConstrs((gp.quicksum(ykg[k, g]*dkg[k, g] for k in K_index) + paths[g-1][2] + gp.quicksum(ykg[k, g]*dkg_prima[k, g] for k in K_index))/vD <= capacity for g in G_index)
    # MODEL.addConstrs((dkk[k1, k2] / vC <= capacity for k1, k2 in dkk.keys()))
    
    MODEL.addConstrs((difkg[k, g, dim] >= (Ck[k, dim] - paths[g-1][1][0][dim])*14000/1e6 for k, g, dim in difkg.keys()))
    MODEL.addConstrs((difkg[k, g, dim] >= (- Ck[k, dim] + paths[g-1][1][0][dim])*14000/1e6 for k, g, dim in difkg.keys()))
    MODEL.addConstrs((difkg[k, g, 0] * difkg[k, g, 0] + difkg[k, g, 1] * difkg[k, g, 1] <= dkg[k, g] * dkg[k, g] for k, g in dkg.keys()))
    
    MODEL.addConstrs((difkg_prima[k, g, dim] >= (Ck[k, dim] - paths[g-1][1][1][dim])*14000/1e6 for k, g, dim in difkg_prima.keys()))
    MODEL.addConstrs((difkg_prima[k, g, dim] >= (- Ck[k, dim] + paths[g-1][1][1][dim])*14000/1e6 for k, g, dim in difkg_prima.keys()))
    MODEL.addConstrs((difkg_prima[k, g, 0] * difkg_prima[k, g, 0] + difkg_prima[k, g, 1] * difkg_prima[k, g, 1] <= dkg_prima[k, g] * dkg_prima[k, g] for k, g in dkg_prima.keys()))
    
    MODEL.addConstrs((difkk[k1, k2, dim] >= (Ck[k1, dim] - Ck[k2, dim])*14000/1e6 for k1, k2, dim in difkk.keys()))
    MODEL.addConstrs((difkk[k1, k2, dim] >= (-Ck[k1, dim] + Ck[k2, dim])*14000/1e6 for k1, k2, dim in difkk.keys()))
    MODEL.addConstrs(gp.quicksum(difkk[k1, k2, dim]*difkk[k1, k2, dim] for dim in range(2)) <= dkk[k1, k2]*dkk[k1, k2] for k1, k2 in dkk.keys())
    
    MODEL.addConstrs((difk[k, dim] >= (Ck[k, dim] - orig[dim])*14000/1e6 for k, dim in difk.keys()))
    MODEL.addConstrs((difk[k, dim] >= (-Ck[k, dim] + orig[dim])*14000/1e6 for k, dim in difk.keys()))
    MODEL.addConstrs(gp.quicksum(difk[k, dim]*difk[k, dim] for dim in range(2)) <= dk[k]*dk[k] for k in dk.keys())
    
    # objective = gp.quicksum(pkg[k, g] + pkg_prima[k, g] for k, g in pkg.keys()) + gp.quicksum(dkk[k1, k2] for k1, k2 in dkk.keys()) + gp.quicksum(dk[k] for k in dk.keys())
    objective = gp.quicksum(dkk[k1, k2] for k1, k2 in dkk.keys()) + gp.quicksum(dk[k] for k in dk.keys())# + gp.quicksum(zk[k]*BigM for k in zk.keys())
    
    MODEL.Params.OutputFlag = 1
    MODEL.setObjective(objective, GRB.MINIMIZE)
    
    MODEL.update()
    
    MODEL.optimize()
    
    MODEL.update()
    
    # print(Ck)
    # print(ykg)
    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result = []
        if datos.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return None
    
    
    return MODEL.getAttr('x', Ck)
    
    
    