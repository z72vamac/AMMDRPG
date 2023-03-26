from vns import *


def clustering_easy(data, paths, clusters):
    """
    data: problem data,
    paths: list of (path_g, points_g, cost_g) associated to the graph g
    """

    fleet_size = data.fleet_size
    graphs_number = data.graphs_number
    drone_speed = data.drone_speed
    truck_speed = data.truck_speed
    origin = data.origin
    time_endurance = data.time_endurance
    scale = data.scale

    K_index = list(clusters.keys())
    G_index = range(1, graphs_number + 1)

    MODEL = gp.Model('Clustering')

    assign_k_g = MODEL.addVars(K_index, G_index, vtype=GRB.BINARY, name='assign_k_g')

    dist_k_g = MODEL.addVars(K_index, G_index, vtype=GRB.CONTINUOUS, name='dist_k_g')
    dif_k_g = MODEL.addVars(K_index, G_index, 2, vtype=GRB.CONTINUOUS, name='dif_k_g')

    dist_k_g_prime = MODEL.addVars(K_index, G_index, vtype=GRB.CONTINUOUS, name='dist_k_g_prime')
    dif_k_g_prime = MODEL.addVars(K_index, G_index, 2, vtype=GRB.CONTINUOUS, name='dif_k_g_prime')

    dist_k_k = MODEL.addVars(K_index, K_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_k_k')
    dif_k_k = MODEL.addVars(K_index, K_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_k_k')

    dist_k = MODEL.addVars(K_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_k')
    dif_k = MODEL.addVars(K_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_k')

    C_k = MODEL.addVars(K_index, 2, vtype=GRB.CONTINUOUS, name='C_k')

    MODEL.update()

    for k in clusters.keys():
        for g in clusters[k]:
            MODEL.addConstr(assign_k_g[k, g] >= 0.5)

    MODEL.addConstrs((dif_k_g[k, g, dim]/scale >=  C_k[k, dim] - paths[g - 1][1][0][dim] for k, g, dim in dif_k_g.keys()))
    MODEL.addConstrs((dif_k_g[k, g, dim]/scale >= -C_k[k, dim] + paths[g - 1][1][0][dim] for k, g, dim in dif_k_g.keys()))
    MODEL.addConstrs((dif_k_g[k, g, 0] * dif_k_g[k, g, 0] + dif_k_g[k, g, 1] * dif_k_g[k, g, 1] <= dist_k_g[k, g] * dist_k_g[k, g] for k, g in dist_k_g.keys()))

    MODEL.addConstrs((dif_k_g_prime[k, g, dim]/scale >=  C_k[k, dim] - paths[g - 1][1][1][dim] for k, g, dim in dif_k_g_prime.keys()))
    MODEL.addConstrs((dif_k_g_prime[k, g, dim]/scale >= -C_k[k, dim] + paths[g - 1][1][1][dim] for k, g, dim in dif_k_g_prime.keys()))
    MODEL.addConstrs((dif_k_g_prime[k, g, 0] * dif_k_g_prime[k, g, 0] + dif_k_g_prime[k, g, 1] * dif_k_g_prime[k, g, 1] <= dist_k_g_prime[k, g] * dist_k_g_prime[k, g] for k, g in dist_k_g_prime.keys()))

    MODEL.addConstrs((dif_k_k[k1, k2, dim]/scale >=  C_k[k1, dim] - C_k[k2, dim] for k1, k2, dim in dif_k_k.keys()))
    MODEL.addConstrs((dif_k_k[k1, k2, dim]/scale >= -C_k[k1, dim] + C_k[k2, dim] for k1, k2, dim in dif_k_k.keys()))
    MODEL.addConstrs(gp.quicksum(dif_k_k[k1, k2, dim] * dif_k_k[k1, k2, dim] for dim in range(2)) <= dist_k_k[k1, k2] * dist_k_k[k1, k2] for k1, k2 in dist_k_k.keys())

    MODEL.addConstrs((dif_k[k, dim]/scale >=  C_k[k, dim] - origin[dim] for k, dim in dif_k.keys()))
    MODEL.addConstrs((dif_k[k, dim]/scale >= -C_k[k, dim] + origin[dim] for k, dim in dif_k.keys()))
    MODEL.addConstrs(gp.quicksum(dif_k[k, dim] * dif_k[k, dim] for dim in range(2)) <= dist_k[k] * dist_k[k] for k in dist_k.keys())

    MODEL.addConstrs((gp.quicksum(assign_k_g[k, g] * dist_k_g[k, g] for k in K_index) + paths[g - 1][2] + gp.quicksum(assign_k_g[k, g] * dist_k_g_prime[k, g] for k in K_index)) / drone_speed <= time_endurance for g in G_index)

    objective = gp.quicksum(dist_k_k[k1, k2] for k1, k2 in dist_k_k.keys()) + gp.quicksum(dist_k[k] for k in dist_k.keys())

    MODEL.Params.OutputFlag = 1
    MODEL.setObjective(objective, GRB.MINIMIZE)

    MODEL.update()

    MODEL.optimize()

    MODEL.update()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')
        result = []
        if data.grid:
            result.append('Grid')
        else:
            result.append('Delauney')

        result.append('Stages')

        return None

    return MODEL.getAttr('x', C_k)
