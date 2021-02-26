# Este documento es para definir funciones que se utilizan en varios ficheros.

import numpy as np
import gurobipy as gp
from gurobipy import GRB
from entorno import Elipse, Poligono, Poligonal
import estimacion_M as eM
import copy
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
import networkx as nx

def path2matrix(path):
    "Toma un camino y lo devuelve como matriz de adyacencia"
    m = len(path)
    zcc = np.zeros([m, m])
    for i in range(m-1):
        zcc[path[i]][path[i+1]]=1
    zcc[path[m-1]][path[0]] = 1
    return zcc

def matrix2path(matrix):
    " Toma una matriz y lo devuelve como camino "
    matrix = np.array(matrix, int)
    ind = 0
    path = []
    while ind not in path:
        path.append(ind)
        lista = matrix[ind]
        counter = 0
        for i in lista:
            if i == 1:
                ind = counter
                break
            counter += 1
    return path


def subtour(edges):
    "Genera un subtour de una lista de aristas"
    m = len(edges)
    unvisited = list(range(m))
    cycle = range(m+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

def subtour_cplex(edges):
    "Genera un subtour de una lista de aristas"
    m = len(edges)
    unvisited = list(range(m))
    cycle = range(m+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            edges_selected = [(i, j) for i, j in edges if i == current]
            neighbors = [j for i, j in edges_selected
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

def subtours(edges):
    "Genera un subtour de una lista de aristas"
    m = len(edges)
    unvisited = edges
    cycle = range(m+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited] + [i for i, j in edges.select('*', current) if i in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle

# def subtours(edges):
#     "Genera un subtour de una lista de aristas"
#     m = len(edges)
#     unvisited = list(range(m))
#     cycles = []  # initial length has 1 more city
#     while unvisited:  # true if list is non-empty
#         thiscycle = []
#         neighbors = unvisited
#         while neighbors:
#             current = neighbors[0]
#             thiscycle.append(current)
#             unvisited.remove(current)
#             neighbors = [j for i, j in edges.select(current, '*')
#                          if j in unvisited]
#         # if len(cycle) > len(thiscycle):
#         cycles.append(thiscycle)
#     return cycles
#
#
# def subtour_s(edges):
#     m = int(len(edges)/2)
#     unvisited = list(range(m))
#     cycle = list(range(m)) # Dummy - guaranteed to be replaced
#     while unvisited:  # true if list is non-empty
#         thiscycle = []
#         neighbors = unvisited
#         while neighbors:
#             current = neighbors[0]
#             thiscycle.append(current)
#             unvisited.remove(current)
#             neighbors = [j for i, j in edges.select(current, '*')
#                          if j in unvisited]
#         if len(thiscycle) <= len(cycle):
#             cycle = thiscycle # New shortest subtour
#     return cycle

def min_dist(comp0, comp1):

        MODEL = gp.Model('minima_distancia')

        x0 = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'x0')
        x1 = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'x1')

        if type(comp0) is Poligono:
            mu0 = MODEL.addVars(comp0.num_puntos, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'mu0')

        if type(comp0) is Poligonal:
            landa_index = []
            sublanda_index = []
            s_index = []

            # landa de la variable de entrada en la poligonal c
            landa_index.append(0)
            # landa de la variable de salida en la poligonal c
            for segm in range(comp0.num_segmentos):
                s_index.append(segm)
            for punto in range(comp0.num_puntos):
                sublanda_index.append(punto)

            landa0 = MODEL.addVar(vtype=GRB.CONTINUOUS, name='landa')
            sublanda0 = MODEL.addVars(sublanda_index, vtype=GRB.CONTINUOUS,
                                 lb=0.0, ub=1.0, name='sublanda')
            s0 = MODEL.addVars(s_index, vtype=GRB.BINARY, name='s')

        if type(comp1) is Poligono:
            mu1 = MODEL.addVars(comp1.num_puntos, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'mu1')

        if type(comp1) is Poligonal:
            landa_index = []
            sublanda_index = []
            s_index = []

            # landa de la variable de salida en la poligonal c
            for segm in range(comp1.num_segmentos):
                s_index.append(segm)
            for punto in range(comp1.num_puntos):
                sublanda_index.append(punto)

            landa1 = MODEL.addVar(vtype=GRB.CONTINUOUS, name='landa')
            sublanda1 = MODEL.addVars(sublanda_index, vtype=GRB.CONTINUOUS,
                                 lb=0.0, ub=1.0, name='sublanda')
            s1 = MODEL.addVars(s_index, vtype=GRB.BINARY, name='s')

        dif01 = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'dif01')
        d01 = MODEL.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, name = 'd01')

        MODEL.update()

        MODEL.addConstr(dif01[0] >=  x0[0] - x1[0])
        MODEL.addConstr(dif01[0] >= -x0[0] + x1[0])
        MODEL.addConstr(dif01[1] >=  x0[1] - x1[1])
        MODEL.addConstr(dif01[1] >= -x0[1] + x1[1])
        MODEL.addConstr(dif01[0] * dif01[0] + dif01[1] * dif01[1] <= d01 * d01)
        # MODEL.addConstr(d01 <= estima_BigM_local(comp0, comp1))

        if type(comp0) is Poligono:
            MODEL.addConstr(gp.quicksum(mu0[j] for j in range(comp0.num_puntos)) == 1, name = 'envConv')
            for j in range(2):
                MODEL.addConstr(x0[j] == gp.quicksum(mu0[v]*comp0.V[v][j] for v in range(comp0.num_puntos)), name = 'inP1')
        if type(comp0) is Elipse:
            MODEL.addConstr(comp0.P[0, 0] * x0[0] * x0[0] + comp0.P[1, 0] * x0[0] * x0[1] +
                            comp0.P[0, 1] * x0[0] * x0[1] + comp0.P[1, 1] * x0[1] * x0[1] +
                            comp0.q[0] * x0[0] + comp0.q[1] * x0[1] + comp0.r <= 0, name='inC1')
        if type(comp0) is Poligonal:
            for i in range(2):
                for punto in range(1, comp0.num_puntos):
                    MODEL.addConstr(landa0 - punto >= sublanda0[punto] - comp0.num_puntos * (1 - s0[punto - 1]))
                    MODEL.addConstr(landa0 - punto <= sublanda0[punto] + comp0.num_puntos * (1 - s0[punto - 1]))
                MODEL.addConstr(sublanda0[0] <= s0[0])
                MODEL.addConstr(sublanda0[comp0.num_puntos - 1] <= s0[comp0.num_puntos - 2])
                for punto in range(1, comp0.num_puntos - 1):
                    MODEL.addConstr(sublanda0[punto] <= s0[punto - 1] + s0[punto])
                MODEL.addConstr(s0.sum('*') == 1)
                MODEL.addConstr(sublanda0.sum('*') == 1)
                for j in range(2):
                    MODEL.addConstr(x0[j] == gp.quicksum(sublanda0[punto] * comp0.V[punto][j] for punto in range(comp0.num_puntos)), name='seg1')
        if type(comp1) is Poligono:
            MODEL.addConstr(gp.quicksum(mu1[j] for j in range(comp1.num_puntos)) == 1, name = 'envConv')
            for j in range(2):
                MODEL.addConstr(x1[j] == gp.quicksum(mu1[v]*comp1.V[v][j] for v in range(comp1.num_puntos)), name = 'inP1')
        if type(comp1) is Elipse:
            MODEL.addConstr(comp1.P[0, 0] * x1[0] * x1[0] + comp1.P[1, 0] * x1[0] * x1[1] +
                            comp1.P[0, 1] * x1[0] * x1[1] + comp1.P[1, 1] * x1[1] * x1[1] +
                            comp1.q[0] * x1[0] + comp1.q[1] * x1[1] + comp1.r <= 0, name='inC1')
        if type(comp1) is Poligonal:
            for i in range(2):
                for punto in range(1, comp1.num_puntos):
                    MODEL.addConstr(landa1 - punto >= sublanda1[punto] - comp1.num_puntos * (1 - s1[punto - 1]))
                    MODEL.addConstr(landa1 - punto <= sublanda1[punto] + comp1.num_puntos * (1 - s1[punto - 1]))
                MODEL.addConstr(sublanda1[0] <= s1[0])
                MODEL.addConstr(sublanda1[comp1.num_puntos - 1] <= s1[comp1.num_puntos - 2])
                for punto in range(1, comp1.num_puntos - 1):
                    MODEL.addConstr(sublanda1[punto] <= s1[punto - 1] + s1[punto])
                MODEL.addConstr(s1.sum('*') == 1)
                MODEL.addConstr(sublanda1.sum('*') == 1)
                for j in range(2):
                    MODEL.addConstr(x1[j] == gp.quicksum(sublanda1[punto] * comp1.V[punto][j] for punto in range(comp1.num_puntos)), name='seg1')

        MODEL.setParam('OutputFlag', 1)

        MODEL.setObjective(d01, GRB.MINIMIZE)
        MODEL.Params.FeasibilityTol = 1e-2
        MODEL.update()

        MODEL.optimize()

        x_0 = [x0[0].X, x0[1].X]
        x_1 = [x1[0].X, x1[1].X]

        return d01.X, x_0, x_1

def XPPND(datos, vals_xL, grafo, vals_xR):

    MODEL = gp.Model('XPPND')
    ugi_index = []

    for i in grafo.aristas:
        ugi_index.append(i)


    ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # Variable continua no negativa pgLi = ugi * dgLi
    pgLi_index = ugi_index

    pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    vgi_index = ugi_index

    vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    pgRi_index = ugi_index

    pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []

    for i in grafo.aristas:
        sgi_index.append(i)
        for j in grafo.aristas:
            if i != j:
                zgij_index.append((i, j))

    zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')
    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for i in grafo.aristas:
        rhogi_index.append(i)
        for dim in range(2):
            Rgi_index.append((i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')

    xL = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'xL')
    difL = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'difL')

    xR = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'xR')
    difR = MODEL.addVars(2, vtype = GRB.CONTINUOUS, name = 'difR')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstr((ugi.sum('*') == 1), name = 'entrag')
    MODEL.addConstr((vgi.sum('*') == 1), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs((mugi[i] - ugi[i] == zgij.sum('*', i) for i, j in zgij.keys()), name = 'flujou')
    MODEL.addConstrs((mugi[i] - vgi[i] == zgij.sum(i, '*') for i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[i] >= mugi[i] + alphagi[i] - 1 for i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[i] <= mugi[i] for i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[i] <= alphagi[i] for i in rhogi.keys()), name = 'pgi3')

    # MODEL.addConstr(ugi[0, 101, 0] == 0)
    # MODEL.addConstr(ugi[0, 101, 1] == 0)


    # Eliminación de subtours
    for i in grafo.aristas[0:]:
        for j in grafo.aristas[0:]:
            if i != j:
                MODEL.addConstr(grafo.num_aristas - 1 >= (sgi[i] - sgi[j]) + grafo.num_aristas * zgij[i, j])

    # for g in range(nG):
    #     MODEL.addConstr(sgi[grafos[g].aristas[0]] == 0)

    for i in grafo.aristas[0:]:
        MODEL.addConstr(sgi[i] >= 0)
        MODEL.addConstr(sgi[i] <= grafo.num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[i, dim] >=   xL[dim] - Rgi[i, dim]) for i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[i, dim] >= - xL[dim] + Rgi[i, dim]) for i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[i, 0]*auxgLi[i, 0] + auxgLi[i, 1] * auxgLi[i, 1] <= dgLi[i] * dgLi[i] for i in ugi.keys()), name = 'u-conic')

    SmallML = dist_grafo(vals_xL, grafo)[0]
    BigML = max([np.linalg.norm(vals_xL - v) for v in grafo.V])

    MODEL.addConstrs((pgLi[i] >= SmallML * ugi[i]) for i in ugi.keys())
    MODEL.addConstrs((pgLi[i] >= dgLi[i] - BigML * (1 - ugi[i])) for i in ugi.keys())

    MODEL.addConstrs((auxgij[i, j, dim] >=   Lgi[i, dim] - Rgi[j, dim]) for i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[i, j, dim] >= - Lgi[i, dim] + Rgi[j, dim]) for i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[i, j, 0]*auxgij[i, j, 0] + auxgij[i, j, 1] * auxgij[i, j, 1] <= dgij[i, j] * dgij[i, j] for i, j in dgij.keys()), name = 'zgij-conic')


    for i, j in zgij.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Poligonal(np.array([[grafo.V[first_i, 0], grafo.V[first_i, 1]], [
                           grafo.V[second_i, 0], grafo.V[second_i, 1]]]), grafo.A[first_i, second_i])
        segm_j = Poligonal(np.array([[grafo.V[first_j, 0], grafo.V[first_j, 1]], [
                           grafo.V[second_j, 0], grafo.V[second_j, 1]]]), grafo.A[first_j, second_j])

        BigM_local = eM.estima_BigM_local(segm_i, segm_j)
        SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
        MODEL.addConstr((pgij[i, j] >= SmallM_local * zgij[i, j]))
        MODEL.addConstr((pgij[i, j] >= dgij[i, j] - BigM_local * (1 - zgij[i, j])))


    SmallMR = dist_grafo(vals_xR, grafo)[0]
    BigMR = max([np.linalg.norm(vals_xR - v) for v in grafo.V])

    MODEL.addConstrs((pgRi[i] >= SmallMR * vgi[i]) for i in vgi.keys())
    MODEL.addConstrs((pgRi[i] >= dgRi[i] - BigMR * (1 - vgi[i])) for i in vgi.keys())

    MODEL.addConstrs((auxgRi[i, dim] >=   Lgi[i, dim] - xR[dim]) for i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[i, dim] >= - Lgi[i, dim] + xR[dim]) for i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[i, 0]*auxgRi[i, 0] + auxgRi[i, 1] * auxgRi[i, 1] <= dgRi[i] * dgRi[i] for i in vgi.keys()), name = 'v-conic')


    for i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[i] - landagi[i] == maxgi[i] - mingi[i])
        MODEL.addConstr(maxgi[i] + mingi[i] == alphagi[i])
        if datos.alpha:
            MODEL.addConstr(pgi[i] == grafo.A[first, second])
        MODEL.addConstr(maxgi[i] <= 1 - entrygi[i])
        MODEL.addConstr(mingi[i] <= entrygi[i])
        MODEL.addConstr(Rgi[i, 0] == rhogi[i] * grafo.V[first, 0] + (1 - rhogi[i]) * grafo.V[second, 0])
        MODEL.addConstr(Rgi[i, 1] == rhogi[i] * grafo.V[first, 1] + (1 - rhogi[i]) * grafo.V[second, 1])
        MODEL.addConstr(Lgi[i, 0] == landagi[i] * grafo.V[first, 0] + (1 - landagi[i]) * grafo.V[second, 0])
        MODEL.addConstr(Lgi[i, 1] == landagi[i] * grafo.V[first, 1] + (1 - landagi[i]) * grafo.V[second, 1])


    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[i]*grafo.longaristas[i // 100 - 1, i % 100] for i in grafo.aristas) >= grafo.alpha*grafo.longitud)

    MODEL.addConstrs(xL[dim] ==  vals_xL[dim] for dim in range(2))
    MODEL.addConstrs(xR[dim] ==  vals_xR[dim] for dim in range(2))

    MODEL.addConstrs((auxLR[dim] >=   xL[dim] - xR[dim]) for dim in auxLR.keys())
    MODEL.addConstrs((auxLR[dim] >= - xL[dim] + xR[dim]) for dim in auxLR.keys())
    MODEL.addConstr((auxLR[0]*auxLR[0] + auxLR[1] * auxLR[1] <= dLR * dLR), name = 'LR-conic')

    MODEL.update()

    objective = gp.quicksum(pgLi[i] + pgRi[i] for i in pgRi.keys()) + gp.quicksum(pgij[i, j] for i, j in pgij.keys()) + gp.quicksum(pgi[i]*grafo.longaristas[i // 100 - 1, i % 100] for i in grafo.aristas)

    MODEL.setObjective(objective, GRB.MINIMIZE)

    MODEL.update()

    MODEL.setParam('OutputFlag', 0)

    MODEL.optimize()

    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist(i for i in vals_u.keys() if vals_u[i] > 0.5)
    #print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((i, j) for i, j in vals_zgij.keys() if vals_zgij[i, j] > 0.5)
    #print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    #selected_v = gp.tuplelist(i for i in vals_v.keys() if vals_v[i] > 0.5)
    #print(selected_v)

    vals_xL = MODEL.getAttr('x', xL)
    vals_xR = MODEL.getAttr('x', xR)
    #print(vals_xL)

    index_i = selected_u[0]
    unvisited = grafo.aristas.copy()
    cycle = []
    unvisited.remove(index_i)
    cycle.append(index_i)

    while unvisited:
        neighbors = [tupla for tupla in selected_zgij if tupla[0] == index_i]
        while neighbors:
            current = neighbors[0][1]
            cycle.append(current)
            unvisited.remove(current)
            neighbors = [(i, j) for i, j in selected_zgij if i == current or j == current and j in unvisited]

    # #print(cycle)


    return vals_u, vals_zgij, vals_v, MODEL.ObjVal

def XPPNM(datos, vals_u, vals_zgij, vals_v, vals_z, orig, dest, iter):

    grafos = datos.mostrar_datos()

    nG = len(grafos)

    T_index = range(nG + 2)
    T_index_prima = range(1, nG+1)
    T_index_primaprima = range(nG+1)

    origin = orig
    dest = orig

    vD = 3

    vC = 1

    MODEL = gp.Model('XPPNM')

    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            ugi_index.append((g, i))
    #
    #
    # ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # # Variable continua no negativa pgLi = ugi * dgLi
    # pgLi_index = ugi_index
    #
    # pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    # vgi_index = ugi_index
    #
    # vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    # pgRi_index = ugi_index
    #
    # pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []
    #
    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sgi_index.append((g, i))
            for j in grafos[g-1].aristas:
                if i != j:
                    zgij_index.append((g, i, j))
    #
    #
    # zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    # sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))

    # z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL')
    pRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL')

    # Variables que modelan los puntos de entrada o recogida
    # xL: punto de salida del dron del camion en la etapa t
    xL_index = []

    for g in T_index:
        for dim in range(2):
            xL_index.append((g, dim))

    xL = MODEL.addVars(xL_index, vtype=GRB.CONTINUOUS, name='xL')

    # xR: punto de recogida del dron del camion en la etapa t
    xR_index = []

    for t in T_index:
        for dim in range(2):
            xR_index.append((t, dim))

    xR = MODEL.addVars(xR_index, vtype=GRB.CONTINUOUS, name='xR')

    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhogi_index.append((g, i))
            for dim in range(2):
                Rgi_index.append((g, i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')

    difL = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difL')

    difR = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difR')

    MODEL.update()

    # for g1, g2 in dRL.keys():
    #     z[g1, g2].start = zs[g1, g2]
    # # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    # MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name = 'entrag')
    # MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    # MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name = 'flujou')
    # MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name = 'pgi3')


    # # Eliminación de subtours
    # for g in T_index_prima:
    #     for i in grafos[g-1].aristas[0:]:
    #         for j in grafos[g-1].aristas[0:]:
    #             if i != j:
    #                 MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g-1].num_aristas * zgij[g, i, j])


    # for g in T_index_prima:
    #     for i in grafos[g-1].aristas[0:]:
    #         MODEL.addConstr(sgi[g, i] >= 0)
    #         MODEL.addConstr(sgi[g, i] <= grafos[g-1].num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >=   xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[g, i, 0]*auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in dgLi.keys()), name = 'u-conic')

    # SmallM = []
    # BigM = []
    #
    # for g in T_index_prima:
    #     BigM.append(max([np.linalg.norm(elipses[g-1].centro - v) for v in grafos[g-1].V]) + elipses[g].radio)
    #     SmallM.append(dist_grafo(elipses[g-1].centro, grafos[g-1])[0] - elipses[g-1].radio)

    # MODEL.addConstrs((pgLi[g, i] >= SmallM[g] * ugi[g, i]) for g, i in ugi.keys())
    # MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM[g] * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >=   Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0]*auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name = 'zgij-conic')


    # for g, i, j in zgij.keys():
    #     first_i = i // 100 - 1
    #     second_i = i % 100
    #     first_j = j // 100 - 1
    #     second_j = j % 100
    #
    #     segm_i = Poligonal(np.array([[grafos[g-1].V[first_i, 0], grafos[g-1].V[first_i, 1]], [
    #                        grafos[g-1].V[second_i, 0], grafos[g-1].V[second_i, 1]]]), grafos[g-1].A[first_i, second_i])
    #     segm_j = Poligonal(np.array([[grafos[g-1].V[first_j, 0], grafos[g-1].V[first_j, 1]], [
    #                        grafos[g-1].V[second_j, 0], grafos[g-1].V[second_j, 1]]]), grafos[g-1].A[first_j, second_j])
    #
    #     BigM_local = eM.estima_BigM_local(segm_i, segm_j)
    #     SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
    #     MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
    #     MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >=   Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[g, i, 0]*auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in dgRi.keys()), name = 'v-conic')


    # SmallM = 0
    #BigM = 10000
    # SmallM = []
    # BigM = []
    #
    # for g in T_index_prima:
    #     BigM.append(max([np.linalg.norm(elipses[g].centro - v) for v in grafos[g-1].V]) + elipses[g].radio)
    #     SmallM.append(dist_grafo(elipses[g].centro, grafos[g-1])[0] - elipses[g].radio)

    # MODEL.addConstrs((pgRi[g, i] >= SmallM[g] * vgi[g, i]) for g, i in vgi.keys())
    # MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM[g] * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >=   xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, 0]*auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for g1, g2 in dRL.keys()), name = 'RL-conic')



    SmallM = 0
    BigM = 10000

    # BigM = 0
    # for g in T_index_prima:
    #     for v in grafos[g-1].V:
    #         BigM = max([np.linalg.norm(origin - v), BigM])
    # MODEL.addConstrs((pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # SmallM = np.zeros((nG+2, nG+2))
    # BigM = np.zeros((nG+2, nG+2))
    # BigM = 10000*np.ones((nG+2, nG+2))

    # for g1, g2 in z.keys():
    #     BigM[g1, g2] = eM.estima_BigM_local(elipses[g1], elipses[g2])
    #     SmallM[g1, g2] = eM.estima_SmallM_local(elipses[g1], elipses[g2])
    #
    # MODEL.addConstrs((pRL[g1, g2] >= SmallM[g1, g2] * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM[g1, g2] * (1 - z[g1, g2]) for g1, g2 in z.keys()))



    # Restricciones para formar un tour
    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    # MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index if w != v) == 1 for v in T_index)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index if w != v) == 1 for v in T_index)


    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * vals_z[v, w])

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[nG + 1] == nG+2)

    MODEL.addConstrs((auxLR[g, dim] >=   xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0]*auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()), name = 'LR-conic')


    MODEL.addConstrs( ( gp.quicksum(dgLi[g, i]*vals_u[g, i] for i in grafos[g-1].aristas) + gp.quicksum(dgij[g, i, j]*vals_zgij[g, i, j] for g, i, j in dgij.keys())
                      + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas)
                      + gp.quicksum(dgRi[g, i]*vals_v[g, i] for i in grafos[g-1].aristas))/vD <= dLR[g]/vC for g in T_index_prima)


    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if datos.alpha:
            MODEL.addConstr(pgi[g, i] == grafos[g-1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(Rgi[g, i, 0] == rhogi[g, i] * grafos[g-1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rgi[g, i, 1] == rhogi[g, i] * grafos[g-1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lgi[g, i, 0] == landagi[g, i] * grafos[g-1].V[first, 0] + (1 - landagi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lgi[g, i, 1] == landagi[g, i] * grafos[g-1].V[first, 1] + (1 - landagi[g, i]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)

    # # Fijado de variables
    # for g in T_index_prima:
    #     MODEL.addConstrs(zgij[g, i, j] == 1 for h, i, j in vals_zgij if h == g)
    #     MODEL.addConstrs(ugi[h, i] == 1 for h, i in vals_u if h == g)
    #     MODEL.addConstrs(vgi[h, i] == 1 for h, i in vals_v if h == g)

    # MODEL.addConstrs(difL[g, dim] >=  xL[g, dim] - elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, dim] >= -xL[g, dim] + elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, 0]*difL[g, 0] + difL[g, 1]*difL[g, 1] <= elipses[g].radio*elipses[g].radio for g in T_index_prima)
    #
    # MODEL.addConstrs(difR[g, dim] >=  xR[g, dim] - elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, dim] >= -xR[g, dim] + elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, 0]*difR[g, 0] + difR[g, 1]*difR[g, 1] <= elipses[g+1].radio*elipses[g+1].radio for g in T_index_prima)

    # Origen y destino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xR[nG+1, dim] == dest[dim] for dim in range(2))
    MODEL.addConstrs(xL[nG+1, dim] == dest[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(dgLi[g, i]*vals_u[g, i] for g, i in dgLi.keys()) + gp.quicksum(dgRi[g, i]*vals_v[g, i] for g, i in dgRi.keys()) + gp.quicksum(dgij[g, i, j]*vals_zgij[g, i, j] for g, i, j in dgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(2*dLR[g] for g in dLR.keys()) + gp.quicksum(2*dRL[g1, g2]*vals_z[g1, g2] for g1, g2 in dRL.keys())
    # objective = gp.quicksum(pgLi[g, i] + pgRi[g, i] for g, i in pgRi.keys()) + gp.quicksum(pgij[g, i, j] for g, i, j in pgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(2*dLR[g] for g in dLR.keys()) + gp.quicksum(2*pRL[g1, g2] for g1, g2 in dRL.keys())


    # objective = gp.quicksum(2*dLR[g] for g in dLR.keys()) + gp.quicksum(2*pRL[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    Model.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 150

    MODEL.setParam('OutputFlag', 1)

    MODEL.update()


    MODEL.write('AMDRPG-MTZaux.lp')
    MODEL.write('AMDRPG-MTZ.mps')

    MODEL.optimize()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')

    # fig, ax = plt.subplots()
    # plt.axis([0, 100, 0, 100])

    # vals_u = MODEL.getAttr('x', ugi)
    # selected_u = gp.tuplelist((g, i)
    #                           for g, i in ugi_index if vals_u[g, i] > 0.5)
    selected_u = vals_u
    #print(selected_u)

    # vals_zgij = MODEL.getAttr('x', zgij)
    # selected_zgij = gp.tuplelist((g, i, j)
    #                           for g, i, j in zgij_index if vals_zgij[g, i, j] > 0.5)
    selected_zgij = vals_zgij
    #print(selected_zgij)

    # vals_v = MODEL.getAttr('x', vgi)
    # selected_v = gp.tuplelist((g, i)
    #                           for g, i in vgi_index if vals_v[g, i] > 0.5)
    #print(selected_v)
    selected_v = vals_v

    # valsz = MODEL.getAttr('x', z)

    selected_z = gp.tuplelist(e for e in dRL.keys() if vals_z[e] > 0)
    #print(selected_z)
    #print(selected_z)
    path = subtour(selected_z)
    #print(path)

    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])


    for p in path[1:]:
        #    if ind < nG:
        if ind < nG:
            path_D = []
            path_D.append([xL[p, 0].X, xL[p, 1].X])
            index_g = 0
            index_i = 0
            for g, i in selected_u:
                if g == p:
                    index_g = g
                    index_i = i

            count = 0
            path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
            path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])
            limite = sum([1 for g, i, j in selected_zgij if g == index_g])
            while count < limite:
                for g, i, j in selected_zgij:
                    if index_g == g and index_i == i:
                        count += 1
                        index_i = j
                        path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
                        path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])

            ind += 1
            path_D.append([xR[p, 0].X, xR[p, 1].X])
        paths_D.append(path_D)
    # path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])


    for g, i in rhogi.keys():
        plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
        plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha = 0.3, markersize=10, color='green')
        ax.annotate("L" + str(i), xy = (xL[p, 0].X+0.5, xL[p, 1].X+0.5))
        plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=5, color='blue')
        ax.annotate("R" + str(i), xy = (xR[p, 0].X-1.5, xR[p, 1].X-1.5))

    #
    # for e in elipses:
    #     ax.add_artist(e.artist)

    ax.add_artist(Polygon(path_C, fill=False, animated=False,
                  linestyle='-', alpha=1, color='blue'))

    for path in paths_D:
        ax.add_artist(Polygon(path, fill=False, closed=False,
                      animated=False, alpha=1, color='red'))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))

    for g in T_index_prima:
        grafo = grafos[g-1]
        centroide = np.mean(grafo.V, axis = 0)
        nx.draw(grafo.G, grafo.pos, node_size=20,
                node_color='black', alpha=0.3, edge_color='gray')
        ax.annotate(g, xy = (centroide[0], centroide[1]))


    plt.savefig('PD-MTZ-Heuristic ' + str(iter) + '.png')

    # plt.show()
    path = subtour(selected_z)

    return MODEL.getAttr('x', xL), MODEL.getAttr('x', xR), path, MODEL.ObjVal

def XPPNZ(datos, z, orig, dest, iter, elipses = []):

    print()
    print('--------------------------------------------')
    print('Exact Formulation: Fixing w. Iteration: {0}'.format(iter))
    print('--------------------------------------------')
    print()

    grafos = datos.mostrar_datos()

    nG = len(grafos)

    origin = orig


    T_index = range(nG + 2)
    T_index_prima = range(1, nG+1)
    T_index_primaprima = range(nG+1)

    vD = 3

    vC = 1
    # Creamos el modelo8
    MODEL = gp.Model("PD-Graph")

    # Variables que modelan las distancias
    # Variable binaria ugi = 1 si en la etapa t entramos por el segmento sgi
    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            ugi_index.append((g, i))


    ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # Variable continua no negativa pgLi = ugi * dgLi
    pgLi_index = ugi_index

    pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    vgi_index = ugi_index

    vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    pgRi_index = ugi_index

    pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sgi_index.append((g, i))
            for j in grafos[g-1].aristas:
                if i != j:
                    zgij_index.append((g, i, j))

    zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))
    #
    # z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL')
    pRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL')

    # Variables que modelan los puntos de entrada o recogida
    # xL: punto de salida del dron del camion en la etapa t
    xL_index = []

    for g in T_index:
        for dim in range(2):
            xL_index.append((g, dim))

    xL = MODEL.addVars(xL_index, vtype=GRB.CONTINUOUS, name='xL')

    # xR: punto de recogida del dron del camion en la etapa t
    xR_index = []

    for t in T_index:
        for dim in range(2):
            xR_index.append((t, dim))

    xR = MODEL.addVars(xR_index, vtype=GRB.CONTINUOUS, name='xR')

    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhogi_index.append((g, i))
            for dim in range(2):
                Rgi_index.append((g, i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')

    difL = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difL')

    difR = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difR')


    MODEL.update()


    # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name = 'entrag')
    MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name = 'flujou')
    MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name = 'pgi3')

    # MODEL.addConstr(ugi[0, 101, 0] == 0)
    # MODEL.addConstr(ugi[0, 101, 1] == 0)


    # Eliminación de subtours
    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            for j in grafos[g-1].aristas[0:]:
                if i != j:
                    MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g-1].num_aristas * zgij[g, i, j])

    # for g in range(nG):
    #     MODEL.addConstr(sgi[g, grafos[g].aristas[0]] == 0)

    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            MODEL.addConstr(sgi[g, i] >= 0)
            MODEL.addConstr(sgi[g, i] <= grafos[g-1].num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >=   xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[g, i, 0]*auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in ugi.keys()), name = 'u-conic')

    SmallM = 0
    BigM = 10000

    # BigM = 0
    # for g in T_index_prima:
    #     for v in grafos[g-1].V:
    #         BigM = max([np.linalg.norm(origin - v), BigM])
    #
    # BigM += 5
    #BigM = max([np.linalg.norm(origin-grafos[g].V) for g in range(nG)])

    # MODEL.addConstr(ugi[1, 101] == 1)
    # MODEL.addConstr(vgi[1, 203] == 1)

    MODEL.addConstrs((pgLi[g, i] >= SmallM * ugi[g, i]) for g, i in ugi.keys())
    MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >=   Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0]*auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name = 'zgij-conic')


    for g, i, j in zgij.keys():
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
        MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
        MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >=   Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[g, i, 0]*auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in vgi.keys()), name = 'v-conic')


    # SmallM = 0
    #BigM = 10000
    MODEL.addConstrs((pgRi[g, i] >= SmallM * vgi[g, i]) for g, i in vgi.keys())
    MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >=   xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, 0]*auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for g1, g2 in dRL.keys()), name = 'RL-conic')

    # MODEL.addConstrs((pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in dRL.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM * (1 - z[g1, g2]) for g1, g2 in dRL.keys()))

    # Restricciones para formar un tour
    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    # MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index if w != v) == 1 for v in T_index)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index if w != v) == 1 for v in T_index)

    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * z[v, w])

    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[v] - s[0] + (nG+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[0] - s[v] + (nG+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, nG+1):
    #     MODEL.addConstr(-z[0,v] - s[v] + (nG+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     MODEL.addConstr(-z[v,0] + s[v] + (nG+1-3)*z[0,v] <= nG+1-2, name="LiftedUB(%s)"%v)

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[nG + 1] == nG+1)

    MODEL.addConstrs((auxLR[g, dim] >=   xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0]*auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()), name = 'LR-conic')

    MODEL.addConstrs((pgLi.sum(g, '*') + pgij.sum(g, '*', '*') +  gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + pgRi.sum(g, '*'))/vD <= dLR[g]/vC for g in T_index_prima)

    # MODEL.addConstrs(dLR[g] <= 150 for g in dLR.keys())
    # MODEL.addConstrs((pgLi.sum('*', '*', t) +
    #                   pgij.sum(g, '*', '*') +
    #                   ugi.sum(g, '*', '*')*longitudes[g-1] +
    #                   pgRi.sum('*', '*', t))/vD <= dLR[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLR[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pgLi[g, i, t]
    #                   + pgij.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pgRi[g, i, t])/vD <= dLR[t]/vC for g, i, t in pgLi.keys())

    # MODEL.addConstr(z[0, 2] + z[1, 3] + z[2, 1] + z[3, 4] == 4)

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if datos.alpha:
            MODEL.addConstr(pgi[g, i] >= grafos[g-1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(Rgi[g, i, 0] == rhogi[g, i] * grafos[g-1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rgi[g, i, 1] == rhogi[g, i] * grafos[g-1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lgi[g, i, 0] == landagi[g, i] * grafos[g-1].V[first, 0] + (1 - landagi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lgi[g, i, 1] == landagi[g, i] * grafos[g-1].V[first, 1] + (1 - landagi[g, i]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)


    # if elipses:
    #     MODEL.addConstrs(difL[g, dim] >=  xL[g, dim] - elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    #     MODEL.addConstrs(difL[g, dim] >= -xL[g, dim] + elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    #     MODEL.addConstrs(difL[g, 0]*difL[g, 0] + difL[g, 1]*difL[g, 1] <= elipses[g].radio*elipses[g].radio for g in T_index_prima)
    #
    #     MODEL.addConstrs(difR[g, dim] >=  xR[g, dim] - elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    #     MODEL.addConstrs(difR[g, dim] >= -xR[g, dim] + elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    #     MODEL.addConstrs(difR[g, 0]*difR[g, 0] + difR[g, 1]*difR[g, 1] <= elipses[g+1].radio*elipses[g+1].radio for g in T_index_prima)

    # Origen y destino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xR[nG+1, dim] == dest[dim] for dim in range(2))
    MODEL.addConstrs(xL[nG+1, dim] == dest[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(pgLi[g, i] + pgRi[g, i] for g, i in pgRi.keys()) + gp.quicksum(pgij[g, i, j] for g, i, j in pgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLR[g] for g in dLR.keys()) + gp.quicksum(3*dRL[g1, g2]*z[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(1*dLR[g] for g in dLR.keys()) + gp.quicksum(dRL[g1, g2]*z[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 60
    MODEL.Params.SolutionLimit = 3

    MODEL.update()

    MODEL.write('AMDRPG-MTZ.lp')
    MODEL.write('AMDRPG-MTZ.mps')
    MODEL.optimize()


    MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')

    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist((g, i)
                              for g, i in vals_u.keys() if vals_u[g, i] > 0.5)
    #print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((g, i, j)
                              for g, i, j in vals_zgij.keys() if vals_zgij[g, i, j] > 0.5)
    #print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    selected_v = gp.tuplelist((g, i)
                              for g, i in vals_v.keys() if vals_v[g, i] > 0.5)
    #print(selected_v)

    selected_z = gp.tuplelist(e for e in dRL.keys() if z[e] > 0)
    # print(selected_z)
    # path = subtour(selected_z)
    # print(selected_z)
    path = subtour(selected_z)


    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])


    for p in path[1:]:
        #    if ind < nG:
        if ind < nG:
            path_D = []
            path_D.append([xL[p, 0].X, xL[p, 1].X])
            index_g = 0
            index_i = 0
            for g, i in selected_u:
                if g == p:
                    index_g = g
                    index_i = i

            count = 0
            path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
            path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])
            limite = sum([1 for g, i, j in selected_zgij if g == index_g])
            while count < limite:
                for g, i, j in selected_zgij:
                    if index_g == g and index_i == i:
                        count += 1
                        index_i = j
                        path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
                        path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])

            ind += 1
            path_D.append([xR[p, 0].X, xR[p, 1].X])
        paths_D.append(path_D)

    # path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])


    # for g, i in rhogi.keys():
    #     plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #     plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha = 0.3, markersize=10, color='green')
        ax.annotate("L" + str(i), xy = (xL[p, 0].X+0.5, xL[p, 1].X+0.5))
        plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=5, color='blue')
        ax.annotate("R" + str(i), xy = (xR[p, 0].X-1.5, xR[p, 1].X-1.5))


    ax.add_artist(Polygon(path_C, fill=False, animated=False,
                  linestyle='-', alpha=1, color='blue'))

    for paths in paths_D:
        ax.add_artist(Polygon(paths, fill=False, closed=False,
                      animated=False, alpha=1, color='red', lw = 0.1))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))

    if elipses:
        for e in elipses:
            ax.add_artist(e.artist)

    for g in T_index_prima:
        grafo = grafos[g-1]
        centroide = np.mean(grafo.V, axis = 0)
        nx.draw(grafo.G, grafo.pos, node_size=30,
                node_color='black', alpha=1, edge_color='gray')
        ax.annotate(g, xy = (centroide[0], centroide[1]))
        nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=5)

    plt.savefig('PD-MTZ-Heuristic ' + str(iter) + '.png')

    # plt.show()
    return MODEL.getAttr('x', xL), MODEL.getAttr('x', xR), MODEL.ObjVal#
#
#
#
#
#
#
#
def XPPNZZ(datos, vals_u, vals_zgij, vals_v, z, orig, dest, iter):

    grafos = datos.data

    nG = len(grafos)
    T_index = range(nG + 2)
    T_index_prima = range(1, nG+1)
    T_index_primaprima = range(nG+1)

    origin = orig
    dest = orig

    vD = 3

    vC = 1

    MODEL = gp.Model('XPPNM')

    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            ugi_index.append((g, i))
    #
    #
    #ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # # Variable continua no negativa pgLi = ugi * dgLi
    # pgLi_index = ugi_index
    #
    # pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    # vgi_index = ugi_index
    #
    # vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    # pgRi_index = ugi_index
    #
    # pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []
    #
    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sgi_index.append((g, i))
            for j in grafos[g-1].aristas:
                if i != j:
                    zgij_index.append((g, i, j))
    #
    #
    # zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    # sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    # pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))

    # z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL')
    pRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL')

    # Variables que modelan los puntos de entrada o recogida
    # xL: punto de salida del dron del camion en la etapa t
    xL_index = []

    for g in T_index:
        for dim in range(2):
            xL_index.append((g, dim))

    xL = MODEL.addVars(xL_index, vtype=GRB.CONTINUOUS, name='xL')

    # xR: punto de recogida del dron del camion en la etapa t
    xR_index = []

    for t in T_index:
        for dim in range(2):
            xR_index.append((t, dim))

    xR = MODEL.addVars(xR_index, vtype=GRB.CONTINUOUS, name='xR')

    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhogi_index.append((g, i))
            for dim in range(2):
                Rgi_index.append((g, i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')

    difL = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difL')

    difR = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difR')

    MODEL.update()

    # # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    # MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name = 'entrag')
    # MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    # MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name = 'flujou')
    # MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name = 'pgi3')


    # # Eliminación de subtours
    # for g in T_index_prima:
    #     for i in grafos[g-1].aristas[0:]:
    #         for j in grafos[g-1].aristas[0:]:
    #             if i != j:
    #                 MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g-1].num_aristas * zgij[g, i, j])


    # for g in T_index_prima:
    #     for i in grafos[g-1].aristas[0:]:
    #         MODEL.addConstr(sgi[g, i] >= 0)
    #         MODEL.addConstr(sgi[g, i] <= grafos[g-1].num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >=   xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[g, i, 0]*auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in dgLi.keys()), name = 'u-conic')

    # SmallM = []
    # BigM = []
    #
    # for g in T_index_prima:
    #     BigM.append(max([np.linalg.norm(elipses[g-1].centro - v) for v in grafos[g-1].V]) + elipses[g].radio)
    #     SmallM.append(dist_grafo(elipses[g-1].centro, grafos[g-1])[0] - elipses[g-1].radio)

    # MODEL.addConstrs((pgLi[g, i] >= SmallM[g] * ugi[g, i]) for g, i in ugi.keys())
    # MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM[g] * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >=   Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0]*auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name = 'zgij-conic')


    # for g, i, j in zgij.keys():
    #     first_i = i // 100 - 1
    #     second_i = i % 100
    #     first_j = j // 100 - 1
    #     second_j = j % 100
    #
    #     segm_i = Poligonal(np.array([[grafos[g-1].V[first_i, 0], grafos[g-1].V[first_i, 1]], [
    #                        grafos[g-1].V[second_i, 0], grafos[g-1].V[second_i, 1]]]), grafos[g-1].A[first_i, second_i])
    #     segm_j = Poligonal(np.array([[grafos[g-1].V[first_j, 0], grafos[g-1].V[first_j, 1]], [
    #                        grafos[g-1].V[second_j, 0], grafos[g-1].V[second_j, 1]]]), grafos[g-1].A[first_j, second_j])
    #
    #     BigM_local = eM.estima_BigM_local(segm_i, segm_j)
    #     SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
    #     MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
    #     MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >=   Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[g, i, 0]*auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in dgRi.keys()), name = 'v-conic')


    # SmallM = 0
    #BigM = 10000
    # SmallM = []
    # BigM = []
    #
    # for g in T_index_prima:
    #     BigM.append(max([np.linalg.norm(elipses[g].centro - v) for v in grafos[g-1].V]) + elipses[g].radio)
    #     SmallM.append(dist_grafo(elipses[g].centro, grafos[g-1])[0] - elipses[g].radio)

    # MODEL.addConstrs((pgRi[g, i] >= SmallM[g] * vgi[g, i]) for g, i in vgi.keys())
    # MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM[g] * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >=   xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, 0]*auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for g1, g2 in dRL.keys()), name = 'RL-conic')



    # SmallM = 0
    # BigM = 10000
    #
    # BigM = 0
    # for g in T_index_prima:
    #     for v in grafos[g-1].V:
    #         BigM = max([np.linalg.norm(origin - v), BigM])
    # MODEL.addConstrs((pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # SmallM = np.zeros((nG+2, nG+2))
    # BigM = np.zeros((nG+2, nG+2))
    #
    # for g1, g2 in z.keys():
    #     BigM[g1, g2] = eM.estima_BigM_local(elipses[g1], elipses[g2])
    #     SmallM[g1, g2] = eM.estima_SmallM_local(elipses[g1], elipses[g2])

    # MODEL.addConstrs((pRL[g1, g2] >= SmallM[g1, g2] * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM[g1, g2] * (1 - z[g1, g2]) for g1, g2 in z.keys()))



    # Restricciones para formar un tour
    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    # MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index if w != v) == 1 for v in T_index)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index if w != v) == 1 for v in T_index)

    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * z[v, w])

    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[v] - s[0] + (nG+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[0] - s[v] + (nG+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, nG+1):
    #     MODEL.addConstr(-z[0,v] - s[v] + (nG+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     MODEL.addConstr(-z[v,0] + s[v] + (nG+1-3)*z[0,v] <= nG+1-2, name="LiftedUB(%s)"%v)

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[nG + 1] == nG+1)

    MODEL.addConstrs((auxLR[g, dim] >=   xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0]*auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()), name = 'LR-conic')

    u_prim = 0
    v_prim = 0

    MODEL.addConstrs( ( gp.quicksum(dgLi[g, i]*vals_u[g, i] for i in grafos[g-1].aristas) + gp.quicksum(dgij[g, i, j]*vals_zgij[g, i, j] for g, i, j in dgij.keys())
                      + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas)
                      + gp.quicksum(dgRi[g, i]*vals_v[g, i] for i in grafos[g-1].aristas))/vD <= dLR[g]/vC for g in T_index_prima)

    # MODEL.addConstrs(dLR[g] <= 150 for g in dLR.keys())
    # MODEL.addConstrs((pgLi.sum('*', '*', t) +
    #                   pgij.sum(g, '*', '*') +
    #                   ugi.sum(g, '*', '*')*longitudes[g-1] +
    #                   pgRi.sum('*', '*', t))/vD <= dLR[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLR[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pgLi[g, i, t]
    #                   + pgij.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pgRi[g, i, t])/vD <= dLR[t]/vC for g, i, t in pgLi.keys())

    # MODEL.addConstr(z[0, 2] + z[1, 3] + z[2, 1] + z[3, 4] == 4)

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if datos.alpha:
            MODEL.addConstr(pgi[g, i] >= grafos[g-1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(Rgi[g, i, 0] == rhogi[g, i] * grafos[g-1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rgi[g, i, 1] == rhogi[g, i] * grafos[g-1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lgi[g, i, 0] == landagi[g, i] * grafos[g-1].V[first, 0] + (1 - landagi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lgi[g, i, 1] == landagi[g, i] * grafos[g-1].V[first, 1] + (1 - landagi[g, i]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)

    # # Fijado de variables
    # for g in T_index_prima:
    #     lista = [tuplas for h, tuplas in vals_zgij if h == g]
    #     MODEL.addConstrs(zgij[g, i, j] == 1 for i, j in lista[0])
    #     MODEL.addConstrs(ugi[h, i] == 1 for h, i in vals_u if h == g)
    #     MODEL.addConstrs(vgi[h, i] == 1 for h, i in vals_v if h == g)

    # MODEL.addConstrs(difL[g, dim] >=  xL[g, dim] - elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, dim] >= -xL[g, dim] + elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, 0]*difL[g, 0] + difL[g, 1]*difL[g, 1] <= elipses[g].radio*elipses[g].radio for g in T_index_prima)
    #
    # MODEL.addConstrs(difR[g, dim] >=  xR[g, dim] - elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, dim] >= -xR[g, dim] + elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, 0]*difR[g, 0] + difR[g, 1]*difR[g, 1] <= elipses[g+1].radio*elipses[g+1].radio for g in T_index_prima)

    # Origen y destino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xR[nG+1, dim] == dest[dim] for dim in range(2))
    MODEL.addConstrs(xL[nG+1, dim] == dest[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(dgLi[g, i]*vals_u[(g, i)] for g, i in dgLi.keys()) + gp.quicksum(dgRi[g, i]*vals_v[g, i] for g, i in dgRi.keys()) + gp.quicksum(dgij[g, i, j]*vals_zgij[g, i, j] for g, i, j in dgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLR[g] for g in dLR.keys()) + gp.quicksum(3*dRL[g1, g2]*z[g1, g2] for g1, g2 in dRL.keys())

    #objective = gp.quicksum(1*dLR[g] for g in dLR.keys()) + gp.quicksum(1*pRL[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    Model.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 150

    MODEL.setParam('OutputFlag', 1)

    MODEL.update()


    MODEL.write('AMDRPG-MTZ.lp')
    MODEL.write('AMDRPG-MTZ.mps')

    MODEL.optimize()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')

    # fig, ax = plt.subplots()
    # plt.axis([0, 100, 0, 100])

    # vals_u = MODEL.getAttr('x', ugi)
    # selected_u = gp.tuplelist((g, i)
    #                           for g, i in ugi_index if vals_u[g, i] > 0.5)
    selected_u = vals_u
    #print(selected_u)

    # vals_zgij = MODEL.getAttr('x', zgij)
    # selected_zgij = gp.tuplelist((g, i, j)
    #                           for g, i, j in zgij_index if vals_zgij[g, i, j] > 0.5)
    selected_zgij = vals_zgij
    #print(selected_zgij)

    # vals_v = MODEL.getAttr('x', vgi)
    # selected_v = gp.tuplelist((g, i)
    #                           for g, i in vgi_index if vals_v[g, i] > 0.5)
    #print(selected_v)
    selected_v = vals_v

    # valsz = MODEL.getAttr('x', z)

    selected_z = gp.tuplelist(e for e in dRL.keys() if z[e] > 0)
    #print(selected_z)
    path = subtour(selected_z)
    #print(path)

    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])


    for p in path[1:]:
        #    if ind < nG:
        if ind < nG:
            path_D = []
            path_D.append([xL[p, 0].X, xL[p, 1].X])
            index_g = 0
            index_i = 0
            for g, i in selected_u:
                if g == p:
                    index_g = g
                    index_i = i

            count = 0
            path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
            path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])
            limite = sum([1 for g, i, j in selected_zgij if g == index_g])
            while count < limite:
                for g, i, j in selected_zgij:
                    if index_g == g and index_i == i:
                        count += 1
                        index_i = j
                        path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
                        path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])

            ind += 1
            path_D.append([xR[p, 0].X, xR[p, 1].X])
        paths_D.append(path_D)
    # path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])


    for g, i in rhogi.keys():
        plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
        plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha = 0.3, markersize=10, color='green')
        ax.annotate("L" + str(i), xy = (xL[p, 0].X+0.5, xL[p, 1].X+0.5))
        plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=5, color='blue')
        ax.annotate("R" + str(i), xy = (xR[p, 0].X-1.5, xR[p, 1].X-1.5))


    ax.add_artist(Polygon(path_C, fill=False, animated=False,
                  linestyle='-', alpha=1, color='blue'))

    for path in paths_D:
        ax.add_artist(Polygon(path, fill=False, closed=False,
                      animated=False, alpha=1, color='red'))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))
    # for g in elipses:
    #     print(g.radio)
    #     ax.add_artist(g.artist)

    for g in T_index_prima:
        grafo = grafos[g-1]
        centroide = np.mean(grafo.V, axis = 0)
        nx.draw(grafo.G, grafo.pos, node_size=30,
                node_color='black', alpha=1, edge_color='gray')
        ax.annotate(g, xy = (centroide[0], centroide[1]))
        nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=5)

    plt.savefig('PD-MTZ-Heuristic ' + str(iter) + '.png')

    # plt.show()
    path = subtour(selected_z)

    return MODEL.getAttr('x', xL), MODEL.getAttr('x', xR), path, MODEL.ObjVal







def dist_grafo(point, graph):
    """Short summary.

    Parameters
    ----------
    point : list of two coordinates
        Point to calculate the distance.
    graph : entorno graph
        Graph from which we want to search the closest point to the origin.

    Returns
    -------
    list
        Closest point to punto

    """
    minimum = np.inf
    # x = []

    for segm in graph.aristas:
        first_V = graph.V[segm // 100 - 1]
        second_V = graph.V[segm % 100]

        M = gp.Model('min_dist')

        landa = M.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'landa')
        x_segm = M.addVars(2, vtype = GRB.CONTINUOUS, name = 'x_segm')
        dif = M.addVars(2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dif')
        d = M.addVar(vtype = GRB.CONTINUOUS, lb = 0.0, name = 'd')

        M.update()

        M.addConstrs(x_segm[dim] == landa*first_V[dim] + (1-landa)*second_V[dim] for dim in range(2))
        M.addConstrs(dif[dim] >=  x_segm[dim] - point[dim] for dim in range(2))
        M.addConstrs(dif[dim] >= -x_segm[dim] + point[dim] for dim in range(2))
        M.addConstr(dif[0]*dif[0] + dif[1]*dif[1] <= d*d)

        M.update()

        M.setObjective(d, GRB.MINIMIZE)

        M.setParam('OutputFlag', 0)
        M.update()

        M.optimize()

        if d.X < minimum:
            x = [x_segm[0].X, x_segm[1].X]
            minimum = d.X
    # else:
    #     for v in graph.V:
    #         if np.linalg.norm(point - v) <= minimum:
    #             x = v
    #             minimum = np.linalg.norm(point - v)

    return minimum, x
































def XPPNe(datos, orig, dest, elipses, iter):

    grafos = datos.mostrar_datos()

    nG = len(grafos)

    T_index = range(nG + 2)
    T_index_prima = range(1, nG+1)
    T_index_primaprima = range(nG+1)

    origin = orig
    dest = orig

    vD = 3

    vC = 1

    # Creamos el modelo8
    MODEL = gp.Model("PD-Graph")

    # Variables que modelan las distancias
    # Variable binaria ugi = 1 si en la etapa t entramos por el segmento sgi
    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            ugi_index.append((g, i))


    ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # Variable continua no negativa pgLi = ugi * dgLi
    pgLi_index = ugi_index

    pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    vgi_index = ugi_index

    vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    pgRi_index = ugi_index

    pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sgi_index.append((g, i))
            for j in grafos[g-1].aristas:
                if i != j:
                    zgij_index.append((g, i, j))

    zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))

    z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL')
    pRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL')

    # Variables que modelan los puntos de entrada o recogida
    # xL: punto de salida del dron del camion en la etapa t
    xL_index = []

    for g in T_index:
        for dim in range(2):
            xL_index.append((g, dim))

    xL = MODEL.addVars(xL_index, vtype=GRB.CONTINUOUS, name='xL')

    # xR: punto de recogida del dron del camion en la etapa t
    xR_index = []

    for t in T_index:
        for dim in range(2):
            xR_index.append((t, dim))

    xR = MODEL.addVars(xR_index, vtype=GRB.CONTINUOUS, name='xR')

    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhogi_index.append((g, i))
            for dim in range(2):
                Rgi_index.append((g, i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')
    difL = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difL')

    difR = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difR')

    MODEL.update()


    # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name = 'entrag')
    MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name = 'flujou')
    MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name = 'pgi3')

    # MODEL.addConstr(ugi[0, 101, 0] == 0)
    # MODEL.addConstr(ugi[0, 101, 1] == 0)


    # Eliminación de subtours
    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            for j in grafos[g-1].aristas[0:]:
                if i != j:
                    MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g-1].num_aristas * zgij[g, i, j])

    # for g in range(nG):
    #     MODEL.addConstr(sgi[g, grafos[g].aristas[0]] == 0)

    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            MODEL.addConstr(sgi[g, i] >= 0)
            MODEL.addConstr(sgi[g, i] <= grafos[g-1].num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >=   xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[g, i, 0]*auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in ugi.keys()), name = 'u-conic')

    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio

    SmallM = 0
    BigM = 10000
    #
    # BigM = 0
    # for g in T_index_prima:
    #     for v in grafos[g-1].V:
    #         BigM = max([np.linalg.norm(origin - v), BigM])
    #
    # BigM += 5
    #BigM = max([np.linalg.norm(origin-grafos[g].V) for g in range(nG)])

    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio


    MODEL.addConstrs((pgLi[g, i] >= SmallM * ugi[g, i]) for g, i in ugi.keys())
    MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >=   Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0]*auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name = 'zgij-conic')


    for g, i, j in zgij.keys():
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
        MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
        MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >=   Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[g, i, 0]*auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in vgi.keys()), name = 'v-conic')

    # SmallM = 0
    # BigM = 10000
    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g+1]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio

    # SmallM = 0
    #BigM = 10000
    MODEL.addConstrs((pgRi[g, i] >= SmallM * vgi[g, i]) for g, i in vgi.keys())
    MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >=   xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, 0]*auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for g1, g2 in dRL.keys()), name = 'RL-conic')

    SmallM = 0
    BigM = 10000
    MODEL.addConstrs((pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in z.keys()))
    MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # SmallM = np.zeros((nG+2, nG+2))
    # BigM = np.zeros((nG+2, nG+2))
    #
    # for g1, g2 in z.keys():
    #     BigM[g1, g2] = eM.estima_BigM_local(elipses[g1], elipses[g2])
    #     SmallM[g1, g2] = eM.estima_SmallM_local(elipses[g1], elipses[g2])

    # for g in T_index_prima:
    #     BigM[g, g+1] = eM.estima_BigM_local(elipses[g], elipses[g+1])
    #     SmallM[g, g+1] = eM.estima_SmallM_local(elipses[g], elipses[g+1])


    # MODEL.addConstrs((pRL[g1, g2] >= SmallM[g1, g2] * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM[g1, g2] * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # Restricciones para formar un tour
    MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index if w != v) == 1 for v in T_index)
    MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index if w != v) == 1 for v in T_index)

    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index if v != 0) == 0)
    # MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstr(gp.quicksum(z[0, w] for w in T_index if w != 0) == 1)
    # MODEL.addConstr(gp.quicksum(z[v, nG+1] for v in T_index if v != nG+1) == 0)

    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * z[v, w])

    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[v] - s[0] + (nG+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[0] - s[v] + (nG+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, nG+1):
    #     MODEL.addConstr(-z[0,v] - s[v] + (nG+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     MODEL.addConstr(-z[v,0] + s[v] + (nG+1-3)*z[0,v] <= nG+1-2, name="LiftedUB(%s)"%v)

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[nG + 1] == nG+1)

    MODEL.addConstrs((auxLR[g, dim] >=   xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0]*auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()), name = 'LR-conic')

    MODEL.addConstrs((pgLi.sum(g, '*') + pgij.sum(g, '*', '*') +  gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + pgRi.sum(g, '*'))/vD <= dLR[g]/vC for g in T_index_prima)

    # MODEL.addConstrs(dLR[g] <= 150 for g in dLR.keys())
    # MODEL.addConstrs((pgLi.sum('*', '*', t) +
    #                   pgij.sum(g, '*', '*') +
    #                   ugi.sum(g, '*', '*')*longitudes[g-1] +
    #                   pgRi.sum('*', '*', t))/vD <= dLR[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLR[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pgLi[g, i, t]
    #                   + pgij.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pgRi[g, i, t])/vD <= dLR[t]/vC for g, i, t in pgLi.keys())

    # MODEL.addConstr(z[0, 2] + z[1, 3] + z[2, 1] + z[3, 4] == 4)

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if datos.alpha:
            MODEL.addConstr(pgi[g, i] == grafos[g-1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(Rgi[g, i, 0] == rhogi[g, i] * grafos[g-1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rgi[g, i, 1] == rhogi[g, i] * grafos[g-1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lgi[g, i, 0] == landagi[g, i] * grafos[g-1].V[first, 0] + (1 - landagi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lgi[g, i, 1] == landagi[g, i] * grafos[g-1].V[first, 1] + (1 - landagi[g, i]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)

    MODEL.addConstrs(difL[g, dim] >=  xL[g, dim] - elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    MODEL.addConstrs(difL[g, dim] >= -xL[g, dim] + elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    MODEL.addConstrs(difL[g, 0]*difL[g, 0] + difL[g, 1]*difL[g, 1] <= elipses[g].radio*elipses[g].radio for g in T_index_prima)

    MODEL.addConstrs(difR[g, dim] >=  xR[g, dim] - elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    MODEL.addConstrs(difR[g, dim] >= -xR[g, dim] + elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    MODEL.addConstrs(difR[g, 0]*difR[g, 0] + difR[g, 1]*difR[g, 1] <= elipses[g+1].radio*elipses[g+1].radio for g in T_index_prima)


    # Origen y destino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xR[nG+1, dim] == dest[dim] for dim in range(2))
    MODEL.addConstrs(xL[nG+1, dim] == dest[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(pgLi[g, i] + pgRi[g, i] for g, i in pgRi.keys()) + gp.quicksum(pgij[g, i, j] for g, i, j in pgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLR[g] for g in dLR.keys()) + gp.quicksum(3*pRL[g1, g2] for g1, g2 in dRL.keys())

    #objective = gp.quicksum(1*dLR[g] for g in dLR.keys()) + gp.quicksum(1*pRL[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    Model.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    #MODEL.Params.timeLimit = 10
    MODEL.Params.SolutionLimit = 2

    MODEL.update()

    MODEL.write('AMDRPG-MTZ.lp')
    MODEL.write('AMDRPG-MTZ.mps')
    MODEL.optimize()


    MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')


    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist((g, i)
                              for g, i in ugi_index if vals_u[g, i] > 0.5)
    #selected_u = vals_u
    #print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((g, i, j)
                              for g, i, j in zgij_index if vals_zgij[g, i, j] > 0.5)
    #selected_zgij = vals_zgij
    #print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    selected_v = gp.tuplelist((g, i)
                              for g, i in vgi_index if vals_v[g, i] > 0.5)
    #print(selected_v)
    #selected_v = vals_v

    valsz = MODEL.getAttr('x', z)

    selected_z = gp.tuplelist(e for e in valsz if valsz[e] > 0)
    #print(selected_z)
    ##print(selected_z)
    path = subtour(selected_z)
    #print(path)

    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist((g, i)
                              for g, i in vals_u.keys() if vals_u[g, i] > 0.5)
    #print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((g, i, j)
                              for g, i, j in vals_zgij.keys() if vals_zgij[g, i, j] > 0.5)
    #print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    selected_v = gp.tuplelist((g, i)
                              for g, i in vals_v.keys() if vals_v[g, i] > 0.5)
    #print(selected_v)

    valsz = MODEL.getAttr('x', z)
    selected_z = gp.tuplelist(e for e in valsz if valsz[e] > 0)
    #print(selected_z)
    path = subtour(selected_z)


    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])


    for p in path[1:]:
        #    if ind < nG:
        if ind < nG:
            path_D = []
            path_D.append([xL[p, 0].X, xL[p, 1].X])
            index_g = 0
            index_i = 0
            for g, i in selected_u:
                if g == p:
                    index_g = g
                    index_i = i

            count = 0
            path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
            path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])
            limite = sum([1 for g, i, j in selected_zgij if g == index_g])
            while count < limite:
                for g, i, j in selected_zgij:
                    if index_g == g and index_i == i:
                        count += 1
                        index_i = j
                        path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
                        path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])

            ind += 1
            path_D.append([xR[p, 0].X, xR[p, 1].X])
        paths_D.append(path_D)

    # path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])


    # for g, i in rhogi.keys():
    #     plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #     plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha = 0.3, markersize=10, color='green')
        ax.annotate("L" + str(i), xy = (xL[p, 0].X+0.5, xL[p, 1].X+0.5))
        plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=5, color='blue')
        ax.annotate("R" + str(i), xy = (xR[p, 0].X-1.5, xR[p, 1].X-1.5))


    ax.add_artist(Polygon(path_C, fill=False, animated=False,
                  linestyle='-', alpha=1, color='blue'))

    for paths in paths_D:
        ax.add_artist(Polygon(paths, fill=False, closed=False,
                      animated=False, alpha=1, color='red', lw = 0.1))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))

    # if elipses:
    #     for e in elipses:
    #         ax.add_artist(e.artist)

    for g in T_index_prima:
        grafo = grafos[g-1]
        centroide = np.mean(grafo.V, axis = 0)
        nx.draw(grafo.G, grafo.pos, node_size=30,
                node_color='black', alpha=1, edge_color='gray')
        ax.annotate(g, xy = (centroide[0], centroide[1]))
        nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=5)

    plt.savefig('PD-MTZ-Heuristic ' + str(iter) + '.png')

    # plt.show()
    return MODEL.getAttr('x', xL), MODEL.getAttr('x', xR), MODEL.ObjVal, path#

def XPPNxl(datos, vals_xL, vals_xR, orig, dest, iter):

    print()
    print('--------------------------------------------')
    print('Exact Formulation: Fixing points. Iteration: {i})'.format(i = iter))
    print('--------------------------------------------')
    print()

    grafos = datos.mostrar_datos()

    nG = len(grafos)

    T_index = range(nG + 2)
    T_index_prima = range(1, nG+1)
    T_index_primaprima = range(nG+1)

    origin = orig
    dest = orig

    vD = 3

    vC = 1

    # Creamos el modelo8
    MODEL = gp.Model("PD-Graph")

    # Variables que modelan las distancias
    # Variable binaria ugi = 1 si en la etapa t entramos por el segmento sgi
    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            ugi_index.append((g, i))


    ugi = MODEL.addVars(ugi_index, vtype=GRB.BINARY, name='ugi')

    # Variable continua no negativa dgLi que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sgi.
    dgLi_index = ugi_index

    dgLi = MODEL.addVars(dgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgLi')
    auxgLi = MODEL.addVars(dgLi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgLi')

    # Variable continua no negativa pgLi = ugi * dgLi
    pgLi_index = ugi_index

    pgLi = MODEL.addVars(pgLi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgLi')


    # Variable binaria vgi = 1 si en la etapa t salimos por el segmento sgi
    vgi_index = ugi_index

    vgi = MODEL.addVars(vgi_index, vtype=GRB.BINARY, name='vgi')

    # Variable continua no negativa dgRi que indica la distancia desde el punto de salida del segmento sgi hasta el
    # punto de recogida del camion
    dgRi_index = ugi_index

    dgRi = MODEL.addVars(dgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgRi')
    auxgRi = MODEL.addVars(dgRi_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difgRi')


    # Variable continua no negativa pgRi = vgi * dgRi
    pgRi_index = ugi_index

    pgRi = MODEL.addVars(pgRi_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgRi')


    # Variable binaria zgij = 1 si voy del segmento i al segmento j del grafo g.
    zgij_index = []
    sgi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            sgi_index.append((g, i))
            for j in grafos[g-1].aristas:
                if i != j:
                    zgij_index.append((g, i, j))

    zgij = MODEL.addVars(zgij_index, vtype=GRB.BINARY, name='zgij')
    sgi = MODEL.addVars(sgi_index, vtype=GRB.CONTINUOUS, lb=0, name='sgi')

    # Variable continua no negativa dgij que indica la distancia entre los segmentos i j en el grafo g.
    dgij_index = zgij_index

    dgij = MODEL.addVars(dgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')
    auxgij = MODEL.addVars(
        dgij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dgij')

    # Variable continua no negativa pgij = zgij * dgij
    pgij_index = zgij_index

    pgij = MODEL.addVars(pgij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pgij')

    # Distancia del punto de lanzamiento al punto de recogida
    dLR = MODEL.addVars(T_index_prima, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))

    z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'difRL')
    pRL = MODEL.addVars(z_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pRL')

    # Variables que modelan los puntos de entrada o recogida
    # xL: punto de salida del dron del camion en la etapa t
    xL_index = []

    for g in T_index:
        for dim in range(2):
            xL_index.append((g, dim))

    xL = MODEL.addVars(xL_index, vtype=GRB.CONTINUOUS, name='xL')

    # xR: punto de recogida del dron del camion en la etapa t
    xR_index = []

    for t in T_index:
        for dim in range(2):
            xR_index.append((t, dim))

    xR = MODEL.addVars(xR_index, vtype=GRB.CONTINUOUS, name='xR')

    # Rgi: punto de recogida del dron para el segmento sgi
    Rgi_index = []
    rhogi_index = []

    for g in T_index_prima:
        for i in grafos[g-1].aristas:
            rhogi_index.append((g, i))
            for dim in range(2):
                Rgi_index.append((g, i, dim))

    Rgi = MODEL.addVars(Rgi_index, vtype=GRB.CONTINUOUS, name='Rgi')
    rhogi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhogi')

    # Lgi: punto de lanzamiento del dron del segmento sgi
    Lgi_index = Rgi_index
    landagi_index = rhogi_index

    Lgi = MODEL.addVars(Lgi_index, vtype=GRB.CONTINUOUS, name='Lgi')
    landagi = MODEL.addVars(landagi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landagi')

    # Variables auxiliares para modelar el valor absoluto
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype = GRB.BINARY, name = 'mugi')
    pgi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphagi')
    difL = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difL')

    difR = MODEL.addVars(T_index, 2, vtype = GRB.CONTINUOUS, name = 'difR')

    MODEL.update()


    # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name = 'entrag')
    MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name = 'saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(nG))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(nG))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name = 'flujou')
    MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name = 'flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name = 'pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name = 'pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name = 'pgi3')

    # MODEL.addConstr(ugi[0, 101, 0] == 0)
    # MODEL.addConstr(ugi[0, 101, 1] == 0)


    # Eliminación de subtours
    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            for j in grafos[g-1].aristas[0:]:
                if i != j:
                    MODEL.addConstr(grafos[g-1].num_aristas - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g-1].num_aristas * zgij[g, i, j])

    # for g in range(nG):
    #     MODEL.addConstr(sgi[g, grafos[g].aristas[0]] == 0)

    for g in T_index_prima:
        for i in grafos[g-1].aristas[0:]:
            MODEL.addConstr(sgi[g, i] >= 0)
            MODEL.addConstr(sgi[g, i] <= grafos[g-1].num_aristas - 1)


    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >=   xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs((auxgLi[g, i, 0]*auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in ugi.keys()), name = 'u-conic')

    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio

    SmallM = 0
    BigM = 10000
    #
    # BigM = 0
    # for g in T_index_prima:
    #     for v in grafos[g-1].V:
    #         BigM = max([np.linalg.norm(origin - v), BigM])
    #
    # BigM += 5
    #BigM = max([np.linalg.norm(origin-grafos[g].V) for g in range(nG)])

    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio


    MODEL.addConstrs((pgLi[g, i] >= SmallM * ugi[g, i]) for g, i in ugi.keys())
    MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >=   Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0]*auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name = 'zgij-conic')


    for g, i, j in zgij.keys():
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
        MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
        MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >=   Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs((auxgRi[g, i, 0]*auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in vgi.keys()), name = 'v-conic')

    # SmallM = 0
    # BigM = 10000
    # SmallM = {}
    # BigM = {}
    #
    # for g in T_index_prima:
    #     elipse = elipses[g+1]
    #     SmallM[g] = dist_grafo(elipse.centro, grafos[g-1])[0] - elipse.radio
    #     BigM[g] = max([np.linalg.norm(elipse.centro-v) for v in grafos[g-1].V]) + elipse.radio

    # SmallM = 0
    #BigM = 10000
    MODEL.addConstrs((pgRi[g, i] >= SmallM * vgi[g, i]) for g, i in vgi.keys())
    MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >=   xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, 0]*auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for g1, g2 in dRL.keys()), name = 'RL-conic')

    # SmallM = 0
    # BigM = 10000
    MODEL.addConstrs((pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in z.keys()))
    MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # SmallM = np.zeros((nG+2, nG+2))
    # BigM = np.zeros((nG+2, nG+2))
    #
    # for g1, g2 in z.keys():
    #     BigM[g1, g2] = eM.estima_BigM_local(elipses[g1], elipses[g2])
    #     SmallM[g1, g2] = eM.estima_SmallM_local(elipses[g1], elipses[g2])

    # for g in T_index_prima:
    #     BigM[g, g+1] = eM.estima_BigM_local(elipses[g], elipses[g+1])
    #     SmallM[g, g+1] = eM.estima_SmallM_local(elipses[g], elipses[g+1])


    # MODEL.addConstrs((pRL[g1, g2] >= SmallM[g1, g2] * z[g1, g2] for g1, g2 in z.keys()))
    # MODEL.addConstrs((pRL[g1, g2] >= dRL[g1, g2] - BigM[g1, g2] * (1 - z[g1, g2]) for g1, g2 in z.keys()))

    # Restricciones para formar un tour
    MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index if w != v) == 1 for v in T_index)
    MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index if w != v) == 1 for v in T_index)

    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index if v != 0) == 0)
    # MODEL.addConstr(gp.quicksum(z[nG+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstr(gp.quicksum(z[0, w] for w in T_index if w != 0) == 1)
    # MODEL.addConstr(gp.quicksum(z[v, nG+1] for v in T_index if v != nG+1) == 0)

    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * z[v, w])

    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[v] - s[0] + (nG+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, nG+1):
    #     MODEL.addConstr(s[0] - s[v] + (nG+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, nG+1):
    #     MODEL.addConstr(-z[0,v] - s[v] + (nG+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     MODEL.addConstr(-z[v,0] + s[v] + (nG+1-3)*z[0,v] <= nG+1-2, name="LiftedUB(%s)"%v)

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[nG + 1] == nG+1)

    MODEL.addConstrs((auxLR[g, dim] >=   xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0]*auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()), name = 'LR-conic')

    MODEL.addConstrs((pgLi.sum(g, '*') + pgij.sum(g, '*', '*') +  gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) + pgRi.sum(g, '*'))/vD <= dLR[g]/vC for g in T_index_prima)

    # MODEL.addConstrs(dLR[g] <= 150 for g in dLR.keys())
    # MODEL.addConstrs((pgLi.sum('*', '*', t) +
    #                   pgij.sum(g, '*', '*') +
    #                   ugi.sum(g, '*', '*')*longitudes[g-1] +
    #                   pgRi.sum('*', '*', t))/vD <= dLR[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLR[t]/vD <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pgLi[g, i, t]
    #                   + pgij.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].longaristas[i // 100 - 1, i % 100]
    #                   + pgRi[g, i, t])/vD <= dLR[t]/vC for g, i, t in pgLi.keys())

    # MODEL.addConstr(z[0, 2] + z[1, 3] + z[2, 1] + z[3, 4] == 4)

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if datos.alpha:
            MODEL.addConstr(pgi[g, i] >= grafos[g-1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(Rgi[g, i, 0] == rhogi[g, i] * grafos[g-1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Rgi[g, i, 1] == rhogi[g, i] * grafos[g-1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g-1].V[second, 1])
        MODEL.addConstr(Lgi[g, i, 0] == landagi[g, i] * grafos[g-1].V[first, 0] + (1 - landagi[g, i]) * grafos[g-1].V[second, 0])
        MODEL.addConstr(Lgi[g, i, 1] == landagi[g, i] * grafos[g-1].V[first, 1] + (1 - landagi[g, i]) * grafos[g-1].V[second, 1])

    if not(datos.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for i in grafos[g-1].aristas) >= grafos[g-1].alpha*grafos[g-1].longitud)

    # MODEL.addConstrs(difL[g, dim] >=  xL[g, dim] - elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, dim] >= -xL[g, dim] + elipses[g].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difL[g, 0]*difL[g, 0] + difL[g, 1]*difL[g, 1] <= elipses[g].radio*elipses[g].radio for g in T_index_prima)
    #
    # MODEL.addConstrs(difR[g, dim] >=  xR[g, dim] - elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, dim] >= -xR[g, dim] + elipses[g+1].centro[dim] for dim in range(2) for g in T_index_prima)
    # MODEL.addConstrs(difR[g, 0]*difR[g, 0] + difR[g, 1]*difR[g, 1] <= elipses[g+1].radio*elipses[g+1].radio for g in T_index_prima)
    for g in T_index_prima:
        MODEL.addConstrs(xL[g, dim] == vals_xL[g][dim] for dim in range(2))
        MODEL.addConstrs(xR[g, dim] == vals_xR[g][dim] for dim in range(2))


    # Origen y destino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xR[nG+1, dim] == dest[dim] for dim in range(2))
    MODEL.addConstrs(xL[nG+1, dim] == dest[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(pgLi[g, i] + pgRi[g, i] for g, i in pgRi.keys()) + gp.quicksum(pgij[g, i, j] for g, i, j in pgij.keys()) + gp.quicksum(pgi[g, i]*grafos[g-1].longaristas[i // 100 - 1, i % 100] for g in T_index_prima for i in grafos[g-1].aristas) + gp.quicksum(3*dLR[g] for g in dLR.keys()) + gp.quicksum(3*pRL[g1, g2] for g1, g2 in dRL.keys())

    #objective = gp.quicksum(1*dLR[g] for g in dLR.keys()) + gp.quicksum(1*pRL[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 6
    # MODEL.Params.OutputFlag = 1
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 120
    MODEL.Params.SolutionLimit = 2

    MODEL.update()

    MODEL.write('AMDRPG-MTZ.lp')
    MODEL.write('AMDRPG-MTZ.mps')
    MODEL.optimize()


    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')


    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist((g, i)
                              for g, i in ugi_index if vals_u[g, i] > 0.5)
    #selected_u = vals_u
    #print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((g, i, j)
                              for g, i, j in zgij_index if vals_zgij[g, i, j] > 0.5)
    #selected_zgij = vals_zgij
    #print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    selected_v = gp.tuplelist((g, i)
                              for g, i in vgi_index if vals_v[g, i] > 0.5)
    #print(selected_v)
    #selected_v = vals_v

    valsz = MODEL.getAttr('x', z)

    selected_z = gp.tuplelist(e for e in valsz if valsz[e] > 0)
    #print(selected_z)
    #print(selected_z)
    path = subtour(selected_z)
    #print(path)

    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    vals_u = MODEL.getAttr('x', ugi)
    selected_u = gp.tuplelist((g, i)
                              for g, i in vals_u.keys() if vals_u[g, i] > 0.5)
    # print(selected_u)

    vals_zgij = MODEL.getAttr('x', zgij)
    selected_zgij = gp.tuplelist((g, i, j)
                              for g, i, j in vals_zgij.keys() if vals_zgij[g, i, j] > 0.5)
    # print(selected_zgij)

    vals_v = MODEL.getAttr('x', vgi)
    selected_v = gp.tuplelist((g, i)
                              for g, i in vals_v.keys() if vals_v[g, i] > 0.5)
    # print(selected_v)

    valsz = MODEL.getAttr('x', z)
    selected_z = gp.tuplelist(e for e in valsz if valsz[e] > 0)
    # print(selected_z)
    path = subtour(selected_z)


    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])


    for p in path[1:]:
        #    if ind < nG:
        if ind < nG:
            path_D = []
            path_D.append([xL[p, 0].X, xL[p, 1].X])
            index_g = 0
            index_i = 0
            for g, i in selected_u:
                if g == p:
                    index_g = g
                    index_i = i

            count = 0
            path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
            path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])
            limite = sum([1 for g, i, j in selected_zgij if g == index_g])
            while count < limite:
                for g, i, j in selected_zgij:
                    if index_g == g and index_i == i:
                        count += 1
                        index_i = j
                        path_D.append([Rgi[index_g, index_i, 0].X, Rgi[index_g, index_i, 1].X])
                        path_D.append([Lgi[index_g, index_i, 0].X, Lgi[index_g, index_i, 1].X])

            ind += 1
            path_D.append([xR[p, 0].X, xR[p, 1].X])
        paths_D.append(path_D)

    # path_C.append([xLt[nG+1, 0].X, xLt[nG+1, 1].X])


    # for g, i in rhogi.keys():
    #     plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #     plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'ko', markersize=1, color='cyan')
    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha = 0.3, markersize=10, color='green')
        ax.annotate("L" + str(i), xy = (xL[p, 0].X+0.5, xL[p, 1].X+0.5))
        plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=5, color='blue')
        ax.annotate("R" + str(i), xy = (xR[p, 0].X-1.5, xR[p, 1].X-1.5))


    ax.add_artist(Polygon(path_C, fill=False, animated=False,
                  linestyle='-', alpha=1, color='blue'))

    for paths in paths_D:
        ax.add_artist(Polygon(paths, fill=False, closed=False,
                      animated=False, alpha=1, color='red', lw = 0.1))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))

    # if elipses:
    #     for e in elipses:
    #         ax.add_artist(e.artist)

    for g in T_index_prima:
        grafo = grafos[g-1]
        centroide = np.mean(grafo.V, axis = 0)
        nx.draw(grafo.G, grafo.pos, node_size=30,
                node_color='black', alpha=1, edge_color='gray')
        ax.annotate(g, xy = (centroide[0], centroide[1]))
        nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=5)

    plt.savefig('PD-MTZ-Heuristic ' + str(iter) + '.png')

    # plt.show()
    return MODEL.getAttr('x', xL), MODEL.getAttr('x', xR), MODEL.ObjVal, path#
