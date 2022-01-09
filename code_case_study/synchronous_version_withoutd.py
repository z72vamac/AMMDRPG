"""Tenemos un conjunto E de entornos y un conjunto de poligonales P de las que queremos recorrer un porcentaje alfa p . Buscamos
   un tour de mínima distancia que alterne poligonal-entorno y que visite todas las poligonales"""


# Incluimos primero los paquetes
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
from heuristic import heuristic
import ast


# np.random.seed(4)
#
# lista = list(4*np.ones(3, np.int))
# nG = len(lista)
# datos = Data([], m=nG, grid = True, tmax=150, alpha = True,
#              init=True,
#              show=True,
#              capacity = 100,
#              seed=2)
#
# datos.generar_grid()
#
#
#
# datos.generar_grafos(lista)

def SYNCHRONOUS(datos): #, vals_xL, vals_xR):

    
    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            if model.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                # creates new model attribute '_startobjval'
                model._startobjval = model.cbGet(GRB.Callback.MIPSOL_OBJ)
                
    grafos = datos.mostrar_datos()

    result = []

    nG = datos.m
    nD = datos.nD
    
        
    print('SYNCHRONOUS VERSION. Settings:  \n')
    
    print('Number of graphs: ' + str(datos.m))
    print('Number of drones: ' + str(datos.nD))
    print('Endurance: ' + str(datos.capacity))
    print('Speed of Mothership: ' + str(datos.vC))
    print('Speed of Drone: ' + str(datos.vD) + '\n')
    
    T_index = range(datos.m + 2)
    T_index_prima = range(1, datos.m+1)
    T_index_primaprima = range(datos.m+1)
    D_index = range(nD)
    
    Capacity = datos.capacity


    # Creamos el modelo8
    MODEL = gp.Model("PD-Stages")

    # Variables que modelan las distancias
    # Variable binaria uigt = 1 si en la etapa t entramos por el segmento sig
    uigt_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            for t in T_index_prima:
                uigt_index.append((i, g, t))


    uigt = MODEL.addVars(uigt_index, vtype=GRB.BINARY, name='uigt')

    # Variable continua no negativa dLigt que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sig.
    dLigt_index = uigt_index

    dLigt = MODEL.addVars(dLigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLigt')
    difLigt = MODEL.addVars(dLigt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLigt')

    # Variable continua no negativa pLigt = uigt * dLigt
    pLigt_index = uigt_index

    pLigt = MODEL.addVars(pLigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pLigt')


    # Variable binaria vigt = 1 si en la etapa t salimos por el segmento sig
    vigt_index = uigt_index

    vigt = MODEL.addVars(vigt_index, vtype=GRB.BINARY, name='vigt')

    # Variable continua no negativa dRigt que indica la distancia desde el punto de salida del segmento sig hasta el
    # punto de recogida del camion
    dRigt_index = uigt_index

    dRigt = MODEL.addVars(dRigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRigt')
    difRigt = MODEL.addVars(dRigt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRigt')


    # Variable continua no negativa pRigt = vigt * dRigt
    pRigt_index = uigt_index

    pRigt = MODEL.addVars(pRigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pRigt')


    # Variable binaria zigjg = 1 si voy del segmento i al segmento j del grafo g.
    zigjg_index = []
    sig_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sig_index.append((i, g))
            for j in grafos[g-1].aristas:
                if i != j:
                    zigjg_index.append((i, j, g))

    zigjg = MODEL.addVars(zigjg_index, vtype=GRB.BINARY, name='zigjg')
    sig = MODEL.addVars(sig_index, vtype=GRB.CONTINUOUS, lb=0, name='sig')

    # Variable continua no negativa digjg que indica la distancia entre los segmentos i j en el grafo g.
    digjg_index = zigjg_index

    digjg = MODEL.addVars(digjg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='digjg')
    difigjg = MODEL.addVars(digjg_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difigjg')

    # Variable continua no negativa pigjg = zigjg * digjg
    pigjg_index = zigjg_index

    pigjg = MODEL.addVars(pigjg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pigjg')

    # Variable continua no negativa dRLt que indica la distancia entre el punto de recogida en la etapa t y el punto de
    # salida para la etapa t+1
    dRLt_index = T_index_primaprima

    dRLt = MODEL.addVars(dRLt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRLt')
    difRLt = MODEL.addVars(dRLt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRLt')

    # Variable continua no negativa dLRt que indica la distancia que recorre el camión en la etapa t mientras el dron se mueve
    dLRt_index = T_index

    dLRt = MODEL.addVars(dLRt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLRt')
    difLRt = MODEL.addVars(dLRt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLRt')

    betat = MODEL.addVars(T_index, vtype = GRB.BINARY, lb = 0, ub = 1, name = 'betat')

    # Variables que modelan los puntos de entrada o recogida
    # xLt: punto de salida del dron del camion en la etapa t
    xLt_index = []

    for t in T_index:
        for dim in range(2):
            xLt_index.append((t, dim))

    xLt = MODEL.addVars(xLt_index, vtype=GRB.CONTINUOUS, name='xLt')

    # xRt: punto de recogida del dron del camion en la etapa t
    xRt_index = []

    for t in T_index:
        for dim in range(2):
            xRt_index.append((t, dim))

    xRt = MODEL.addVars(xRt_index, vtype=GRB.CONTINUOUS, name='xRt')
    
    timetD = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'timetD')
    timetM = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'timetM')
    
    
    # Rig: punto de recogida del dron para el segmento sig
    Rig_index = []
    rhoig_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhoig_index.append((i, g))
            for dim in range(2):
                Rig_index.append((i, g, dim))

    Rig = MODEL.addVars(Rig_index, vtype=GRB.CONTINUOUS, name='Rig')
    rhoig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhoig')

    # Lig: punto de lanzamiento del dron del segmento sig
    Lig_index = Rig_index
    landaig_index = rhoig_index

    Lig = MODEL.addVars(Lig_index, vtype=GRB.CONTINUOUS, name='Lig')
    landaig = MODEL.addVars(landaig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landaig')

    # Variables difiliares para modelar el valor absoluto
    minig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='minig')
    maxig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxig')
    entryig = MODEL.addVars(rhoig_index, vtype=GRB.BINARY, name='entryig')
    muig = MODEL.addVars(rhoig_index, vtype = GRB.BINARY, name = 'muig')
    pig = MODEL.addVars(rhoig_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pig')
    alphaig = MODEL.addVars(rhoig_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphaig')

    MODEL.update()
    
    if datos.init:
        
        hola = heuristic(datos)
        
        if hola != None:
            uigt_sol = hola[0]
            vigt_sol = hola[1]
            z_sol = hola[2]
            heuristic_time = hola[3]
            # uigt_sol, vigt_sol, z_sol, heuristic_time = heuristic(datos)
        
        # for i, g, t in uigt_sol:
            # uigt[i, g, t].start = 1
            #
        
        # my_file = open('./case_study/uigt_keys.txt', "r")
        # content = my_file.read()
        
        
        # uigt_sol = ast.literal_eval(content[:-1])

        # MODEL.read('./case_study/uigt.sol')
        
            for i, g, t in uigt.keys():
                if (i, g, t) in uigt_sol:
                    uigt[i, g, t].start = 1
                else:
                    uigt[i, g, t].start = 0
        
        # my_file = open('./case_study/vigt_keys.txt', "r")
        # content = my_file.read()
        #
        #
        # vigt_sol = ast.literal_eval(content)


            for i, g, t in vigt.keys():
                if (i, g, t) in vigt_sol:
                    vigt[i, g, t].start = 1
                else:
                    vigt[i, g, t].start = 0
            
            for i, j, g in zigjg.keys():
                if (i, j, g) in z_sol:
                    zigjg[i, j, g].start = 1
                else:
                    zigjg[i, j, g].start = 0
        # for g in T_index_prima:
            # MODEL.read('./case_study/graph' + str(g) + '.sol')
        # for i, g, t in vigt_sol:
            # vigt[i, g, t].start = 1
            #
    # En cada etapa hay que visitar/salir un segmento de un grafo
    MODEL.addConstrs(uigt.sum('*', '*', t) <= nD for t in T_index_prima)
    MODEL.addConstrs(vigt.sum('*', '*', t) <= nD for t in T_index_prima)

    # # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs(uigt.sum('*', g, '*') == 1 for g in T_index_prima)
    MODEL.addConstrs(vigt.sum('*', g, '*') == 1 for g in T_index_prima)

    # VI-1
    MODEL.addConstrs(betat[t] <= betat[t+1] for t in T_index_prima)
    
    # VI-2
    MODEL.addConstrs(gp.quicksum(uigt[i, g, t1] for i, g, t1 in uigt.keys() if t1 < t) >= nG*betat[t] for t in T_index_prima)
    
    # VI-3
    MODEL.addConstrs(gp.quicksum(uigt[i, g, t1] for i, g, t1 in uigt.keys() if t1 == t) >= 1 - betat[t] for t in T_index)
    
    # MODEL.addConstrs(uigt.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vigt.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs(muig[i, g] - uigt.sum(i, g, '*') == zigjg.sum('*', i, g) for i, g in rhoig.keys())
    MODEL.addConstrs(muig[i, g] - vigt.sum(i, g, '*') == zigjg.sum(i, '*', g) for i, g in rhoig.keys())

    MODEL.addConstrs(uigt.sum('*', g, t) - vigt.sum('*', g, t) == 0 for t in T_index_prima for g in T_index_prima)

    # MODEL.addConstrs(uigt[i, g, t] == vgi)
    # MODEL.addConstrs((uigt.sum(i, g, '*') + zigjg.sum(g, '*', i))
    #                  - (vigt.sum(i, g, '*') + zigjg.sum(i, g, '*')) == 0 for g in T_index_prima for i in grafos[g-1].aristas)

    MODEL.addConstrs(pig[i, g] >= muig[i, g] + alphaig[i, g] - 1 for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= muig[i, g] for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= alphaig[i, g] for i, g in rhoig.keys())

    # MODEL.addConstr(uigt[0, 101, 0] == 0)
    # MODEL.addConstr(uigt[0, 101, 1] == 0)


    # Eliminación de subtours
    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            for j in grafos[g-1].aristas[0:]:
                if i != j:
                    MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sig[i, g] - sig[j, g]) + grafos[g-1].num_aristas * zigjg[i, j, g])
                    
    # for g in range(nG):
    #     MODEL.addConstr(sig[g, grafos[g].aristas[0]] == 0)
    
    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            MODEL.addConstr(sig[i, g] >= 0)
            MODEL.addConstr(sig[i, g] <= grafos[g-1].num_aristas - 1)
    
    # Restricciones de distancias y producto
    MODEL.addConstrs((difLigt[i, g, t, dim] >=  (xLt[t, dim] - Rig[i, g, dim])*14000/1e6) for i, g, t, dim in difLigt.keys())
    MODEL.addConstrs((difLigt[i, g, t, dim] >= (- xLt[t, dim] + Rig[i, g, dim])*14000/1e6) for i, g, t, dim in difLigt.keys())

    MODEL.addConstrs((difLigt[i, g, t, 0]*difLigt[i, g, t, 0] + difLigt[i, g, t, 1] * difLigt[i, g, t, 1] <= dLigt[i, g, t] * dLigt[i, g, t] for i, g, t in uigt.keys()), name = 'difLigt')

    SmallM = 0
    BigM = datos.capacity*datos.vD*2
    # BigM = 1e5
    # BigM = 0
    # for g in T_index_prima:
        # for h in T_index_prima:
            # BigM = max(max([np.linalg.norm(v - w) for v in grafos[g-1].V for w in grafos[h-1].V]), BigM)
    
    # MODEL.addConstr(uigt[303, 1, 1, 0] == 1)
    # MODEL.addConstr(uigt[203, 2, 1, 1] == 1)
    
    # BigM += 5
    #BigM = max([np.linalg.norm(origin-grafos[g].V) for g in range(nG)])
    MODEL.addConstrs((pLigt[i, g, t] <= BigM * uigt[i, g, t]) for i, g, t in uigt.keys())
    MODEL.addConstrs((pLigt[i, g, t] <= dLigt[i, g, t]) for i, g, t in uigt.keys())
    MODEL.addConstrs((pLigt[i, g, t] >= SmallM * uigt[i, g, t]) for i, g, t in uigt.keys())
    MODEL.addConstrs((pLigt[i, g, t] >= dLigt[i, g, t] - BigM * (1 - uigt[i, g, t])) for i, g, t in uigt.keys())
    

    MODEL.addConstrs((difigjg[i, j, g, dim] >=  (Lig[i, g, dim] - Rig[j, g, dim])*14000/1e6) for i, j, g, dim in difigjg.keys())
    MODEL.addConstrs((difigjg[i, j, g, dim] >= (- Lig[i, g, dim] + Rig[j, g, dim])*14000/1e6) for i, j, g, dim in difigjg.keys())

    MODEL.addConstrs((difigjg[i, j, g, 0]*difigjg[i, j, g, 0] + difigjg[i, j, g, 1] * difigjg[i, j, g, 1] <= digjg[i, j, g] * digjg[i, j, g] for i, j, g in digjg.keys()), name = 'difigjg')


    for i, j, g in zigjg.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Poligonal(np.array([[grafos[g-1].V[first_i, 0], grafos[g-1].V[first_i, 1]], [
                           grafos[g-1].V[second_i, 0], grafos[g-1].V[second_i, 1]]]), grafos[g-1].A[first_i, second_i])
        segm_j = Poligonal(np.array([[grafos[g-1].V[first_j, 0], grafos[g-1].V[first_j, 1]], [
                           grafos[g-1].V[second_j, 0], grafos[g-1].V[second_j, 1]]]), grafos[g-1].A[first_j, second_j])

        BigM_local = eM.estima_BigM_local(segm_i, segm_j)
        SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
        MODEL.addConstr((pigjg[i, j, g] <= BigM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] <= digjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= SmallM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= digjg[i, j, g] - BigM_local * (1 - zigjg[i, j, g])))

    MODEL.addConstrs((difRigt[i, g, t, dim] >=   (Lig[i, g, dim] - xRt[t, dim])*14000/1e6) for i, g, t, dim in difRigt.keys())
    MODEL.addConstrs((difRigt[i, g, t, dim] >= (- Lig[i, g, dim] + xRt[t, dim])*14000/1e6) for i, g, t, dim in difRigt.keys())

    MODEL.addConstrs((difRigt[i, g, t, 0]*difRigt[i, g, t, 0] + difRigt[i, g, t, 1] * difRigt[i, g, t, 1] <= dRigt[i, g, t] * dRigt[i, g, t] for i, g, t in vigt.keys()), name = 'difRigt')


    #SmallM = 0
    #BigM = 10000
    MODEL.addConstrs((pRigt[i, g, t] <= BigM * vigt[i, g, t]) for i, g, t in vigt.keys())
    MODEL.addConstrs((pRigt[i, g, t] <= dRigt[i, g, t]) for i, g, t in vigt.keys())
    MODEL.addConstrs((pRigt[i, g, t] >= SmallM * vigt[i, g, t]) for i, g, t in vigt.keys())
    MODEL.addConstrs((pRigt[i, g, t] >= dRigt[i, g, t] - BigM * (1 - vigt[i, g, t])) for i, g, t in vigt.keys())

    MODEL.addConstrs((difRLt[t, dim] >=   (xRt[t, dim] - xLt[t + 1, dim])*14000/1e6 for t in dRLt.keys() for dim in range(2)), name = 'error')
    MODEL.addConstrs((difRLt[t, dim] >= (- xRt[t, dim] + xLt[t + 1, dim])*14000/1e6 for t in dRLt.keys() for dim in range(2)), name = 'error2')
    MODEL.addConstrs((difRLt[t, 0]*difRLt[t, 0] + difRLt[t, 1] * difRLt[t, 1] <= dRLt[t] * dRLt[t] for t in dRLt.keys()), name = 'difRLt')

    MODEL.addConstrs((difLRt[t, dim] >=   (xLt[t, dim] - xRt[t, dim])*14000/1e6) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, dim] >= (- xLt[t, dim] + xRt[t, dim])*14000/1e6) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, 0]*difLRt[t, 0] + difLRt[t, 1] * difLRt[t, 1] <= dLRt[t] * dLRt[t] for t in dLRt.keys()), name = 'difLRt')


    # longitudes = []
    # for g in T_index_prima:
    #     longitudes.append(sum([grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas]))

    BigM = 1e5
    # BigM = datos.capacity

    MODEL.addConstrs(timetD[t] >= (gp.quicksum(pLigt[i, g, t] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigt[i, g, t] for i in grafos[g-1].aristas))/datos.vD -  BigM*(1- gp.quicksum(uigt[i, g, t] for i in grafos[g-1].aristas)) for t in T_index_prima for g in T_index_prima)
    MODEL.addConstrs(timetM[t] == dLRt[t]/datos.vC for t in T_index_prima)
    
    MODEL.addConstrs(timetD[t] <= timetM[t] for t in T_index_prima)
    MODEL.addConstrs(timetD[t] <= datos.capacity for t in T_index_prima)
    # MODEL.addConstrs((gp.quicksum(pLigt[i, g, t] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigt[i, g, t] for i in grafos[g-1].aristas))/datos.vD <= dLRt[t]/datos.vC + BigM*(1- gp.quicksum(uigt[i, g, t] for i in grafos[g-1].aristas)) for t in T_index_prima for g in T_index_prima for d in D_index)
    # MODEL.addConstrs((gp.quicksum(pLigt[i, g, t] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigt[i, g, t] for i in grafos[g-1].aristas))/datos.vD
    # MODEL.addConstrs(dLRt[t]/datos.vC <= datos.capacity for t in T_index_prima)
    
    # MODEL.addConstrs((gp.quicksum(pLigt[i, g, t] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigt[i, g, t] for i in grafos[g-1].aristas))/datos.vD <=  zetat[t] + BigM*(1- gp.quicksum(uigt[i, g, t] for i in grafos[g-1].aristas)) for t in T_index_prima for g in T_index_prima for d in D_index)

    # MODEL.addConstrs(2*zetat[t]*deltat[t]*datos.vC >= dLRt[t]*dLRt[t] for t in T_index_prima)
    # MODEL.addConstrs(dLRt[t] >= deltat[t]*datos.vC*zetat[t] for t in T_index_prima)
    # MODEL.addConstrs(zetat[t] <= datos.capacity for t in T_index_prima)
    
    #MODEL.addConstrs(zigjg[i, j, g] <= uigt.sum(g, '*', '*') for i, j, g in zigjg.keys())
    #MODEL.addConstrs(muig[i, g] <= uigt.sum(i, g, '*') for i, g in muig.keys())

    # MODEL.addConstrs((pLigt.sum('*', '*', t) +
    #                   pigjg.sum(g, '*', '*') +
    #                   uigt.sum(g, '*', '*')*longitudes[g-1] +
    #                   pRigt.sum('*', '*', t))/vD <= dLRt[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLRt[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pLigt[i, g, t]
    #                   + pigjg.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pRigt[i, g, t])/vD <= dLRt[t]/vC for i, g, t in pLigt.keys())

    for i, g in rhoig.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhoig[i, g] - landaig[i, g] == maxig[i, g] - minig[i, g])
        MODEL.addConstr(maxig[i, g] + minig[i, g] == alphaig[i, g])
        if datos.alpha:
            MODEL.addConstr(pig[i, g] >= grafos[g-1].A[first, second])
        MODEL.addConstr(maxig[i, g] <= 1 - entryig[i, g])
        MODEL.addConstr(minig[i, g] <= entryig[i, g])
        MODEL.addConstr(Rig[i, g, 0] == rhoig[i, g] * grafos[g-1].V[first, 0] + (1 - rhoig[i, g]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rig[i, g, 1] == rhoig[i, g] * grafos[g-1].V[first, 1] + (1 - rhoig[i, g]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lig[i, g, 0] == landaig[i, g] * grafos[g-1].V[first, 0] + (1 - landaig[i, g]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lig[i, g, 1] == landaig[i, g] * grafos[g-1].V[first, 1] + (1 - landaig[i, g]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) == grafos[g-1].alpha*grafos[g-1].longitud)

    # [0, 2, 1, 3, 4]
    # MODEL.addConstr(uigt[2, 102, 1] >= 0.5)
    # MODEL.addConstr(uigt[1, 101, 2] >= 0.5)
    # MODEL.addConstr(uigt[3, 102, 3] >= 0.5)
    #
    # MODEL.addConstr(vigt[2, 303, 1] >= 0.5)
    # MODEL.addConstr(vigt[1, 203, 2] >= 0.5)
    # MODEL.addConstr(vigt[3, 101, 3] >= 0.5)
    #
    # MODEL.addConstr(dLRt[1] <= 3.1490912899469254e+01 + 1e-5)
    # MODEL.addConstr(dLRt[2] <= 8.1903472383647316e+00 + 1e-5)
    # MODEL.addConstr(dLRt[3] <= 3.2352819808730416e+01 + 1e-5)
    #
    #
    # MODEL.addConstr(xLt[1, 0] == 5.0000000005633247e+01)
    # MODEL.addConstr(xLt[1, 1] == 4.9999999994606391e+01)
    # MODEL.addConstr(xLt[2, 0] == 45.0173764234826)
    # MODEL.addConstr(xLt[2, 1] == 7.3845420113314660e+01)
    # MODEL.addConstr(xLt[3, 0] == 4.5080138866746275e+01)
    # MODEL.addConstr(xLt[3, 1] == 8.0665242773352233e+01)
    #
    # MODEL.addConstr(xRt[1, 0] == 4.5017376430147451e+01)
    # MODEL.addConstr(xRt[1, 1] == 7.3845420106065134e+01)
    # MODEL.addConstr(xRt[2, 0] == 45.0801388601561)
    # MODEL.addConstr(xRt[2, 1] == 80.6652427666625)
    # MODEL.addConstr(xRt[3, 0] == 5.0000000002577934e+01)
    # MODEL.addConstr(xRt[3, 1] == 5.0000000007343687e+01)

    # Origen y destino
    MODEL.addConstrs(xLt[0, dim] == datos.orig[dim] for dim in range(2))
    MODEL.addConstrs(xRt[0, dim] == datos.orig[dim] for dim in range(2))

    MODEL.addConstrs(xLt[datos.m+1, dim] == datos.dest[dim] for dim in range(2))
    MODEL.addConstrs(xRt[datos.m+1, dim] == datos.dest[dim] for dim in range(2))

    # for t in T_index_prima:
    #     MODEL.addConstrs(xLt[t, dim] == datos.orig[dim] for dim in range(2))
    #     MODEL.addConstrs(xRt[t, dim] == datos.orig[dim] for dim in range(2))
    # print(vals_xL)
    # for g in T_index_prima:
    #     MODEL.addConstrs(xLt[g, dim] == vals_xL[g][dim] for dim in range(2))
    #     MODEL.addConstrs(xRt[g, dim] == vals_xR[g][dim] for dim in range(2))

    MODEL.update()

    # objective = gp.quicksum(pLigt[i, g, t] + pRigt[i, g, t] for i, g, t in pRigt.keys()) + gp.quicksum(pigjg[i, j, g] for i, j, g in pigjg.keys()) + gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLRt[t] for t in dLRt.keys()) + gp.quicksum(3*dRLt[t] for t in dRLt.keys())

    # objective = gp.quicksum(1*dRLt[g1] for g1 in dRLt.keys()) + gp.quicksum(zetat[t] for t in zetat.keys()) + gp.quicksum(1*dLRt[g] for g in dLRt.keys())
    
    objective = gp.quicksum(1*dRLt[g1]/datos.vC for g1 in dRLt.keys()) + gp.quicksum(1*dLRt[g]/datos.vC for g in dLRt.keys())

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 6
    # MODEL.Params.FeasibilityTol = 1e-3
    # MODEL.Params.NonConvex = 2
    # MODEL.Params.MIPFocus = 3
    MODEL.Params.timeLimit = datos.tmax

    MODEL.update()

    # MODEL.write('./case_study/patios-{0}-{1}-{2}.lp'.format(datos.nD, datos.capacity, datos.vD))
    # MODEL.write('./AMMDRPGST-Init.mps')
    
    if datos.init:
        MODEL.optimize(callback)
    else:
        MODEL.optimize()


    # MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result =  [np.nan, np.nan, np.nan, np.nan]
        if datos.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return result

    if MODEL.SolCount == 0:
        result =  [np.nan, np.nan, np.nan, np.nan]
        if datos.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return result

    result = []

    result.append(MODEL.getAttr('MIPGap'))
    result.append(MODEL.Runtime)
    result.append(MODEL.getAttr('NodeCount'))
    result.append(MODEL.ObjVal)
    
    if datos.init:
        result.append(heuristic_time)
        result.append(MODEL._startobjval)
    
    # if datos.grid:
        # result.append('Grid')
    # else:
        # result.append('Delauney')

    # result.append('Stages')
    
    MODEL.write('./final_solution.sol')
    # MODEL.write('solution_patios.sol')

    # print(xRt)
    # print(xLt)
    # print('Selected_u')
    vals_u = MODEL.getAttr('x', uigt)
    selected_u = gp.tuplelist((i, g, t) for i, g, t in vals_u.keys() if vals_u[i, g, t] > 0.5)
    print(selected_u)
    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', zigjg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    # print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', vigt)
    selected_v = gp.tuplelist((i, g, t) for i, g, t in vals_v.keys() if vals_v[i, g, t] > 0.5)
    # print(selected_v)
    #
    # path = []
    # path.append(0)
    
    print('Total time: ' + str(MODEL.ObjVal/datos.vC))
    
    distance = 0
    
    for t in T_index_prima:
        distance += np.linalg.norm(np.array([xLt[t, 0].X, xLt[t, 1].X]) - np.array([xRt[t, 0].X, xRt[t, 1].X]))
        
    for t in T_index_primaprima:
        distance += np.linalg.norm(np.array([xRt[t, 0].X, xRt[t, 1].X]) - np.array([xLt[t, 0].X, xLt[t, 1].X]))

        
    print('Time operating: ' + str(distance/datos.vC))
    print('Time waiting: ' + str(MODEL.ObjVal - distance/datos.vC))
    

    # path_C.append(origin)
    path_C = []
    paths_D = []

    path = []
    
    path_C.append([xLt[0, 0].X, xLt[0, 1].X])
    path.append(0)
    for t in T_index:
        if len(selected_u.select('*', '*', t)) > 0:
            path.append(t)
            path_C.append([xLt[t, 0].X, xLt[t, 1].X])
        if len(selected_v.select('*', '*', t)) > 0:
            path.append(t)
            path_C.append([xRt[t, 0].X, xRt[t, 1].X])
    
    path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])
    path.append(nG+1)
    
    for t in path:
        tuplas = selected_u.select('*', '*', t)
        # print(tuplas)
        drones = len(tuplas)


        for (i, g, t1), d in zip(tuplas, range(drones)):
            path_D = []

            path_D.append([xLt[t1, 0].X, xLt[t1, 1].X])

            index_i = i
            index_g = g
            count = 0

            limite = sum([1 for i1, j1, g1 in selected_z if g1 == g])

            path_D.append([Rig[index_i, index_g, 0].X, Rig[index_i, index_g, 1].X])
            path_D.append([Lig[index_i, index_g, 0].X, Lig[index_i, index_g, 1].X])
            
            while count < limite:
                for i1, j1, g1 in selected_z:
                    if i1 == index_i and g1 == g:
                        count += 1
                        index_i =j1
                        path_D.append([Rig[index_i, index_g, 0].X, Rig[index_i, index_g, 1].X])
                        path_D.append([Lig[index_i, index_g, 0].X, Lig[index_i, index_g, 1].X])
                        
            path_D.append([xRt[t1, 0].X, xRt[t1, 1].X])

            paths_D.append((path_D, d))

    # print(paths_D)
    log = True
    
    if log:
        fig, ax = plt.subplots()
        colors = ['lime', 'darkorange', 'y', 'k']
        colors = ['darkorange', 'fuchsia', 'y', 'k']
        # plt.axis([0, 100, 0, 100])
        #
        logue = False
        
        if logue:
            for i, g in rhoig.keys():
                first = i // 100 - 1
                second = i % 100
                if muig[i, g].X > 0.5:
                    plt.plot(Rig[i, g, 0].X, Rig[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$R_" + str(g) + "^{" + str((first, second)) + "}$", xy = (Rig[i, g, 0].X+0.75, Rig[i, g, 1].X+0.75))
                    plt.plot(Lig[i, g, 0].X, Lig[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$L_" + str(g) + "^{" + str((first, second)) + "}$", xy = (Lig[i, g, 0].X+0.75, Lig[i, g, 1].X+0.75))
    
        # #
        # # path_C = []
        
        plt.plot(xLt[0, 0].X, xLt[0, 1].X, 's', alpha = 1, markersize=10, color='black')
        plt.plot(xLt[nG+1, 0].X, xLt[nG+1, 1].X, 's', alpha = 1, markersize=10, color='black')
        
        logue = True
        if logue:
            for t in path:
                # path_C.append([xLt[t, 0].X, xLt[t, 1].X])
                # path_C.append([xRt[t, 0].X, xRt[t, 1].X])
                # plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha = 1, markersize=5, color='black')
                plt.plot(xLt[1, 0].X, xLt[1, 1].X, 'o', alpha = 1, markersize=10,  color='red')
        
                if t == 0:
                    plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha = 1, markersize=10, color='black')
                    ax.annotate("orig", xy = (xLt[t, 0].X-2, xLt[t, 1].X+1), fontsize = 15)
                if t > 0 and t < nG+1:
                    plt.plot(xRt[t, 0].X, xRt[t, 1].X, 'o', alpha = 1, markersize=10,  color='red')
                    ax.annotate("$x_R^{t}$".format(t = t), xy = (xRt[t, 0].X+1.5, xRt[t, 1].X), fontsize = 15)
                    ax.annotate("$x_L^{t}$".format(t = t), xy = (xLt[t, 0].X-3, xLt[t, 1].X), fontsize = 15)
                if t == nG+1:
                    plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha = 1, markersize=10, color='black')
                    ax.annotate("dest", xy = (xLt[t, 0].X+0.5, xLt[t, 1].X+1), fontsize = 15)
        
        
            ax.add_artist(Polygon(path_C, fill=False, animated=False, closed = False,
                          linestyle='-', lw = 2, alpha=1, color='black'))
            #
            for t in T_index_prima:
                
                n_drones = len(selected_u.select('*', '*', t))
                
                if n_drones > 0:
                    for drone in range(n_drones):
                        edge = selected_u.select('*', '*', t)[drone][0]
                        g = selected_u.select('*', '*', t)[drone][1]
                        
                        ax.arrow(xLt[t, 0].X, xLt[t, 1].X, Rig[edge, g, 0].X - xLt[t, 0].X, Rig[edge, g, 1].X - xLt[t, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = colors[drone])
                        
                        for e1, e2, g in selected_z.select('*', '*', g):
                            if pigjg[e1, e2, g].X >= 0.05:
                                ax.arrow(Lig[e1, g, 0].X, Lig[e1, g, 1].X, Rig[e2, g, 0].X - Lig[e1, g, 0].X, Rig[e2, g, 1].X - Lig[e1, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = colors[drone])            
        
                        for e in grafos[g-1].aristas:
                            if muig[e, g].X >= 0.5 and pig[e, g].X >= 0.01:
                                ax.arrow(Rig[e, g, 0].X, Rig[e, g, 1].X, Lig[e, g, 0].X - Rig[e, g, 0].X, Lig[e, g, 1].X - Rig[e, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = colors[drone])            
        
        
                        edge = selected_v.select('*', '*', t)[drone][0]
                        g = selected_v.select('*', '*', t)[drone][1]
                        
                        ax.arrow(Lig[edge, g, 0].X, Lig[edge, g, 1].X, xRt[t, 0].X - Lig[edge, g, 0].X, xRt[t, 1].X - Lig[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = colors[drone])            
                
            for p in range(len(path_C)-1):
                ax.arrow(path_C[p][0], path_C[p][1], path_C[p+1][0] - path_C[p][0], path_C[p+1][1] - path_C[p][1], width = 0.3, head_width = 0.7, length_includes_head = True, color = 'black')
 
        # def esCerrado(path):
        #     return path[0] == path[-1]
        #
        # for pathd, color in paths_D:
        #     if esCerrado(pathd):
        #         # print(pathd)
        #         ax.add_artist(Polygon(pathd, fill=False, closed = True, lw = 2, alpha=1, color=colors[color]))
        #     else:
        #         ax.add_artist(Polygon(pathd, fill=False, closed = False, lw = 2, alpha=1, color=colors[color]))
                
        
        # # ax.add_artist(Polygon(path_D, fill=False, animated=False,
        # #               linestyle='dotted', alpha=1, color='red'))
        
        # colors = ['blue', 'purple', 'cyan', 'orange', 'red', 'green']
        # for g in T_index_prima:
            # grafo = grafos[g-1]
            # centroide = np.mean(grafo.V, axis = 0)
            # nx.draw(grafo.G, grafo.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
            # ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
            # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)
        
        # for g in T_index_prima:
        #     grafo = grafos[g-1]
        #     centroide = np.mean(grafo.V, axis = 0)
        #     nx.draw(grafo.G, grafo.pos, node_size=90, width = 2,
        #             node_color='blue', alpha=1, edge_color='blue')
            # ax.annotate('$\\alpha_{0} = {1:0.2f}$'.format(g, grafo.alpha), xy = (centroide[0]+5, centroide[1]+10), fontsize = 12)
            
            # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)
        
        for g in grafos:
            nx.draw(g.G, g.pos, node_size=10, width = 1, 
                    node_color = 'blue', alpha = 1, edge_color = 'blue')
            
        plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = datos.m, c = int(datos.alpha), d = datos.capacity, e = datos.nD))
        plt.show()
        
        import tikzplotlib
        import matplotlib
        
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        tikzplotlib.save('synchronous.tex', encoding = 'utf-8')
            
        # plt.show()
        # plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = datos.m, c = int(datos.alpha), d = datos.capacity, e = datos.nD))
        # plt.savefig('PDST-Sinc2.png')

        # plt.savefig('Prueba.png')
        
        # plt.show()
    print(result)
    print()
    
    return result