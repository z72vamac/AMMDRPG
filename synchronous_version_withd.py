# Incluimos primero los paquetes
import gurobipy as gp
import networkx as nx
from gurobipy import GRB
from matplotlib.patches import Polygon

import bigM_estimation as eM
from neighbourhood import *
from heuristic import heuristic


# np.random.seed(4)
#
# lista = list(4*np.ones(3, np.int))
# graphs_number = len(lista)
# data = Data([], m=graphs_number, grid = True, time_limit=150, alpha = True,
#              initialization=True,
#              show=True,
#              time_endurance = 100,
#              seed=2)
#
# data.generate_grid()
#
#
#
# data.generate_graphs(lista)

def SYNCHRONOUS(data):  # , vals_xL, vals_xR):

    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            if model.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                # creates new model attribute '_startobjval'
                model._startobjval = model.cbGet(GRB.Callback.MIPSOL_OBJ)

    graphs = data.graphs_numberostrar_data()

    result = []

    graphs_number = data.graphs_number
    fleet_size = data.fleet_size
    scale = data.scale

    print('SYNCHRONOUS VERSION. Settings:  \n')

    print('Number of graphs: ' + str(data.graphs_number))
    print('Number of drones: ' + str(data.fleet_size))
    print('time_endurance: ' + str(data.time_endurance))
    print('Speed of Mothership: ' + str(data.truck_speed))
    print('Speed of Drone: ' + str(data.drone_speed) + '\n')

    T_index = range(data.graphs_number + 2)
    T_index_prima = range(1, data.graphs_number + 1)
    T_index_primaprima = range(data.graphs_number + 1)
    D_index = range(fleet_size)

    time_endurance = data.time_endurance

    # Creamos el modelo8
    MODEL = gp.Model("PD-Stages")

    # Variables que modelan las distancias
    # Variable binaria uigtd = 1 si en la etapa t entramos por el segmento sig
    uigtd_index = []
    holgtd_index = []

    for g in T_index_prima:
        for i in graphs[g - 1].edges:
            for t in T_index_prima:
                for d in D_index:
                    uigtd_index.append((i, g, t, d))

    for g in T_index_prima:
        for t in T_index_prima:
            for d in D_index:
                holgtd_index.append((g, t, d))

    # holg = MODEL.addVars(holgtd_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'holgtd')

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

    # Variable binaria zigjg = 1 si voy del segmento i al segmento j del graph g.
    zigjg_index = []
    sig_index = []

    for g in T_index_prima:
        for i in graphs[g - 1].edges:
            sig_index.append((i, g))
            for j in graphs[g - 1].edges:
                if i != j:
                    zigjg_index.append((i, j, g))

    zigjg = MODEL.addVars(zigjg_index, vtype=GRB.BINARY, name='zigjg')
    sig = MODEL.addVars(sig_index, vtype=GRB.CONTINUOUS, lb=0, name='sig')

    # Variable continua no negativa digjg que indica la distancia entre los segmentos i j en el graph g.
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

    # Variable continua no negativa dLRt que indica la distancia que recorre el cami�n en la etapa t mientras el dron se mueve
    dLRt_index = T_index

    dLRt = MODEL.addVars(dLRt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLRt')
    difLRt = MODEL.addVars(dLRt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLRt')

    betat = MODEL.addVars(T_index, vtype=GRB.BINARY, lb=0, ub=1, name='betat')
    # deltat = MODEL.addVars(T_index, vtype = GRB.CONTINUOUS, lb = 0, ub = 1, name = 'deltat')
    # zetat = MODEL.addVars(T_index, vtype = GRB.CONTINUOUS, lb = 0, name = 'zetat')

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
        for i in graphs[g - 1].edges:
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
    minig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='minig')
    maxig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='maxig')
    entryig = MODEL.addVars(rhoig_index, vtype=GRB.BINARY, name='entryig')
    muig = MODEL.addVars(rhoig_index, vtype=GRB.BINARY, name='muig')
    pig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='pig')
    alphaig = MODEL.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alphaig')

    MODEL.update()

    if data.initialization:

        hola = heuristic(data)

        if hola != None:
            uigtd_sol = hola[0]
            vigtd_sol = hola[1]
            z_sol = hola[2]
            heuristic_time = hola[3]
            # uigtd_sol, vigtd_sol, z_sol, heuristic_time = heuristic(data)

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
        # for g in T_index_prima:
        # MODEL.read('./case_study/graph' + str(g) + '.sol')
        # for i, g, t, d in vigtd_sol:
        # vigtd[i, g, t, d].start = 1
        #
    # En cada etapa hay que visitar/salir un segmento de un graph
    MODEL.addConstrs(uigtd.sum('*', '*', t, d) <= 1 for t in T_index_prima for d in D_index)
    MODEL.addConstrs(vigtd.sum('*', '*', t, d) <= 1 for t in T_index_prima for d in D_index)

    # # Para cada graph g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs(uigtd.sum('*', g, '*', '*') == 1 for g in T_index_prima)
    MODEL.addConstrs(vigtd.sum('*', g, '*', '*') == 1 for g in T_index_prima)

    # VI-1
    MODEL.addConstrs(betat[t] <= betat[t + 1] for t in T_index_prima)

    # VI-2
    MODEL.addConstrs(gp.quicksum(uigtd[i, g, t1, d] for i, g, t1, d in uigtd.keys() if t1 < t) >= graphs_number * betat[t] for t in
                     T_index_prima)

    # VI-3
    MODEL.addConstrs(
        gp.quicksum(uigtd[i, g, t1, d] for i, g, t1, d in uigtd.keys() if t1 == t) >= 1 - betat[t] for t in T_index)

    # MODEL.addConstrs(uigtd.sum('*', i, '*') == 1 for i in range(graphs_number))
    # MODEL.addConstrs(vigtd.sum('*', i, '*') == 1 for g in range(graphs_number))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al graph y como salida del graph
    MODEL.addConstrs(muig[i, g] - uigtd.sum(i, g, '*', '*') == zigjg.sum('*', i, g) for i, g in rhoig.keys())
    MODEL.addConstrs(muig[i, g] - vigtd.sum(i, g, '*', '*') == zigjg.sum(i, '*', g) for i, g in rhoig.keys())

    MODEL.addConstrs(
        uigtd.sum('*', g, t, d) - vigtd.sum('*', g, t, d) == 0 for t in T_index_prima for g in T_index_prima for d in
        D_index)

    # MODEL.addConstrs(uigtd[i, g, t, d] == vgi)
    # MODEL.addConstrs((uigtd.sum(i, g, '*') + zigjg.sum(g, '*', i))
    #                  - (vigtd.sum(i, g, '*') + zigjg.sum(i, g, '*')) == 0 for g in T_index_prima for i in graphs[g-1].edges)

    MODEL.addConstrs(pig[i, g] >= muig[i, g] + alphaig[i, g] - 1 for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= muig[i, g] for i, g in rhoig.keys())
    MODEL.addConstrs(pig[i, g] <= alphaig[i, g] for i, g in rhoig.keys())

    # MODEL.addConstr(uigtd[0, 101, 0] == 0)
    # MODEL.addConstr(uigtd[0, 101, 1] == 0)

    # Eliminaci�n de subtours
    for g in T_index_prima:
        for i in graphs[g - 1].edges[0:]:
            for j in graphs[g - 1].edges[0:]:
                if i != j:
                    MODEL.addConstr(
                        graphs[g - 1].edges_number - 1 >= (sig[i, g] - sig[j, g]) + graphs[g - 1].edges_number * zigjg[
                            i, j, g])

    # for g in range(graphs_number):
    #     MODEL.addConstr(sig[g, graphs[g].edges[0]] == 0)

    for g in T_index_prima:
        for i in graphs[g - 1].edges[0:]:
            MODEL.addConstr(sig[i, g] >= 0)
            MODEL.addConstr(sig[i, g] <= graphs[g - 1].edges_number - 1)

    MODEL.addConstrs(
        uigtd[i, g, t, d1] <= uigtd.sum('*', '*', '*', d2) for i, g, t, d1 in uigtd.keys() for d2 in D_index if d1 > d2)
    MODEL.addConstrs(
        vigtd[i, g, t, d1] <= vigtd.sum('*', '*', '*', d2) for i, g, t, d1 in vigtd.keys() for d2 in D_index if d1 > d2)

    # Restricciones de distancias y producto
    MODEL.addConstrs((difLigtd[i, g, t, d, dim]/scale >= xLt[t, dim] - Rig[i, g, dim]) for i, g, t, d, dim in difLigtd.keys())
    MODEL.addConstrs((difLigtd[i, g, t, d, dim]/scale >= - xLt[t, dim] + Rig[i, g, dim]) for i, g, t, d, dim in difLigtd.keys())

    MODEL.addConstrs((difLigtd[i, g, t, d, 0] * difLigtd[i, g, t, d, 0] + difLigtd[i, g, t, d, 1] * difLigtd[
        i, g, t, d, 1] <= dLigtd[i, g, t, d] * dLigtd[i, g, t, d] for i, g, t, d in uigtd.keys()), name='difLigtd')

    SmallM = 0
    BigM = 2 * data.drone_speed * data.time_endurance
    # BigM = 0
    # for g in T_index_prima:
    # for h in T_index_prima:
    # BigM = max(max([np.linalg.norm(v - w) for v in graphs[g-1].V for w in graphs[h-1].V]), BigM)

    # MODEL.addConstr(uigtd[303, 1, 1, 0] == 1)
    # MODEL.addConstr(uigtd[203, 2, 1, 1] == 1)

    # BigM += 5
    # BigM = max([np.linalg.norm(origin-graphs[g].V) for g in range(graphs_number)])
    MODEL.addConstrs((pLigtd[i, g, t, d] <= BigM * uigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs((pLigtd[i, g, t, d] <= dLigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs((pLigtd[i, g, t, d] >= SmallM * uigtd[i, g, t, d]) for i, g, t, d in uigtd.keys())
    MODEL.addConstrs(
        (pLigtd[i, g, t, d] >= dLigtd[i, g, t, d] - BigM * (1 - uigtd[i, g, t, d])) for i, g, t, d in uigtd.keys())

    MODEL.addConstrs((difigjg[i, j, g, dim]/scale >= Lig[i, g, dim] - Rig[j, g, dim]) for i, j, g, dim in difigjg.keys())
    MODEL.addConstrs((difigjg[i, j, g, dim]/scale >= - Lig[i, g, dim] + Rig[j, g, dim]) for i, j, g, dim in difigjg.keys())

    MODEL.addConstrs((difigjg[i, j, g, 0] * difigjg[i, j, g, 0] + difigjg[i, j, g, 1] * difigjg[i, j, g, 1] <= digjg[
        i, j, g] * digjg[i, j, g] for i, j, g in digjg.keys()), name='difigjg')

    for i, j, g in zigjg.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Polygonal(np.array([[graphs[g - 1].V[first_i, 0], graphs[g - 1].V[first_i, 1]], [
            graphs[g - 1].V[second_i, 0], graphs[g - 1].V[second_i, 1]]]), graphs[g - 1].A[first_i, second_i])
        segm_j = Polygonal(np.array([[graphs[g - 1].V[first_j, 0], graphs[g - 1].V[first_j, 1]], [
            graphs[g - 1].V[second_j, 0], graphs[g - 1].V[second_j, 1]]]), graphs[g - 1].A[first_j, second_j])

        BigM_local = eM.estimate_local_U(segm_i, segm_j)
        SmallM_local = eM.estimate_local_L(segm_i, segm_j)
        MODEL.addConstr((pigjg[i, j, g] <= BigM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] <= digjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= SmallM_local * zigjg[i, j, g]))
        MODEL.addConstr((pigjg[i, j, g] >= digjg[i, j, g] - BigM_local * (1 - zigjg[i, j, g])))

    MODEL.addConstrs((difRigtd[i, g, t, d, dim]/scale >= Lig[i, g, dim] - xRt[t, dim]) for i, g, t, d, dim in difRigtd.keys())
    MODEL.addConstrs((difRigtd[i, g, t, d, dim]/scale >= - Lig[i, g, dim] + xRt[t, dim]) for i, g, t, d, dim in difRigtd.keys())

    MODEL.addConstrs((difRigtd[i, g, t, d, 0] * difRigtd[i, g, t, d, 0] + difRigtd[i, g, t, d, 1] * difRigtd[
        i, g, t, d, 1] <= dRigtd[i, g, t, d] * dRigtd[i, g, t, d] for i, g, t, d in vigtd.keys()), name='difRigtd')

    # SmallM = 0
    # BigM = 10000
    MODEL.addConstrs((pRigtd[i, g, t, d] <= BigM * vigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs((pRigtd[i, g, t, d] <= dRigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs((pRigtd[i, g, t, d] >= SmallM * vigtd[i, g, t, d]) for i, g, t, d in vigtd.keys())
    MODEL.addConstrs(
        (pRigtd[i, g, t, d] >= dRigtd[i, g, t, d] - BigM * (1 - vigtd[i, g, t, d])) for i, g, t, d in vigtd.keys())

    MODEL.addConstrs((difRLt[t, dim]/scale >= xRt[t, dim] - xLt[t + 1, dim] for t in dRLt.keys() for dim in range(2)), name='error')
    MODEL.addConstrs((difRLt[t, dim]/scale >= - xRt[t, dim] + xLt[t + 1, dim] for t in dRLt.keys() for dim in range(2)), name='error2')
    MODEL.addConstrs(
        (difRLt[t, 0] * difRLt[t, 0] + difRLt[t, 1] * difRLt[t, 1] <= dRLt[t] * dRLt[t] for t in dRLt.keys()),
        name='difRLt')

    MODEL.addConstrs((difLRt[t, dim]/scale >= xLt[t, dim] - xRt[t, dim]) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, dim]/scale >= - xLt[t, dim] + xRt[t, dim]) for t, dim in difLRt.keys())
    MODEL.addConstrs((difLRt[t, 0] * difLRt[t, 0] + difLRt[t, 1] * difLRt[t, 1] <= dLRt[t] * dLRt[t] for t in dLRt.keys()), name='difLRt')

    # longitudes = []
    # for g in T_index_prima:
    #     longitudes.append(sum([graphs[g-1].A[i // 100 - 1, i % 100]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges]))

    BigM = 1e5
    BigM = data.time_endurance

    MODEL.addConstrs((gp.quicksum(pLigtd[i, g, t, d] for i in graphs[g - 1].edges) + pigjg.sum('*', '*',
                                                                                                 g) + gp.quicksum(
        pig[i, g] * graphs[g - 1].edges_length[i // 100 - 1, i % 100] * scale for i in graphs[g - 1].edges) + gp.quicksum(
        pRigtd[i, g, t, d] for i in graphs[g - 1].edges)) / data.drone_speed <= dLRt[t] / data.truck_speed + BigM * (
                                 1 - gp.quicksum(uigtd[i, g, t, d] for i in graphs[g - 1].edges)) for t in
                     T_index_prima for g in T_index_prima for d in D_index)
    MODEL.addConstrs(dLRt[t] / data.truck_speed <= data.time_endurance for t in T_index_prima)

    # MODEL.addConstrs((gp.quicksum(pLigtd[i, g, t, d] for i in graphs[g-1].edges) + pigjg.sum('*', '*', g) +  gp.quicksum(pig[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges) + gp.quicksum(pRigtd[i, g, t, d] for i in graphs[g-1].edges))/data.drone_speed <=  zetat[t] + BigM*(1- gp.quicksum(uigtd[i, g, t, d] for i in graphs[g-1].edges)) for t in T_index_prima for g in T_index_prima for d in D_index)

    # MODEL.addConstrs(2*zetat[t]*deltat[t]*data.truck_speed >= dLRt[t]*dLRt[t] for t in T_index_prima)
    # MODEL.addConstrs(dLRt[t] >= deltat[t]*data.truck_speed*zetat[t] for t in T_index_prima)
    # MODEL.addConstrs(zetat[t] <= data.time_endurance for t in T_index_prima)

    # MODEL.addConstrs(zigjg[i, j, g] <= uigtd.sum(g, '*', '*') for i, j, g in zigjg.keys())
    # MODEL.addConstrs(muig[i, g] <= uigtd.sum(i, g, '*') for i, g in muig.keys())

    # MODEL.addConstrs((pLigtd.sum('*', '*', t) +
    #                   pigjg.sum(g, '*', '*') +
    #                   uigtd.sum(g, '*', '*')*longitudes[g-1] +
    #                   pRigtd.sum('*', '*', t))/drone_speed <= dLRt[t]/vC for t in T_index_prima for g in T_index_prima)
    # MODEL.addConstrs((dLRt[t]/drone_speed <= 50) for t in T_index_prima)
    # MODEL.addConstrs((pLigtd[i, g, t, d]
    #                   + pigjg.sum(g, '*', '*') + graphs[g-1].A[i // 100 - 1, i % 100]*graphs[g-1].edges_length[i // 100 - 1, i % 100]
    #                   + pRigtd[i, g, t, d])/drone_speed <= dLRt[t]/vC for i, g, t, d in pLigtd.keys())

    for i, g in rhoig.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhoig[i, g] - landaig[i, g] == maxig[i, g] - minig[i, g])
        MODEL.addConstr(maxig[i, g] + minig[i, g] == alphaig[i, g])
        if data.alpha:
            MODEL.addConstr(pig[i, g] >= graphs[g - 1].A[first, second])
        MODEL.addConstr(maxig[i, g] <= 1 - entryig[i, g])
        MODEL.addConstr(minig[i, g] <= entryig[i, g])
        MODEL.addConstr(
            Rig[i, g, 0] == rhoig[i, g] * graphs[g - 1].V[first, 0] + (1 - rhoig[i, g]) * graphs[g - 1].V[second, 0])
        MODEL.addConstr(
            Rig[i, g, 1] == rhoig[i, g] * graphs[g - 1].V[first, 1] + (1 - rhoig[i, g]) * graphs[g - 1].V[second, 1])
        MODEL.addConstr(
            Lig[i, g, 0] == landaig[i, g] * graphs[g - 1].V[first, 0] + (1 - landaig[i, g]) * graphs[g - 1].V[
                second, 0])
        MODEL.addConstr(
            Lig[i, g, 1] == landaig[i, g] * graphs[g - 1].V[first, 1] + (1 - landaig[i, g]) * graphs[g - 1].V[
                second, 1])

    if not (data.alpha):
        for g in T_index_prima:
            MODEL.addConstr(gp.quicksum(
                pig[i, g] * graphs[g - 1].edges_length[i // 100 - 1, i % 100] * scale for i in graphs[g - 1].edges) == graphs[
                                g - 1].alpha * graphs[g - 1].length)

    # [0, 2, 1, 3, 4]
    # MODEL.addConstr(uigtd[2, 102, 1] >= 0.5)
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

    # originen y destinationino
    MODEL.addConstrs(xLt[0, dim] == data.origin[dim] for dim in range(2))
    MODEL.addConstrs(xRt[0, dim] == data.origin[dim] for dim in range(2))

    MODEL.addConstrs(xLt[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))
    MODEL.addConstrs(xRt[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))

    # print(vals_xL)
    # for g in T_index_prima:
    #     MODEL.addConstrs(xLt[g, dim] == vals_xL[g][dim] for dim in range(2))
    #     MODEL.addConstrs(xRt[g, dim] == vals_xR[g][dim] for dim in range(2))

    MODEL.update()

    # objective = gp.quicksum(pLigtd[i, g, t, d] + pRigtd[i, g, t, d] for i, g, t, d in pRigtd.keys()) + gp.quicksum(pigjg[i, j, g] for i, j, g in pigjg.keys()) + gp.quicksum(pig[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for g in T_index_prima for i in graphs[g-1].edges) + gp.quicksum(3*dLRt[t] for t in dLRt.keys()) + gp.quicksum(3*dRLt[t] for t in dRLt.keys())

    # objective = gp.quicksum(1*dRLt[g1] for g1 in dRLt.keys()) + gp.quicksum(zetat[t] for t in zetat.keys()) + gp.quicksum(1*dLRt[g] for g in dLRt.keys())

    objective = gp.quicksum(1 * dRLt[g1] for g1 in dRLt.keys()) + gp.quicksum(1 * dLRt[g] for g in dLRt.keys())

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 6
    # MODEL.Params.FeasibilityTol = 1e-3
    # MODEL.Params.NonConvex = 2
    # MODEL.Params.MIPFocus = 3
    MODEL.Params.timeLimit = data.time_limit

    MODEL.update()

    MODEL.write('./case_study/patios-{0}-{1}-{2}.lp'.format(data.fleet_size, data.time_endurance, data.drone_speed))
    # MODEL.write('./AMMDRPGST-initialization.mps')

    if data.initialization:
        MODEL.optimize(callback)
    else:
        MODEL.optimize()

    # MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return result

    if MODEL.SolCount == 0:
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.grid:
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

    if data.initialization:
        result.append(heuristic_time)
        result.append(MODEL._startobjval)

    # if data.grid:
    # result.append('Grid')
    # else:
    # result.append('Delauney')

    # result.append('Stages')

    MODEL.write('./final_solution.sol')
    # MODEL.write('solution_patios.sol')

    # print(xRt)
    # print(xLt)
    # print('Selected_u')
    vals_u = MODEL.getAttr('x', uigtd)
    selected_u = gp.tuplelist((i, g, t, d) for i, g, t, d in vals_u.keys() if vals_u[i, g, t, d] > 0.5)
    print(selected_u)
    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', zigjg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    # print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', vigtd)
    selected_v = gp.tuplelist((i, g, t, d) for i, g, t, d in vals_v.keys() if vals_v[i, g, t, d] > 0.5)
    # print(selected_v)
    #
    # path = []
    # path.append(0)

    print('Total time: ' + str(MODEL.ObjVal / data.truck_speed))

    distance = 0

    for t in T_index_prima:
        distance += np.linalg.norm(np.array([xLt[t, 0].X, xLt[t, 1].X]) - np.array([xRt[t, 0].X, xRt[t, 1].X]))

    for t in T_index_primaprima:
        distance += np.linalg.norm(np.array([xRt[t, 0].X, xRt[t, 1].X]) - np.array([xLt[t, 0].X, xLt[t, 1].X]))

    print('Time operating: ' + str(distance / data.truck_speed))
    print('Time waiting: ' + str(MODEL.ObjVal - distance / data.truck_speed))

    # path_C.append(origin)
    path_C = []
    paths_D = []

    path = []

    path_C.append([xLt[0, 0].X, xLt[0, 1].X])
    path.append(0)
    for t in T_index:
        if len(selected_u.select('*', '*', t, '*')) > 0:
            path.append(t)
            path_C.append([xLt[t, 0].X, xLt[t, 1].X])
        if len(selected_v.select('*', '*', t, '*')) > 0:
            path.append(t)
            path_C.append([xRt[t, 0].X, xRt[t, 1].X])

    path_C.append([xLt[graphs_number + 1, 0].X, xLt[graphs_number + 1, 1].X])
    path.append(graphs_number + 1)

    for t in path:
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
                        index_i = j1
                        path_D.append([Rig[index_i, index_g, 0].X, Rig[index_i, index_g, 1].X])
                        path_D.append([Lig[index_i, index_g, 0].X, Lig[index_i, index_g, 1].X])

            path_D.append([xRt[t1, 0].X, xRt[t1, 1].X])

            paths_D.append((path_D, d))

    # print(paths_D)
    log = False

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

        plt.plot(xLt[0, 0].X, xLt[0, 1].X, 's', alpha=1, markersize=10, color='black')
        plt.plot(xLt[graphs_number + 1, 0].X, xLt[graphs_number + 1, 1].X, 's', alpha=1, markersize=10, color='black')

        if logue:
            for t in path:
                # path_C.append([xLt[t, 0].X, xLt[t, 1].X])
                # path_C.append([xRt[t, 0].X, xRt[t, 1].X])
                # plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha = 1, markersize=5, color='black')
                plt.plot(xLt[1, 0].X, xLt[1, 1].X, 'o', alpha=1, markersize=10, color='red')

                if t == 0:
                    plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("origin", xy=(xLt[t, 0].X - 2, xLt[t, 1].X + 1), fontsize=15)
                if t > 0 and t < graphs_number + 1:
                    plt.plot(xRt[t, 0].X, xRt[t, 1].X, 'o', alpha=1, markersize=10, color='red')
                    ax.annotate("$x_R^{t}$".format(t=t), xy=(xRt[t, 0].X + 1.5, xRt[t, 1].X), fontsize=15)
                    ax.annotate("$x_L^{t}$".format(t=t), xy=(xLt[t, 0].X - 3, xLt[t, 1].X), fontsize=15)
                if t == graphs_number + 1:
                    plt.plot(xLt[t, 0].X, xLt[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("destination", xy=(xLt[t, 0].X + 0.5, xLt[t, 1].X + 1), fontsize=15)

            ax.add_artist(Polygon(path_C, fill=False, animated=False, closed=False,
                                  linestyle='-', lw=2, alpha=1, color='black'))
            #
            for t in T_index_prima:

                n_drones = len(selected_u.select('*', '*', t, '*'))

                if n_drones > 0:
                    for drone in range(n_drones):
                        edge = selected_u.select('*', '*', t, '*')[drone][0]
                        g = selected_u.select('*', '*', t, '*')[drone][1]

                        ax.arrow(xLt[t, 0].X, xLt[t, 1].X, Rig[edge, g, 0].X - xLt[t, 0].X,
                                 Rig[edge, g, 1].X - xLt[t, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=colors[drone])

                        for e1, e2, g in selected_z.select('*', '*', g):
                            if pigjg[e1, e2, g].X >= 0.05:
                                ax.arrow(Lig[e1, g, 0].X, Lig[e1, g, 1].X, Rig[e2, g, 0].X - Lig[e1, g, 0].X,
                                         Rig[e2, g, 1].X - Lig[e1, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        for e in graphs[g - 1].edges:
                            if muig[e, g].X >= 0.5 and pig[e, g].X >= 0.01:
                                ax.arrow(Rig[e, g, 0].X, Rig[e, g, 1].X, Lig[e, g, 0].X - Rig[e, g, 0].X,
                                         Lig[e, g, 1].X - Rig[e, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        edge = selected_v.select('*', '*', t, '*')[drone][0]
                        g = selected_v.select('*', '*', t, '*')[drone][1]

                        ax.arrow(Lig[edge, g, 0].X, Lig[edge, g, 1].X, xRt[t, 0].X - Lig[edge, g, 0].X,
                                 xRt[t, 1].X - Lig[edge, g, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=colors[drone])

            for p in range(len(path_C) - 1):
                ax.arrow(path_C[p][0], path_C[p][1], path_C[p + 1][0] - path_C[p][0], path_C[p + 1][1] - path_C[p][1],
                         width=0.3, head_width=0.7, length_includes_head=True, color='black')

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
        # graph = graphs[g-1]
        # centroide = np.mean(graph.V, axis = 0)
        # nx.draw(graph.G, graph.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
        # ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
        # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'white', font_size=9)

        # for g in T_index_prima:
        #     graph = graphs[g-1]
        #     centroide = np.mean(graph.V, axis = 0)
        #     nx.draw(graph.G, graph.pos, node_size=90, width = 2,
        #             node_color='blue', alpha=1, edge_color='blue')
        # ax.annotate('$\\alpha_{0} = {1:0.2f}$'.format(g, graph.alpha), xy = (centroide[0]+5, centroide[1]+10), fontsize = 12)

        # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'white', font_size=9)

        for g in graphs:
            nx.draw(g.G, g.pos, node_size=10, width=1,
                    node_color='blue', alpha=1, edge_color='blue')

        plt.savefig(
            'Synchronous{b}-{c}-{d}-{e}.png'.format(b=data.graphs_number, c=int(data.alpha), d=data.time_endurance, e=data.fleet_size))
        plt.show()

        import tikzplotlib
        import matplotlib

        matplotlib.rcParams['axes.unicode_minus'] = False

        tikzplotlib.save('synchronous.tex', encoding='utf-8')

        # plt.show()
        # plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = data.graphs_number, c = int(data.alpha), d = data.time_endurance, e = data.fleet_size))
        # plt.savefig('PDST-Sinc2.png')

        # plt.savefig('Prueba.png')

        # plt.show()
    print(result)
    print()

    return result
    # plt.show()

# AMMDRPGST(data)
