# General case

# Incluimos primero los paquetes
import gurobipy as gp
import networkx as nx
from gurobipy import GRB

import bigM_estimation as eM
from neighbourhood import *
from heuristic import heuristic
from prepro import SYNCHRONOUS


# np.random.seed(30)
#
# lista = list(4*np.ones(2, int))
# graphs_number = len(lista)
# data = Data([], m=graphs_number, grid = True, time_limit=150, alpha = True, fleet_size = 2,
#              origin = [0, 0],
#              destination = [100, 0],
#              drone_speed = 2,
#              initialization=False,
#              show=True,
#              time_endurance = 20,
#              seed=2)
#
# data.generate_grid()
#
# data.generate_graphs(lista)

# np.random.seed(13)
#
# lista = list(4*np.ones(4, int))
#
# graphs_number = len(lista)
#
# data = Data([], m=4, grid = True, time_limit=60, alpha = True, fleet_size = 2, time_endurance = 40,
#             initialization=True,
#             show=True,
#             drone_speed = 2,
#             origin = [0, 0],
#             destination = [100, 0],
#             seed=2)
#
# data.generate_grid()
# data.generate_graphs(lista)

def ASYNCHRONOUS(data):
    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            if model.cbGet(GRB.Callback.MIPSOL_SOLCNT) == 0:
                # creates new model attribute '_startobjval'
                model._startobjval = model.cbGet(GRB.Callback.MIPSOL_OBJ)

    grafos = data.graphs_numberostrar_data()

    result = []

    graphs_number = data.graphs_number
    fleet_size = data.fleet_size

    print('SYNCHRONOUS VERSION. Settings:  \n')

    print('Number of graphs: ' + str(data.graphs_number))
    print('Number of drones: ' + str(data.fleet_size))
    print('time_endurance: ' + str(data.time_endurance))
    print('Speed of Mothership: ' + str(data.truck_speed))
    print('Speed of Drone: ' + str(data.drone_speed))
    print('-----------------------------------------------------\n')

    # Sets
    O_index = range(1, data.graphs_number * 2 + 1)
    G_index = range(1, data.graphs_number + 1)

    MODEL = gp.Model('Asynchoronous-Version')

    # u^{e_g o} : x_L^o -> R^{e_g}

    u_eg_o_index = []

    for g in G_index:
        for e in grafos[g - 1].edges:
            for o in O_index:
                u_eg_o_index.append((e, g, o))

    u_eg_o = MODEL.addVars(u_eg_o_index, vtype=GRB.BINARY, name='u_eg_o')

    # d_L^{e_g o} = || x_L^o - R^{e_g} ||

    dist_L_eg_o_index = u_eg_o_index

    dist_L_eg_o = MODEL.addVars(dist_L_eg_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dL_eg_o')

    dif_L_eg_o = MODEL.addVars(dist_L_eg_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difL_eg_o')

    # p_L^{e_g o} = d_L^{e_g o} u^{e_g o} 

    prod_L_eg_o_index = u_eg_o_index

    prod_L_eg_o = MODEL.addVars(prod_L_eg_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pL_eg_o')

    # v^{e_g o} : L^{e_g} -> x_R^o

    v_eg_o_index = []

    for g in G_index:
        for e in grafos[g - 1].edges:
            for o in O_index:
                v_eg_o_index.append((e, g, o))

    v_eg_o = MODEL.addVars(v_eg_o_index, vtype=GRB.BINARY, name='v_eg_o')

    # d_R^{e_g o} = || L^{e_g} - x_R^o ||

    dist_R_eg_o_index = v_eg_o_index

    dist_R_eg_o = MODEL.addVars(dist_R_eg_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dR_eg_o')

    dif_R_eg_o = MODEL.addVars(dist_R_eg_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difR_eg_o')

    # p_R^{e_g o} = d_R^{e_g o} v^{e_g o} 

    pR_eg_o_index = v_eg_o_index

    prod_R_eg_o = MODEL.addVars(pR_eg_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pR_eg_o')

    # gamma_g_o = 1 if graph g is being visited for the event o

    gamma_g_o_index = []

    for g in G_index:
        for o in O_index:
            gamma_g_o_index.append((g, o))

    gammago = MODEL.addVars(gamma_g_o_index, vtype=GRB.BINARY, name='gamma_g_o')

    # K^o = # drones available in the event o

    k_o_index = O_index

    ko = MODEL.addVars(k_o_index, vtype=GRB.INTEGER, lb=0.0, ub=fleet_size, name='k_o')

    # z^{e_g e'_g}: L^{e_g} -> R^{e_g'}

    flow_eg_eg_index = []

    s_eg_index = []

    mu_eg_index = []

    for g in G_index:
        for e in grafos[g - 1].edges:
            s_eg_index.append((e, g))
            mu_eg_index.append((e, g))

            for e_prima in grafos[g - 1].edges:
                if e != e_prima:
                    flow_eg_eg_index.append((e, e_prima, g))

    zegeg = MODEL.addVars(flow_eg_eg_index, vtype=GRB.BINARY, name='z_eg_e\'g')

    s_eg = MODEL.addVars(s_eg_index, vtype=GRB.CONTINUOUS, lb=0, name='s_eg')

    mu_eg = MODEL.addVars(mu_eg_index, vtype=GRB.BINARY, name='mu_eg')

    # d_{LR}^g: distance associated to graph g

    dist_L_R_g_index = G_index

    dist_L_R_g = MODEL.addVars(dist_L_R_g_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLR_g')

    # d^{e_g e'_g} = || L^{e_g} - R^{e'_g} ||

    dist_eg_eg_index = flow_eg_eg_index

    dist_eg_eg = MODEL.addVars(dist_eg_eg_index, vtype=GRB.CONTINUOUS, lb=0, name='d_eg_e\'g')

    dif_eg_eg = MODEL.addVars(dist_eg_eg_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_eg_e\'g')

    # p^{e_g e'_g} = d^{e_g e'_g} z^{e_g e'_g}

    prod_eg_eg = flow_eg_eg_index

    prod_eg_eg = MODEL.addVars(prod_eg_eg, vtype=GRB.CONTINUOUS, lb=0.0, name='p_eg_e\'g')

    # R^{e_g}: retrieving point associated to edge e_g

    R_eg_index = []
    rho_eg_index = []

    for g in G_index:
        for e in grafos[g - 1].edges:
            rho_eg_index.append((e, g))
            for dim in range(2):
                R_eg_index.append((e, g, dim))

    R_eg = MODEL.addVars(R_eg_index, vtype=GRB.CONTINUOUS, name='R_eg')
    rho_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rho_eg')

    # L^{e_g}: launching point associated to edge e_g

    L_eg_index = []
    lambda_eg_index = []

    for g in G_index:
        for e in grafos[g - 1].edges:
            lambda_eg_index.append((e, g))
            for dim in range(2):
                L_eg_index.append((e, g, dim))

    L_eg = MODEL.addVars(L_eg_index, vtype=GRB.CONTINUOUS, name='L_eg')
    lambda_eg = MODEL.addVars(lambda_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='lambda_eg')

    # Modelling the absolute value
    min_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='min_eg')
    max_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='max_eg')
    entry_eg = MODEL.addVars(rho_eg_index, vtype=GRB.BINARY, name='entry_eg')
    prod_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='p_eg')
    alpha_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alpha_eg')

    # x_L^o: Launching point associated to event o
    x_L_o_index = []

    for o in O_index:
        for dim in range(2):
            x_L_o_index.append((o, dim))

    x_L_o = MODEL.addVars(x_L_o_index, vtype=GRB.CONTINUOUS, name='xL_o')

    # x_R^o: Retrieving point associated to event o
    x_R_o_index = []

    for o in O_index:
        for dim in range(2):
            x_R_o_index.append((o, dim))

    x_R_o = MODEL.addVars(x_R_o_index, vtype=GRB.CONTINUOUS, name='xR_o')

    # d_origin: Distance from the origin to the first launching point
    dist_origin = MODEL.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name='d_origin')

    dif_origin = MODEL.addVars(2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_origin')

    # d_destination: Distance from the origin to the first launching point
    dist_destination = MODEL.addVar(vtype=GRB.CONTINUOUS, lb=0.0, name='d_destination')

    difdestination = MODEL.addVars(2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_destination')

    # y_{LL}^o: x_L^o -> x_L^{o+1}

    y_LL_o_index = O_index[:-1]

    yLLo = MODEL.addVars(y_LL_o_index, vtype=GRB.BINARY, name='yLL_o')

    dist_L_L_o_index = y_LL_o_index

    dLLo = MODEL.addVars(dist_L_L_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLL_o')

    difLLo = MODEL.addVars(dist_L_L_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLL_o')

    # p_{LL}^o = d_{LL}^o y_{LL}^o

    prod_L_L_o = MODEL.addVars(dist_L_L_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pLL_o')

    # y_{LR}^o: x_L^o -> x_R^{o+1}

    flow_L_R_o_index = O_index[:-1]

    flow_L_R_o = MODEL.addVars(flow_L_R_o_index, vtype=GRB.BINARY, name='flow_L_R_o')

    dist_L_R_o_index = flow_L_R_o_index

    dist_L_R_o = MODEL.addVars(dist_L_R_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dLR_o')

    dif_L_R_o = MODEL.addVars(dist_L_R_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difLR_o')

    # p_{LR}^o = d_{LR}^o y_{LR}^o

    prod_L_R_o = MODEL.addVars(dist_L_R_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pLR_o')

    # y_{RL}^o: x_R^o -> x_L^{o+1}

    flow_R_L_o_index = O_index[:-1]

    flow_R_L_o = MODEL.addVars(flow_R_L_o_index, vtype=GRB.BINARY, name='yRL_o')

    dist_R_L_o_index = flow_R_L_o_index

    dist_R_L_o = MODEL.addVars(dist_R_L_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRL_o')

    dif_R_L_o = MODEL.addVars(dist_R_L_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRL_o')

    # p_{RL}^o = d_{RL}^o y_{RL}^o

    prod_R_L_o = MODEL.addVars(dist_R_L_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pRL_o')

    # y_{RR}^o: x_R^o -> x_R^{o+1}

    flow_R_R_o_index = O_index[:-1]

    flow_R_R_o = MODEL.addVars(flow_R_R_o_index, vtype=GRB.BINARY, name='yRR_o')

    dist_R_R_o_index = flow_R_R_o_index

    dist_R_R_o = MODEL.addVars(dist_R_R_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dRR_o')

    dif_R_R_o = MODEL.addVars(dist_R_R_o_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difRR_o')

    # p_{RR}^o = d_{RR}^o y_{RR}^o

    prod_R_R_o = MODEL.addVars(dist_R_R_o_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pRR_o')

    # drone distance associated to graph g

    drone_time_g = MODEL.addVars(G_index, vtype=GRB.CONTINUOUS, lb=0.0, name='drone_time_g')

    MODEL.update()

    ### INITIALIZATION ###  
    if data.initialization:
        hola = SYNCHRONOUS(data)

        # print(hola)

        if hola != None:
            uigtd_sol = hola[0]
            vigtd_sol = hola[1]
            z_sol = hola[2]

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
                to_list.append(to_list[-1] + 2 * len(G_list[o - 1]))

            print(to_list)

            tuo_list = list()
            for o in list(O_set):
                tu_list = []
                for t in O_index:
                    if t >= to_list[o - 1] and t <= to_list[o - 1] + len(G_list[o - 1]) - 1:
                        tu_list.append(t)
                tuo_list.append(tu_list)

            print(tuo_list)

            tvo_list = list()
            for o in list(O_set):
                tv_list = []
                for t in O_index:
                    if t - len(G_list[o - 1]) >= to_list[o - 1] and t <= to_list[o - 1] + 2 * len(G_list[o - 1]) - 1:
                        tv_list.append(t)
                tvo_list.append(tv_list)

            print(tvo_list)

            indices = []

            for o in O_set:
                filtro = [(a, b) for a, b, c in uigtd_sol if c == o]
                for t, (e, g) in zip(tuo_list[o - 1], filtro):
                    u_eg_o[e, g, t].start = 1
                    indices.append((e, g, t))
                    uigtd_sol.remove((e, g, o))

            for o in O_set:
                filtro = [(a, b) for a, b, c in vigtd_sol if c == o]
                for t, (e, g) in zip(tvo_list[o - 1], filtro):
                    v_eg_o[e, g, t].start = 1
                    indices.append((e, g, t))
                    vigtd_sol.remove((e, g, o))

            for e, g, o in u_eg_o.keys():
                if not (e, g, o in indices):
                    u_eg_o[e, g, o].start = 0
                    v_eg_o[e, g, o].start = 0

            for i, j, g in zegeg.keys():
                if (i, j, g) in z_sol:
                    zegeg[i, j, g].start = 1
                else:
                    zegeg[i, j, g].start = 0

            print(indices)

    if data.initialization:

        hola = heuristic(data)

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
                to_list.append(to_list[-1] + 2 * len(G_list[o - 1]))

            print(to_list)

            tuo_list = list()
            for o in list(O_set):
                tu_list = []
                for t in O_index:
                    if t >= to_list[o - 1] and t <= to_list[o - 1] + len(G_list[o - 1]) - 1:
                        tu_list.append(t)
                tuo_list.append(tu_list)

            print(tuo_list)

            tvo_list = list()
            for o in list(O_set):
                tv_list = []
                for t in O_index:
                    if t - len(G_list[o - 1]) >= to_list[o - 1] and t <= to_list[o - 1] + 2 * len(G_list[o - 1]) - 1:
                        tv_list.append(t)
                tvo_list.append(tv_list)

            print(tvo_list)

            indices = []

            for o in O_set:
                filtro = [(a, b) for a, b, c in uigtd_sol if c == o]
                for t, (e, g) in zip(tuo_list[o - 1], filtro):
                    u_eg_o[e, g, t].start = 1
                    indices.append((e, g, t))
                    uigtd_sol.remove((e, g, o))

            for o in O_set:
                filtro = [(a, b) for a, b, c in vigtd_sol if c == o]
                for t, (e, g) in zip(tvo_list[o - 1], filtro):
                    v_eg_o[e, g, t].start = 1
                    indices.append((e, g, t))
                    vigtd_sol.remove((e, g, o))

            for e, g, o in u_eg_o.keys():
                if not (e, g, o in indices):
                    u_eg_o[e, g, o].start = 0
                    v_eg_o[e, g, o].start = 0

            for i, j, g in zegeg.keys():
                if (i, j, g) in z_sol:
                    zegeg[i, j, g].start = 1
                else:
                    zegeg[i, j, g].start = 0

            print(indices)

    ### DRONE CONSTRAINTS ###

    # (44): x_L^o must be associated to one point R^{e_g}

    for g in G_index:
        MODEL.addConstr(u_eg_o.sum('*', g, '*') == 1)

    # (45): L^{e_g} must be associated to one point x_R^o

    for g in G_index:
        MODEL.addConstr(v_eg_o.sum('*', g, '*') == 1)

    # (46): If there exists available drones in the event o, we can assign a launching point to this event

    for o in O_index:
        MODEL.addConstr(u_eg_o.sum('*', '*', o) <= ko[o])

    # (47): For each operation, we associate only a launching point or a retrieving point.

    for o in O_index:
        MODEL.addConstr(u_eg_o.sum('*', '*', o) + v_eg_o.sum('*', '*', o) <= 1)

    # (48): If edge e_g is visited, it is because we enter to this edge or the visit comes from the other edges
    # (49): If edge e_g is visited, it is because we exit from this edge or the visit comes from the other edges

    for g in G_index:
        for e in grafos[g - 1].edges:
            # (48)
            MODEL.addConstr(u_eg_o.sum(e, g, '*') + zegeg.sum('*', e, g) == mu_eg[e, g])

            # (49)
            MODEL.addConstr(v_eg_o.sum(e, g, '*') + zegeg.sum(e, '*', g) == mu_eg[e, g])

    # (*): The retrieving associated to graph g must be after the launching

    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr(u_eg_o.sum('*', g, o) <= gp.quicksum(
                v_eg_o[e, g, o_prima] for e in grafos[g - 1].edges for o_prima in O_index if o_prima > o))

    # (MTZ) Constraints
    for g in G_index:
        for e in grafos[g - 1].edges:
            for e_prima in grafos[g - 1].edges:
                if e != e_prima:
                    MODEL.addConstr(
                        grafos[g - 1].edges_number - 1 >= (s_eg[e, g] - s_eg[e_prima, g]) + grafos[g - 1].edges_number *
                        zegeg[e, e_prima, g])

    for g in G_index:
        for e in grafos[g - 1].edges:
            MODEL.addConstr(s_eg[e, g] >= 0)
            MODEL.addConstr(s_eg[e, g] <= grafos[g - 1].edges_number - 1)

    # (50): If we start the visit of g in event o, the gamma starts to be one at event o

    for g in G_index:
        for o in O_index:
            MODEL.addConstr(u_eg_o.sum('*', g, o) <= gammago[g, o])

    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr((o - 1) * (1 - u_eg_o.sum('*', g, o)) >= gp.quicksum(
                gammago[g, o_prima] for o_prima in O_index if o_prima < o))

    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr((len(O_index) - o + 1) * (1 - v_eg_o.sum('*', g, o)) >= gp.quicksum(
                gammago[g, o_prima] for o_prima in O_index if o_prima >= o))

    # (51): If we finish the visit of g in event o, the new gamma is zero.

    for g in G_index:
        for o in O_index[:-1]:
            MODEL.addConstr(gammago[g, o + 1] >= gammago[g, o] - v_eg_o.sum('*', g, o + 1))

    # for g in G_index:
    #     for o in O_index[:-1]:
    #         MODEL.addConstr(1 - v_eg_o.sum('*', g, o) >= gp.quicksum(gammago[g, o_prima] for o_prima in O_index if o_prima > o))

    # (52): The number of drones available at event 1 is |D|

    MODEL.addConstr(ko[1] == fleet_size)

    # (53): The number of drones available at event o+1 depends on what happens at event o

    for o in O_index[:-1]:
        MODEL.addConstr(ko[o + 1] == ko[o] + v_eg_o.sum('*', '*', o) - u_eg_o.sum('*', '*', o))

    ### MOTHERSHIP CONSTRAINTS ###

    # (54): The first point must be a launching point, so the first transition should be LL or LR

    MODEL.addConstr(yLLo[1] + flow_L_R_o[1] == 1)

    # (55): If we launch a drone at event o+1, then it is because the previous transition was RL or LL
    # (56): If we retrieve a drone at event o+1, then it is because the previous transition was LR or RR

    for o in O_index[:-2]:
        # (55)
        MODEL.addConstr(yLLo[o + 1] + flow_L_R_o[o + 1] >= flow_R_L_o[o] + yLLo[o])

        # (56)
        MODEL.addConstr(flow_R_R_o[o + 1] + flow_R_L_o[o + 1] >= flow_L_R_o[o] + flow_R_R_o[o])

    # (57): The last point must be a retrieving point

    MODEL.addConstr(flow_L_R_o[O_index[-2]] + flow_R_R_o[O_index[-2]] == 1)

    ### DISTANCE CONSTRAINTS ###

    # d_L^{e_g o}

    for o in O_index:
        for g in G_index:
            for e in grafos[g - 1].edges:
                for dim in range(2):
                    MODEL.addConstr(dif_L_eg_o[e, g, o, dim] >= (x_L_o[o, dim] - R_eg[e, g, dim]) * 14000 / 1e6)
                    MODEL.addConstr(dif_L_eg_o[e, g, o, dim] >= (-x_L_o[o, dim] + R_eg[e, g, dim]) * 14000 / 1e6)

                MODEL.addConstr(
                    dif_L_eg_o[e, g, o, 0] * dif_L_eg_o[e, g, o, 0] + dif_L_eg_o[e, g, o, 1] * dif_L_eg_o[e, g, o, 1] <= dist_L_eg_o[
                        e, g, o] * dist_L_eg_o[e, g, o])

    # d_R^{e_g o}

    for o in O_index:
        for g in G_index:
            for e in grafos[g - 1].edges:
                for dim in range(2):
                    MODEL.addConstr(dif_R_eg_o[e, g, o, dim] >= (L_eg[e, g, dim] - x_R_o[o, dim]) * 14000 / 1e6)
                    MODEL.addConstr(dif_R_eg_o[e, g, o, dim] >= (-L_eg[e, g, dim] + x_R_o[o, dim]) * 14000 / 1e6)

                MODEL.addConstr(
                    dif_R_eg_o[e, g, o, 0] * dif_R_eg_o[e, g, o, 0] + dif_R_eg_o[e, g, o, 1] * dif_R_eg_o[e, g, o, 1] <= dist_R_eg_o[
                        e, g, o] * dist_R_eg_o[e, g, o])

    # d^{e_g e'_g}

    for g in G_index:
        for e in grafos[g - 1].edges:
            for e_prima in grafos[g - 1].edges:
                if e != e_prima:
                    for dim in range(2):
                        MODEL.addConstr(
                            dif_eg_eg[e, e_prima, g, dim] >= (L_eg[e, g, dim] - R_eg[e_prima, g, dim]) * 14000 / 1e6)
                        MODEL.addConstr(
                            dif_eg_eg[e, e_prima, g, dim] >= (-L_eg[e, g, dim] + R_eg[e_prima, g, dim]) * 14000 / 1e6)

                    MODEL.addConstr(
                        dif_eg_eg[e, e_prima, g, 0] * dif_eg_eg[e, e_prima, g, 0] + dif_eg_eg[e, e_prima, g, 1] * dif_eg_eg[
                            e, e_prima, g, 1] <= dist_eg_eg[e, e_prima, g] * dist_eg_eg[e, e_prima, g])

    # d_origin

    for dim in range(2):
        MODEL.addConstr(dif_origin[dim] >= (data.origin[dim] - x_L_o[1, dim]) * 14000 / 1e6)
        MODEL.addConstr(dif_origin[dim] >= (-data.origin[dim] + x_L_o[1, dim]) * 14000 / 1e6)

    MODEL.addConstr(dif_origin[0] * dif_origin[0] + dif_origin[1] * dif_origin[1] <= dist_origin * dist_origin)

    # d_{LL}^{o}

    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(difLLo[o, dim] >= (x_L_o[o, dim] - x_L_o[o + 1, dim]) * 14000 / 1e6)
            MODEL.addConstr(difLLo[o, dim] >= (-x_L_o[o, dim] + x_L_o[o + 1, dim]) * 14000 / 1e6)

        MODEL.addConstr(difLLo[o, 0] * difLLo[o, 0] + difLLo[o, 1] * difLLo[o, 1] <= dLLo[o] * dLLo[o])

    # d_{LR}^{o}

    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(dif_L_R_o[o, dim] >= (x_L_o[o, dim] - x_R_o[o + 1, dim]) * 14000 / 1e6)
            MODEL.addConstr(dif_L_R_o[o, dim] >= (-x_L_o[o, dim] + x_R_o[o + 1, dim]) * 14000 / 1e6)

        MODEL.addConstr(dif_L_R_o[o, 0] * dif_L_R_o[o, 0] + dif_L_R_o[o, 1] * dif_L_R_o[o, 1] <= dist_L_R_o[o] * dist_L_R_o[o])

    # d_{RL}^{o}

    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(dif_R_L_o[o, dim] >= (x_R_o[o, dim] - x_L_o[o + 1, dim]) * 14000 / 1e6)
            MODEL.addConstr(dif_R_L_o[o, dim] >= (-x_R_o[o, dim] + x_L_o[o + 1, dim]) * 14000 / 1e6)

        MODEL.addConstr(dif_R_L_o[o, 0] * dif_R_L_o[o, 0] + dif_R_L_o[o, 1] * dif_R_L_o[o, 1] <= dist_R_L_o[o] * dist_R_L_o[o])

    # d_{RR}^{o}

    for o in O_index[:-1]:
        for dim in range(2):
            MODEL.addConstr(dif_R_R_o[o, dim] >= (x_R_o[o, dim] - x_R_o[o + 1, dim]) * 14000 / 1e6)
            MODEL.addConstr(dif_R_R_o[o, dim] >= (-x_R_o[o, dim] + x_R_o[o + 1, dim]) * 14000 / 1e6)

        MODEL.addConstr(dif_R_R_o[o, 0] * dif_R_R_o[o, 0] + dif_R_R_o[o, 1] * dif_R_R_o[o, 1] <= dist_R_R_o[o] * dist_R_R_o[o])

    # d_destination

    for dim in range(2):
        MODEL.addConstr(difdestination[dim] >= (x_R_o[O_index[-1], dim] - data.destination[dim]) * 14000 / 1e6)
        MODEL.addConstr(difdestination[dim] >= (-x_R_o[O_index[-1], dim] + data.destination[dim]) * 14000 / 1e6)

    MODEL.addConstr(difdestination[0] * difdestination[0] + difdestination[1] * difdestination[1] <= dist_destination * dist_destination)

    # (58) Mothership distance: dM

    dM = (dist_origin + prod_L_L_o.sum('*') + prod_L_R_o.sum('*') + prod_R_L_o.sum('*') + prod_R_R_o.sum('*') + dist_destination) / data.truck_speed

    MODEL.setObjective(dM, GRB.MINIMIZE)

    # (59): Distance associated to the graph g: d_{LR}^g

    for g in G_index:
        MODEL.addConstr(
            dist_L_R_g[g] == gp.quicksum(gammago[g, o] * (prod_L_L_o[o] + prod_L_R_o[o] + prod_R_L_o[o] + prod_R_R_o[o]) for o in O_index[:-1]))

    ### LINEARIZATION CONSTRAINTS ###

    # p^{e_g} = \alpha^{e_g} \mu^{e_g}

    for g in G_index:
        for e in grafos[g - 1].edges:
            MODEL.addConstr(prod_eg[e, g] <= mu_eg[e, g])
            MODEL.addConstr(prod_eg[e, g] <= alpha_eg[e, g])
            MODEL.addConstr(prod_eg[e, g] >= mu_eg[e, g] + alpha_eg[e, g] - 1)

    # p_L^{e_g o} = d_L^{e_g o} u^{e_g o}

    # BigM = 1e5
    BigM = data.time_endurance * data.drone_speed * 2
    SmallM = 0

    for g in G_index:
        for e in grafos[g - 1].edges:
            for o in O_index:
                MODEL.addConstr(prod_L_eg_o[e, g, o] <= BigM * u_eg_o[e, g, o])
                MODEL.addConstr(prod_L_eg_o[e, g, o] <= dist_L_eg_o[e, g, o])
                MODEL.addConstr(prod_L_eg_o[e, g, o] >= SmallM * u_eg_o[e, g, o])
                MODEL.addConstr(prod_L_eg_o[e, g, o] >= dist_L_eg_o[e, g, o] - BigM * (1 - u_eg_o[e, g, o]))

    # p_R^{e_g o} = d_R^{e_g o} v^{e_g o}

    BigM = data.time_endurance * data.drone_speed * 2
    SmallM = 0

    for g in G_index:
        for e in grafos[g - 1].edges:
            for o in O_index:
                MODEL.addConstr(prod_R_eg_o[e, g, o] <= BigM * v_eg_o[e, g, o])
                MODEL.addConstr(prod_R_eg_o[e, g, o] <= dist_R_eg_o[e, g, o])
                MODEL.addConstr(prod_R_eg_o[e, g, o] >= SmallM * v_eg_o[e, g, o])
                MODEL.addConstr(prod_R_eg_o[e, g, o] >= dist_R_eg_o[e, g, o] - BigM * (1 - v_eg_o[e, g, o]))

    # p^{e_g e'_g} = d^{e_g e'_g} z^{e_g e'_g}

    for g in G_index:
        for e in grafos[g - 1].edges:
            for e_prima in grafos[g - 1].edges:
                if e != e_prima:
                    first_e = e // 100 - 1
                    second_e = e % 100
                    first_e_prima = e_prima // 100 - 1
                    second_e_prima = e_prima % 100

                    segm_e = Polygonal(np.array([[grafos[g - 1].V[first_e, 0], grafos[g - 1].V[first_e, 1]],
                                                 [grafos[g - 1].V[second_e, 0], grafos[g - 1].V[second_e, 1]]]),
                                       grafos[g - 1].A[first_e, second_e])
                    segm_e_prima = Polygonal(
                        np.array([[grafos[g - 1].V[first_e_prima, 0], grafos[g - 1].V[first_e_prima, 1]],
                                  [grafos[g - 1].V[second_e_prima, 0], grafos[g - 1].V[second_e_prima, 1]]]),
                        grafos[g - 1].A[first_e_prima, second_e_prima])

                    BigM_local = eM.estimate_local_U(segm_e, segm_e_prima)
                    SmallM_local = eM.estimate_local_L(segm_e, segm_e_prima)
                    MODEL.addConstr((prod_eg_eg[e, e_prima, g] <= BigM_local * zegeg[e, e_prima, g]))
                    MODEL.addConstr((prod_eg_eg[e, e_prima, g] <= dist_eg_eg[e, e_prima, g]))
                    MODEL.addConstr((prod_eg_eg[e, e_prima, g] >= SmallM_local * zegeg[e, e_prima, g]))
                    MODEL.addConstr(
                        (prod_eg_eg[e, e_prima, g] >= dist_eg_eg[e, e_prima, g] - BigM_local * (1 - zegeg[e, e_prima, g])))

    # y_{LL}^o = \sum_{e_g\in E_g} u^{e_g o} \sum_{e_g\in E_g} u^{e_g (o+1)}

    # (64)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] <= u_eg_o.sum('*', '*', o))

    # (65)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] <= u_eg_o.sum('*', '*', o + 1))

    # (66)
    for o in O_index[:-1]:
        MODEL.addConstr(yLLo[o] >= u_eg_o.sum('*', '*', o) + u_eg_o.sum('*', '*', o + 1) - 1)

    # p_{LL}^o = d_{LL}^o y_{LL}^o

    BigM = 1e5

    for o in O_index[:-1]:
        MODEL.addConstr(prod_L_L_o[o] <= BigM * yLLo[o])
        MODEL.addConstr(prod_L_L_o[o] <= dLLo[o])
        MODEL.addConstr(prod_L_L_o[o] >= SmallM * dLLo[o])
        MODEL.addConstr(prod_L_L_o[o] >= dLLo[o] - BigM * (1 - yLLo[o]))

    # y_{LR}^o = \sum_{e_g\in E_g} u^{e_g o} \sum_{e_g\in E_g} v^{e_g (o+1)}

    # (61)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_L_R_o[o] <= u_eg_o.sum('*', '*', o))

    # (62)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_L_R_o[o] <= v_eg_o.sum('*', '*', o + 1))

    # (63)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_L_R_o[o] >= u_eg_o.sum('*', '*', o) + v_eg_o.sum('*', '*', o + 1) - 1)

    # p_{LR}^o = d_{LR}^o y_{LR}^o

    for o in O_index[:-1]:
        MODEL.addConstr(prod_L_R_o[o] <= BigM * flow_L_R_o[o])
        MODEL.addConstr(prod_L_R_o[o] <= dist_L_R_o[o])
        MODEL.addConstr(prod_L_R_o[o] >= SmallM * dist_L_R_o[o])
        MODEL.addConstr(prod_L_R_o[o] >= dist_L_R_o[o] - BigM * (1 - flow_L_R_o[o]))

    # y_{RL}^o = \sum_{e_g\in E_g} v^{e_g o} \sum_{e_g\in E_g} u^{e_g (o+1)}

    # (70)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_L_o[o] <= v_eg_o.sum('*', '*', o))

    # (71)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_L_o[o] <= u_eg_o.sum('*', '*', o + 1))

    # (72)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_L_o[o] >= v_eg_o.sum('*', '*', o) + u_eg_o.sum('*', '*', o + 1) - 1)

    # p_{RL}^o = d_{RL}^o y_{RL}^o

    for o in O_index[:-1]:
        MODEL.addConstr(prod_R_L_o[o] <= BigM * flow_R_L_o[o])
        MODEL.addConstr(prod_R_L_o[o] <= dist_R_L_o[o])
        MODEL.addConstr(prod_R_L_o[o] >= SmallM * dist_R_L_o[o])
        MODEL.addConstr(prod_R_L_o[o] >= dist_R_L_o[o] - BigM * (1 - flow_R_L_o[o]))

    # y_{RR}^o = \sum_{e_g\in E_g} v^{e_g o} \sum_{e_g\in E_g} v^{e_g (o+1)}

    # (67)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_R_o[o] <= v_eg_o.sum('*', '*', o))

    # (68)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_R_o[o] <= v_eg_o.sum('*', '*', o + 1))

    # (69)
    for o in O_index[:-1]:
        MODEL.addConstr(flow_R_R_o[o] >= v_eg_o.sum('*', '*', o) + v_eg_o.sum('*', '*', o + 1) - 1)

    # p_{RR}^o = d_{RR}^o y_{RR}^o

    for o in O_index[:-1]:
        MODEL.addConstr(prod_R_R_o[o] <= BigM * flow_R_R_o[o])
        MODEL.addConstr(prod_R_R_o[o] <= dist_R_R_o[o])
        MODEL.addConstr(prod_R_R_o[o] >= SmallM * dist_R_R_o[o])
        MODEL.addConstr(prod_R_R_o[o] >= dist_R_R_o[o] - BigM * (1 - flow_R_R_o[o]))

    ### COORDINATION CONSTRAINT ###

    for g in G_index:
        MODEL.addConstr((prod_L_eg_o.sum('*', g, '*') + prod_eg_eg.sum('*', '*', g) + gp.quicksum(
            prod_eg[e, g] * grafos[g - 1].edges_length[e // 100 - 1, e % 100] for e in grafos[g - 1].edges) + prod_R_eg_o.sum(
            '*', g, '*')) / data.drone_speed <= dist_L_R_g[g] / data.truck_speed)

    for g in G_index:
        MODEL.addConstr(drone_time_g[g] == (prod_L_eg_o.sum('*', g, '*') + prod_eg_eg.sum('*', '*', g) + gp.quicksum(
            prod_eg[e, g] * grafos[g - 1].edges_length[e // 100 - 1, e % 100] for e in grafos[g - 1].edges) + prod_R_eg_o.sum(
            '*', g, '*')) / data.drone_speed)

    ### time_endurance CONSTRAINT ###

    for g in G_index:
        MODEL.addConstr(dist_L_R_g[g] / data.truck_speed <= data.time_endurance)

    ### (\ALPHA-E) and (\ALPHA-G) CONSTRAINTS ###

    for g in G_index:
        for e in grafos[g - 1].edges:
            start = e // 100 - 1
            end = e % 100

            MODEL.addConstr(rho_eg[e, g] - lambda_eg[e, g] == max_eg[e, g] - min_eg[e, g])
            MODEL.addConstr(max_eg[e, g] + min_eg[e, g] == alpha_eg[e, g])
            if data.alpha:
                MODEL.addConstr(prod_eg[e, g] >= grafos[g - 1].A[start, end])
            MODEL.addConstr(max_eg[e, g] <= 1 - entry_eg[e, g])
            MODEL.addConstr(min_eg[e, g] <= entry_eg[e, g])
            MODEL.addConstr(
                R_eg[e, g, 0] == rho_eg[e, g] * grafos[g - 1].V[start, 0] + (1 - rho_eg[e, g]) * grafos[g - 1].V[end, 0])
            MODEL.addConstr(
                R_eg[e, g, 1] == rho_eg[e, g] * grafos[g - 1].V[start, 1] + (1 - rho_eg[e, g]) * grafos[g - 1].V[end, 1])
            MODEL.addConstr(
                L_eg[e, g, 0] == lambda_eg[e, g] * grafos[g - 1].V[start, 0] + (1 - lambda_eg[e, g]) * grafos[g - 1].V[
                    end, 0])
            MODEL.addConstr(
                L_eg[e, g, 1] == lambda_eg[e, g] * grafos[g - 1].V[start, 1] + (1 - lambda_eg[e, g]) * grafos[g - 1].V[
                    end, 1])

    if not (data.alpha):
        for g in G_index:
            MODEL.addConstr(gp.quicksum(
                prod_eg[e, g] * grafos[g - 1].edges_length[e // 100 - 1, e % 100] for e in grafos[g - 1].edges) == grafos[
                                g - 1].alpha * grafos[g - 1].longitud)

    # MODEL.read('solution.sol')
    acum = 0
    if data.alpha:
        for g in G_index:
            for e in grafos[g - 1].edges:
                start = e // 100 - 1
                end = e % 100
                # acum + = grafos[g-1].A[start,end]*grafos[g-1].A
        MODEL.addConstr(dM >= gp.quicksum(drone_time_g[g] for g in G_index))

    MODEL.update()

    MODEL.Params.Threads = 6
    MODEL.Params.TimeLimit = data.time_limit

    # MODEL.write('model.lp')
    # MODEL.read('Synchronous_solution (simplified).sol')
    MODEL.read('Asynchronous_solution (simplified).sol')

    if data.initialization:
        MODEL.optimize(callback)
    else:
        MODEL.optimize()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result = [np.nan, np.nan, np.nan, np.nan]
        # if data.grid:
        #     result.append('Grid')
        # else:
        #     result.append('Delauney')
        #
        # result.append('Stages')
        if data.initialization:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)

        return result

        # return result

    elif MODEL.SolCount == 0:
        result = [np.nan, np.nan, np.nan, np.nan]
        # if data.grid:
        #     result.append('Grid')
        # else:
        #     result.append('Delauney')
        #
        # result.append('Stages')

        if data.initialization:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)

        return result

        if data.initialization:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)

    else:
        if data.initialization:
            result.append(heuristic_time)
            result.append(MODEL._startobjval)

        result.append(MODEL.getAttr('MIPGap'))
        result.append(MODEL.Runtime)
        result.append(MODEL.getAttr('NodeCount'))
        result.append(MODEL.ObjVal)

    MODEL.write('solution.sol')

    vals_u = MODEL.getAttr('x', u_eg_o)
    selected_u = gp.tuplelist((e, g, o) for e, g, o in vals_u.keys() if vals_u[e, g, o] > 0.5)
    print(selected_u)
    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', zegeg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', v_eg_o)
    selected_v = gp.tuplelist((e, g, o) for e, g, o in vals_v.keys() if vals_v[e, g, o] > 0.5)
    print(selected_v)

    vals_gamma = MODEL.getAttr('x', gammago)
    selected_gamma = gp.tuplelist((g, o) for g, o in vals_gamma.keys() if vals_gamma[g, o] > 0.5)
    print(selected_gamma)

    # vals_drone_time_g = MODEL.getAttr('x', drone_time_g)
    # print(vals_drone_time_g)
    print('Total time: ' + str(MODEL.ObjVal / data.truck_speed))

    distance = dist_origin.X + dist_destination.X

    wasU = True
    isU = True

    for o in O_index[1:]:
        isU = len(selected_u.select('*', '*', o)) > 0

        if wasU and isU:
            distance += np.linalg.norm(
                np.array([x_L_o[o - 1, 0].X, x_L_o[o - 1, 1].X]) - np.array([x_L_o[o, 0].X, x_L_o[o, 1].X]))

        elif not (wasU) and isU:
            distance += np.linalg.norm(
                np.array([x_R_o[o - 1, 0].X, x_R_o[o - 1, 1].X]) - np.array([x_L_o[o, 0].X, x_L_o[o, 1].X]))

        elif wasU and not (isU):
            distance += np.linalg.norm(
                np.array([x_L_o[o - 1, 0].X, x_L_o[o - 1, 1].X]) - np.array([x_R_o[o, 0].X, x_R_o[o, 1].X]))

        elif not (wasU) and not (isU):
            distance += np.linalg.norm(
                np.array([x_R_o[o - 1, 0].X, x_R_o[o - 1, 1].X]) - np.array([x_R_o[o, 0].X, x_R_o[o, 1].X]))

        wasU = isU

    print('Time operating: ' + str(distance / data.truck_speed))
    print('Time waiting: ' + str(MODEL.ObjVal - distance / data.truck_speed))

    log = True

    if log:
        fig, ax = plt.subplots()

        colors = {'lime': 0, 'orange': 0, 'fuchsia': 0}

        # Mothership Route

        ax.arrow(data.origin[0], data.origin[1], x_L_o[1, 0].X - data.origin[0], x_L_o[1, 1].X - data.origin[1], width=0.3,
                 head_width=1, length_includes_head=True, color='black')
        plt.plot(data.origin[0], data.origin[1], 's', markersize=10, c='black')

        wasU = True
        isU = True

        for o in O_index[1:]:
            isU = len(selected_u.select('*', '*', o)) > 0

            if wasU and isU:

                ax.arrow(x_L_o[o - 1, 0].X, x_L_o[o - 1, 1].X, x_L_o[o, 0].X - x_L_o[o - 1, 0].X, x_L_o[o, 1].X - x_L_o[o - 1, 1].X,
                         width=0.3, head_width=1, length_includes_head=True, color='black')

                edge = selected_u.select('*', '*', o)[0][0]
                g = selected_u.select('*', '*', o)[0][1]

                # ax.arrow(x_L_o[o, 0].X, x_L_o[o, 1].X, R_eg[edge, g, 0].X - x_L_o[o, 0].X, R_eg[edge, g, 1].X - x_L_o[o, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')

            elif not (wasU) and isU:

                ax.arrow(x_R_o[o - 1, 0].X, x_R_o[o - 1, 1].X, x_L_o[o, 0].X - x_R_o[o - 1, 0].X, x_L_o[o, 1].X - x_R_o[o - 1, 1].X,
                         width=0.3, head_width=1, length_includes_head=True, color='black')

                edge = selected_u.select('*', '*', o)[0][0]
                g = selected_u.select('*', '*', o)[0][1]

                # ax.arrow(L_eg[edge, g, 0].X, L_eg[edge, g, 1].X, x_R_o[o, 0].X - L_eg[edge, g, 0].X, x_R_o[o, 1].X - L_eg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            

            elif wasU and not (isU):

                ax.arrow(x_L_o[o - 1, 0].X, x_L_o[o - 1, 1].X, x_R_o[o, 0].X - x_L_o[o - 1, 0].X, x_R_o[o, 1].X - x_L_o[o - 1, 1].X,
                         width=0.3, head_width=1, length_includes_head=True, color='black')

                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]

                # ax.arrow(L_eg[edge, g, 0].X, L_eg[edge, g, 1].X, x_R_o[o, 0].X - L_eg[edge, g, 0].X, x_R_o[o, 1].X - L_eg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            

            elif not (wasU) and not (isU):

                ax.arrow(x_R_o[o - 1, 0].X, x_R_o[o - 1, 1].X, x_R_o[o, 0].X - x_R_o[o - 1, 0].X, x_R_o[o, 1].X - x_R_o[o - 1, 1].X,
                         width=0.3, head_width=1, length_includes_head=True, color='black')

                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]

                # ax.arrow(L_eg[edge, g, 0].X, L_eg[edge, g, 1].X, x_R_o[o, 0].X - L_eg[edge, g, 0].X, x_R_o[o, 1].X - L_eg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = 'red')            

            wasU = isU

        ax.arrow(x_R_o[len(O_index), 0].X, x_R_o[len(O_index), 1].X, data.destination[0] - x_R_o[len(O_index), 0].X,
                 data.destination[1] - x_R_o[len(O_index), 1].X, width=0.3, head_width=1, length_includes_head=True,
                 color='black')
        plt.plot(data.destination[0], data.destination[1], 's', markersize=10, c='black')

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

                ax.arrow(x_L_o[o, 0].X, x_L_o[o, 1].X, R_eg[edge, g, 0].X - x_L_o[o, 0].X, R_eg[edge, g, 1].X - x_L_o[o, 1].X,
                         width=0.1, head_width=0.5, length_includes_head=True, color=color)

                for e1, e2, g in selected_z.select('*', '*', g):
                    if prod_eg_eg[e1, e2, g].X >= 0.1:
                        ax.arrow(L_eg[e1, g, 0].X, L_eg[e1, g, 1].X, R_eg[e2, g, 0].X - L_eg[e1, g, 0].X,
                                 R_eg[e2, g, 1].X - L_eg[e1, g, 1].X, width=0.1, head_width=0.5,
                                 length_includes_head=True, color=color)

                for e in grafos[g - 1].edges:
                    if mu_eg[e, g].X >= 0.5 and prod_eg[e, g].X >= 0.05:
                        ax.arrow(R_eg[e, g, 0].X, R_eg[e, g, 1].X, L_eg[e, g, 0].X - R_eg[e, g, 0].X,
                                 L_eg[e, g, 1].X - R_eg[e, g, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=color)

                edge_new = selected_v.select('*', g, '*')[0][0]
                o_new = selected_v.select('*', g, '*')[0][2]

                ax.arrow(L_eg[edge_new, g, 0].X, L_eg[edge_new, g, 1].X, x_R_o[o_new, 0].X - L_eg[edge_new, g, 0].X,
                         x_R_o[o_new, 1].X - L_eg[edge_new, g, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                         color=color)

            else:

                edge = selected_v.select('*', '*', o)[0][0]
                g = selected_v.select('*', '*', o)[0][1]

                for key, value in colors.items():
                    if value == g:
                        colors[key] = 0
                        break
            #
            #     ax.arrow(L_eg[edge, g, 0].X, L_eg[edge, g, 1].X, x_R_o[o, 0].X - L_eg[edge, g, 0].X, x_R_o[o, 1].X - L_eg[edge, g, 1].X, width = 0.1, head_width = 0.5, length_includes_head = True, color = color)            

            wasU = isU

        for g in grafos:
            nx.draw(g.G, g.pos, node_size=10, width=1,
                    node_color='blue', alpha=1, edge_color='blue')

        plt.savefig(
            'Asynchronous{b}-{c}-{d}-{e}.png'.format(b=data.graphs_number, c=int(data.alpha), d=data.time_endurance, e=data.fleet_size))

        import tikzplotlib
        import matplotlib

        matplotlib.rcParams['axes.unicode_minus'] = False

        tikzplotlib.save('asynchronous.tex', encoding='utf-8')

        plt.show()

    print(result)
    print()

    return result
    # plt.show()
