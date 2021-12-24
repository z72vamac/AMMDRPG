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


# Definicion de los datos
""" P: conjunto de poligonales a agrupar
    E: conjunto de entornos
    T: sucesion de etapas
    C(e): centro del entorno e
    R(e): radio del entorno e
    p: indice de las poligonales
    e: indice de los entornos
    t: indice de las etapas
    n: dimension del problema
"""

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
np.random.seed(13)


# Experimento para ver diferencias
# datos = Data([], m=2, grid = True, tmax=600, alpha = False, nD = 2, capacity = 6,
            # init=False,
            # show=True,
            # vD = 5.11,
            # orig = [0, 5],
            # dest = [20, 5],
            # seed=2)
            #
# datos.generar_grafo_personalizado(1)


lista = list(4*np.ones(4, int))

nG = len(lista)

datos = Data([], m=4, grid = True, tmax=1800, alpha = True, nD = 2, capacity = 40,
            init=False,
            show=True,
            vD = 2,
            orig = [0, 0],
            dest = [100, 0],
            seed=2)

datos.generar_grid()
datos.generar_grafos(lista)

def AMMDRPGSTSINC(datos): #, vals_xL, vals_xR):

    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            if model.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                # creates new model attribute '_startobjval'
                model._startobjval = model.cbGet(GRB.Callback.MIPSOL_OBJ)

    grafos = datos.mostrar_datos()

    result = []

    nG = datos.m
    nD = datos.nD
    
    T_index = range(datos.m + 2)
    T_index_prima = range(1, datos.m+1)
    T_index_primaprima = range(datos.m+1)
    D_index = range(nD)
    
    Capacity = datos.capacity


    # Creamos el modelo8
    MODEL = gp.Model("PD-Stages")

    # Variables que modelan las distancias
    # Variable binaria uigtd = 1 si en la etapa t entramos por el segmento sig
    uigtd_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            for t in T_index_prima:
                for d in D_index:
                    uigtd_index.append((i, g, t, d))


    uigtd = MODEL.addVars(uigtd_index, vtype=GRB.BINARY, name='uigtd')

    # Variable continua no negativa dLigtd que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sig.
    dLigtd_index = uigtd_index

    dLigtd = MODEL.addVars(dLigtd_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLigtd')
    difLigtd = MODEL.addVars(dLigtd_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLigtd')

    # Variable continua no negativa pLigtd = uigtd * dLigtd
    pLigtd_index = uigtd_index

    pLigtd = MODEL.addVars(pLigtd_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pLigtd')


    # Variable binaria vigtd = 1 si en la etapa t salimos por el segmento sig
    vigtd_index = uigtd_index

    vigtd = MODEL.addVars(vigtd_index, vtype=GRB.BINARY, name='vigtd')

    # Variable continua no negativa dRigtd que indica la distancia desde el punto de salida del segmento sig hasta el
    # punto de recogida del camion
    dRigtd_index = uigtd_index

    dRigtd = MODEL.addVars(dRigtd_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRigtd')
    difRigtd = MODEL.addVars(dRigtd_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRigtd')


    # Variable continua no negativa pRigtd = vigtd * dRigtd
    pRigtd_index = uigtd_index

    pRigtd = MODEL.addVars(pRigtd_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pRigtd')


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
    deltat = MODEL.addVars(T_index, vtype = GRB.CONTINUOUS, lb = 0, ub = 1, name = 'deltat')
    zetat = MODEL.addVars(T_index, vtype = GRB.CONTINUOUS, lb = 0, name = 'zetat')

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

    # Rig: punto de recogida del dron para el segmento sig
    Rig_index = []
    rhoig_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhoig_index.append((i, g))
            for dim in range(2):
                Rig_index.append((i, g, dim))

    Rig = MODEL.addVars(Rig_index, vtype=GRB.CONTINUOUS, name='Rig')
    rhoig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS,
                          lb=0.0, ub=1.0, name='rhoig')

    # Lig: punto de lanzamiento del dron del segmento sig
    Lig_index = Rig_index
    landaig_index = rhoig_index

    Lig = MODEL.addVars(Lig_index, vtype=GRB.CONTINUOUS, name='Lig')
    landaig = MODEL.addVars(
        landaig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landaig')

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
            uigtd_sol = hola[0]
            vigtd_sol = hola[1]
            z_sol = hola[2]
            heuristic_time = hola[3]
            # uigtd_sol, vigtd_sol, z_sol, heuristic_time = heuristic(datos)
        
        # for i, g, t, d in uigtd_sol:
            # uigtd[i, g, t, d].start = 1
            #
        
        # my_file = open('./case_study/uigtd_keys.txt', "r")
        # content = my_file.read()
        
        
        # uigtd_sol = ast.literal_eval(content[:-1])

        # MODEL.read('./case_study/uigtd.sol')
        
            for i, g, t, d in uigtd.keys():
                if (i, g, t, d) in uigtd_sol:
                    uigtd[i, g, t, d].start = 1
                else:
                    uigtd[i, g, t, d].start = 0
        
        # my_file = open('./case_study/vigtd_keys.txt', "r")
        # content = my_file.read()
        #
        #
        # vigtd_sol = ast.literal_eval(content)


            for i, g, t, d in vigtd.keys():
                if (i, g, t, d) in vigtd_sol:
                    vigtd[i, g, t, d].start = 1
                else:
                    vigtd[i, g, t, d].start = 0
            
            for i, j, g in zigjg.keys():
                if (i, j, g) in z_sol:
                    zigjg[i, j, g].start = 1
                else:
                    zigjg[i, j, g].start = 0

    SmallM = 0
    BigM = datos.capacity*datos.vD + 1e2
    # BigM = 10000
    

    # En cada etapa hay que visitar/salir un segmento de un grafo
    MODEL.addConstrs(uigtd.sum('*', '*', t, d) <= 1 for t in T_index_prima for d in D_index)
    MODEL.addConstrs(vigtd.sum('*', '*', t, d) <= 1 for t in T_index_prima for d in D_index)

    # # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs(uigtd.sum('*', g, '*', '*') == 1 for g in T_index_prima)
    MODEL.addConstrs(vigtd.sum('*', g, '*', '*') == 1 for g in T_index_prima)

    # # VI-1
    MODEL.addConstrs(betat[t] <= betat[t+1] for t in T_index_prima)
    #
    # # VI-2
    MODEL.addConstrs(gp.quicksum(uigtd[i, g, t1, d] for i, g, t1, d in uigtd.keys() if t1 < t) >= nG*betat[t] for t in T_index_prima)
    #
    # # VI-3
    MODEL.addConstrs(gp.quicksum(uigtd[i, g, t1, d] for i, g, t1, d in uigtd.keys() if t1 == t) >= 1 - betat[t] for t in T_index)
    
    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs(muig[i, g] - uigtd.sum(i, g, '*', '*') == zigjg.sum('*', i, g) for i, g in rhoig.keys())
    MODEL.addConstrs(muig[i, g] - vigtd.sum(i, g, '*', '*') == zigjg.sum(i, '*', g) for i, g in rhoig.keys())
    
    for t1 in T_index_prima:
        for t2 in T_index_prima:
            if t1 < t2:
                MODEL.addConstrs((gp.quicksum(uigtd[i, g1, t, d] for g1 in T_index_prima for i in grafos[g1-1].aristas for t in T_index_prima if t > t1 and t <= t2) <= 10*(2 - uigtd.sum('*', g, t1, d) - vigtd.sum('*', g, t2, d)) for g in T_index_prima for d in D_index), name = "syncronized1")
                MODEL.addConstrs((gp.quicksum(vigtd[i, g1, t, d] for g1 in T_index_prima for i in grafos[g1-1].aristas for t in T_index_prima if t >= t1 and t < t2) <= 10*(2 - uigtd.sum('*', g, t1, d) - vigtd.sum('*', g, t2, d)) for g in T_index_prima for d in D_index), name = "syncronized2")
                
            # if t1 == t2:
                # MODEL.addConstrs((gp.quicksum(uigtd[i, g, t, d] for i in grafos[g-1].aristas for t in T_index_prima if t > t1 and t <= t2) <= 2 - uigtd.sum('*', g, t1, d) - vigtd.sum('*', g, t2, d) for g in T_index_prima for d in D_index), name = "syncronized1")
                # MODEL.addConstrs((gp.quicksum(vigtd[i, g, t, d] for i in grafos[g-1].aristas for t in T_index_prima if t >= t1 and t < t2) <= 2 - uigtd.sum('*', g, t1, d) - vigtd.sum('*', g, t2, d) for g in T_index_prima for d in D_index), name = "syncronized2")
    
            if t1 <= t2:    
                MODEL.addConstrs((gp.quicksum(pLigtd[i, g, t1, d] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigtd[i, g, t2, d] for i in grafos[g-1].aristas))/datos.vD <=  gp.quicksum(dLRt[t]/datos.vC for t in T_index_prima if t >= t1 and t <= t2) + gp.quicksum(dRLt[t]/datos.vC for t in T_index_prima if t >= t1 and t < t2) + BigM*(2- gp.quicksum(uigtd[i, g, t1, d] for i in grafos[g-1].aristas) - gp.quicksum(vigtd[i, g, t2, d] for i in grafos[g-1].aristas)) for g in T_index_prima for d in D_index)               
                MODEL.addConstrs(gp.quicksum(dLRt[t]/datos.vC for t in T_index_prima if t >= t1 and t <= t2)  + gp.quicksum(dRLt[t]/datos.vC for t in T_index_prima if t >= t1 and t < t2)<= datos.capacity + BigM*(2- gp.quicksum(uigtd[i, g, t1, d] for i in grafos[g-1].aristas) - gp.quicksum(vigtd[i, g, t2, d] for i in grafos[g-1].aristas)) for g in T_index_prima for d in D_index)               
                # MODEL.addConstr(gp.quicksum(dLRt[t]/datos.vC for t in T_index_prima if t >= t1 and t <= t2)  + gp.quicksum(dRLt[t]/datos.vC for t in T_index_prima if t >= t1 and t < t2)<= Capacity + BigM*(2- gp.quicksum(uigtd[i, g, t1, )
    
    # MODEL.addConstrs(gp.quicksum(uigtd[i, g, t1, d] for i in grafos[g-1].aristas for t1 in T_index_prima if t1 <= t) - gp.quicksum(vigtd[i, g, t1, d] for i in grafos[g-1].aristas for t1 in T_index_prima if t1 >= t) == 0 for g in T_index_prima for d in D_index for t in T_index_prima)
    MODEL.addConstrs(uigtd.sum('*', g, t, d) <= gp.quicksum(vigtd[i, g, t1, d] for i in grafos[g-1].aristas for t1 in T_index_prima if t1 >= t) for t in T_index_prima for g in T_index_prima for d in D_index)
    # MODEL.addConstrs(vigtd.sum('*', g, t, d) <= gp.quicksum(uigtd[i, g, t1, d] for i in grafos[g-1].aristas for t1 in T_index_prima if t1 > t) for t in T_index_prima for g in T_index_prima for d in D_index)
    # MODEL.addConstrs(vigtd.sum('*', g, t, d) >= gp.quicksum(uigtd[i, g, t1, d] for i in grafos[g-1].aristas for t1 in T_index_prima if t1 < t) for t in T_index_prima for g in T_index_prima for d in D_index)
    
    MODEL.addConstrs(pig[i, g] >= muig[i, g] + alphaig[i, g] - 1 for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= muig[i, g] for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= alphaig[i, g] for i, g in rhoig.keys())

    # MODEL.addConstr(xLt[1, 0] == 7)
    # MODEL.addConstr(xLt[1, 1] == 5)
    #
    # MODEL.addConstr(xRt[1, 0] == 13)
    # MODEL.addConstr(xRt[1, 1] == 5)
    #
    # MODEL.addConstr(xLt[2, 0] == 9)
    # MODEL.addConstr(xLt[2, 1] == 5)
    #
    # MODEL.addConstr(xRt[2, 0] == 15)
    # MODEL.addConstr(xRt[2, 1] == 5)
    
    # MODEL.addConstr(uigtd[101, 1, 1, 0] == 1)
    # MODEL.addConstr(uigtd[101, 2, 2, 1] == 1)
    
    
    
    
    # MODEL.addConstr(uigtd[101,2,1,0] == 1)
    # MODEL.addConstr(vigtd[203,2,2,0] == 1)
    # MODEL.addConstr(uigtd[101,1,1,1] == 1)
    # MODEL.addConstr(vigtd[203,1,2,1] == 1)
    # MODEL.addConstr(uigtd[101,3,3,0] == 1)
    # MODEL.addConstr(vigtd[203,3,3,0] == 1)
    
    
    # MODEL.addConstr(uigtd[101, 2])
    # MODEL.addConstr(uigtd[101,3,3,0] == 1)
    # MODEL.addConstr(vigtd[203,3,3,0] == 1)
    
    # MODEL.addConstr(uigtd[101,1,1,1] == 1)
    # MODEL.addConstr(vigtd[203,1,1,1] == 1)
    
    # MODEL.addConstr(uigtd[0, 101, 1] == 0)


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


    # MODEL.addConstrs(uigtd[i, g, t, d1] <= uigtd.sum('*', '*', '*', d2) for i, g, t, d1 in uigtd.keys() for d2 in D_index if d1 > d2)
    # MODEL.addConstrs(vigtd[i, g, t, d1] <= vigtd.sum('*', '*', '*', d2) for i, g, t, d1 in vigtd.keys() for d2 in D_index if d1 > d2)
    
    # Restricciones de distancias y producto
    MODEL.addConstrs((difLigtd[i, g, t, d, dim] >=   xLt[t, dim] - Rig[i, g, dim]) for i, g, t, d, dim in difLigtd.keys())
    MODEL.addConstrs((difLigtd[i, g, t, d, dim] >= - xLt[t, dim] + Rig[i, g, dim]) for i, g, t, d, dim in difLigtd.keys())

    MODEL.addConstrs((difLigtd[i, g, t, d, 0]*difLigtd[i, g, t, d, 0] + difLigtd[i, g, t, d, 1] * difLigtd[i, g, t, d, 1] <= dLigtd[i, g, t, d] * dLigtd[i, g, t, d] for i, g, t, d in uigtd.keys()), name = 'difLigtd')


    # BigM = 0
    # for g in T_index_prima:
        # for h in T_index_prima:
            # BigM = max(max([np.linalg.norm(v - w) for v in grafos[g-1].V for w in grafos[h-1].V]), BigM)
    
    # MODEL.addConstr(uigtd[303, 1, 1, 0] == 1)
    # MODEL.addConstr(uigtd[203, 2, 2, 1] == 1)
    # MODEL.addConstr(uigtd[203, 3, 3, 2] == 1)
    # MODEL.addConstr(vigtd[101, 1, 3, 0] == 1)
    # MODEL.addConstr(vigtd[101, 2, 3, 1] == 1)
    # MODEL.addConstr(vigtd[101, 3, 3, 2] == 1)
    
    # MODEL.addConstr(vigtd[101, 1, 2, 0] == 1)
    # MODEL.addConstr(vigtd[101, 2, 2, 1] == 1)    
    # MODEL.addConstr(uigtd[303, 1, 1, 0] == 1)
    # MODEL.addConstr(uigtd[203, 2, 1, 1] == 1)    
    # BigM += 5
    #BigM = max([np.linalg.norm(origin-grafos[g].V) for g in range(nG)])
    MODEL.addConstrs((pLigtd[i, g, t, d] <= BigM * uigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs((pLigtd[i, g, t, d] <= dLigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs((pLigtd[i, g, t, d] >= SmallM * uigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs((pLigtd[i, g, t, d] >= dLigtd[i, g, t, d] - BigM * (1 - uigtd[i, g, t, d])) for i, g, t, d in uigtd.keys())
    

    MODEL.addConstrs((difigjg[i, j, g, dim] >=   Lig[i, g, dim] - Rig[j, g, dim]) for i, j, g, dim in difigjg.keys())
    MODEL.addConstrs((difigjg[i, j, g, dim] >= - Lig[i, g, dim] + Rig[j, g, dim]) for i, j, g, dim in difigjg.keys())

    MODEL.addConstrs((difigjg[i, j, g, 0]*difigjg[i, j, g, 0] + difigjg[i, j, g, 1] * difigjg[i, j, g, 1] <= digjg[i, j, g] * digjg[i, j, g] for i, j, g in digjg.keys()), name = 'difigjg')


    for i, j, g in zigjg.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Poligonal(np.array([[grafos[g-1].V[first_i, 0], grafos[g-1].V[first_i, 1]], [grafos[g-1].V[second_i, 0], grafos[g-1].V[second_i, 1]]]), grafos[g-1].A[first_i, second_i])
        segm_j = Poligonal(np.array([[grafos[g-1].V[first_j, 0], grafos[g-1].V[first_j, 1]], [grafos[g-1].V[second_j, 0], grafos[g-1].V[second_j, 1]]]), grafos[g-1].A[first_j, second_j])

        BigM_local = eM.estima_BigM_local(segm_i, segm_j)
        SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
        MODEL.addConstr((pigjg[i, j, g] <= BigM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] <= digjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= SmallM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= digjg[i, j, g] - BigM_local * (1 - zigjg[i, j, g])))

    MODEL.addConstrs((difRigtd[i, g, t, d, dim] >=   Lig[i, g, dim] - xRt[t, dim]) for i, g, t, d, dim in difRigtd.keys())
    MODEL.addConstrs((difRigtd[i, g, t, d, dim] >= - Lig[i, g, dim] + xRt[t, dim]) for i, g, t, d, dim in difRigtd.keys())

    MODEL.addConstrs((difRigtd[i, g, t, d, 0]*difRigtd[i, g, t, d, 0] + difRigtd[i, g, t, d, 1] * difRigtd[i, g, t, d, 1] <= dRigtd[i, g, t, d] * dRigtd[i, g, t, d] for i, g, t, d in vigtd.keys()), name = 'difRigtd')


    #SmallM = 0
    #BigM = 10000
    MODEL.addConstrs((pRigtd[i, g, t, d] <= BigM * vigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs((pRigtd[i, g, t, d] <= dRigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs((pRigtd[i, g, t, d] >= SmallM * vigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs((pRigtd[i, g, t, d] >= dRigtd[i, g, t, d] - BigM * (1 - vigtd[i, g, t, d])) for i, g, t, d in vigtd.keys())

    MODEL.addConstrs((difRLt[t, dim] >=   xRt[t, dim] - xLt[t + 1, dim] for t in dRLt.keys() for dim in range(2)), name = 'error')
    MODEL.addConstrs((difRLt[t, dim] >= - xRt[t, dim] + xLt[t + 1, dim] for t in dRLt.keys() for dim in range(2)), name = 'error2')
    MODEL.addConstrs((difRLt[t, 0]*difRLt[t, 0] + difRLt[t, 1] * difRLt[t, 1] <= dRLt[t] * dRLt[t] for t in dRLt.keys()), name = 'difRLt')

    MODEL.addConstrs((difLRt[t, dim] >=   xLt[t, dim] - xRt[t, dim]) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, dim] >= - xLt[t, dim] + xRt[t, dim]) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, 0]*difLRt[t, 0] + difLRt[t, 1] * difLRt[t, 1] <= dLRt[t] * dLRt[t] for t in dLRt.keys()), name = 'difLRt')


    # longitudes = []
    # for g in T_index_prima:
    #     longitudes.append(sum([grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas]))

    BigM = 1e5

    # MODEL.addConstrs((gp.quicksum(pLigtd[i, g, t, d] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigtd[i, g, t, d] for i in grafos[g-1].aristas))/vD <= dLRt[t]/vC + BigM*(1- gp.quicksum(uigtd[i, g, t, d] for i in grafos[g-1].aristas)) for t in T_index_prima for g in T_index_prima for d in D_index)
    # MODEL.addConstrs((gp.quicksum(pLigtd[i, g, t, d] for i in grafos[g-1].aristas) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + gp.quicksum(pRigtd[i, g, t, d] for i in grafos[g-1].aristas))/datos.vD <=  zetat[t] + BigM*(1- gp.quicksum(uigtd[i, g, t, d] for i in grafos[g-1].aristas)) for t in T_index_prima for g in T_index_prima for d in D_index)

    # MODEL.addConstrs(2*zetat[t]*deltat[t]*datos.vC >= dLRt[t]*dLRt[t] for t in T_index_prima)
    # MODEL.addConstrs(dLRt[t] >= deltat[t]*datos.vC*zetat[t] for t in T_index_prima)
    # MODEL.addConstrs(zetat[t] <= datos.capacity for t in T_index_prima)
    
    #MODEL.addConstrs(zigjg[i, j, g] <= uigtd.sum(g, '*', '*') for i, j, g in zigjg.keys())
    #MODEL.addConstrs(muig[i, g] <= uigtd.sum(i, g, '*') for i, g in muig.keys())

    # MODEL.addConstrs((pLigtd.sum('*', '*', t) +
    #                   pigjg.sum(g, '*', '*') +
    #                   uigtd.sum(g, '*', '*')*longitudes[g-1] +
    #                   pRigtd.sum('*', '*', t))/vD <= dLRt[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLRt[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pLigtd[i, g, t, d]
    #                   + pigjg.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pRigtd[i, g, t, d])/vD <= dLRt[t]/vC for i, g, t, d in pLigtd.keys())

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
            MODEL.addConstr(gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)

    # [0, 2, 1, 3, 4]
    # MODEL.addConstr(uigtd[101, 2, 1, 1] >= 0.5)
    # MODEL.addConstr(vigtd[101, 1, 2, 0] >= 0.5)
    # MODEL.addConstr(vigtd[101, 2, 2, 1] >= 0.5)
    
    # MODEL.addConstr(uigtd[1, 101, 2] >= 0.5)
    # MODEL.addConstr(uigtd[3, 102, 3] >= 0.5)
    #
    # MODEL.addConstr(vigtd[2, 303, 1] >= 0.5)
    # MODEL.addConstr(vigtd[1, 203, 2] >= 0.5)
    # MODEL.addConstr(vigtd[3, 101, 3] >= 0.5)
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

    # print(vals_xL)
    # for g in T_index_prima:
    #     MODEL.addConstrs(xLt[g, dim] == vals_xL[g][dim] for dim in range(2))
    #     MODEL.addConstrs(xRt[g, dim] == vals_xR[g][dim] for dim in range(2))

    MODEL.update()

    # objective = gp.quicksum(pLigtd[i, g, t, d] + pRigtd[i, g, t, d] for i, g, t, d in pRigtd.keys()) + gp.quicksum(pigjg[i, j, g] for i, j, g in pigjg.keys()) + gp.quicksum(pig[i, g]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLRt[t] for t in dLRt.keys()) + gp.quicksum(3*dRLt[t] for t in dRLt.keys())

    # objective = gp.quicksum(1*dRLt[g1] for g1 in dRLt.keys()) + gp.quicksum(zetat[t] for t in zetat.keys()) + gp.quicksum(1*dLRt[g] for g in dLRt.keys())
    
    objective = gp.quicksum(1*dRLt[g1] for g1 in dRLt.keys()) + gp.quicksum(1*dLRt[g] for g in dLRt.keys())
    

    MODEL.setObjective(objective, GRB.MINIMIZE)
    # MODEL.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = datos.tmax
    MODEL.Params.FeasibilityTol = 1e-3

    MODEL.update()

    MODEL.read('final_solution(seed13).sol')

    # MODEL.write('AMMDRPG-Stages.lp')
    # MODEL.write('AMMDRPG-Stages.mps')
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

    MODEL.write('./solution_Stages_SINC.sol')

    # print(xRt)
    # print(xLt)
    # print('Selected_u')
    vals_u = MODEL.getAttr('x', uigtd)
    selected_u = gp.tuplelist((i, g, t, d) for i, g, t, d in vals_u.keys() if vals_u[i, g, t, d] > 0.5)
    print('u')
    print(selected_u)
    
    vals_pLigtd = [pLigtd[i, g, t, d].X for i, g, t, d in pLigtd.keys() if pLigtd[i, g, t, d].X > 0.5]
    print(vals_pLigtd)

    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', zigjg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    print('z')
    print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', vigtd)
    selected_v = gp.tuplelist((i, g, t, d) for i, g, t, d in vals_v.keys() if vals_v[i, g, t, d] > 0.5)
    print('v')
    print(selected_v)
    
    
    display = False
    
    if display:
        
    # path = []
    # path.append(0)
        colores = ['blue', 'green', 'red', 'purple', 'black']
        # path_C.append(origin)
        path_C = []
        paths_D = []
        
        for t in T_index_prima:
            if len(selected_u.select('*', '*', t, '*')) > 0: 
                path_C.append([xLt[t, 0].X, xLt[t, 1].X])
            if len(selected_v.select('*', '*', t, '*')) > 0: 
                path_C.append([xRt[t, 0].X, xRt[t, 1].X])
            
        for t in T_index_prima:
            tuplas = selected_u.select('*', '*', t, '*')
            # print(tuplas)
    
    
            for i, g, t1, d in tuplas:
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
            
                tuplas2 = selected_v.select('*', index_g, '*', '*')
            
                i, g, t2, d = tuplas2[0]
            
                path_D.append([xRt[t2, 0].X, xRt[t2, 1].X])
    
                paths_D.append((path_D, colores[d]))
    
        # print(paths_D)
        fig, ax = plt.subplots()
        # plt.axis([0, 100, 0, 100])
        #
        # for i, g in rhoig.keys():
            # plt.plot(Rig[i, g, 0].X, Rig[i, g, 1].X, 'kD', markersize=1, color='cyan')
            # plt.plot(Lig[i, g, 0].X, Lig[i, g, 1].X, 'kD', markersize=1, color='cyan')
        # #
        # # path_C = []
        for t in T_index:
            # path_C.append([xLt[t, 0].X, xLt[t, 1].X])
            # path_C.append([xRt[t, 0].X, xRt[t, 1].X])
            if len(selected_u.select('*', '*', t, '*')) > 0: 
                plt.plot(xLt[t, 0].X, xLt[t, 1].X, 'ko', alpha = 1, markersize=7, color='red')
                ax.annotate("L" + str(t), xy = (xLt[t, 0].X + 0.5, xLt[t, 1].X+0.5))
            if len(selected_v.select('*', '*', t, '*')) > 0: 
                plt.plot(xRt[t, 0].X, xRt[t, 1].X, 'ko', alpha = 1, markersize=7, color='red')
                ax.annotate("R" + str(t), xy = (xRt[t, 0].X-0.5, xRt[t, 1].X-0.5))
        #
        ax.add_artist(Polygon(path_C, fill=False, animated=False, closed = False,
                      linestyle='-', alpha=1, color='red'))
        #
        
        def esCerrado(path):
            return path[0] == path[-1]
        
        for pathd in paths_D:
            path_D, color = pathd
            if esCerrado(path_D):
                # print(pathd)
                ax.add_artist(Polygon(path_D, fill=False, closed = True, lw = 2, alpha=1, color=color))
            else:
                ax.add_artist(Polygon(path_D, fill=False, closed = False, lw = 2, alpha=1, color=color))
                
        # #
        # # ax.add_artist(Polygon(path_D, fill=False, animated=False,
        # #               linestyle='dotted', alpha=1, color='red'))
        #
        for g in T_index_prima:
            grafo = grafos[g-1]
            centroide = np.mean(grafo.V, axis = 0)
            nx.draw(grafo.G, grafo.pos, node_size=100,
                    node_color='black', alpha=1, width = 1, edge_color='black')
            ax.annotate(g, xy = (centroide[0], centroide[1]))
            nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=9)
        #
        plt.savefig('PDST-Sinc' + str(result[4]) +  '.png')

    # plt.show()
    print(result)
    return result

AMMDRPGSTSINC(datos)
