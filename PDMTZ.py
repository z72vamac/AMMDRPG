"""Tenemos un conjunto E de entornos y un conjunto de poligonales P de las que queremos recorrer un porcentaje alfa p . Buscamos
   un tour de mínima distancia que alterne poligonal-entorno y que visite todas las poligonales"""

# Incluimos primero los paquetes
import gurobipy as gp
import networkx as nx
from gurobipy import GRB
from matplotlib.patches import Polygon

import auxiliar_functions as af
import bigM_estimation as eM
from neighbourhood import *
from tsp_heuristic import heuristic

# Definicion de los data
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


# np.random.seed(1)
#
# lista = [4, 4, 4, 4]
# graphs_number = len(lista)
# data = Data([], m=graphs_number, r=1, grid = False, time_limit=120, alpha = True,
#              initialization=True,
#              show=True,
#              seed=2)
#
# data.generate_grid()
# #
# # # path = [0, 2, 3, 4, 1, 5]
# # # z = af.path2matrix(path)
# #
# data.generate_graphs(lista)

def PDMTZ(data):
    origin = [5, 5]
    destination = [95, 5]
    # destination = origin
    grafos = data.graphs_numberostrar_data()
    # print(grafos[0].V)

    result = []

    graphs_number = data.graphs_number
    T_index = range(data.graphs_number + 2)
    T_index_prima = range(1, data.graphs_number + 1)
    T_index_primaprima = range(data.graphs_number + 1)

    drone_speed = 3

    vC = 1
    # Creamos el modelo8
    MODEL = gp.Model("PD-Mtz")

    # Variables que modelan las distancias
    # Variable binaria ugi = 1 si en la etapa t entramos por el segmento sgi
    ugi_index = []

    for g in T_index_prima:
        for i in grafos[g - 1].edges:
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
        for i in grafos[g - 1].edges:
            sgi_index.append((g, i))
            for j in grafos[g - 1].edges:
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
    dLR = MODEL.addVars(T_index_prima, vtype=GRB.CONTINUOUS, lb=0.0, name='dLR')
    auxLR = MODEL.addVars(T_index_prima, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLR')

    # Variable binaria z que vale uno si se va del grafo g al grafo g'
    z_index = []

    for v in T_index:
        for w in T_index:
            if v != w:
                z_index.append((v, w))

    z = MODEL.addVars(z_index, vtype=GRB.BINARY, name='z')
    s = MODEL.addVars(T_index, vtype=GRB.CONTINUOUS, lb=0, name='s')

    dRL = MODEL.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRL')
    auxRL = MODEL.addVars(z_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRL')
    pRL = MODEL.addVars(z_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pRL')

    holg = MODEL.addVars(T_index_prima, vtype=GRB.CONTINUOUS, lb=0.0, name='holg')
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
        for i in grafos[g - 1].edges:
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
    mingi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='mingi')
    maxgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='maxgi')
    entrygi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='entrygi')
    mugi = MODEL.addVars(rhogi_index, vtype=GRB.BINARY, name='mugi')
    pgi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='pgi')
    alphagi = MODEL.addVars(rhogi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alphagi')

    MODEL.update()

    if data.initialization:
        try:
            z_init, xL_init, xR_init, results = heuristic(data)

            for g1, g2 in z_index:
                z[g1, g2].start = z_init[g1, g2]

            for g in T_index_prima:
                for dim in range(2):
                    xL[g, dim].start = vals_xL[g][dim]
                    xR[g, dim].start = vals_xR[g][dim]

        except:
            print('No ha encontrado solucion inicial')
    else:
        print('Resolviendo sin solucion inicial')

    # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs((ugi.sum(g, '*') == 1 for g in T_index_prima), name='entrag')
    MODEL.addConstrs((vgi.sum(g, '*') == 1 for g in T_index_prima), name='saleg')

    # MODEL.addConstrs(ugi.sum('*', i, '*') == 1 for i in range(graphs_number))
    # MODEL.addConstrs(vgi.sum('*', i, '*') == 1 for g in range(graphs_number))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida del grafo
    MODEL.addConstrs((mugi[g, i] - ugi[g, i] == zgij.sum(g, '*', i) for g, i, j in zgij.keys()), name='flujou')
    MODEL.addConstrs((mugi[g, i] - vgi[g, i] == zgij.sum(g, i, '*') for g, i, j in zgij.keys()), name='flujov')

    MODEL.addConstrs((pgi[g, i] >= mugi[g, i] + alphagi[g, i] - 1 for g, i in rhogi.keys()), name='pgi1')
    MODEL.addConstrs((pgi[g, i] <= mugi[g, i] for g, i in rhogi.keys()), name='pgi2')
    MODEL.addConstrs((pgi[g, i] <= alphagi[g, i] for g, i in rhogi.keys()), name='pgi3')

    # Eliminación de subtours
    for g in T_index_prima:
        for i in grafos[g - 1].edges[0:]:
            for j in grafos[g - 1].edges[0:]:
                if i != j:
                    MODEL.addConstr(
                        grafos[g - 1].edges_number - 1 >= (sgi[g, i] - sgi[g, j]) + grafos[g - 1].edges_number * zgij[
                            g, i, j])

    # for g in range(graphs_number):
    #     MODEL.addConstr(sgi[g, grafos[g].edges[0]] == 0)

    for g in T_index_prima:
        for i in grafos[g - 1].edges[0:]:
            MODEL.addConstr(sgi[g, i] >= 0)
            MODEL.addConstr(sgi[g, i] <= grafos[g - 1].edges_number - 1)

    # Restricciones de distancias y producto
    MODEL.addConstrs((auxgLi[g, i, dim] >= xL[g, dim] - Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())
    MODEL.addConstrs((auxgLi[g, i, dim] >= - xL[g, dim] + Rgi[g, i, dim]) for g, i, dim in auxgLi.keys())

    MODEL.addConstrs(
        (auxgLi[g, i, 0] * auxgLi[g, i, 0] + auxgLi[g, i, 1] * auxgLi[g, i, 1] <= dgLi[g, i] * dgLi[g, i] for g, i in
         ugi.keys()), name='u-conic')

    SmallM = 0
    # BigM = 10000

    BigM = 0
    for g in T_index_prima:
        for h in T_index_prima:
            BigM = max(max([np.linalg.norm(v - w) for v in grafos[g - 1].V for w in grafos[h - 1].V]), BigM)

    # MODEL.addConstr(ugi[1, 101] == 1)
    # MODEL.addConstr(vgi[1, 203] == 1)

    MODEL.addConstrs((pgLi[g, i] >= SmallM * ugi[g, i]) for g, i in ugi.keys())
    MODEL.addConstrs((pgLi[g, i] >= dgLi[g, i] - BigM * (1 - ugi[g, i])) for g, i in ugi.keys())

    MODEL.addConstrs((auxgij[g, i, j, dim] >= Lgi[g, i, dim] - Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())
    MODEL.addConstrs((auxgij[g, i, j, dim] >= - Lgi[g, i, dim] + Rgi[g, j, dim]) for g, i, j, dim in auxgij.keys())

    MODEL.addConstrs((auxgij[g, i, j, 0] * auxgij[g, i, j, 0] + auxgij[g, i, j, 1] * auxgij[g, i, j, 1] <= dgij[
        g, i, j] * dgij[g, i, j] for g, i, j in dgij.keys()), name='zgij-conic')

    for g, i, j in zgij.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Polygonal(np.array([[grafos[g - 1].V[first_i, 0], grafos[g - 1].V[first_i, 1]], [
            grafos[g - 1].V[second_i, 0], grafos[g - 1].V[second_i, 1]]]), grafos[g - 1].A[first_i, second_i])
        segm_j = Polygonal(np.array([[grafos[g - 1].V[first_j, 0], grafos[g - 1].V[first_j, 1]], [
            grafos[g - 1].V[second_j, 0], grafos[g - 1].V[second_j, 1]]]), grafos[g - 1].A[first_j, second_j])

        BigM_local = eM.estimate_local_U(segm_i, segm_j)
        SmallM_local = eM.estimate_local_L(segm_i, segm_j)
        MODEL.addConstr((pgij[g, i, j] >= SmallM_local * zgij[g, i, j]))
        MODEL.addConstr((pgij[g, i, j] >= dgij[g, i, j] - BigM_local * (1 - zgij[g, i, j])))

    MODEL.addConstrs((auxgRi[g, i, dim] >= Lgi[g, i, dim] - xR[g, dim]) for g, i, dim in auxgRi.keys())
    MODEL.addConstrs((auxgRi[g, i, dim] >= - Lgi[g, i, dim] + xR[g, dim]) for g, i, dim in auxgRi.keys())

    MODEL.addConstrs(
        (auxgRi[g, i, 0] * auxgRi[g, i, 0] + auxgRi[g, i, 1] * auxgRi[g, i, 1] <= dgRi[g, i] * dgRi[g, i] for g, i in
         vgi.keys()), name='v-conic')

    # SmallM = 0
    # BigM = 10000
    MODEL.addConstrs((pgRi[g, i] >= SmallM * vgi[g, i]) for g, i in vgi.keys())
    MODEL.addConstrs((pgRi[g, i] >= dgRi[g, i] - BigM * (1 - vgi[g, i])) for g, i in vgi.keys())

    MODEL.addConstrs((auxRL[g1, g2, dim] >= xR[g1, dim] - xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs((auxRL[g1, g2, dim] >= - xR[g1, dim] + xL[g2, dim]) for g1, g2, dim in auxRL.keys())
    MODEL.addConstrs(
        (auxRL[g1, g2, 0] * auxRL[g1, g2, 0] + auxRL[g1, g2, 1] * auxRL[g1, g2, 1] <= dRL[g1, g2] * dRL[g1, g2] for
         g1, g2 in dRL.keys()), name='RL-conic')

    BigM_z = np.zeros((graphs_number + 2, graphs_number + 2))

    for g1, g2 in z_index:
        if g1 == 0 and g2 < graphs_number + 1:
            BigM_z[g1, g2] = max([np.linalg.norm(origin - v) for v in grafos[g2 - 1].V])
        elif g2 == 0 and g1 < graphs_number + 1:
            BigM_z[g1, g2] = max([np.linalg.norm(origin - v) for v in grafos[g1 - 1].V])
        elif g1 == graphs_number + 1 and g2 > 0:
            BigM_z[g1, g2] = max([np.linalg.norm(destination - v) for v in grafos[g2 - 1].V])
        elif g2 == graphs_number + 1 and g1 > 0:
            BigM_z[g1, g2] = max([np.linalg.norm(destination - v) for v in grafos[g1 - 1].V])
        if g1 > 0 and g2 > 0 and g1 < graphs_number + 1 and g2 < graphs_number + 1:
            BigM_z[g1, g2] = max([np.linalg.norm(u - v) for u in grafos[g1 - 1].V for v in grafos[g2 - 1].V])

    # MODEL.addConstrs(pRL[g1, g2] <= dRL[g1, g2] for g1, g2 in z_index)
    MODEL.addConstrs(pRL[g1, g2] >= SmallM * z[g1, g2] for g1, g2 in z_index)
    MODEL.addConstrs(pRL[g1, g2] >= dRL[g1, g2] - BigM_z[g1, g2] * (1 - z[g1, g2]) for g1, g2 in z_index)

    # Restricciones para formar un tour
    MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index_prima) == 0)
    MODEL.addConstr(gp.quicksum(z[graphs_number + 1, w] for w in T_index_prima) == 0)
    MODEL.addConstrs(gp.quicksum(z[v, w] for w in T_index if w != v) == 1 for v in T_index)
    MODEL.addConstrs(gp.quicksum(z[w, v] for w in T_index if w != v) == 1 for v in T_index)

    # MODEL.addConstr(gp.quicksum(z[v, 0] for v in T_index if v != 0) == 0)
    # MODEL.addConstr(gp.quicksum(z[graphs_number+1, w] for w in T_index_prima) == 0)
    # MODEL.addConstrs(gp.quicksum(z[v , w] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstrs(gp.quicksum(z[w , v] for w in T_index_prima if w != v) == 1 for v in T_index_prima)
    # MODEL.addConstr(gp.quicksum(z[0, w] for w in T_index if w != 0) == 1)
    # MODEL.addConstr(gp.quicksum(z[v, graphs_number+1] for v in T_index if v != graphs_number+1) == 0)

    # Conectividad
    for v in T_index_prima:
        for w in T_index_prima:
            if v != w:
                MODEL.addConstr(len(T_index) - 1 >= (s[v] - s[w]) + len(T_index) * z[v, w])

    # for v in range(1, graphs_number+1):
    #     MODEL.addConstr(s[v] - s[0] + (graphs_number+1 - 2)*z[0, v] <= len(T_index) - 1)
    #
    # for v in range(1, graphs_number+1):
    #     MODEL.addConstr(s[0] - s[v] + (graphs_number+1 - 1)*z[v, 0] <= 0)

    # for v in range(1, graphs_number+1):
    #     MODEL.addConstr(-z[0,v] - s[v] + (graphs_number+1-3)*z[v,0] <= -2, name="LiftedLB(%s)"%v)
    #     MODEL.addConstr(-z[v,0] + s[v] + (graphs_number+1-3)*z[0,v] <= graphs_number+1-2, name="LiftedUB(%s)"%v)

    for v in T_index_prima:
        MODEL.addConstr(s[v] >= 1)
        MODEL.addConstr(s[v] <= len(T_index) - 1)

    MODEL.addConstr(s[0] == 0)
    MODEL.addConstr(s[graphs_number + 1] == graphs_number + 1)

    MODEL.addConstrs((auxLR[g, dim] >= xL[g, dim] - xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, dim] >= - xL[g, dim] + xR[g, dim]) for g, dim in auxLR.keys())
    MODEL.addConstrs((auxLR[g, 0] * auxLR[g, 0] + auxLR[g, 1] * auxLR[g, 1] <= dLR[g] * dLR[g] for g in dLR.keys()),
                     name='LR-conic')

    MODEL.addConstrs((pgLi.sum(g, '*') + pgij.sum(g, '*', '*') + gp.quicksum(
        pgi[g, i] * grafos[g - 1].edges_length[i // 100 - 1, i % 100] for i in grafos[g - 1].edges) + pgRi.sum(g,
                                                                                                                '*')) / drone_speed <=
                     dLR[g] / vC for g in T_index_prima)

    # MODEL.addConstrs(dLR[g] <= 150 for g in dLR.keys())
    # MODEL.addConstrs((pgLi.sum('*', '*', t) +
    #                   pgij.sum(g, '*', '*') +
    #                   ugi.sum(g, '*', '*')*longitudes[g-1] +
    #                   pgRi.sum('*', '*', t))/drone_speed <= dLR[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLR[t]/drone_speed <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pgLi[g, i, t]
    #                   + pgij.sum(g, '*', '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].edges_length[i // 100 - 1, i % 100]
    #                   + pgRi[g, i, t])/drone_speed <= dLR[t]/vC for g, i, t in pgLi.keys())

    # MODEL.addConstr(z[0, 2] + z[1, 3] + z[2, 1] + z[3, 4] == 4)

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhogi[g, i] - landagi[g, i] == maxgi[g, i] - mingi[g, i])
        MODEL.addConstr(maxgi[g, i] + mingi[g, i] == alphagi[g, i])
        if data.alpha:
            MODEL.addConstr(pgi[g, i] >= grafos[g - 1].A[first, second])
        MODEL.addConstr(maxgi[g, i] <= 1 - entrygi[g, i])
        MODEL.addConstr(mingi[g, i] <= entrygi[g, i])
        MODEL.addConstr(
            Rgi[g, i, 0] == rhogi[g, i] * grafos[g - 1].V[first, 0] + (1 - rhogi[g, i]) * grafos[g - 1].V[second, 0])
        MODEL.addConstr(
            Rgi[g, i, 1] == rhogi[g, i] * grafos[g - 1].V[first, 1] + (1 - rhogi[g, i]) * grafos[g - 1].V[second, 1])
        MODEL.addConstr(
            Lgi[g, i, 0] == landagi[g, i] * grafos[g - 1].V[first, 0] + (1 - landagi[g, i]) * grafos[g - 1].V[
                second, 0])
        MODEL.addConstr(
            Lgi[g, i, 1] == landagi[g, i] * grafos[g - 1].V[first, 1] + (1 - landagi[g, i]) * grafos[g - 1].V[
                second, 1])

    if not (data.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(
                pgi[g, i] * grafos[g - 1].edges_length[i // 100 - 1, i % 100] for i in grafos[g - 1].edges) >= grafos[
                                g - 1].alpha * grafos[g - 1].longitud)

    # originen y destinationino
    MODEL.addConstrs(xL[0, dim] == origin[dim] for dim in range(2))
    MODEL.addConstrs(xR[0, dim] == origin[dim] for dim in range(2))

    MODEL.addConstrs(xL[graphs_number + 1, dim] == destination[dim] for dim in range(2))
    MODEL.addConstrs(xR[graphs_number + 1, dim] == destination[dim] for dim in range(2))

    MODEL.update()

    objective = gp.quicksum(pgLi[g, i] + pgRi[g, i] for g, i in pgRi.keys()) + gp.quicksum(
        pgij[g, i, j] for g, i, j in pgij.keys()) + gp.quicksum(
        pgi[g, i] * grafos[g - 1].edges_length[i // 100 - 1, i % 100] for g in T_index_prima for i in
        grafos[g - 1].edges) + gp.quicksum(3 * dLR[g] for g in dLR.keys()) + gp.quicksum(
        3 * pRL[g1, g2] for g1, g2 in dRL.keys())

    # objective = gp.quicksum(1*dLR[g] for g in dLR.keys()) + gp.quicksum(1*pRL[g1, g2] for g1, g2 in dRL.keys()) # + gp.quicksum(1e5*holg[g] for g in holg.keys())

    # objective = gp.quicksum(dRL[t] + dLR[t] for t in T_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 6
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = data.time_limit
    # MODEL.Params.FeasibilityTol = 1e-2

    MODEL.update()
    # MODEL.computeIIS()
    # MODEL.write('casa.ilp')

    MODEL.write('AMDRPG-MTZ.lp')
    MODEL.write('AMDRPG-MTZ.mps')
    MODEL.optimize()

    # MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.initialization:
            try:
                result.append(results[0])
                result.append(results[1])
            except:
                print('El heuristico no ha encontrado initial sol')
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        if data.alpha:
            result.append('Alpha-e')
        else:
            result.append('Alpha-g')

        result.append('MTZ')

        return result

    if MODEL.SolCount == 0:
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.initialization:
            try:
                result.append(results[0])
                result.append(results[1])
            except:
                print('El heuristico no ha encontrado initial sol')
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        if data.alpha:
            result.append('Alpha-e')
        else:
            result.append('Alpha-g')

        result.append('MTZ')

        return result

    MODEL.write('solution_MTZ.sol')

    result.append(MODEL.getAttr('MIPGap'))
    result.append(MODEL.Runtime)
    result.append(MODEL.getAttr('NodeCount'))
    result.append(MODEL.ObjVal)

    if data.initialization:
        try:
            result.append(results[0])
            result.append(results[1])
        except:
            print('El heuristico no ha encontrado initial sol')

    if data.grid:
        result.append('Grid')
    else:
        result.append('Delauney')

    if data.alpha:
        result.append('Alpha-e')
    else:
        result.append('Alpha-g')

    result.append('MTZ')

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
    path = af.subtour(selected_z)
    print(path)

    ind = 0
    path_C = []
    paths_D = []

    for p in path:
        path_C.append([xL[p, 0].X, xL[p, 1].X])
        path_C.append([xR[p, 0].X, xR[p, 1].X])

    for p in path[1:]:
        #    if ind < graphs_number:
        if ind < graphs_number:
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

    # path_C.append([xLt[graphs_number+1, 0].X, xLt[graphs_number+1, 1].X])
    fig, ax = plt.subplots()
    plt.axis([0, 100, 0, 100])

    for g, i in rhogi.keys():
        first = i // 100 - 1
        second = i % 100
        if mugi[g, i].X > 0.5:
            plt.plot(Rgi[g, i, 0].X, Rgi[g, i, 1].X, 'kD', markersize=5, color='orange')
            # ax.annotate("$R^{{({0}, {1})_{2}}}$".format(first, second, g), xy = (Rgi[g, i, 0].X, Rgi[g, i, 1].X))
            plt.plot(Lgi[g, i, 0].X, Lgi[g, i, 1].X, 'kD', markersize=5, color='orange')
            # if np.linalg.norm(np.array([Rgi[g, i, 0].X, Rgi[g, i, 1].X]) - np.array([Lgi[g, i, 0].X, Lgi[g, i, 1].X])) > 8:
            ax.annotate("$L^{{({0}, {1})_{2}}}$".format(first, second, g), xy=(Lgi[g, i, 0].X, Lgi[g, i, 1].X),
                        fontsize=11)
        if ugi[g, i].X > 0.5:
            ax.annotate("$R^{{({0}, {1})_{2}}}$".format(first, second, g), xy=(Rgi[g, i, 0].X, Rgi[g, i, 1].X),
                        fontsize=11)

    #
    for p, i in zip(path, range(len(path))):
        # path_C.append([xL[t, 0].X, xL[t, 1].X])
        # path_C.append([xR[t, 0].X, xR[t, 1].X])
        plt.plot(xL[p, 0].X, xL[p, 1].X, 'ko', alpha=1, markersize=30, color='black', mfc='white')
        ax.annotate("$x_L^{0}$".format(i), xy=(xL[p, 0].X - 0.5, xL[p, 1].X - 0.5), fontsize=11)
        if i > 0 and i < graphs_number + 1:
            plt.plot(xR[p, 0].X, xR[p, 1].X, 'ko', markersize=30, color='black', mfc='white')
            ax.annotate("$x_R^{0}$".format(i), xy=(xR[p, 0].X - 0.5, xR[p, 1].X - 0.5), fontsize=11)

    ax.add_artist(Polygon(path_C, fill=False, closed=False, animated=False, lw=2,
                          linestyle='-', alpha=1, color='black'))

    for pathd in paths_D:
        ax.add_artist(Polygon(pathd, fill=False, closed=False, lw=2,
                              animated=False, alpha=1, color='red'))
    #
    # ax.add_artist(Polygon(path_D, fill=False, animated=False,
    #               linestyle='dotted', alpha=1, color='red'))

    for g in range(graphs_number):
        grafo = grafos[g]
        centroide = np.mean(grafo.V, axis=0)
        nx.draw(grafo.G, grafo.pos, node_size=20, width=0.5,
                node_color='blue', alpha=1, edge_color='blue')
        ax.annotate('$\\alpha_{0} = {1:0.2f}$'.format(g + 1, grafo.alpha), xy=(centroide[0] + 5, centroide[1] + 10),
                    fontsize=12)

    plt.savefig('PDMTZ.png')

    plt.show()

    print(result)
    return result

# PDMTZ(data)
