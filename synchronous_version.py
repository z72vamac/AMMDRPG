# Package import
import gurobipy as gp
from gurobipy import GRB
from matplotlib.patches import Polygon

import matplotlib.pyplot as plt

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
                # creates new MODEL attribute '_startobjval'
                m._startobjval = m.cbGet(GRB.Callback.MIPSOL_OBJ)
                m._starttime = m.cbGet(GRB.Callback.RUNTIME)

                # m.terminate()

    graphs = data.instances

    result = []

    graphs_number = data.graphs_number
    fleet_size = data.fleet_size
    scale = data.scale
    drone_speed = data.drone_speed
    truck_speed = data.truck_speed
    
    heuristic_time = 0

    print('SYNCHRONOUS VERSION. Settings:  \n')

    print('Number of graphs: ' + str(data.graphs_number))
    print('Number of drones: ' + str(data.fleet_size))
    print('time_endurance: ' + str(data.time_endurance))
    print('Speed of Mothership: ' + str(data.truck_speed))
    print('Speed of Drone: ' + str(data.drone_speed) + '\n')

    T_index = range(data.graphs_number + 2)
    T_index_prime = range(1, data.graphs_number + 1)
    T_index_prime2 = range(data.graphs_number + 1)

    # Instatianing the model.
    MODEL = gp.Model("Synchronous-Version")

    # Indices of the variables

    u_eg_t_index = []
    
    # Variables que modelan las distancias
    # Variable binaria u_eg_t = 1 si en la etapa t entramos por el segmento s_eg
    u_eg_t_index = []

    for g in T_index_prime:
        for i in graphs[g - 1].edges:
            for t in T_index_prime:
                u_eg_t_index.append((i, g, t))

    dist_L_eg_t_index = u_eg_t_index
    prod_L_eg_t_index = u_eg_t_index

    v_eg_t_index = u_eg_t_index
    dist_R_eg_t_index = v_eg_t_index
    prod_R_eg_t_index = v_eg_t_index


    # Variable binaria flow_eg_eg = 1 si voy del segmento i al segmento j del graph g.
    flow_eg_eg_index = []
    s_eg_index = []
    mu_eg_index = []

    for g in T_index_prime:
        for e in graphs[g - 1].edges:
            s_eg_index.append((e, g))
            mu_eg_index.append((e, g))

            for e_prima in graphs[g - 1].edges:
                if e != e_prima:
                    flow_eg_eg_index.append((e, e_prima, g))

    dist_eg_eg_index = flow_eg_eg_index
    prod_eg_eg_index = flow_eg_eg_index

    R_eg_index = []
    rho_eg_index = []

    for g in T_index_prime:
        for e in graphs[g - 1].edges:
            rho_eg_index.append((e, g))
            for dim in range(2):
                R_eg_index.append((e, g, dim))

    L_eg_index = R_eg_index
    lambda_eg_index = rho_eg_index

    x_L_t_index = []

    for t in T_index:
        for dim in range(2):
            x_L_t_index.append((t, dim))
    
    x_R_t_index = x_L_t_index

    dist_R_L_t_index = T_index_prime2
    dist_L_R_t_index = T_index

    beta_t_index = T_index

    # Variables
    # u_eg_t : x_L_t -> R_eg
    u_eg_t = MODEL.addVars(u_eg_t_index, vtype=GRB.BINARY, name='u_eg_t')

    # dist_L_eg_t : || x_L_t - R_eg ||
    dist_L_eg_t = MODEL.addVars(dist_L_eg_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_L_eg_t')
    dif_L_eg_t = MODEL.addVars(dist_L_eg_t_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_L_eg_t')

    # prod_L_eg_t : dist_L_eg_t * u_eg_t
    prod_L_eg_t = MODEL.addVars(prod_L_eg_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='prod_L_eg_t')

    # v_eg_t : L_eg -> x_R_t
    v_eg_t = MODEL.addVars(v_eg_t_index, vtype=GRB.BINARY, name='v_eg_t')

    # dist_R_eg_t : || x_R_t - L_eg ||
    dist_R_eg_t = MODEL.addVars(dist_R_eg_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_R_eg_t')
    dif_R_eg_t = MODEL.addVars(dist_R_eg_t_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_R_eg_t')

    # prod_R_eg_t: dist_R_eg_t * v_eg_t
    prod_R_eg_t = MODEL.addVars(prod_R_eg_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='prod_R_eg_t')

    # flow_eg_eg': L_eg -> R_eg'
    flow_eg_eg = MODEL.addVars(flow_eg_eg_index, vtype=GRB.BINARY, name='flow_eg_eg')
    s_eg = MODEL.addVars(s_eg_index, vtype=GRB.CONTINUOUS, lb=0, name='s_eg')
    mu_eg = MODEL.addVars(mu_eg_index, vtype=GRB.BINARY, name='mu_eg')
    
    # dist_eg_eg': || L_eg - R_eg' ||
    dist_eg_eg = MODEL.addVars(dist_eg_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_eg_eg')
    dif_eg_eg = MODEL.addVars(dist_eg_eg_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_eg_eg')
    
    # prod_eg_eg' = dist_eg_eg' * flow_eg_eg'
    prod_eg_eg = MODEL.addVars(prod_eg_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, name='prod_eg_eg')

    # R_eg: retrieving point associated to edge eg
    R_eg = MODEL.addVars(R_eg_index, vtype=GRB.CONTINUOUS, name='R_eg')
    rho_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rho_eg')

    # L_eg: retrieving point associated to edge eg
    L_eg = MODEL.addVars(L_eg_index, vtype=GRB.CONTINUOUS, name='L_eg')
    lambda_eg = MODEL.addVars(lambda_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='lambda_eg')

    # Modelling the absolute value
    min_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='min_eg')
    max_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='max_eg')
    entry_eg = MODEL.addVars(rho_eg_index, vtype=GRB.BINARY, name='entry_eg')
    prod_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='prod_eg')
    alpha_eg = MODEL.addVars(rho_eg_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alpha_eg')

    # x_L_t: Launching point associated to stage t
    x_L_t = MODEL.addVars(x_L_t_index, vtype=GRB.CONTINUOUS, name = 'x_L_t')

    # x_R_t: Retrieving point associated to stage t
    x_R_t = MODEL.addVars(x_R_t_index, vtype=GRB.CONTINUOUS, name = 'x_R_t')

    # dist_R_L_t: || x_R_t - x_L_{t+1} ||
    dist_R_L_t = MODEL.addVars(dist_R_L_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_R_L_t')
    dif_R_L_t = MODEL.addVars(dist_R_L_t_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_R_L_t')

    # dist_L_R_t: || x_L_t - x_R_t ||
    dist_L_R_t = MODEL.addVars(dist_L_R_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_L_R_t')
    dif_L_R_t = MODEL.addVars(dist_L_R_t_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_L_R_t')
    
    # beta_t: number of graphs visited up to stage t
    beta_t = MODEL.addVars(beta_t_index, vtype=GRB.CONTINUOUS, lb=0.0, name='beta_t')

    # time_D_t: time spent by the drone for stage t
    time_D_t = MODEL.addVars(T_index_prime, vtype=GRB.CONTINUOUS, lb=0.0, name='time_D_t')

    # time_D_t: time spent by the mothership for stage t    
    time_M_t = MODEL.addVars(T_index_prime, vtype=GRB.CONTINUOUS, lb=0.0, name='time_M_t')

    MODEL.update()

    if data.initialization:

        heuristic_solution = heuristic(data)

        if heuristic_solution is not None:
            u_eg_t_sol = heuristic_solution[0]
            v_eg_t_sol = heuristic_solution[1]
            z_sol = heuristic_solution[2]
            heuristic_time = heuristic_solution[3]
            # u_eg_t_sol, v_eg_t_sol, z_sol, heuristic_time = heuristic(data)

            # for i, g, t in u_eg_t_sol:
            # u_eg_t[i, g, t].start = 1
            #

            # my_file = open('./case_study/u_eg_t_keys.txt', "r")
            # content = my_file.read()

            # u_eg_t_sol = ast.literal_eval(content[:-1])

            # MODEL.read('./case_study/u_eg_t.sol')

            for i, g, t in u_eg_t.keys():
                if (i, g, t) in u_eg_t_sol:
                    u_eg_t[i, g, t].start = 1
                else:
                    u_eg_t[i, g, t].start = 0

            # my_file = open('./case_study/v_eg_t_keys.txt', "r")
            # content = my_file.read()
            #
            #
            # v_eg_t_sol = ast.literal_eval(content)

            for i, g, t in v_eg_t.keys():
                if (i, g, t) in v_eg_t_sol:
                    v_eg_t[i, g, t].start = 1
                else:
                    v_eg_t[i, g, t].start = 0

            for i, j, g in flow_eg_eg.keys():
                if (i, j, g) in z_sol:
                    flow_eg_eg[i, j, g].start = 1
                else:
                    flow_eg_eg[i, j, g].start = 0
        # for g in T_index_prime:
        # MODEL.read('./case_study/graph' + str(g) + '.sol')
        # for i, g, t in v_eg_t_sol:
        # v_eg_t[i, g, t].start = 1
        #
    # En cada etapa hay que visitar/salir un segmento de un graph
    MODEL.addConstrs(u_eg_t.sum('*', '*', t) <= fleet_size for t in T_index_prime)
    MODEL.addConstrs(v_eg_t.sum('*', '*', t) <= fleet_size for t in T_index_prime)

    # # Para cada graph g, existe un segmento i y una etapa t donde hay que recoger al dron
    MODEL.addConstrs(u_eg_t.sum('*', g, '*') == 1 for g in T_index_prime)
    MODEL.addConstrs(v_eg_t.sum('*', g, '*') == 1 for g in T_index_prime)

    # VI-1
    MODEL.addConstrs(beta_t[t] <= beta_t[t + 1] for t in T_index_prime)

    # VI-2
    MODEL.addConstrs(
        gp.quicksum(u_eg_t[i, g, t1] for i, g, t1 in u_eg_t.keys() if t1 < t) >= graphs_number * beta_t[t] for t in T_index_prime)

    # VI-3
    MODEL.addConstrs(
        gp.quicksum(u_eg_t[i, g, t1] for i, g, t1 in u_eg_t.keys() if t1 == t) >= 1 - beta_t[t] for t in T_index)

    # MODEL.addConstrs(u_eg_t.sum('*', i, '*') == 1 for i in range(graphs_number))
    # MODEL.addConstrs(v_eg_t.sum('*', i, '*') == 1 for g in range(graphs_number))

    # De todos los segmentos hay que salir y entrar menos de aquel que se toma como entrada al graph y como salida
    # del graph
    MODEL.addConstrs(mu_eg[i, g] - u_eg_t.sum(i, g, '*') == flow_eg_eg.sum('*', i, g) for i, g in rho_eg.keys())
    MODEL.addConstrs(mu_eg[i, g] - v_eg_t.sum(i, g, '*') == flow_eg_eg.sum(i, '*', g) for i, g in rho_eg.keys())

    MODEL.addConstrs(u_eg_t.sum('*', g, t) - v_eg_t.sum('*', g, t) == 0 for t in T_index_prime for g in T_index_prime)

    # MODEL.addConstrs(u_eg_t[i, g, t] == vgi) MODEL.addConstrs((u_eg_t.sum(i, g, '*') + flow_eg_eg.sum(g, '*',
    # i)) - (v_eg_t.sum(i, g, '*') + flow_eg_eg.sum(i, g, '*')) == 0 for g in T_index_prime for i in graphs[g-1].edges)

    MODEL.addConstrs(prod_eg[i, g] >= mu_eg[i, g] + alpha_eg[i, g] - 1 for i, g in rho_eg.keys())
    MODEL.addConstrs(prod_eg[i, g] <= mu_eg[i, g] for i, g in rho_eg.keys())
    MODEL.addConstrs(prod_eg[i, g] <= alpha_eg[i, g] for i, g in rho_eg.keys())

    # MODEL.addConstr(u_eg_t[0, 101, 0] == 0)
    # MODEL.addConstr(u_eg_t[0, 101, 1] == 0)

    # Eliminación de subtours
    for g in T_index_prime:
        for i in graphs[g - 1].edges[0:]:
            for j in graphs[g - 1].edges[0:]:
                if i != j:
                    MODEL.addConstr(
                        graphs[g - 1].edges_number - 1 >= (s_eg[i, g] - s_eg[j, g]) + graphs[g - 1].edges_number * flow_eg_eg[i, j, g])

    # for g in range(graphs_number):
    #     MODEL.addConstr(s_eg[g, graphs[g].edges[0]] == 0)

    for g in T_index_prime:
        for i in graphs[g - 1].edges[0:]:
            MODEL.addConstr(s_eg[i, g] >= 0)
            MODEL.addConstr(s_eg[i, g] <= graphs[g - 1].edges_number - 1)

    # Restricciones de distancias y producto
    MODEL.addConstrs((dif_L_eg_t[i, g, t, dim]/scale >= x_L_t[t, dim] - R_eg[i, g, dim]) for i, g, t, dim in dif_L_eg_t.keys())
    MODEL.addConstrs((dif_L_eg_t[i, g, t, dim]/scale >= - x_L_t[t, dim] + R_eg[i, g, dim]) for i, g, t, dim in dif_L_eg_t.keys())

    MODEL.addConstrs(
        (dif_L_eg_t[i, g, t, 0] * dif_L_eg_t[i, g, t, 0] + dif_L_eg_t[i, g, t, 1] * dif_L_eg_t[i, g, t, 1] <= dist_L_eg_t[
            i, g, t] * dist_L_eg_t[i, g, t] for i, g, t in u_eg_t.keys()), name='dif_L_eg_t')

    small_m = 0
    big_m = 1e5
    # big_m = 0
    # for g in T_index_prime:
    # for h in T_index_prime:
    # big_m = max(max([np.linalg.norm(v - w) for v in graphs[g-1].V for w in graphs[h-1].V]), big_m)

    # MODEL.addConstr(u_eg_t[303, 1, 1, 0] == 1)
    # MODEL.addConstr(u_eg_t[203, 2, 1, 1] == 1)

    # big_m += 5
    # big_m = max([np.linalg.norm(origin-graphs[g].V) for g in range(graphs_number)])
    MODEL.addConstrs((prod_L_eg_t[i, g, t] <= big_m * u_eg_t[i, g, t]) for i, g, t in u_eg_t.keys())
    MODEL.addConstrs((prod_L_eg_t[i, g, t] <= dist_L_eg_t[i, g, t]) for i, g, t in u_eg_t.keys())
    MODEL.addConstrs((prod_L_eg_t[i, g, t] >= small_m * u_eg_t[i, g, t]) for i, g, t in u_eg_t.keys())
    MODEL.addConstrs((prod_L_eg_t[i, g, t] >= dist_L_eg_t[i, g, t] - big_m * (1 - u_eg_t[i, g, t])) for i, g, t in u_eg_t.keys())

    MODEL.addConstrs((dif_eg_eg[i, j, g, dim]/scale >= L_eg[i, g, dim] - R_eg[j, g, dim]) for i, j, g, dim in dif_eg_eg.keys())
    MODEL.addConstrs((dif_eg_eg[i, j, g, dim]/scale >= - L_eg[i, g, dim] + R_eg[j, g, dim]) for i, j, g, dim in dif_eg_eg.keys())

    MODEL.addConstrs((dif_eg_eg[i, j, g, 0] * dif_eg_eg[i, j, g, 0] + dif_eg_eg[i, j, g, 1] * dif_eg_eg[i, j, g, 1] <= dist_eg_eg[
        i, j, g] * dist_eg_eg[i, j, g] for i, j, g in dist_eg_eg.keys()), name='dif_eg_eg')

    for i, j, g in flow_eg_eg.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Polygonal(np.array([[graphs[g - 1].V[first_i, 0], graphs[g - 1].V[first_i, 1]], [
            graphs[g - 1].V[second_i, 0], graphs[g - 1].V[second_i, 1]]]), graphs[g - 1].A[first_i, second_i])
        segm_j = Polygonal(np.array([[graphs[g - 1].V[first_j, 0], graphs[g - 1].V[first_j, 1]], [
            graphs[g - 1].V[second_j, 0], graphs[g - 1].V[second_j, 1]]]), graphs[g - 1].A[first_j, second_j])

        big_m_local = eM.estimate_local_U(segm_i, segm_j) * scale
        small_m_local = eM.estimate_local_L(segm_i, segm_j) * scale
        MODEL.addConstr((prod_eg_eg[i, j, g] <= big_m_local * flow_eg_eg[i, j, g]))
        MODEL.addConstr((prod_eg_eg[i, j, g] <= dist_eg_eg[i, j, g]))
        MODEL.addConstr((prod_eg_eg[i, j, g] >= small_m_local * flow_eg_eg[i, j, g]))
        MODEL.addConstr((prod_eg_eg[i, j, g] >= dist_eg_eg[i, j, g] - big_m_local * (1 - flow_eg_eg[i, j, g])))

    MODEL.addConstrs((dif_R_eg_t[i, g, t, dim]/scale >= L_eg[i, g, dim] - x_R_t[t, dim]) for i, g, t, dim in dif_R_eg_t.keys())
    MODEL.addConstrs((dif_R_eg_t[i, g, t, dim]/scale >= - L_eg[i, g, dim] + x_R_t[t, dim]) for i, g, t, dim in dif_R_eg_t.keys())

    MODEL.addConstrs(
        (dif_R_eg_t[i, g, t, 0] * dif_R_eg_t[i, g, t, 0] + dif_R_eg_t[i, g, t, 1] * dif_R_eg_t[i, g, t, 1] <= dist_R_eg_t[i, g, t] * dist_R_eg_t[i, g, t] for i, g, t in v_eg_t.keys()), name='dif_R_eg_t')

    # small_m = 0
    # big_m = 10000
    MODEL.addConstrs((prod_R_eg_t[i, g, t] <= big_m * v_eg_t[i, g, t]) for i, g, t in v_eg_t.keys())
    MODEL.addConstrs((prod_R_eg_t[i, g, t] <= dist_R_eg_t[i, g, t]) for i, g, t in v_eg_t.keys())
    MODEL.addConstrs((prod_R_eg_t[i, g, t] >= small_m * v_eg_t[i, g, t]) for i, g, t in v_eg_t.keys())
    MODEL.addConstrs((prod_R_eg_t[i, g, t] >= dist_R_eg_t[i, g, t] - big_m * (1 - v_eg_t[i, g, t])) for i, g, t in v_eg_t.keys())

    MODEL.addConstrs((dif_R_L_t[t, dim]/scale >= x_R_t[t, dim] - x_L_t[t + 1, dim] for t in dist_R_L_t.keys() for dim in range(2)), name='error')
    MODEL.addConstrs((dif_R_L_t[t, dim]/scale >= - x_R_t[t, dim] + x_L_t[t + 1, dim] for t in dist_R_L_t.keys() for dim in range(2)), name='error2')
    MODEL.addConstrs((dif_R_L_t[t, 0] * dif_R_L_t[t, 0] + dif_R_L_t[t, 1] * dif_R_L_t[t, 1] <= dist_R_L_t[t] * dist_R_L_t[t] for t in dist_R_L_t.keys()), name='dif_R_L_t')

    MODEL.addConstrs((dif_L_R_t[t, dim]/scale >= x_L_t[t, dim] - x_R_t[t, dim]) for t, dim in dif_L_R_t.keys())
    MODEL.addConstrs((dif_L_R_t[t, dim]/scale >= - x_L_t[t, dim] + x_R_t[t, dim]) for t, dim in dif_L_R_t.keys())
    MODEL.addConstrs((dif_L_R_t[t, 0] * dif_L_R_t[t, 0] + dif_L_R_t[t, 1] * dif_L_R_t[t, 1] <= dist_L_R_t[t] * dist_L_R_t[t] for t in dist_L_R_t.keys()), name='dif_L_R_t')

    # longitudes = [] for g in T_index_prime: longitudes.append(sum([graphs[g-1].A[i // 100 - 1, i % 100]*graphs[
    # g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges]))

    big_m = 1e5
    # big_m = data.time_endurance

    MODEL.addConstrs((gp.quicksum(prod_L_eg_t[i, g, t] for i in graphs[g - 1].edges) + prod_eg_eg.sum('*', '*', g)
                      + gp.quicksum(prod_eg[i, g] * graphs[g - 1].edges_length[i // 100 - 1, i % 100]*scale for i in graphs[g - 1].edges)
                      + gp.quicksum(prod_R_eg_t[i, g, t] for i in graphs[g - 1].edges)) / data.drone_speed
                     - big_m * (1 - gp.quicksum(u_eg_t[i, g, t] for i in graphs[g - 1].edges))
                     <= time_D_t[t] for t in T_index_prime for g in T_index_prime)
    MODEL.addConstrs(time_M_t[t] == dist_L_R_t[t] / data.truck_speed for t in T_index_prime)

    MODEL.addConstrs(time_D_t[t] <= time_M_t[t] for t in T_index_prime)
    MODEL.addConstrs(time_D_t[t] <= data.time_endurance for t in T_index_prime)
    # MODEL.addConstrs((gp.quicksum(prod_L_eg_t[i, g, t] for i in graphs[g-1].edges) + prod_eg_eg.sum('*', '*',
    # g) +  gp.quicksum(prod_eg[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges) +
    # gp.quicksum(prod_R_eg_t[i, g, t] for i in graphs[g-1].edges))/data.drone_speed <= dist_L_R_t[t]/data.truck_speed + big_m*(1-
    # gp.quicksum(u_eg_t[i, g, t] for i in graphs[g-1].edges)) for t in T_index_prime for g in T_index_prime for d in
    # D_index) MODEL.addConstrs((gp.quicksum(prod_L_eg_t[i, g, t] for i in graphs[g-1].edges) + prod_eg_eg.sum('*', '*',
    # g) +  gp.quicksum(prod_eg[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges) +
    # gp.quicksum(prod_R_eg_t[i, g, t] for i in graphs[g-1].edges))/data.drone_speed MODEL.addConstrs(dist_L_R_t[t]/data.truck_speed <=
    # data.time_endurance for t in T_index_prime)

    # MODEL.addConstrs((gp.quicksum(prod_L_eg_t[i, g, t] for i in graphs[g-1].edges) + prod_eg_eg.sum('*', '*',
    # g) +  gp.quicksum(prod_eg[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for i in graphs[g-1].edges) +
    # gp.quicksum(prod_R_eg_t[i, g, t] for i in graphs[g-1].edges))/data.drone_speed <=  zetat[t] + big_m*(1- gp.quicksum(u_eg_t[
    # i, g, t] for i in graphs[g-1].edges)) for t in T_index_prime for g in T_index_prime for d in D_index)

    # MODEL.addConstrs(2*zetat[t]*deltat[t]*data.truck_speed >= dist_L_R_t[t]*dist_L_R_t[t] for t in T_index_prime)
    # MODEL.addConstrs(dist_L_R_t[t] >= deltat[t]*data.truck_speed*zetat[t] for t in T_index_prime)
    # MODEL.addConstrs(zetat[t] <= data.time_endurance for t in T_index_prime)

    # MODEL.addConstrs(flow_eg_eg[i, j, g] <= u_eg_t.sum(g, '*', '*') for i, j, g in flow_eg_eg.keys())
    # MODEL.addConstrs(mu_eg[i, g] <= u_eg_t.sum(i, g, '*') for i, g in mu_eg.keys())

    # MODEL.addConstrs((prod_L_eg_t.sum('*', '*', t) + prod_eg_eg.sum(g, '*', '*') + u_eg_t.sum(g, '*', '*')*longitudes[g-1] +
    # prod_R_eg_t.sum('*', '*', t))/drone_speed <= dist_L_R_t[t]/vC for t in T_index_prime for g in T_index_prime) MODEL.addConstrs((
    # dist_L_R_t[t]/drone_speed <= 50) for t in T_index_prime) MODEL.addConstrs((prod_L_eg_t[i, g, t] + prod_eg_eg.sum(g, '*',
    # '*') + graphs[g-1].A[i // 100 - 1, i % 100]*graphs[g-1].edges_length[i // 100 - 1, i % 100] + prod_R_eg_t[i, g,
    # t])/drone_speed <= dist_L_R_t[t]/vC for i, g, t in prod_L_eg_t.keys())

    for i, g in rho_eg.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rho_eg[i, g] - lambda_eg[i, g] == max_eg[i, g] - min_eg[i, g])
        MODEL.addConstr(max_eg[i, g] + min_eg[i, g] == alpha_eg[i, g])
        if data.alpha:
            MODEL.addConstr(prod_eg[i, g] >= graphs[g - 1].A[first, second])
        MODEL.addConstr(max_eg[i, g] <= 1 - entry_eg[i, g])
        MODEL.addConstr(min_eg[i, g] <= entry_eg[i, g])
        MODEL.addConstr(R_eg[i, g, 0] == rho_eg[i, g] * graphs[g - 1].V[first, 0] + (1 - rho_eg[i, g]) * graphs[g - 1].V[second, 0])
        MODEL.addConstr(R_eg[i, g, 1] == rho_eg[i, g] * graphs[g - 1].V[first, 1] + (1 - rho_eg[i, g]) * graphs[g - 1].V[second, 1])
        MODEL.addConstr(L_eg[i, g, 0] == lambda_eg[i, g] * graphs[g - 1].V[first, 0] + (1 - lambda_eg[i, g]) * graphs[g - 1].V[second, 0])
        MODEL.addConstr(L_eg[i, g, 1] == lambda_eg[i, g] * graphs[g - 1].V[first, 1] + (1 - lambda_eg[i, g]) * graphs[g - 1].V[second, 1])

    if not data.alpha:
        for g in T_index_prime:
            MODEL.addConstr(gp.quicksum(
                prod_eg[i, g] * graphs[g - 1].edges_length[i // 100 - 1, i % 100] for i in graphs[g - 1].edges) == graphs[g - 1].alpha * graphs[g - 1].length)

    # [0, 2, 1, 3, 4]
    # MODEL.addConstr(u_eg_t[2, 102, 1] >= 0.5)
    # MODEL.addConstr(u_eg_t[1, 101, 2] >= 0.5)
    # MODEL.addConstr(u_eg_t[3, 102, 3] >= 0.5)
    #
    # MODEL.addConstr(v_eg_t[2, 303, 1] >= 0.5)
    # MODEL.addConstr(v_eg_t[1, 203, 2] >= 0.5)
    # MODEL.addConstr(v_eg_t[3, 101, 3] >= 0.5)
    #
    # MODEL.addConstr(dist_L_R_t[1] <= 3.1490912899469254e+01 + 1e-5)
    # MODEL.addConstr(dist_L_R_t[2] <= 8.1903472383647316e+00 + 1e-5)
    # MODEL.addConstr(dist_L_R_t[3] <= 3.2352819808730416e+01 + 1e-5)
    #
    #
    # MODEL.addConstr(x_L_t[1, 0] == 5.0000000005633247e+01)
    # MODEL.addConstr(x_L_t[1, 1] == 4.9999999994606391e+01)
    # MODEL.addConstr(x_L_t[2, 0] == 45.0173764234826)
    # MODEL.addConstr(x_L_t[2, 1] == 7.3845420113314660e+01)
    # MODEL.addConstr(x_L_t[3, 0] == 4.5080138866746275e+01)
    # MODEL.addConstr(x_L_t[3, 1] == 8.0665242773352233e+01)
    #
    # MODEL.addConstr(x_R_t[1, 0] == 4.5017376430147451e+01)
    # MODEL.addConstr(x_R_t[1, 1] == 7.3845420106065134e+01)
    # MODEL.addConstr(x_R_t[2, 0] == 45.0801388601561)
    # MODEL.addConstr(x_R_t[2, 1] == 80.6652427666625)
    # MODEL.addConstr(x_R_t[3, 0] == 5.0000000002577934e+01)
    # MODEL.addConstr(x_R_t[3, 1] == 5.0000000007343687e+01)

    # originen y destinationino
    MODEL.addConstrs(x_L_t[0, dim] == data.origin[dim] for dim in range(2))
    MODEL.addConstrs(x_R_t[0, dim] == data.origin[dim] for dim in range(2))

    MODEL.addConstrs(x_L_t[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))
    MODEL.addConstrs(x_R_t[data.graphs_number + 1, dim] == data.destination[dim] for dim in range(2))

    # print(vals_xL)
    # for g in T_index_prime:
    #     MODEL.addConstrs(x_L_t[g, dim] == vals_xL[g][dim] for dim in range(2))
    #     MODEL.addConstrs(x_R_t[g, dim] == vals_xR[g][dim] for dim in range(2))

    MODEL.update()

    # objective = gp.quicksum(prod_L_eg_t[i, g, t] + prod_R_eg_t[i, g, t] for i, g, t in prod_R_eg_t.keys()) + gp.quicksum(prod_eg_eg[i,
    # j, g] for i, j, g in prod_eg_eg.keys()) + gp.quicksum(prod_eg[i, g]*graphs[g-1].edges_length[i // 100 - 1, i % 100] for g
    # in T_index_prime for i in graphs[g-1].edges) + gp.quicksum(3*dist_L_R_t[t] for t in dist_L_R_t.keys()) + gp.quicksum(
    # 3*dist_R_L_t[t] for t in dist_R_L_t.keys())

    # objective = gp.quicksum(1*dist_R_L_t[g1] for g1 in dist_R_L_t.keys()) + gp.quicksum(zetat[t] for t in zetat.keys()) +
    # gp.quicksum(1*dist_L_R_t[g] for g in dist_L_R_t.keys())

    objective = gp.quicksum(1 * dist_R_L_t[g1] / data.truck_speed for g1 in dist_R_L_t.keys()) + gp.quicksum(1 * dist_L_R_t[g] / data.truck_speed for g in dist_L_R_t.keys())

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
        MODEL.optimize(_callback)
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

    result = [MODEL.getAttr('MIPGap'), MODEL.Runtime, MODEL.getAttr('NodeCount'), MODEL.ObjVal]

    if data.initialization:
        result.append(heuristic_time + MODEL._starttime)
        result.append(MODEL._startobjval)

    # if data.grid:
    # result.append('Grid')
    # else:
    # result.append('Delauney')

    # result.append('Stages')

    MODEL.write('./final_solution.sol')
    # MODEL.write('solution_patios.sol')

    # print(x_R_t)
    # print(x_L_t)
    # print('Selected_u')
    vals_u = MODEL.getAttr('x', u_eg_t)
    selected_u = gp.tuplelist((i, g, t) for i, g, t in vals_u.keys() if vals_u[i, g, t] > 0.5)
    # print(selected_u)
    # #
    # print('Selected_z')
    vals_z = MODEL.getAttr('x', flow_eg_eg)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    print(selected_z)
    # #
    # print('Selected_v')
    vals_v = MODEL.getAttr('x', v_eg_t)
    selected_v = gp.tuplelist((i, g, t) for i, g, t in vals_v.keys() if vals_v[i, g, t] > 0.5)
    # print(selected_v)
    #
    # path = []
    # path.append(0)

    print('Total time: ' + str(MODEL.ObjVal))

    distance = 0

    for t in T_index_prime:
        distance += np.linalg.norm(np.array([x_L_t[t, 0].X, x_L_t[t, 1].X]) - np.array([x_R_t[t, 0].X, x_R_t[t, 1].X]))

    for t in T_index_prime2:
        distance += np.linalg.norm(np.array([x_R_t[t, 0].X, x_R_t[t, 1].X]) - np.array([x_L_t[t, 0].X, x_L_t[t, 1].X]))

    print('Time operating: ' + str(distance * scale / data.truck_speed))
    print('Time waiting: ' + str(MODEL.ObjVal - distance * scale / data.truck_speed))

    # path_c.append(origin)
    path_c = []
    paths_d = []

    path = []

    path_c.append([x_L_t[0, 0].X, x_L_t[0, 1].X])
    path.append(0)
    for t in T_index:
        if len(selected_u.select('*', '*', t)) > 0:
            path.append(t)
            path_c.append([x_L_t[t, 0].X, x_L_t[t, 1].X])
        if len(selected_v.select('*', '*', t)) > 0:
            path.append(t)
            path_c.append([x_R_t[t, 0].X, x_R_t[t, 1].X])

    path_c.append([x_L_t[graphs_number + 1, 0].X, x_L_t[graphs_number + 1, 1].X])
    path.append(graphs_number + 1)

    for t in path:
        tuplas = selected_u.select('*', '*', t)
        # print(tuplas)
        drones = len(tuplas)

        for (i, g, t1), d in zip(tuplas, range(drones)):
            path_d = [[x_L_t[t1, 0].X, x_L_t[t1, 1].X]]

            index_i = i
            index_g = g
            count = 0

            limite = sum([1 for i1, j1, g1 in selected_z if g1 == g])

            path_d.append([R_eg[index_i, index_g, 0].X, R_eg[index_i, index_g, 1].X])
            path_d.append([L_eg[index_i, index_g, 0].X, L_eg[index_i, index_g, 1].X])

            while count < limite:
                for i1, j1, g1 in selected_z:
                    if i1 == index_i and g1 == g:
                        count += 1
                        index_i = j1
                        path_d.append([R_eg[index_i, index_g, 0].X, R_eg[index_i, index_g, 1].X])
                        path_d.append([L_eg[index_i, index_g, 0].X, L_eg[index_i, index_g, 1].X])

            path_d.append([x_R_t[t1, 0].X, x_R_t[t1, 1].X])

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
            for i, g in rho_eg.keys():
                if mu_eg[i, g].X > 0.5:
                    plt.plot(R_eg[i, g, 0].X, R_eg[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$R_" + str(g) + "^{" + str((first, second)) + "}$", xy = (R_eg[i, g, 0].X+0.75,
                    # R_eg[i, g, 1].X+0.75))
                    plt.plot(L_eg[i, g, 0].X, L_eg[i, g, 1].X, 'o', markersize=5, color='red')
                    # ax.annotate("$L_" + str(g) + "^{" + str((first, second)) + "}$", xy = (L_eg[i, g, 0].X+0.75,
                    # L_eg[i, g, 1].X+0.75))

        # #
        # # path_c = []

        plt.plot(x_L_t[0, 0].X, x_L_t[0, 1].X, 's', alpha=1, markersize=10, color='black')
        plt.plot(x_L_t[graphs_number + 1, 0].X, x_L_t[graphs_number + 1, 1].X, 's', alpha=1, markersize=10, color='black')

        logue = True
        if logue:
            for t in path:
                # path_c.append([x_L_t[t, 0].X, x_L_t[t, 1].X])
                # path_c.append([x_R_t[t, 0].X, x_R_t[t, 1].X])
                # plt.plot(x_L_t[t, 0].X, x_L_t[t, 1].X, 's', alpha = 1, markersize=5, color='black')
                plt.plot(x_L_t[1, 0].X, x_L_t[1, 1].X, 'o', alpha=1, markersize=10, color='red')

                if t == 0:
                    plt.plot(x_L_t[t, 0].X, x_L_t[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("origin", xy=(x_L_t[t, 0].X - 2, x_L_t[t, 1].X + 1), fontsize=15)
                if 0 < t < graphs_number + 1:
                    plt.plot(x_R_t[t, 0].X, x_R_t[t, 1].X, 'o', alpha=1, markersize=10, color='red')
                    ax.annotate("$x_R^{t}$".format(t=t), xy=(x_R_t[t, 0].X + 1.5, x_R_t[t, 1].X), fontsize=15)
                    ax.annotate("$x_L^{t}$".format(t=t), xy=(x_L_t[t, 0].X - 3, x_L_t[t, 1].X), fontsize=15)
                if t == graphs_number + 1:
                    plt.plot(x_L_t[t, 0].X, x_L_t[t, 1].X, 's', alpha=1, markersize=10, color='black')
                    ax.annotate("destination", xy=(x_L_t[t, 0].X + 0.5, x_L_t[t, 1].X + 1), fontsize=15)

            ax.add_artist(Polygon(path_c, fill=False, animated=False, closed=False,
                                  linestyle='-', lw=2, alpha=1, color='black'))

            for t in T_index_prime:

                n_drones = len(selected_u.select('*', '*', t))

                if n_drones > 0:
                    for drone in range(n_drones):
                        edge = selected_u.select('*', '*', t)[drone][0]
                        g = selected_u.select('*', '*', t)[drone][1]

                        ax.arrow(x_L_t[t, 0].X, x_L_t[t, 1].X, R_eg[edge, g, 0].X - x_L_t[t, 0].X,
                                 R_eg[edge, g, 1].X - x_L_t[t, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
                                 color=colors[drone])

                        for e1, e2, g in selected_z.select('*', '*', g):
                            if prod_eg_eg[e1, e2, g].X >= 0.05:
                                ax.arrow(L_eg[e1, g, 0].X, L_eg[e1, g, 1].X, R_eg[e2, g, 0].X - L_eg[e1, g, 0].X,
                                         R_eg[e2, g, 1].X - L_eg[e1, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        for ed in graphs[g - 1].edges:
                            if mu_eg[ed, g].X >= 0.5 and prod_eg[ed, g].X >= 0.01:
                                ax.arrow(R_eg[ed, g, 0].X, R_eg[ed, g, 1].X, L_eg[ed, g, 0].X - R_eg[ed, g, 0].X,
                                         L_eg[ed, g, 1].X - R_eg[ed, g, 1].X, width=0.1, head_width=0.5,
                                         length_includes_head=True, color=colors[drone])

                        edge = selected_v.select('*', '*', t)[drone][0]
                        g = selected_v.select('*', '*', t)[drone][1]

                        ax.arrow(L_eg[edge, g, 0].X, L_eg[edge, g, 1].X, x_R_t[t, 0].X - L_eg[edge, g, 0].X,
                                 x_R_t[t, 1].X - L_eg[edge, g, 1].X, width=0.1, head_width=0.5, length_includes_head=True,
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
        # for g in T_index_prime:
        # graph = graphs[g-1]
        # centroide = np.mean(graph.V, axis = 0)
        # nx.draw(graph.G, graph.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
        # ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
        # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'white', font_size=9)

        # for g in T_index_prime: graph = graphs[g-1] centroide = np.mean(graph.V, axis = 0) nx.draw(graph.G,
        # graph.pos, node_size=90, width = 2, node_color='blue', alpha=1, edge_color='blue') ax.annotate('$\\alpha_{
        # 0} = {1:0.2f}$'.format(g, graph.alpha), xy = (centroide[0]+5, centroide[1]+10), fontsize = 12)

        # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'white', font_size=9)

        # for g in graphs:
        #     nx.draw(g.G, g.pos, node_size=10, width = 1, 
        #             node_color = 'blue', alpha = 1, edge_color = 'blue')
        #
        # plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = data.graphs_number, c = int(data.alpha), d = data.time_endurance,
        # e = data.fleet_size)) plt.show()
        #
        # import tikzplotlib
        # import matplotlib
        #
        # matplotlib.rcParams['axes.unicode_minus'] = False
        #
        # tikzplotlib.save('synchronous.tex', encoding = 'utf-8')

        # plt.show() plt.savefig('Synchronous{b}-{c}-{d}-{e}.png'.format(b = data.graphs_number, c = int(data.alpha),
        # d = data.time_endurance, e = data.fleet_size)) plt.savefig('PDST-Sinc2.png')

        # plt.savefig('Prueba.png')

        # plt.show()
    print(result)
    print()

    return result
