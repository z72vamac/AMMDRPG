#!/usr/bin/python

# Copyright 2019, Gurobi Optimization, LLC

# Solve the classic diet model, showing how to add constraints
# to an existing model.


import gurobipy as gp
from gurobipy import GRB
import numpy as np
from entorno import Poligono, Elipse, Poligonal
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
import estimacion_M as eM
from data import *
from itertools import combinations
import auxiliar_functions as af
import time
# Con 15 todavia no la encuentra
# np.random.seed(112)
# np.random.seed(11112)
# 168.60477938110762

def MTZ(datos):

    print()
    print('--------------------------------------------')
    print('Heuristic: MTZ of centroids')
    print('--------------------------------------------')
    print()
    
    data = datos.data
    m = len(data)

    # modo = datos.modo

    # Model
    M = gp.Model("MTZ_MODEL")

    # Generando variables continuas de entrada y salida
    x_index = []
    d_index = []

    for c in range(m):
        # comp = data[c]
        # if type(comp) is Poligonal:
        x_index.append((c, 0))
        x_index.append((c, 1))
        d_index.append(c)

    x = M.addVars(x_index, vtype=GRB.CONTINUOUS, name="x")

    z_index = []

    for c1 in d_index:
        for c2 in d_index:
            if c1 != c2:
                z_index.append((c1, c2))

    p = M.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0, name="p")

    z = M.addVars(z_index, vtype=GRB.BINARY, name='z')
    d = M.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0, name='dcc')

    # if datos.init:
    #     d = M.addVars(z_index, vtype = GRB.CONTINUOUS, lb = ds, name = 'dcc')

    dif = M.addVars(z_index, 2, vtype=GRB.CONTINUOUS, lb=0, name='dif')

    dc = M.addVars(d_index, vtype=GRB.CONTINUOUS, lb=0, name='dc')
    difc = M.addVars(d_index, 2, vtype=GRB.CONTINUOUS, lb=0, name='difc')

    # Generando los mus de la envolvente convexa, los landas de la poligonal y las
    # variables binarias que indican qué segmento se elige

    mu_index = []
    landa_index = []
    sublanda_index = []
    u_index = []
    s_index = []

    for c in d_index:
        comp = data[c]
        if type(comp) is Poligono:
            for mu in range(comp.num_puntos):
                mu_index.append((c, mu))
        if type(comp) is Poligonal:
            u_index.append(c)
            # landa de la variable de entrada en la poligonal c
            landa_index.append((c, 0))
            # landa de la variable de salida en la poligonal c
            landa_index.append((c, 1))
            for segm in range(comp.num_segmentos):
                s_index.append((c, 0, segm))
                s_index.append((c, 1, segm))
            for punto in range(comp.num_puntos):
                sublanda_index.append((c, 0, punto))
                sublanda_index.append((c, 1, punto))

    mu = M.addVars(mu_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='mu')
    landa = M.addVars(landa_index, vtype=GRB.CONTINUOUS, name='landa')
    sublanda = M.addVars(sublanda_index, vtype=GRB.CONTINUOUS,
                         lb=0.0, ub=1.0, name='sublanda')
    s = M.addVars(s_index, vtype=GRB.BINARY, name='s')
    u = M.addVars(u_index, vtype=GRB.BINARY, name='u')
    minc = M.addVars(u_index, vtype=GRB.CONTINUOUS, lb=0.0, name='min')
    maxc = M.addVars(u_index, vtype=GRB.CONTINUOUS, lb=0.0, name='max')

    sc = M.addVars(d_index, vtype=GRB.CONTINUOUS, lb=0, ub=m - 1, name='sc')

    if datos.pol:
        mu_especial = M.addVars(range(m), len(poligono), 2, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='mu_especial')

    M.update()

    #
    #     for c in sc.keys():
    #         sc[c].start = scs[c]
#            d[i, j].start = ds[i, j]

    # for c in s.keys():
    #     s[c].start = ss[c]
    #
    # for c in u.keys():
    #     u[c].start = us[c]
#        for c in dc.keys():
#            dc[c].start = dcs[c]

    # Constraints
    for c1, c2 in z.keys():
        comp1 = data[c1]
        comp2 = data[c2]
        BigM = eM.estima_BigM_local(comp1, comp2)
        SmallM = eM.estima_SmallM_local(comp1, comp2)
        # M.addConstr(d[c1, c2] <= BigM)
        # M.addConstr(d[c1, c2]>= SmallM)
        # SmallM, x_0, x_1 = af.min_dist(comp1, comp2)
        M.addConstr(p[c1, c2] >= SmallM * z[c1, c2], name='p2')
        M.addConstr(p[c1, c2] >= d[c1, c2] - BigM * (1 - z[c1, c2]), name='p3')
        #
        # M.addConstr(p[c1, c2] >= SmallM*z[c1, c2])
        # M.addConstr(p[c1, c2] <= d[c1, c2] + z[c1, c2]*SmallM - SmallM)
        # M.addConstr(p[c1, c2] <= z[c1, c2]*BigM)

        M.addConstrs(dif[c1, c2, dim] >=  x[c2, dim] - x[c1, dim] for dim in range(2))
        M.addConstrs(dif[c1, c2, dim] >= -x[c2, dim] + x[c1, dim] for dim in range(2))


        M.addConstr(dif[c1, c2, 0] * dif[c1, c2, 0] +
                    dif[c1, c2, 1] * dif[c1, c2, 1] <= d[c1, c2] * d[c1, c2])


    # Restricciones para formar un tour
    M.addConstr(gp.quicksum(z[v, 0] for v in range(1, m-1)) == 0)
    M.addConstr(gp.quicksum(z[m-1, w] for w in range(1, m-1)) == 0)
    M.addConstrs(gp.quicksum(z[v , w] for w in range(m) if w != v) == 1 for v in range(m))
    M.addConstrs(gp.quicksum(z[w , v] for w in range(m) if w != v) == 1 for v in range(m))

    for v in range(1, m-1):
        for w in range(1, m-1):
            if v != w:
                M.addConstr(m - 1 >= (sc[v] - sc[w]) + m * z[v, w])

    # for v in range(1, nG+1):
    #     M.addConstr(s[v] - s[0] + (nG+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, nG+1):
    #     M.addConstr(s[0] - s[v] + (nG+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, nG+1):
    #     M.addConstr(-z[0,v] - s[v] + (nG+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     M.addConstr(-z[v,0] + s[v] + (nG+1-3)*z[0,v] <= nG+1-2, name="LiftedUB(%s)"%v)

    #     M.addConstr(s[v] >= 1)
    #     for v in range(1, m-1):
    #     M.addConstr(s[v] <= len(T_index) - 1)
    #
    # M.addConstr(s[0] == 0)
    # M.addConstr(s[m-1] == m-1)


    # Restriccion 10
    M.addConstr(sc[0] == 0, name = 'rest10')
    M.addConstr(sc[m-1] == m-1)

    for c in range(1, m-1):
        M.addConstr(sc[c] >= 1, name = 'rest11')


    M.addConstrs(difc[c, dim] >=  x[c, dim] - data[c].centro[dim] for dim in range(2) for c in range(m))
    M.addConstrs(difc[c, dim] >= -x[c, dim] + data[c].centro[dim] for dim in range(2) for c in range(m))
    M.addConstrs(difc[c, 0]*difc[c, 0] + difc[c, 1]*difc[c, 1] <= data[c].radio*data[c].radio for c in range(m))

    M.update()

    fc = np.ones(m) * 1

    # for c in range(m):
    #     if fc[c] >= 1.0 and type(data[c]) is not Poligonal:
    #         for j in range(2):
    #             M.addConstr(x[c, 0, j] == x[c, 1, j])

    objective = gp.quicksum(p[c1, c2] for c1 in range(m) for c2 in range(m) if c1 != c2)

    # objective = gp.quicksum(p[index] for index in p.keys())

    M.setObjective(objective, GRB.MINIMIZE)

    M.update()

    #M.addConstr(M.getObjective() <= obj_heur)
    #M.addConstr(M.getObjective() >= suma)


    if datos.tmax is not None:
        M.Params.timeLimit = datos.tmax

    if not(datos.show):
        M.setParam('OutputFlag', 0)

    M.Params.Threads = 8
    # M.Params.tuneTimeLimit = 600
    M.Params.timeLimit = 20
    # M.tune()
    M.Params.Method = 4
    # M.Params.Heuristic = 0
    # M.Params.IntFeasTol = 1e-1
    # M.Params.NonConvex = 2
    # M.Params.FeasibilityTol = 1e-6

    M.update()

    M.write('MTZ.lp')

    # Solve
    M.optimize()

    vals = M.getAttr('x', z)
    selected = gp.tuplelist((i, j)
                            for i, j in vals.keys() if vals[i, j] > 0.5)

    path = af.subtour(selected)

    print('Camino = ' + str(path))

    path_P = []

    for p in path:
        comp = data[p]
        path_P.append([x[(p, 0)].X, x[(p, 1)].X])

    return path, path_P, M.ObjVal
