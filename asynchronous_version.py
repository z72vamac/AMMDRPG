# General case

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

# np.random.seed(30)
#
# lista = list(4*np.ones(2, int))
# nG = len(lista)
# datos = Data([], m=nG, grid = True, tmax=150, alpha = True, nD = 2,
#              orig = [0, 0],
#              dest = [100, 0],
#              vD = 2,
#              init=False,
#              show=True,
#              capacity = 20,
#              seed=2)
#
# datos.generar_grid()
#
# datos.generar_grafos(lista)

# np.random.seed(13)
#
# lista = list(4*np.ones(4, int))
#
# nG = len(lista)
#
# datos = Data([], m=4, grid = True, tmax=60, alpha = True, nD = 2, capacity = 40,
#             init=True,
#             show=True,
#             vD = 2,
#             orig = [0, 0],
#             dest = [100, 0],
#             seed=2)
#
# datos.generar_grid()
# datos.generar_grafos(lista)

def ASYNCHRONOUS(datos):
    
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
    print('Speed of Drone: ' + str(datos.vD))
    print('-----------------------------------------------------\n')
    
    
    
    

    # Sets
    O_index = range(1, datos.m*2 + 1)
    G_index = range(1, datos.m + 1)
        
    MODEL = gp.Model('Asynchoronous-Version')
    
    # u^{e_g o} : x_L^o -> R^{e_g}
    
    u_eg_o_index = []
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for o in O_index:
                u_eg_o_index.append((e, g, o))
    
    
    uego = MODEL.addVars(u_eg_o_index, vtype = GRB.BINARY, name = 'u_eg_o')
    
    # d_L^{e_g o} = || x_L^o - R^{e_g} ||
    
    dL_eg_o_index = u_eg_o_index
    
    dLego = MODEL.addVars(dL_eg_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dL_eg_o')
    
    difLego = MODEL.addVars(dL_eg_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difL_eg_o')
    
    # p_L^{e_g o} = d_L^{e_g o} u^{e_g o} 
    
    pL_eg_o_index = u_eg_o_index
    
    pLego = MODEL.addVars(pL_eg_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pL_eg_o')
    
    # v^{e_g o} : L^{e_g} -> x_R^o
    
    v_eg_o_index = []
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for o in O_index:
                v_eg_o_index.append((e, g, o))
                
    
    vego = MODEL.addVars(v_eg_o_index, vtype = GRB.BINARY, name = 'v_eg_o')
    
    # d_R^{e_g o} = || L^{e_g} - x_R^o ||
    
    dR_eg_o_index = v_eg_o_index
    
    dRego = MODEL.addVars(dR_eg_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dR_eg_o')
    
    difRego = MODEL.addVars(dR_eg_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difR_eg_o')
    
    # p_R^{e_g o} = d_R^{e_g o} v^{e_g o} 
    
    pR_eg_o_index = v_eg_o_index
    
    pRego = MODEL.addVars(pR_eg_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pR_eg_o')
    
    # gamma_g_o = 1 if graph g is being visited for the event o
    
    gamma_g_o_index = []
    
    for g in G_index:
        for o in O_index:
            gamma_g_o_index.append((g, o))
            
    gammago = MODEL.addVars(gamma_g_o_index, vtype = GRB.BINARY, name = 'gamma_g_o')
    
    # K^o = # drones available in the event o
    
    k_o_index = O_index
    
    ko = MODEL.addVars(k_o_index, vtype = GRB.INTEGER, lb = 0.0, ub = nD, name = 'k_o')
    
    # z^{e_g e'_g}: L^{e_g} -> R^{e_g'}
    
    z_eg_eg_index = []
    
    s_eg_index = []
    
    mu_eg_index = []
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            s_eg_index.append((e, g))
            mu_eg_index.append((e, g))
            
            for e_prima in grafos[g-1].aristas:
                if e != e_prima:
                    z_eg_eg_index.append((e, e_prima, g))
    
    
    zegeg = MODEL.addVars(z_eg_eg_index, vtype = GRB.BINARY, name = 'z_eg_e\'g')
    
    seg = MODEL.addVars(s_eg_index, vtype = GRB.CONTINUOUS, lb = 0, name = 's_eg')
    
    mueg = MODEL.addVars(mu_eg_index, vtype = GRB.BINARY, name = 'mu_eg')
    
    # d_{LR}^g: distance associated to graph g
    
    d_LR_g_index = G_index
    
    dLRg = MODEL.addVars(d_LR_g_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR_g')
    
    # d^{e_g e'_g} = || L^{e_g} - R^{e'_g} ||
    
    d_eg_eg_index = z_eg_eg_index
    
    degeg = MODEL.addVars(d_eg_eg_index, vtype = GRB.CONTINUOUS, lb = 0, name = 'd_eg_e\'g')
    
    difegeg = MODEL.addVars(d_eg_eg_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dif_eg_e\'g')
    
    # p^{e_g e'_g} = d^{e_g e'_g} z^{e_g e'_g}
    
    p_eg_eg_index = z_eg_eg_index
    
    pegeg = MODEL.addVars(p_eg_eg_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'p_eg_e\'g')
    
    # R^{e_g}: retrieving point associated to edge e_g
    
    R_eg_index = []
    rho_eg_index = []
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            rho_eg_index.append((e, g))
            for dim in range(2):
                R_eg_index.append((e, g, dim))
    
    Reg = MODEL.addVars(R_eg_index, vtype = GRB.CONTINUOUS, name = 'R_eg')
    rhoeg = MODEL.addVars(rho_eg_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'rho_eg')
    
    # L^{e_g}: launching point associated to edge e_g
    
    L_eg_index = []
    lambda_eg_index = []
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            lambda_eg_index.append((e, g))
            for dim in range(2):
                L_eg_index.append((e, g, dim))
    
    Leg = MODEL.addVars(L_eg_index, vtype = GRB.CONTINUOUS, name = 'L_eg')
    lambdaeg = MODEL.addVars(lambda_eg_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'lambda_eg')
    
    # Modelling the absolute value
    mineg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='min_eg')
    maxeg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='max_eg')
    entryeg = MODEL.addVars(rho_eg_index, vtype=GRB.BINARY, name='entry_eg')
    peg = MODEL.addVars(rho_eg_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'p_eg')
    alphaeg = MODEL.addVars(rho_eg_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alpha_eg')
    
    # x_L^o: Launching point associated to event o
    xLo_index = []
    
    for o in O_index:
        for dim in range(2):
            xLo_index.append((o, dim))
    
    xLo = MODEL.addVars(xLo_index, vtype = GRB.CONTINUOUS, name = 'xL_o')
    
    # x_R^o: Retrieving point associated to event o
    xRo_index = []
    
    for o in O_index:
        for dim in range(2):
            xRo_index.append((o, dim))
    
    xRo = MODEL.addVars(xRo_index, vtype = GRB.CONTINUOUS, name = 'xR_o')
    
    # d_orig: Distance from the origin to the first launching point
    dorig = MODEL.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, name = 'd_orig')
    
    diforig = MODEL.addVars(2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dif_orig')
    
    # d_dest: Distance from the origin to the first launching point
    ddest = MODEL.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, name = 'd_dest')
    
    difdest = MODEL.addVars(2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dif_dest')
    
    # y_{LL}^o: x_L^o -> x_L^{o+1}
    
    y_LL_o_index = O_index[:-1]
    
    yLLo = MODEL.addVars(y_LL_o_index, vtype = GRB.BINARY, name = 'yLL_o')
    
    d_LL_o_index = y_LL_o_index
    
    dLLo = MODEL.addVars(d_LL_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLL_o')
    
    difLLo = MODEL.addVars(d_LL_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLL_o')
    
    # p_{LL}^o = d_{LL}^o y_{LL}^o
    
    pLLo = MODEL.addVars(d_LL_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pLL_o')
    
    # y_{LR}^o: x_L^o -> x_R^{o+1}
    
    y_LR_o_index = O_index[:-1]
    
    yLRo = MODEL.addVars(y_LR_o_index, vtype = GRB.BINARY, name = 'yLR_o')
    
    d_LR_o_index = y_LR_o_index
    
    dLRo = MODEL.addVars(d_LR_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR_o')
    
    difLRo = MODEL.addVars(d_LR_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR_o')
    
    # p_{LR}^o = d_{LR}^o y_{LR}^o
    
    pLRo = MODEL.addVars(d_LR_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pLR_o')
    
    # y_{RL}^o: x_R^o -> x_L^{o+1}
    
    y_RL_o_index = O_index[:-1]
    
    yRLo = MODEL.addVars(y_RL_o_index, vtype = GRB.BINARY, name = 'yRL_o')
    
    d_RL_o_index = y_RL_o_index
    
    dRLo = MODEL.addVars(d_RL_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL_o')
    
    difRLo = MODEL.addVars(d_RL_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL_o')
    
    # p_{RL}^o = d_{RL}^o y_{RL}^o
    
    pRLo = MODEL.addVars(d_RL_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL_o')
    
    # y_{RR}^o: x_R^o -> x_R^{o+1}
    
    y_RR_o_index = O_index[:-1]
    
    yRRo = MODEL.addVars(y_RR_o_index, vtype = GRB.BINARY, name = 'yRR_o')
    
    d_RR_o_index = y_RR_o_index
    
    dRRo = MODEL.addVars(d_RR_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRR_o')
    
    difRRo = MODEL.addVars(d_RR_o_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRR_o')
    
    # p_{RR}^o = d_{RR}^o y_{RR}^o
    
    pRRo = MODEL.addVars(d_RR_o_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRR_o')
    
    # drone distance associated to graph g
    
    droneg = MODEL.addVars(G_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'droneg')
    
    MODEL.update()
    
    ### INITIALIZATION ###
    if datos.init:
        
        hola = heuristic(datos)
        
        # print(hola)
        
        if hola != None:
            uigtd_sol = hola[0]
            vigtd_sol = hola[1]
            z_sol = hola[2]
            heuristic_time = hola[3]
            
            O_set = set()
            
            for e, g, o in uigtd_sol:
                O_set.add(o)
            
            print(O_set)
            
            G_list = list()
            for o in O_set:
                Go_list = list()
                for e, g, u in uigtd_sol:
                    if u == o:
                        Go_list.append(g)
                G_list.append(Go_list)
            
            print(G_list)
            
            to_list = [1]
            
            for o in list(O_set)[:-1]:
                to_list.append(to_list[-1]+2*len(G_list[o-1]))
                
            print(to_list)
            
            tuo_list = list()
            for o in list(O_set):
                tu_list = []
                for t in O_index:
                    if t >= to_list[o-1] and t <= to_list[o-1] + len(G_list[o-1]) - 1:
                        tu_list.append(t)
                tuo_list.append(tu_list)
                
            print(tuo_list)        
                
            
            tvo_list = list()
            for o in list(O_set):
                tv_list = []
                for t in O_index:
                    if t - len(G_list[o-1]) >= to_list[o-1] and t <= to_list[o-1] + 2*len(G_list[o-1]) - 1:
                        tv_list.append(t)
                tvo_list.append(tv_list)
            
            print(tvo_list)
            
            indices = []
                             
            for o in O_set:
                filtro = [(a, b) for a, b, c in uigtd_sol if c == o]
                for t, (e, g) in zip(tuo_list[o-1], filtro):
                    uego[e, g, t].start = 1
                    indices.append((e, g, t))
                    uigtd_sol.remove((e, g, o))
                        
            for o in O_set:
                filtro = [(a, b) for a, b, c in vigtd_sol if c == o]
                for t, (e, g) in zip(tvo_list[o-1], filtro):
                        vego[e, g, t].start = 1
                        indices.append((e, g, t))
                        vigtd_sol.remove((e, g, o))
                        
            for e, g, o in uego.keys():
                if not(e, g, o in indices):
                    uego[e, g, o].start = 0
                    vego[e, g, o].start = 0
                    
                    
            for i, j, g in zegeg.keys():
                if (i, j, g) in z_sol:
                    zegeg[i, j, g].start = 1
                else:
                    zegeg[i, j, g].start = 0                

            
            print(indices)
            
                    
                    
                

                
            
                
    ### DRONE CONSTRAINTS ###
    
    # (44): x_L^o must be associated to one point R^{e_g}
    
    for g in G_index:
        MODEL.addConstr(uego.sum('*', g, '*') == 1)
    
    # (45): L^{e_g} must be associated to one point x_R^o
    
    for g in G_index:
        MODEL.addConstr(vego.sum('*', g, '*') == 1)
        
    # (46): If there exists available drones in the event o, we can assign a launching point to this event
    
    for o in O_index:
        MODEL.addConstr(uego.sum('*', '*', o) <= ko[o])
        
    # (47): For each operation, we associate only a launching point or a retrieving point.
    
    for o in O_index:
        MODEL.addConstr(uego.sum('*', '*', o) + vego.sum('*', '*', o) <= 1)
        
    # (48): If edge e_g is visited, it is because we enter to this edge or the visit comes from the other edges
    # (49): If edge e_g is visited, it is because we exit from this edge or the visit comes from the other edges
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            # (48)
            MODEL.addConstr(uego.sum(e, g, '*') + zegeg.sum('*', e, g) == mueg[e, g])
            
            # (49)
            MODEL.addConstr(vego.sum(e, g, '*') + zegeg.sum(e, '*', g) == mueg[e, g])
    
    # (*): The retrieving associated to graph g must be after the launching
    
    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr(uego.sum('*', g, o) <= gp.quicksum(vego[e, g, o_prima] for e in grafos[g-1].aristas for o_prima in O_index if o_prima > o))
    
    # (MTZ) Constraints
    for g in G_index:
        for e in grafos[g-1].aristas:
            for e_prima in grafos[g-1].aristas:
                if e != e_prima:
                    MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (seg[e, g] - seg[e_prima, g]) + grafos[g-1].num_aristas * zegeg[e, e_prima, g])
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            MODEL.addConstr(seg[e, g] >= 0)
            MODEL.addConstr(seg[e, g] <= grafos[g-1].num_aristas - 1)
    
    # (50): If we start the visit of g in event o, the gamma starts to be one at event o
    
    for g in G_index:
        for o in O_index:
            MODEL.addConstr(uego.sum('*', g, o) <= gammago[g, o])
    
    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr((o-1)*(1 - uego.sum('*', g, o)) >= gp.quicksum(gammago[g, o_prima] for o_prima in O_index if o_prima < o))
    
    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr((len(O_index)-o+1)*(1 - vego.sum('*', g, o)) >= gp.quicksum(gammago[g, o_prima] for o_prima in O_index if o_prima >= o))
    
    
    # (51): If we finish the visit of g in event o, the new gamma is zero.
    
    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr(gammago[g, o+1] >= gammago[g, o] - vego.sum('*', g, o+1))
    
    # for g in G_index:
    #     for o in O_index[:-1]:
    #         MODEL.addConstr(1 - vego.sum('*', g, o) >= gp.quicksum(gammago[g, o_prima] for o_prima in O_index if o_prima > o))
           
    # (52): The number of drones available at event 1 is |D|
    
    MODEL.addConstr(ko[1] == nD)
    
    # (53): The number of drones available at event o+1 depends on what happens at event o
    
    for o in O_index[:-1]:
        MODEL.addConstr(ko[o+1] == ko[o] + vego.sum('*', '*', o) - uego.sum('*', '*', o))
    
    
    ### MOTHERSHIP CONSTRAINTS ###
    
    # (54): The first point must be a launching point, so the first transition should be LL or LR
    
    MODEL.addConstr(yLLo[1] + yLRo[1] == 1)
    
    # (55): If we launch a drone at event o+1, then it is because the previous transition was RL or LL
    # (56): If we retrieving a drone at event o+1, then it is because the previous transition was LR or RR
    
    for o in O_index[:-2]:
        # (55)
        MODEL.addConstr(yLLo[o+1] + yLRo[o+1] >= yRLo[o] + yLLo[o])
        
        # (56)
        MODEL.addConstr(yRRo[o+1] + yRLo[o+1] >= yLRo[o] + yRRo[o])
    
    # (57): The last point must be a retrieving point
    
    MODEL.addConstr(yLRo[O_index[-2]] + yRRo[O_index[-2]] == 1)
    
    ### DISTANCE CONSTRAINTS ###
    
    # d_L^{e_g o}
    
    for o in O_index:
        for g in G_index:
            for e in grafos[g-1].aristas:
                for dim in range(2):
                    MODEL.addConstr(difLego[e, g, o, dim] >=  xLo[o, dim] - Reg[e, g, dim])
                    MODEL.addConstr(difLego[e, g, o, dim] >= -xLo[o, dim] + Reg[e, g, dim])
                
                MODEL.addConstr(difLego[e, g, o, 0] * difLego[e, g, o, 0] + difLego[e, g, o, 1] *difLego[e, g, o, 1] <= dLego[e, g, o] * dLego[e, g, o])
    
    # d_R^{e_g o}
    
    for o in O_index:
        for g in G_index:
            for e in grafos[g-1].aristas:
                for dim in range(2):
                    MODEL.addConstr(difRego[e, g, o, dim] >=  Leg[e, g, dim] - xRo[o, dim])
                    MODEL.addConstr(difRego[e, g, o, dim] >= -Leg[e, g, dim] + xRo[o, dim])
                
                MODEL.addConstr(difRego[e, g, o, 0] * difRego[e, g, o, 0] + difRego[e, g, o, 1] *difRego[e, g, o, 1] <= dRego[e, g, o] * dRego[e, g, o])
    
    # d^{e_g e'_g}
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for e_prima in grafos[g-1].aristas:
                if e != e_prima:
                    for dim in range(2):
                        MODEL.addConstr(difegeg[e, e_prima, g, dim] >=  Leg[e, g, dim] - Reg[e_prima, g, dim])
                        MODEL.addConstr(difegeg[e, e_prima, g, dim] >= -Leg[e, g, dim] + Reg[e_prima, g, dim])
                    
                    MODEL.addConstr(difegeg[e, e_prima, g, 0] * difegeg[e, e_prima, g, 0] + difegeg[e, e_prima, g, 1] * difegeg[e, e_prima, g, 1] <= degeg[e, e_prima, g] * degeg[e, e_prima, g])
    
    # d_orig
    
    for dim in range(2):
        MODEL.addConstr(diforig[dim] >=  datos.orig[dim] - xLo[1, dim])
        MODEL.addConstr(diforig[dim] >= -datos.orig[dim] + xLo[1, dim])
        
    MODEL.addConstr(diforig[0] * diforig[0] + diforig[1] * diforig[1] <= dorig*dorig)
        
    
    # d_{LL}^{o}
    
    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(difLLo[o, dim] >=  xLo[o, dim] - xLo[o+1, dim])
            MODEL.addConstr(difLLo[o, dim] >= -xLo[o, dim] + xLo[o+1, dim])
        
        MODEL.addConstr(difLLo[o, 0] * difLLo[o, 0] + difLLo[o, 1] * difLLo[o, 1] <= dLLo[o] * dLLo[o])
    
    # d_{LR}^{o}
    
    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(difLRo[o, dim] >=  xLo[o, dim] - xRo[o+1, dim])
            MODEL.addConstr(difLRo[o, dim] >= -xLo[o, dim] + xRo[o+1, dim])
        
        MODEL.addConstr(difLRo[o, 0] * difLRo[o, 0] + difLRo[o, 1] * difLRo[o, 1] <= dLRo[o] * dLRo[o])
    
    # d_{RL}^{o}
    
    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(difRLo[o, dim] >=  xRo[o, dim] - xLo[o+1, dim])
            MODEL.addConstr(difRLo[o, dim] >= -xRo[o, dim] + xLo[o+1, dim])
        
        MODEL.addConstr(difRLo[o, 0] * difRLo[o, 0] + difRLo[o, 1] * difRLo[o, 1] <= dRLo[o] * dRLo[o])
    
    # d_{RR}^{o}
    
    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(difRRo[o, dim] >=  xRo[o, dim] - xRo[o+1, dim])
            MODEL.addConstr(difRRo[o, dim] >= -xRo[o, dim] + xRo[o+1, dim])
        
        MODEL.addConstr(difRRo[o, 0] * difRRo[o, 0] + difRRo[o, 1] * difRRo[o, 1] <= dRRo[o] * dRRo[o])
    
    # d_dest
    
    for dim in range(2):
        MODEL.addConstr(difdest[dim] >=  xRo[O_index[-1], dim] - datos.dest[dim])
        MODEL.addConstr(difdest[dim] >= -xRo[O_index[-1], dim] + datos.dest[dim])
        
    MODEL.addConstr(difdest[0] * difdest[0] + difdest[1] * difdest[1] <= ddest*ddest)
    
    # (58) Mothership distance: dM
    
    dM = dorig + pLLo.sum('*') + pLRo.sum('*') + pRLo.sum('*') + pRRo.sum('*') + ddest
    
    MODEL.setObjective(dM, GRB.MINIMIZE)
    
    # (59): Distance associated to the graph g: d_{LR}^g
    
    for g in G_index:
        MODEL.addConstr(dLRg[g] == gp.quicksum(gammago[g, o]* (pLLo[o] + pLRo[o] + pRLo[o] + pRRo[o]) for o in O_index[:-1]))
    
    ### LINEARIZATION CONSTRAINTS ###
    
    # p^{e_g} = \alpha^{e_g} \mu^{e_g}
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            MODEL.addConstr(peg[e, g] <= mueg[e, g])
            MODEL.addConstr(peg[e, g] <= alphaeg[e, g])
            MODEL.addConstr(peg[e, g] >= mueg[e, g] + alphaeg[e, g] - 1)
            
    # p_L^{e_g o} = d_L^{e_g o} u^{e_g o}
    
    # BigM = 1e5
    BigM = datos.capacity*datos.vD*2
    SmallM = 0 
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for o in O_index:
                MODEL.addConstr(pLego[e, g, o] <= BigM * uego[e, g, o])
                MODEL.addConstr(pLego[e, g, o] <= dLego[e, g, o])
                MODEL.addConstr(pLego[e, g, o] >= SmallM * uego[e, g, o])
                MODEL.addConstr(pLego[e, g, o] >= dLego[e, g, o] - BigM * (1 - uego[e, g, o]))
                
    # p_R^{e_g o} = d_R^{e_g o} v^{e_g o}
    
    BigM = datos.capacity*datos.vD*2
    SmallM = 0
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for o in O_index:
                MODEL.addConstr(pRego[e, g, o] <= BigM * vego[e, g, o])
                MODEL.addConstr(pRego[e, g, o] <= dRego[e, g, o])
                MODEL.addConstr(pRego[e, g, o] >= SmallM * vego[e, g, o])
                MODEL.addConstr(pRego[e, g, o] >= dRego[e, g, o] - BigM * (1 - vego[e, g, o]))
                
    # p^{e_g e'_g} = d^{e_g e'_g} z^{e_g e'_g}
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            for e_prima in grafos[g-1].aristas:
                if e != e_prima:
                    first_e = e // 100 - 1
                    second_e = e % 100
                    first_e_prima = e_prima // 100 - 1
                    second_e_prima = e_prima % 100
            
                    segm_e = Poligonal(np.array([[grafos[g-1].V[first_e, 0], grafos[g-1].V[first_e, 1]], 
                                                 [grafos[g-1].V[second_e, 0], grafos[g-1].V[second_e, 1]]]), grafos[g-1].A[first_e, second_e])
                    segm_e_prima = Poligonal(np.array([[grafos[g-1].V[first_e_prima, 0], grafos[g-1].V[first_e_prima, 1]], 
                                                 [grafos[g-1].V[second_e_prima, 0], grafos[g-1].V[second_e_prima, 1]]]), grafos[g-1].A[first_e_prima, second_e_prima])
            
                    BigM_local = eM.estima_BigM_local(segm_e, segm_e_prima)
                    SmallM_local = eM.estima_SmallM_local(segm_e, segm_e_prima)
                    MODEL.addConstr((pegeg[e, e_prima, g] <= BigM_local * zegeg[e, e_prima, g]))
                    MODEL.addConstr((pegeg[e, e_prima, g] <= degeg[e, e_prima, g]))
                    MODEL.addConstr((pegeg[e, e_prima, g] >= SmallM_local * zegeg[e, e_prima, g]))
                    MODEL.addConstr((pegeg[e, e_prima, g] >= degeg[e, e_prima, g] - BigM_local * (1 - zegeg[e, e_prima, g])))
    
    # y_{LL}^o = \sum_{e_g\in E_g} u^{e_g o} \sum_{e_g\in E_g} u^{e_g (o+1)}
    
    # (64)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] <= uego.sum('*', '*', o))
    
    # (65)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] <= uego.sum('*', '*', o+1))
    
    # (66)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] >= uego.sum('*', '*', o) + uego.sum('*', '*', o+1) - 1)
    
    # p_{LL}^o = d_{LL}^o y_{LL}^o
    
    BigM = 1e5
    
    for o in O_index[:-1]:
        MODEL.addConstr(pLLo[o] <= BigM * yLLo[o])
        MODEL.addConstr(pLLo[o] <= dLLo[o])
        MODEL.addConstr(pLLo[o] >= SmallM * dLLo[o])
        MODEL.addConstr(pLLo[o] >= dLLo[o] - BigM * (1 - yLLo[o]))
        
        
    # y_{LR}^o = \sum_{e_g\in E_g} u^{e_g o} \sum_{e_g\in E_g} v^{e_g (o+1)}
    
    # (61)
    for o in O_index[:-1]:
        MODEL.addConstr(yLRo[o] <= uego.sum('*', '*', o))
    
    # (62)
    for o in O_index[:-1]:
        MODEL.addConstr(yLRo[o] <= vego.sum('*', '*', o+1))
    
    # (63)
    for o in O_index[:-1]:
        MODEL.addConstr(yLRo[o] >= uego.sum('*', '*', o) + vego.sum('*', '*', o+1) - 1)
    
    # p_{LR}^o = d_{LR}^o y_{LR}^o
    
    for o in O_index[:-1]:
        MODEL.addConstr(pLRo[o] <= BigM * yLRo[o])
        MODEL.addConstr(pLRo[o] <= dLRo[o])
        MODEL.addConstr(pLRo[o] >= SmallM * dLRo[o])
        MODEL.addConstr(pLRo[o] >= dLRo[o] - BigM * (1 - yLRo[o]))
        
    # y_{RL}^o = \sum_{e_g\in E_g} v^{e_g o} \sum_{e_g\in E_g} u^{e_g (o+1)}
    
    # (70)
    for o in O_index[:-1]:
        MODEL.addConstr(yRLo[o] <= vego.sum('*', '*', o))
    
    # (71)
    for o in O_index[:-1]:
        MODEL.addConstr(yRLo[o] <= uego.sum('*', '*', o+1))
    
    # (72)
    for o in O_index[:-1]:
        MODEL.addConstr(yRLo[o] >= vego.sum('*', '*', o) + uego.sum('*', '*', o+1) - 1)
    
    # p_{RL}^o = d_{RL}^o y_{RL}^o
    
    for o in O_index[:-1]:
        MODEL.addConstr(pRLo[o] <= BigM * yRLo[o])
        MODEL.addConstr(pRLo[o] <= dRLo[o])
        MODEL.addConstr(pRLo[o] >= SmallM * dRLo[o])
        MODEL.addConstr(pRLo[o] >= dRLo[o] - BigM * (1 - yRLo[o]))
        
    # y_{RR}^o = \sum_{e_g\in E_g} v^{e_g o} \sum_{e_g\in E_g} v^{e_g (o+1)}
    
    # (67)
    for o in O_index[:-1]:
        MODEL.addConstr(yRRo[o] <= vego.sum('*', '*', o))
    
    # (68)
    for o in O_index[:-1]:
        MODEL.addConstr(yRRo[o] <= vego.sum('*', '*', o+1))
    
    # (69)
    for o in O_index[:-1]:
        MODEL.addConstr(yRRo[o] >= vego.sum('*', '*', o) + vego.sum('*', '*', o+1) - 1)
    
    # p_{RR}^o = d_{RR}^o y_{RR}^o
    
    for o in O_index[:-1]:
        MODEL.addConstr(pRRo[o] <= BigM * yRRo[o])
        MODEL.addConstr(pRRo[o] <= dRRo[o])
        MODEL.addConstr(pRRo[o] >= SmallM * dRRo[o])
        MODEL.addConstr(pRRo[o] >= dRRo[o] - BigM * (1 - yRRo[o]))
        
    ### COORDINATION CONSTRAINT ###
    
    for g in G_index:
        MODEL.addConstr((pLego.sum('*', g, '*') + pegeg.sum('*', '*', g) + gp.quicksum(peg[e, g]*grafos[g-1].longaristas[e // 100 - 1, e % 100] for e in grafos[g-1].aristas) + pRego.sum('*', g, '*'))/datos.vD <= dLRg[g]/datos.vC)
    
    for g in G_index:
        MODEL.addConstr(droneg[g] == (pLego.sum('*', g, '*') + pegeg.sum('*', '*', g) + gp.quicksum(peg[e, g]*grafos[g-1].longaristas[e // 100 - 1, e % 100] for e in grafos[g-1].aristas) + pRego.sum('*', g, '*'))/datos.vD)
    
    ### ENDURANCE CONSTRAINT ###
    
    for g in G_index:
        MODEL.addConstr(dLRg[g]/datos.vC <= datos.capacity)
        
        
    ### (\ALPHA-E) and (\ALPHA-G) CONSTRAINTS ###
    
    for g in G_index:
        for e in grafos[g-1].aristas:
            start = e // 100 - 1
            end = e % 100
            
            MODEL.addConstr(rhoeg[e, g] - lambdaeg[e, g] == maxeg[e, g] - mineg[e, g])
            MODEL.addConstr(maxeg[e, g] + mineg[e, g] == alphaeg[e, g])
            if datos.alpha:
                MODEL.addConstr(peg[e, g] >= grafos[g-1].A[start, end])
            MODEL.addConstr(maxeg[e, g] <= 1 - entryeg[e, g])
            MODEL.addConstr(mineg[e, g] <= entryeg[e, g])
            MODEL.addConstr(Reg[e, g, 0] == rhoeg[e, g] * grafos[g-1].V[start, 0] + (1 - rhoeg[e, g]) * grafos[g-1].V[end, 0])
            MODEL.addConstr(Reg[e, g, 1] == rhoeg[e, g] * grafos[g-1].V[start, 1] + (1 - rhoeg[e, g]) * grafos[g-1].V[end, 1])
            MODEL.addConstr(Leg[e, g, 0] == lambdaeg[e, g] * grafos[g-1].V[start, 0] + (1 - lambdaeg[e, g]) * grafos[g-1].V[end, 0])
            MODEL.addConstr(Leg[e, g, 1] == lambdaeg[e, g] * grafos[g-1].V[start, 1] + (1 - lambdaeg[e, g]) * grafos[g-1].V[end, 1])
    
    # MODEL.read('solution.sol')
    acum = 0
    if datos.alpha:
        for g in G_index:
            for e in grafos[g-1].aristas:
                start = e // 100 - 1
                end = e % 100
                # acum + = grafos[g-1].A[start,end]*grafos[g-1].A
        MODEL.addConstr(dM >= gp.quicksum(droneg[g] for g in G_index)) 
    
    MODEL.update()
    

    MODEL.Params.Threads = 6
    MODEL.Params.TimeLimit = datos.tmax
    
    MODEL.write('model.lp')

    
    if datos.init:
        MODEL.optimize(callback)
    else:
        MODEL.optimize()
    
    
    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result =  [np.nan, np.nan, np.nan, np.nan]
        # if datos.grid:
        #     result.append('Grid')
        # else:
        #     result.append('Delauney')
        #
        # result.append('Stages')
        if datos.init:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)
        
        return result

        # return result
    
    elif MODEL.SolCount == 0:
        result =  [np.nan, np.nan, np.nan, np.nan]
        # if datos.grid:
        #     result.append('Grid')
        # else:
        #     result.append('Delauney')
        #
        # result.append('Stages')

        if datos.init:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)
        
        return result
    
    else:
        
        if datos.init:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)
            
        result.append(MODEL.getAttr('MIPGap'))
        result.append(MODEL.Runtime)
        result.append(MODEL.getAttr('NodeCount'))
        result.append(MODEL.ObjVal)
    

        
    MODEL.write('solution.sol')
    
    
    vals_u = MODEL.getAttr('x', uego)
    selected_u = gp.tuplelist((e, g, o) for e, g, o in vals_u.keys() if vals_u[e, g, o] > 0.5)
    print(selected_u)
    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', zegeg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', vego)
    selected_v = gp.tuplelist((e, g, o) for e, g, o in vals_v.keys() if vals_v[e, g, o] > 0.5)
    print(selected_v)
    
    vals_gamma = MODEL.getAttr('x', gammago)
    selected_gamma = gp.tuplelist((g, o) for g, o in vals_gamma.keys() if vals_gamma[g, o] > 0.5)
    print(selected_gamma)
    
    # vals_droneg = MODEL.getAttr('x', droneg)
    # print(vals_droneg)
    print('Total time: ' + str(MODEL.ObjVal/datos.vC))
    
    distance = dorig.X + ddest.X
    
    wasU = True
    isU = True
        
    for o in O_index[1:]:
        isU = len(selected_u.select('*', '*', o)) > 0
        
        if wasU and isU:
            distance += np.linalg.norm(np.array([xLo[o-1, 0].X, xLo[o-1, 1].X]) - np.array([xLo[o, 0].X, xLo[o, 1].X]))
        
        elif not(wasU) and isU:
            distance += np.linalg.norm(np.array([xRo[o-1, 0].X, xRo[o-1, 1].X]) - np.array([xLo[o, 0].X, xLo[o, 1].X]))
        
        elif wasU and not(isU):
            distance += np.linalg.norm(np.array([xLo[o-1, 0].X, xLo[o-1, 1].X]) - np.array([xRo[o, 0].X, xRo[o, 1].X]))
        
        elif not(wasU) and not(isU):
            distance += np.linalg.norm(np.array([xRo[o-1, 0].X, xRo[o-1, 1].X]) - np.array([xRo[o, 0].X, xRo[o, 1].X]))
            
        wasU = isU

        
    print('Time operating: ' + str(distance/datos.vC))
    print('Time waiting: ' + str(MODEL.ObjVal - distance/datos.vC))
    
    log = True
    
    if log:
        fig, ax = plt.subplots()
        
        colors = {'lime': 0 , 'orange' : 0, 'fuchsia' : 0}
        
        # Mothership Route
    
        ax.arrow(datos.orig[0], datos.orig[1], xLo[1, 0].X-datos.orig[0], xLo[1, 1].X - datos.orig[1], width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
        plt.plot(datos.orig[0], datos.orig[1], 's', markersize = 10, c = 'black')
        
        wasU = True
        isU = True
        
        for o in O_index[1:]:
            isU = len(selected_u.select('*', '*', o)) > 0
            
            if wasU and isU:
                
                ax.arrow(xLo[o-1, 0].X, xLo[o-1, 1].X, xLo[o, 0].X - xLo[o-1, 0].X, xLo[o, 1].X - xLo[o-1, 1].X, width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
                
                edge = selected_u.select('*', '*', o)[0][0]
                g = selected_u.select('*', '*', o)[0][1]
                
                # ax.arrow(xLo[o, 0].X, xLo[o, 1].X, Reg[edge, g, 0].X - xLo[o, 0].X, Reg[edge, g, 1].X - xLo[o, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')
                        
            elif not(wasU) and isU:
                
                ax.arrow(xRo[o-1, 0].X, xRo[o-1, 1].X, xLo[o, 0].X - xRo[o-1, 0].X, xLo[o, 1].X - xRo[o-1, 1].X, width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
    
                edge = selected_u.select('*', '*', o)[0][0]
                g = selected_u.select('*', '*', o)[0][1]
                
                # ax.arrow(Leg[edge, g, 0].X, Leg[edge, g, 1].X, xRo[o, 0].X - Leg[edge, g, 0].X, xRo[o, 1].X - Leg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            
                        
            elif wasU and not(isU):
                
                ax.arrow(xLo[o-1, 0].X, xLo[o-1, 1].X, xRo[o, 0].X - xLo[o-1, 0].X, xRo[o, 1].X - xLo[o-1, 1].X, width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
    
                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]
                
                # ax.arrow(Leg[edge, g, 0].X, Leg[edge, g, 1].X, xRo[o, 0].X - Leg[edge, g, 0].X, xRo[o, 1].X - Leg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            
    
            elif not(wasU) and not(isU):
                
                ax.arrow(xRo[o-1, 0].X, xRo[o-1, 1].X, xRo[o, 0].X - xRo[o-1, 0].X, xRo[o, 1].X - xRo[o-1, 1].X, width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
    
                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]
                
                # ax.arrow(Leg[edge, g, 0].X, Leg[edge, g, 1].X, xRo[o, 0].X - Leg[edge, g, 0].X, xRo[o, 1].X - Leg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            
            
            wasU = isU
        
        ax.arrow(xRo[len(O_index), 0].X, xRo[len(O_index), 1].X, datos.dest[0]-xRo[len(O_index), 0].X, datos.dest[1] - xRo[len(O_index), 1].X, width = 0.3, head_width = 1, length_includes_head = True, color = 'black')
        plt.plot(datos.dest[0], datos.dest[1], 's', markersize = 10, c = 'black')
    
        # Drone Route
        isU = True
        
        for o in O_index:
            isU = len(selected_u.select('*', '*', o)) > 0
            
                            
            if isU:
                      
                edge = selected_u.select('*', '*', o)[0][0]
                g = selected_u.select('*', '*', o)[0][1]
                
                
                for key, value in colors.items():
                    if value <= 0.5:
                        colors[key] = g
                        break
                
                color = key
                
                
                ax.arrow(xLo[o, 0].X, xLo[o, 1].X, Reg[edge, g, 0].X - xLo[o, 0].X, Reg[edge, g, 1].X - xLo[o, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)
                
                for e1, e2, g in selected_z.select('*', '*', g):
                    if pegeg[e1, e2, g].X >= 0.1:
                        ax.arrow(Leg[e1, g, 0].X, Leg[e1, g, 1].X, Reg[e2, g, 0].X - Leg[e1, g, 0].X, Reg[e2, g, 1].X - Leg[e1, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)          

                for e in grafos[g-1].aristas:
                    if mueg[e, g].X >= 0.5 and peg[e, g].X >= 0.05:
                        ax.arrow(Reg[e, g, 0].X, Reg[e, g, 1].X, Leg[e, g, 0].X - Reg[e, g, 0].X, Leg[e, g, 1].X - Reg[e, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)
                
                edge_new = selected_v.select('*', g, '*')[0][0]
                o_new = selected_v.select('*', g, '*')[0][2]
                
                ax.arrow(Leg[edge_new, g, 0].X, Leg[edge_new, g, 1].X, xRo[o_new, 0].X - Leg[edge_new, g, 0].X, xRo[o_new, 1].X - Leg[edge_new, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)         

            else:              

                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]
                
                for key, value in colors.items():
                    if value == g:
                        colors[key] = 0
                        break
            #
            #     ax.arrow(Leg[edge, g, 0].X, Leg[edge, g, 1].X, xRo[o, 0].X - Leg[edge, g, 0].X, xRo[o, 1].X - Leg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)            
    
            wasU = isU
                                                            
            
        for g in grafos:
            nx.draw(g.G, g.pos, node_size=10, width = 1, 
                    node_color = 'blue', alpha = 1, edge_color = 'blue')
        
        plt.savefig('Asynchronous{b}-{c}-{d}-{e}.png'.format(b = datos.m, c = int(datos.alpha), d = datos.capacity, e = datos.nD))
        
        import tikzplotlib
        import matplotlib
        
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        tikzplotlib.save('asynchronous.tex', encoding = 'utf-8')
        
        # plt.show()

    print(result)
    print()
    
    return result
        # plt.show()















    
    
    
    
    
    
    
    


























            





























































