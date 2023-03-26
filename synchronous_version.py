# Package import
import gurobipy as gp
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

def synchronous(data):  # , vals_xL, vals_xR):

    def _callback(m, where):
        if where == GRB.Callback.MIPSOL:
            if m.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                # creates new model attribute '_startobjval'
                m._startobjval = m.cbGet(GRB.Callback.MIPSOL_OBJ)
                m._starttime = m.cbGet(GRB.Callback.RUNTIME)

                m.terminate()

    grafos = data.graphs_numberostrar_data()

    n_g = data.graphs_number
    n_d = data.fleet_size

    heuristic_time = 0

    print('SYNCHRONOUS VERSION. Settings:  \n')

    print('Number of graphs: ' + str(data.graphs_number))
    print('Number of drones: ' + str(data.fleet_size))
    print('time_endurance: ' + str(data.time_endurance))
    print('Speed of Mothership: ' + str(data.truck_speed))
    print('Speed of Drone: ' + str(data.drone_speed) + '\n')

    t_index = range(data.graphs_number + 2)
    t_index_prima = range(1, data.graphs_number + 1)
    t_index_primaprima = range(data.graphs_number + 1)

    # Creamos el modelo8
    model = gp.Model("PD-Stages")

    # Variables que modelan las distancias
    # Variable binaria uigt = 1 si en la etapa t entramos por el segmento sig
    uigt_index = []

    for g in t_index_prima:
        for i in grafos[g - 1].edges:
            for t in t_index_prima:
                uigt_index.append((i, g, t))

    uigt = model.addVars(uigt_index, vtype=GRB.BINARY, name='uigt')

    # Variable continua no negativa d_ligt que indica la distancia desde el punto de lanzamiento hasta el segmento
    # sig.
    d_ligt_index = uigt_index

    d_ligt = model.addVars(d_ligt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='d_ligt')
    dif_ligt = model.addVars(d_ligt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_ligt')

    # Variable continua no negativa p_ligt = uigt * d_ligt
    p_ligt_index = uigt_index

    p_ligt = model.addVars(p_ligt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='p_ligt')

    # Variable binaria vigt = 1 si en la etapa t salimos por el segmento sig
    vigt_index = uigt_index

    vigt = model.addVars(vigt_index, vtype=GRB.BINARY, name='vigt')

    # Variable continua no negativa d_rigt que indica la distancia desde el punto de salida del segmento sig hasta el
    # punto de recogida del camion
    d_rigt_index = uigt_index

    d_rigt = model.addVars(d_rigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='d_rigt')
    dif_rigt = model.addVars(d_rigt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_rigt')

    # Variable continua no negativa p_rigt = vigt * d_rigt
    p_rigt_index = uigt_index

    p_rigt = model.addVars(p_rigt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='p_rigt')

    # Variable binaria zigjg = 1 si voy del segmento i al segmento j del grafo g.
    zigjg_index = []
    sig_index = []

    for g in t_index_prima:
        for i in grafos[g - 1].edges:
            sig_index.append((i, g))
            for j in grafos[g - 1].edges:
                if i != j:
                    zigjg_index.append((i, j, g))

    zigjg = model.addVars(zigjg_index, vtype=GRB.BINARY, name='zigjg')
    sig = model.addVars(sig_index, vtype=GRB.CONTINUOUS, lb=0, name='sig')

    # Variable continua no negativa digjg que indica la distancia entre los segmentos i j en el grafo g.
    digjg_index = zigjg_index

    digjg = model.addVars(digjg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='digjg')
    difigjg = model.addVars(digjg_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difigjg')

    # Variable continua no negativa pigjg = zigjg * digjg
    pigjg_index = zigjg_index

    pigjg = model.addVars(pigjg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pigjg')

    # Variable continua no negativa d_r_lt que indica la distancia entre el punto de recogida en la etapa t y el
    # punto de salida para la etapa t+1
    d_r_lt_index = t_index_primaprima

    d_r_lt = model.addVars(d_r_lt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='d_r_lt')
    dif_r_lt = model.addVars(d_r_lt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_r_lt')

    # Variable continua no negativa d_l_rt que indica la distancia que recorre el camión en la etapa t mientras el
    # dron se mueve
    d_l_rt_index = t_index

    d_l_rt = model.addVars(d_l_rt_index, vtype=GRB.CONTINUOUS, lb=0.0, name='d_l_rt')
    dif_l_rt = model.addVars(d_l_rt_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_l_rt')

    betat = model.addVars(t_index, vtype=GRB.BINARY, lb=0, ub=1, name='betat')

    # Variables que modelan los puntos de entrada o recogida
    # x_lt: punto de salida del dron del camion en la etapa t
    x_lt_index = []

    for t in t_index:
        for dim in range(2):
            x_lt_index.append((t, dim))

    x_lt = model.addVars(x_lt_index, vtype=GRB.CONTINUOUS, name='x_lt')

    # x_rt: punto de recogida del dron del camion en la etapa t
    x_rt_index = []

    for t in t_index:
        for dim in range(2):
            x_rt_index.append((t, dim))

    x_rt = model.addVars(x_rt_index, vtype=GRB.CONTINUOUS, name='x_rt')

    timet_d = model.addVars(t_index_prima, vtype=GRB.CONTINUOUS, lb=0.0, name='timet_d')
    timet_m = model.addVars(t_index_prima, vtype=GRB.CONTINUOUS, lb=0.0, name='timet_m')

    # rig: punto de recogida del dron para el segmento sig
    rig_index = []
    rhoig_index = []

    for g in t_index_prima:
        for i in grafos[g - 1].edges:
            rhoig_index.append((i, g))
            for dim in range(2):
                rig_index.append((i, g, dim))

    rig = model.addVars(rig_index, vtype=GRB.CONTINUOUS, name='rig')
    rhoig = model.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rhoig')

    # lig: punto de lanzamiento del dron del segmento sig
    lig_index = rig_index
    landaig_index = rhoig_index

    lig = model.addVars(lig_index, vtype=GRB.CONTINUOUS, name='lig')
    landaig = model.addVars(landaig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landaig')

    # Variables difiliares para modelar el valor absoluto
    minig = model.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='minig')
    maxig = model.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='maxig')
    entryig = model.addVars(rhoig_index, vtype=GRB.BINARY, name='entryig')
    muig = model.addVars(rhoig_index, vtype=GRB.BINARY, name='muig')
    pig = model.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='pig')
    alphaig = model.addVars(rhoig_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alphaig')

    model.update()

    if data.initialization:

        hola = heuristic(data)

        if hola is not None:
            uigt_sol = hola[0]
            vigt_sol = hola[1]
            z_sol = hola[2]
            heuristic_time = hola[3]
            # uigt_sol, vigt_sol, z_sol, heuristic_time = heuristic(data)

            # for i, g, t in uigt_sol:
            # uigt[i, g, t].start = 1
            #

            # my_file = open('./case_study/uigt_keys.txt', "r")
            # content = my_file.read()

            # uigt_sol = ast.literal_eval(content[:-1])

            # model.read('./case_study/uigt.sol')

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
        # for g in t_index_prima:
        # model.read('./case_study/graph' + str(g) + '.sol')
        # for i, g, t in vigt_sol:
        # vigt[i, g, t].start = 1
        #
    # En cada etapa hay que visitar/salir un segmento de un grafo
    model.addConstrs(uigt.sum('*', '*', t) <= n_d for t in t_index_prima)
    model.addConstrs(vigt.sum('*', '*', t) <= n_d for t in t_index_prima)

    # # Para cada grafo g, existe un segmento i y una etapa t donde hay que recoger al dron
    model.addConstrs(uigt.sum('*', g, '*') == 1 for g in t_index_prima)
    model.addConstrs(vigt.sum('*', g, '*') == 1 for g in t_index_prima)

    # VI-1
    model.addConstrs(betat[t] <= betat[t + 1] for t in t_index_prima)

    # VI-2
    model.addConstrs(
        gp.quicksum(uigt[i, g, t1] for i, g, t1 in uigt.keys() if t1 < t) >= n_g * betat[t] for t in t_index_prima)

    # VI-3
    model.addConstrs(
        gp.quicksum(uigt[i, g, t1] for i, g, t1 in uigt.keys() if t1 == t) >= 1 - betat[t] for t in t_index)

    # model.addConstrs(uigt.sum('*', i, '*') == 1 for i in range(n_g))
    # model.addConstrs(vigt.sum('*', i, '*') == 1 for g in range(n_g))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al grafo y como salida
    # del grafo
    model.addConstrs(muig[i, g] - uigt.sum(i, g, '*') == zigjg.sum('*', i, g) for i, g in rhoig.keys())
    model.addConstrs(muig[i, g] - vigt.sum(i, g, '*') == zigjg.sum(i, '*', g) for i, g in rhoig.keys())

    model.addConstrs(uigt.sum('*', g, t) - vigt.sum('*', g, t) == 0 for t in t_index_prima for g in t_index_prima)

    # model.addConstrs(uigt[i, g, t] == vgi) model.addConstrs((uigt.sum(i, g, '*') + zigjg.sum(g, '*',
    # i)) - (vigt.sum(i, g, '*') + zigjg.sum(i, g, '*')) == 0 for g in t_index_prima for i in grafos[g-1].edges)

    model.addConstrs(pig[i, g] >= muig[i, g] + alphaig[i, g] - 1 for i, g in rhoig.keys())
    model.addConstrs(pig[i, g] <= muig[i, g] for i, g in rhoig.keys())
    model.addConstrs(pig[i, g] <= alphaig[i, g] for i, g in rhoig.keys())

    # model.addConstr(uigt[0, 101, 0] == 0)
    # model.addConstr(uigt[0, 101, 1] == 0)

    # Eliminación de subtours
    for g in t_index_prima:
        for i in grafos[g - 1].edges[0:]:
            for j in grafos[g - 1].edges[0:]:
                if i != j:
                    model.addConstr(
                        grafos[g - 1].edges_number - 1 >= (sig[i, g] - sig[j, g]) + grafos[g - 1].edges_number * zigjg[
                            i, j, g])

    # for g in range(n_g):
    #     model.addConstr(sig[g, grafos[g].edges[0]] == 0)

    for g in t_index_prima:
        for i in grafos[g - 1].edges[0:]:
            model.addConstr(sig[i, g] >= 0)
            model.addConstr(sig[i, g] <= grafos[g - 1].edges_number - 1)

    # Restricciones de distancias y producto
    model.addConstrs((dif_ligt[i, g, t, dim] >= x_lt[t, dim] - rig[i, g, dim]) for i, g, t, dim in dif_ligt.keys())
    model.addConstrs((dif_ligt[i, g, t, dim] >= - x_lt[t, dim] + rig[i, g, dim]) for i, g, t, dim in dif_ligt.keys())

    model.addConstrs(
        (dif_ligt[i, g, t, 0] * dif_ligt[i, g, t, 0] + dif_ligt[i, g, t, 1] * dif_ligt[i, g, t, 1] <= d_ligt[
            i, g, t] * d_ligt[i, g, t] for i, g, t in uigt.keys()), name='dif_ligt')

    small_m = 0
    big_m = 1e5
    # big_m = 0
    # for g in t_index_prima:
    # for h in t_index_prima:
    # big_m = max(max([np.linalg.norm(v - w) for v in grafos[g-1].V for w in grafos[h-1].V]), big_m)

    # model.addConstr(uigt[303, 1, 1, 0] == 1)
    # model.addConstr(uigt[203, 2, 1, 1] == 1)

    # big_m += 5
    # big_m = max([np.linalg.norm(origin-grafos[g].V) for g in range(n_g)])
    model.addConstrs((p_ligt[i, g, t] <= big_m * uigt[i, g, t]) for i, g, t in uigt.keys())
    model.addConstrs((p_ligt[i, g, t] <= d_ligt[i, g, t]) for i, g, t in uigt.keys())
    model.addConstrs((p_ligt[i, g, t] >= small_m * uigt[i, g, t]) for i, g, t in uigt.keys())
    model.addConstrs((p_ligt[i, g, t] >= d_ligt[i, g, t] - big_m * (1 - uigt[i, g, t])) for i, g, t in uigt.keys())

    model.addConstrs((difigjg[i, j, g, dim] >= lig[i, g, dim] - rig[j, g, dim]) for i, j, g, dim in difigjg.keys())
    model.addConstrs((difigjg[i, j, g, dim] >= - lig[i, g, dim] + rig[j, g, dim]) for i, j, g, dim in difigjg.keys())

    model.addConstrs((difigjg[i, j, g, 0] * difigjg[i, j, g, 0] + difigjg[i, j, g, 1] * difigjg[i, j, g, 1] <= digjg[
        i, j, g] * digjg[i, j, g] for i, j, g in digjg.keys()), name='difigjg')

    for i, j, g in zigjg.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Polygonal(np.array([[grafos[g - 1].V[first_i, 0], grafos[g - 1].V[first_i, 1]], [
            grafos[g - 1].V[second_i, 0], grafos[g - 1].V[second_i, 1]]]), grafos[g - 1].A[first_i, second_i])
        segm_j = Polygonal(np.array([[grafos[g - 1].V[first_j, 0], grafos[g - 1].V[first_j, 1]], [
            grafos[g - 1].V[second_j, 0], grafos[g - 1].V[second_j, 1]]]), grafos[g - 1].A[first_j, second_j])

        big_m_local = eM.estimate_local_U(segm_i, segm_j)
        small_m_local = eM.estimate_local_L(segm_i, segm_j)
        model.addConstr((pigjg[i, j, g] <= big_m_local * zigjg[i, j, g]))
        model.addConstr((pigjg[i, j, g] <= digjg[i, j, g]))
        model.addConstr((pigjg[i, j, g] >= small_m_local * zigjg[i, j, g]))
        model.addConstr((pigjg[i, j, g] >= digjg[i, j, g] - big_m_local * (1 - zigjg[i, j, g])))

    model.addConstrs((dif_rigt[i, g, t, dim] >= lig[i, g, dim] - x_rt[t, dim]) for i, g, t, dim in dif_rigt.keys())
    model.addConstrs((dif_rigt[i, g, t, dim] >= - lig[i, g, dim] + x_rt[t, dim]) for i, g, t, dim in dif_rigt.keys())

    model.addConstrs(
        (dif_rigt[i, g, t, 0] * dif_rigt[i, g, t, 0] + dif_rigt[i, g, t, 1] * dif_rigt[i, g, t, 1] <= d_rigt[
            i, g, t] * d_rigt[i, g, t] for i, g, t in vigt.keys()), name='dif_rigt')

    # small_m = 0
    # big_m = 10000
    model.addConstrs((p_rigt[i, g, t] <= big_m * vigt[i, g, t]) for i, g, t in vigt.keys())
    model.addConstrs((p_rigt[i, g, t] <= d_rigt[i, g, t]) for i, g, t in vigt.keys())
    model.addConstrs((p_rigt[i, g, t] >= small_m * vigt[i, g, t]) for i, g, t in vigt.keys())
    model.addConstrs((p_rigt[i, g, t] >= d_rigt[i, g, t] - big_m * (1 - vigt[i, g, t])) for i, g, t in vigt.keys())

    model.addConstrs((dif_r_lt[t, dim] >= x_rt[t, dim] - x_lt[t + 1, dim] for t in d_r_lt.keys() for dim in range(2)),
                     name='error')
    model.addConstrs((dif_r_lt[t, dim] >= - x_rt[t, dim] + x_lt[t + 1, dim] for t in d_r_lt.keys() for dim in range(2)),
                     name='error2')
    model.addConstrs(
        (dif_r_lt[t, 0] * dif_r_lt[t, 0] + dif_r_lt[t, 1] * dif_r_lt[t, 1] <= d_r_lt[t] * d_r_lt[t] for t in
         d_r_lt.keys()),
        name='dif_r_lt')

    model.addConstrs((dif_l_rt[t, dim] >= x_lt[t, dim] - x_rt[t, dim]) for t, dim in dif_l_rt.keys())
    model.addConstrs((dif_l_rt[t, dim] >= - x_lt[t, dim] + x_rt[t, dim]) for t, dim in dif_l_rt.keys())
    model.addConstrs(
        (dif_l_rt[t, 0] * dif_l_rt[t, 0] + dif_l_rt[t, 1] * dif_l_rt[t, 1] <= d_l_rt[t] * d_l_rt[t] for t in
         d_l_rt.keys()),
        name='dif_l_rt')

    # longitudes = [] for g in t_index_prima: longitudes.append(sum([grafos[g-1].A[i // 100 - 1, i % 100]*grafos[
    # g-1].edges_length[i // 100 - 1, i % 100] for i in grafos[g-1].edges]))

    big_m = 1e5
    # big_m = data.time_endurance

    model.addConstrs((gp.quicksum(p_ligt[i, g, t] for i in grafos[g - 1].edges) + pigjg.sum('*', '*', g)
                      + gp.quicksum(pig[i, g] * grafos[g - 1].edges_length[i // 100 - 1, i % 100] for i in grafos[g - 1].edges)
                      + gp.quicksum(p_rigt[i, g, t] for i in grafos[g - 1].edges)) / data.drone_speed
                     - big_m * (1 - gp.quicksum(uigt[i, g, t] for i in grafos[g - 1].edges))
                     <= timet_d[t] for t in t_index_prima for g in t_index_prima)
    model.addConstrs(timet_m[t] == d_l_rt[t] / data.truck_speed for t in t_index_prima)

    model.addConstrs(timet_d[t] <= timet_m[t] for t in t_index_prima)
    model.addConstrs(timet_d[t] <= data.time_endurance for t in t_index_prima)
    # model.addConstrs((gp.quicksum(p_ligt[i, g, t] for i in grafos[g-1].edges) + pigjg.sum('*', '*',
    # g) +  gp.quicksum(pig[i, g]*grafos[g-1].edges_length[i // 100 - 1, i % 100] for i in grafos[g-1].edges) +
    # gp.quicksum(p_rigt[i, g, t] for i in grafos[g-1].edges))/data.drone_speed <= d_l_rt[t]/data.truck_speed + big_m*(1-
    # gp.quicksum(uigt[i, g, t] for i in grafos[g-1].edges)) for t in t_index_prima for g in t_index_prima for d in
    # D_index) model.addConstrs((gp.quicksum(p_ligt[i, g, t] for i in grafos[g-1].edges) + pigjg.sum('*', '*',
    # g) +  gp.quicksum(pig[i, g]*grafos[g-1].edges_length[i // 100 - 1, i % 100] for i in grafos[g-1].edges) +
    # gp.quicksum(p_rigt[i, g, t] for i in grafos[g-1].edges))/data.drone_speed model.addConstrs(d_l_rt[t]/data.truck_speed <=
    # data.time_endurance for t in t_index_prima)

    # model.addConstrs((gp.quicksum(p_ligt[i, g, t] for i in grafos[g-1].edges) + pigjg.sum('*', '*',
    # g) +  gp.quicksum(pig[i, g]*grafos[g-1].edges_length[i // 100 - 1, i % 100] for i in grafos[g-1].edges) +
    # gp.quicksum(p_rigt[i, g, t] for i in grafos[g-1].edges))/data.drone_speed <=  zetat[t] + big_m*(1- gp.quicksum(uigt[
    # i, g, t] for i in grafos[g-1].edges)) for t in t_index_prima for g in t_index_prima for d in D_index)

    # model.addConstrs(2*zetat[t]*deltat[t]*data.truck_speed >= d_l_rt[t]*d_l_rt[t] for t in t_index_prima)
    # model.addConstrs(d_l_rt[t] >= deltat[t]*data.truck_speed*zetat[t] for t in t_index_prima)
    # model.addConstrs(zetat[t] <= data.time_endurance for t in t_index_prima)

    # model.addConstrs(zigjg[i, j, g] <= uigt.sum(g, '*', '*') for i, j, g in zigjg.keys())
    # model.addConstrs(muig[i, g] <= uigt.sum(i, g, '*') for i, g in muig.keys())

    # model.addConstrs((p_ligt.sum('*', '*', t) + pigjg.sum(g, '*', '*') + uigt.sum(g, '*', '*')*longitudes[g-1] +
    # p_rigt.sum('*', '*', t))/drone_speed <= d_l_rt[t]/vC for t in t_index_prima for g in t_index_prima) model.addConstrs((
    # d_l_rt[t]/drone_speed <= 50) for t in t_index_prima) model.addConstrs((p_ligt[i, g, t] + pigjg.sum(g, '*',
    # '*') + grafos[g-1].A[i // 100 - 1, i % 100]*grafos[g-1].edges_length[i // 100 - 1, i % 100] + p_rigt[i, g,
    # t])/drone_speed <= d_l_rt[t]/vC for i, g, t in p_ligt.keys())

    for i, g in rhoig.keys():
        first = i // 100 - 1
        second = i % 100
        model.addConstr(rhoig[i, g] - landaig[i, g] == maxig[i, g] - minig[i, g])
        model.addConstr(maxig[i, g] + minig[i, g] == alphaig[i, g])
        if data.alpha:
            model.addConstr(pig[i, g] >= grafos[g - 1].A[first, second])
        model.addConstr(maxig[i, g] <= 1 - entryig[i, g])
        model.addConstr(minig[i, g] <= entryig[i, g])
        model.addConstr(
            rig[i, g, 0] == rhoig[i, g] * grafos[g - 1].V[first, 0] + (1 - rhoig[i, g]) * grafos[g - 1].V[second, 0])
        model.addConstr(
            rig[i, g, 1] == rhoig[i, g] * grafos[g - 1].V[first, 1] + (1 - rhoig[i, g]) * grafos[g - 1].V[second, 1])
        model.addConstr(
            lig[i, g, 0] == landaig[i, g] * grafos[g - 1].V[first, 0] + (1 - landaig[i, g]) * grafos[g - 1].V[
                second, 0])
        model.addConstr(
            lig[i, g, 1] == landaig[i, g] * grafos[g - 1].V[first, 1] + (1 - landaig[i, g]) * grafos[g - 1].V[
                second, 1])

    if not data.alpha:
        for g in t_index_prima:
            model.addConstr(gp.quicksum(
                pig[i, g] * grafos[g - 1].edges_length[i // 100 - 1, i % 100] for i in grafos[g - 1].edges) == grafos[
                                g - 1].alpha * grafos[g - 1].longitud)

    # [0, 2, 1, 3, 4]
    # model.addConstr(uigt[2, 102, 1] >= 0.5)
    # model.addConstr(uigt[1, 101, 2] >= 0.5)
    # model.addConstr(uigt[3, 102, 3] >= 0.5)
    #
    # model.addConstr(vigt[2, 303, 1] >= 0.5)
    # model.addConstr(vigt[1, 203, 2] >= 0.5)
    # model.addConstr(vigt[3, 101, 3] >= 0.5)
    #
    # model.addConstr(d_l_rt[1] <= 3.1490912899469254e+01 + 1e-5)
    # model.addConstr(d_l_rt[2] <= 8.1903472383647316e+00 + 1e-5)
    # model.addConstr(d_l_rt[3] <= 3.2352819808730416e+01 + 1e-5)
    #
    #
    # model.addConstr(x_lt[1, 0] == 5.0000000005633247e+01)
    # model.addConstr(x_lt[1, 1] == 4.9999999994606391e+01)
    # model.addConstr(x_lt[2, 0] == 45.0173764234826)
    # model.addConstr(x_lt[2, 1] == 7.3845420113314660e+01)
    # model.addConstr(x_lt[3, 0] == 4.5080138866746275e+01)
    # model.addConstr(x_lt[3, 1] == 8.0665242773352233e+01)
    #
    # model.addConstr(x_rt[1, 0] == 4.5017376430147451e+01)
    # model.addConstr(x_rt[1, 1] == 7.3845420106065134e+01)
    # model.addConstr(x_rt[2, 0] == 45.0801388601561)
    # model.addConstr(x_rt[2, 1] == 80.6652427666625)
    # model.addConstr(x_rt[3, 0] == 5.0000000002577934e+01)
    # model.addConstr(x_rt[3, 1] == 5.0000000007343687e+01)

    # originen y destinationino
    model.addConstrs(x_lt[0, dim] == data.origin[dim] for dim in range(2))
    model.addConstrs(x_rt[0, dim] == data.origin[dim] for dim in range(2))

    model.addConstrs(x_lt[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))
    model.addConstrs(x_rt[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))

    # print(vals_xL)
    # for g in t_index_prima:
    #     model.addConstrs(x_lt[g, dim] == vals_xL[g][dim] for dim in range(2))
    #     model.addConstrs(x_rt[g, dim] == vals_xR[g][dim] for dim in range(2))

    model.update()

    # objective = gp.quicksum(p_ligt[i, g, t] + p_rigt[i, g, t] for i, g, t in p_rigt.keys()) + gp.quicksum(pigjg[i,
    # j, g] for i, j, g in pigjg.keys()) + gp.quicksum(pig[i, g]*grafos[g-1].edges_length[i // 100 - 1, i % 100] for g
    # in t_index_prima for i in grafos[g-1].edges) + gp.quicksum(3*d_l_rt[t] for t in d_l_rt.keys()) + gp.quicksum(
    # 3*d_r_lt[t] for t in d_r_lt.keys())

    # objective = gp.quicksum(1*d_r_lt[g1] for g1 in d_r_lt.keys()) + gp.quicksum(zetat[t] for t in zetat.keys()) +
    # gp.quicksum(1*d_l_rt[g] for g in d_l_rt.keys())

    objective = gp.quicksum(1 * d_r_lt[g1] / data.truck_speed for g1 in d_r_lt.keys()) + gp.quicksum(
        1 * d_l_rt[g] / data.truck_speed for g in d_l_rt.keys())

    model.setObjective(objective, GRB.MINIMIZE)
    model.Params.Threads = 6
    # model.Params.FeasibilityTol = 1e-3
    # model.Params.NonConvex = 2
    # model.Params.MIPFocus = 3
    model.Params.timeLimit = data.time_limit

    model.update()

    model.write('./case_study/patios-{0}-{1}-{2}.lp'.format(data.fleet_size, data.time_endurance, data.drone_speed))
    # model.write('./AMMDRPGST-initialization.mps')

    if data.initialization:
        model.optimize(_callback)
    else:
        model.optimize()

    # model.update()

    if model.Status == 3:
        model.computeIIS()
        model.write('casa.ilp')
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return result

    if model.SolCount == 0:
        result = [np.nan, np.nan, np.nan, np.nan]
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return result

    result = [model.getAttr('MIPGap'), model.Runtime, model.getAttr('NodeCount'), model.ObjVal]

    if data.initialization:
        result.append(heuristic_time + model._starttime)
        result.append(model._startobjval)

    # if data.grid:
    # result.append('Grid')
    # else:
    # result.append('Delauney')

    # result.append('Stages')

    model.write('./final_solution.sol')
    # model.write('solution_patios.sol')

    # print(x_rt)
    # print(x_lt)
    # print('Selected_u')
    vals_u = model.getAttr('x', uigt)
    selected_u = gp.tuplelist((i, g, t) for i, g, t in vals_u.keys() if vals_u[i, g, t] > 0.5)
    print(selected_u)
    # #
    # print('Selected_z')
    vals_z = model.getAttr('x', zigjg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    # print(selected_z)
    # #
    # print('Selected_v')
    vals_v = model.getAttr('x', vigt)
    selected_v = gp.tuplelist((i, g, t) for i, g, t in vals_v.keys() if vals_v[i, g, t] > 0.5)
    # print(selected_v)
    #
    # path = []
    # path.append(0)

    print('Total time: ' + str(model.ObjVal / data.truck_speed))

    distance = 0

    for t in t_index_prima:
        distance += np.linalg.norm(np.array([x_lt[t, 0].X, x_lt[t, 1].X]) - np.array([x_rt[t, 0].X, x_rt[t, 1].X]))

    for t in t_index_primaprima:
        distance += np.linalg.norm(np.array([x_rt[t, 0].X, x_rt[t, 1].X]) - np.array([x_lt[t, 0].X, x_lt[t, 1].X]))

    print('Time operating: ' + str(distance / data.truck_speed))
    print('Time waiting: ' + str(model.ObjVal - distance / data.truck_speed))

    # path_c.append(origin)
    path_c = []
    paths_d = []

    path = []

    path_c.append([x_lt[0, 0].X, x_lt[0, 1].X])
    path.append(0)
    for t in t_index:
        if len(selected_u.select('*', '*', t)) > 0:
            path.append(t)
            path_c.append([x_lt[t, 0].X, x_lt[t, 1].X])
        if len(selected_v.select('*', '*', t)) > 0:
            path.append(t)
            path_c.append([x_rt[t, 0].X, x_rt[t, 1].X])

    path_c.append([x_lt[n_g + 1, 0].X, x_lt[n_g + 1, 1].X])
    path.append(n_g + 1)

    for t in path:
        tuplas = selected_u.select('*', '*', t)
        # print(tuplas)
        drones = len(tuplas)

        for (i, g, t1), d in zip(tuplas, range(drones)):
            path_d = [[x_lt[t1, 0].X, x_lt[t1, 1].X]]

            index_i = i
            index_g = g
            count = 0

            limite = sum([1 for i1, j1, g1 in selected_z if g1 == g])

            path_d.append([rig[index_i, index_g, 0].X, rig[index_i, index_g, 1].X])
            path_d.append([lig[index_i, index_g, 0].X, lig[index_i, index_g, 1].X])

            while count < limite:
                for i1, j1, g1 in selected_z:
                    if i1 == index_i and g1 == g:
                        count += 1
                        index_i = j1
                        path_d.append([rig[index_i, index_g, 0].X, rig[index_i, index_g, 1].X])
                        path_d.append([lig[index_i, index_g, 0].X, lig[index_i, index_g, 1].X])

            path_d.append([x_rt[t1, 0].X, x_rt[t1, 1].X])

            paths_d.append((path_d, d))

    # print(paths_d)
    log = True

    if log:
        fig, ax = plt.subplots()
        colors = ['darkorange', 'fuchsia', 'y', 'k']
        # plt.axis([0, 100, 0, 100])
        #
        logue = False

        if logue:
            for i, g in rhoig.keys():
                if muig[i, g].X > 0.5:
                    plt.plot(rig[i, g, 0].X, rig[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$R_" + str(g) + "^{" + str((first, second)) + "}$", xy = (rig[i, g, 0].X+0.75,
                    # rig[i, g, 1].X+0.75))
                    plt.plot(lig[i, g, 0].X, lig[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$L_" + str(g) + "^{" + str((first, second)) + "}$", xy = (lig[i, g, 0].X+0.75,
                    # lig[i, g, 1].X+0.75))

        # #
        # # path_c = []

        plt.plot(x_lt[0, 0].X, x_lt[0, 1].X, 's', alpha=1, markersize=10, color='black')
        plt.plot(x_lt[n_g + 1, 0].X, x_lt[n_g + 1, 1].X, 's', alpha=1, markersize=10, color='black')

        logue = True
        if logue:
            for t in path:
                # path_c.append([x_lt[t, 0].X, x_lt[t, 1].X])
                # path_c.append([x_rt[t, 0].X, x_rt[t, 1].X])
                # plt.plot(x_lt[t, 0].X, x_lt[t, 1].X, 's', alpha = 1, markersize=5, color='black')
                plt.plot(x_lt[1, 0].X, x_lt[1, 1].X, 'o', alpha=1, markersize=10, color='red')

                if t == 0:
                    plt.plot(x_lt[t, 0].X, x_lt[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("origin", xy=(x_lt[t, 0].X - 2, x_lt[t, 1].X + 1), fontsize=15)
                if 0 < t < n_g + 1:
                    plt.plot(x_rt[t, 0].X, x_rt[t, 1].X, 'o', alpha=1, markersize=10, color='red')
                    ax.annotate("$x_R^{t}$".format(t=t), xy=(x_rt[t, 0].X + 1.5, x_rt[t, 1].X), fontsize=15)
                    ax.annotate("$x_L^{t}$".format(t=t), xy=(x_lt[t, 0].X - 3, x_lt[t, 1].X), fontsize=15)
                if t == n_g + 1:
                    plt.plot(x_lt[t, 0].X, x_lt[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("destination", xy=(x_lt[t, 0].X + 0.5, x_lt[t, 1].X + 1), fontsize=15)

            ax.add_artist(Polygon(path_c, fill=False, animated=False, closed=False,
                                  linestyle='-', lw=2, alpha=1, color='black'))

            for t in t_index_prima:

                n_drones = len(selected_u.select('*', '*', t))

                if n_drones > 0:
                    for drone in range(n_drones):
                        edge = selected_u.select('*', '*', t)[drone][0]
                        g = selected_u.select('*', '*', t)[drone][1]

                        ax.arrow(x_lt[t, 0].X, x_lt[t, 1].X, rig[edge, g, 0].X - x_lt[t, 0].X,
                                 rig[edge, g, 1].X - x_lt[t, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=colors[drone])

                        for e1, e2, g in selected_z.select('*', '*', g):
                            if pigjg[e1, e2, g].X >= 0.05:
                                ax.arrow(lig[e1, g, 0].X, lig[e1, g, 1].X, rig[e2, g, 0].X - lig[e1, g, 0].X,
                                         rig[e2, g, 1].X - lig[e1, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        for ed in grafos[g - 1].edges:
                            if muig[ed, g].X >= 0.5 and pig[ed, g].X >= 0.01:
                                ax.arrow(rig[ed, g, 0].X, rig[ed, g, 1].X, lig[ed, g, 0].X - rig[ed, g, 0].X,
                                         lig[ed, g, 1].X - rig[ed, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        edge = selected_v.select('*', '*', t)[drone][0]
                        g = selected_v.select('*', '*', t)[drone][1]

                        ax.arrow(lig[edge, g, 0].X, lig[edge, g, 1].X, x_rt[t, 0].X - lig[edge, g, 0].X,
                                 x_rt[t, 1].X - lig[edge, g, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=colors[drone])

            for p in range(len(path_c) - 1):
                ax.arrow(path_c[p][0], path_c[p][1], path_c[p + 1][0] - path_c[p][0], path_c[p + 1][1] - path_c[p][1],
                         width=0.3, head_width=0.7, length_includes_head=True, color='black')

        # def esCerrado(path):
        #     return path[0] == path[-1]
        #
        # for pathd, color in paths_d:
        #     if esCerrado(pathd):
        #         # print(pathd)
        #         ax.add_artist(Polygon(pathd, fill=False, closed = True, lw = 2, alpha=1, color=colors[color]))
        #     else:
        #         ax.add_artist(Polygon(pathd, fill=False, closed = False, lw = 2, alpha=1, color=colors[color]))

        # # ax.add_artist(Polygon(path_d, fill=False, animated=False,
        # #               linestyle='dotted', alpha=1, color='red'))

        # colors = ['blue', 'purple', 'cyan', 'orange', 'red', 'green']
        # for g in t_index_prima:
        # grafo = grafos[g-1]
        # centroide = np.mean(grafo.V, axis = 0)
        # nx.draw(grafo.G, grafo.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
        # ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
        # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)

        # for g in t_index_prima: grafo = grafos[g-1] centroide = np.mean(grafo.V, axis = 0) nx.draw(grafo.G,
        # grafo.pos, node_size=90, width = 2, node_color='blue', alpha=1, edge_color='blue') ax.annotate('$\\alpha_{
        # 0} = {1:0.2f}$'.format(g, grafo.alpha), xy = (centroide[0]+5, centroide[1]+10), fontsize = 12)

        # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)

        # for g in grafos:
        #     nx.draw(g.G, g.pos, node_size=10, width = 1, 
        #             node_color = 'blue', alpha = 1, edge_color = 'blue')
        #
        # plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = data.graphs_number, c = int(data.alpha), d = data.time_endurance,
        # e = data.n_d)) plt.show()
        #
        # import tikzplotlib
        # import matplotlib
        #
        # matplotlib.rcParams['axes.unicode_minus'] = False
        #
        # tikzplotlib.save('synchronous.tex', encoding = 'utf-8')

        # plt.show() plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = data.graphs_number, c = int(data.alpha),
        # d = data.time_endurance, e = data.n_d)) plt.savefig('PDST-Sinc2.png')

        # plt.savefig('Prueba.png')

        # plt.show()
    print(result)
    print()

    return result
