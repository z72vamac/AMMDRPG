#!/usr/bin/python

# Copyright 2019, Gurobi Optimization, LLC

# Solve the classic diet model, showing how to add constraints
# to an existing model.


import gurobipy as gp
from gurobipy import GRB

import auxiliar_functions as af
import bigM_estimation as eM
from data import *
from neighbourhood import Polygon, Polygonal


# Con 15 todavia no la encuentra
# np.random.seed(112)
# np.random.seed(11112)
# 168.60477938110762

def mtz(data):
    print()
    print('--------------------------------------------')
    print('Heuristic: MTZ of centroids')
    print('--------------------------------------------')
    print()

    data = data.instances
    m = len(data)

    # modo = data.graphs_numberodo

    # Model
    model = gp.Model("MTZ_MODEL")

    # Generando variables continuas de entrada y salida
    x_index = []
    d_index = []

    for c in range(m):
        # comp = data[c]
        # if type(comp) is Poligonal:
        x_index.append((c, 0))
        x_index.append((c, 1))
        d_index.append(c)

    x = model.addVars(x_index, vtype=GRB.CONTINUOUS, name="x")

    z_index = []

    for c1 in d_index:
        for c2 in d_index:
            if c1 != c2:
                z_index.append((c1, c2))

    p = model.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0, name="p")

    z = model.addVars(z_index, vtype=GRB.BINARY, name='z')
    d = model.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0, name='dcc')

    # if data.initialization:
    #     d = model.addVars(z_index, vtype = GRB.CONTINUOUS, lb = ds, name = 'dcc')

    dif = model.addVars(z_index, 2, vtype=GRB.CONTINUOUS, lb=0, name='dif')

    dc = model.addVars(d_index, vtype=GRB.CONTINUOUS, lb=0, name='dc')
    difc = model.addVars(d_index, 2, vtype=GRB.CONTINUOUS, lb=0, name='difc')

    # Generando los mus de la envolvente convexa, los landas de la poligonal y las
    # variables binarias que indican qué segmento se elige

    mu_index = []
    landa_index = []
    sublanda_index = []
    u_index = []
    s_index = []

    for c in d_index:
        comp = data[c]
        if type(comp) is Polygon:
            for mu in range(comp.num_puntos):
                mu_index.append((c, mu))
        if type(comp) is Polygonal:
            u_index.append(c)
            # landa de la variable de entrada en la poligonal c
            landa_index.append((c, 0))
            # landa de la variable de salida en la poligonal c
            landa_index.append((c, 1))
            for segm in range(comp.segments_number):
                s_index.append((c, 0, segm))
                s_index.append((c, 1, segm))
            for punto in range(comp.num_puntos):
                sublanda_index.append((c, 0, punto))
                sublanda_index.append((c, 1, punto))

    mu = model.addVars(mu_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='mu')
    landa = model.addVars(landa_index, vtype=GRB.CONTINUOUS, name='landa')
    sublanda = model.addVars(sublanda_index, vtype=GRB.CONTINUOUS,
                             lb=0.0, ub=1.0, name='sublanda')
    s = model.addVars(s_index, vtype=GRB.BINARY, name='s')
    u = model.addVars(u_index, vtype=GRB.BINARY, name='u')
    minc = model.addVars(u_index, vtype=GRB.CONTINUOUS, lb=0.0, name='min')
    maxc = model.addVars(u_index, vtype=GRB.CONTINUOUS, lb=0.0, name='max')

    sc = model.addVars(d_index, vtype=GRB.CONTINUOUS, lb=0, ub=m - 1, name='sc')

    model.update()

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
        big_m = eM.estimate_local_U(comp1, comp2)
        small_m = eM.estimate_local_L(comp1, comp2)
        # model.addConstr(d[c1, c2] <= big_m)
        # model.addConstr(d[c1, c2]>= small_m)
        # small_m, x_0, x_1 = af.min_dist(comp1, comp2)
        model.addConstr(p[c1, c2] >= small_m * z[c1, c2], name='p2')
        model.addConstr(p[c1, c2] >= d[c1, c2] - big_m * (1 - z[c1, c2]), name='p3')
        #
        # model.addConstr(p[c1, c2] >= small_m*z[c1, c2])
        # model.addConstr(p[c1, c2] <= d[c1, c2] + z[c1, c2]*small_m - small_m)
        # model.addConstr(p[c1, c2] <= z[c1, c2]*big_m)

        model.addConstrs(dif[c1, c2, dim] >= x[c2, dim] - x[c1, dim] for dim in range(2))
        model.addConstrs(dif[c1, c2, dim] >= -x[c2, dim] + x[c1, dim] for dim in range(2))

        # noinspection PyArgumentList
        model.addConstr(dif[c1, c2, 0] * dif[c1, c2, 0] +
                        dif[c1, c2, 1] * dif[c1, c2, 1] <= d[c1, c2] * d[c1, c2])

    # Restricciones para formar un tour
    # noinspection PyArgumentList
    model.addConstr(gp.quicksum(z[v, 0] for v in range(1, m - 1)) == 0)
    # noinspection PyArgumentList
    model.addConstr(gp.quicksum(z[m - 1, w] for w in range(1, m - 1)) == 0)
    model.addConstrs(gp.quicksum(z[v, w] for w in range(m) if w != v) == 1 for v in range(m))
    model.addConstrs(gp.quicksum(z[w, v] for w in range(m) if w != v) == 1 for v in range(m))

    for v in range(1, m - 1):
        for w in range(1, m - 1):
            if v != w:
                # noinspection PyArgumentList
                model.addConstr(m - 1 >= (sc[v] - sc[w]) + m * z[v, w])

    # for v in range(1, graphs_number+1):
    #     model.addConstr(s[v] - s[0] + (graphs_number+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, graphs_number+1):
    #     model.addConstr(s[0] - s[v] + (graphs_number+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, graphs_number+1):
    #     model.addConstr(-z[0,v] - s[v] + (graphs_number+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     model.addConstr(-z[v,0] + s[v] + (graphs_number+1-3)*z[0,v] <= graphs_number+1-2, name="LiftedUB(%s)"%v)

    #     model.addConstr(s[v] >= 1)
    #     for v in range(1, m-1):
    #     model.addConstr(s[v] <= len(T_index) - 1)
    #
    # model.addConstr(s[0] == 0)
    # model.addConstr(s[m-1] == m-1)

    # Restriccion 10
    model.addConstr(sc[0] == 0, name='rest10')
    # noinspection PyArgumentList
    model.addConstr(sc[m - 1] == m - 1)

    for c in range(1, m - 1):
        model.addConstr(sc[c] >= 1, name='rest11')

    model.addConstrs(difc[c, dim] >= x[c, dim] - data[c].centro[dim] for dim in range(2) for c in range(m))
    model.addConstrs(difc[c, dim] >= -x[c, dim] + data[c].centro[dim] for dim in range(2) for c in range(m))
    model.addConstrs(
        difc[c, 0] * difc[c, 0] + difc[c, 1] * difc[c, 1] <= data[c].radio * data[c].radio for c in range(m))

    model.update()

    fc = np.ones(m) * 1

    # for c in range(m):
    #     if fc[c] >= 1.0 and type(data[c]) is not Poligonal:
    #         for j in range(2):
    #             model.addConstr(x[c, 0, j] == x[c, 1, j])

    objective = gp.quicksum(p[c1, c2] for c1 in range(m) for c2 in range(m) if c1 != c2)

    # objective = gp.quicksum(p[index] for index in p.keys())

    model.setObjective(objective, GRB.MINIMIZE)

    model.update()

    # model.addConstr(model.getObjective() <= obj_heur)
    # model.addConstr(model.getObjective() >= suma)

    if data.time_limit is not None:
        model.Params.timeLimit = data.time_limit

    if not (data.show):
        model.setParam('OutputFlag', 0)

    model.Params.Threads = 8
    # model.Params.tuneTimeLimit = 600
    model.Params.timeLimit = 20
    # model.tune()
    model.Params.Method = 4
    # model.Params.Heuristic = 0
    # model.Params.IntFeasTol = 1e-1
    # model.Params.NonConvex = 2
    # model.Params.FeasibilityTol = 1e-6

    model.update()

    model.write('MTZ.lp')

    # Solve
    model.optimize()

    # noinspection PyArgumentList
    vals = model.getAttr('x', z)
    selected = gp.tuplelist((i, j)
                            for i, j in vals.keys() if vals[i, j] > 0.5)

    path = af.subtour(selected)

    print('Camino = ' + str(path))

    path_P = []

    for p in path:
        comp = data[p]
        path_P.append([x[(p, 0)].X, x[(p, 1)].X])

    return path, path_P, model.ObjVal
