from vns import *


def clustering_easy(data, paths, clusters):
    """
    data: problem data,
    paths: list of (path_g, points_g, cost_g) associated to the graph g
    """

    fleet_size = data.fleet_size
    graphs_number = data.graphs_number
    drone_speed = data.drone_speed
    vC = data.truck_speed
    origin = data.origin
    time_endurance = data.time_endurance

    K_index = list(clusters.keys())
    G_index = range(1, graphs_number + 1)

    MODEL = gp.Model('Clustering')

    assign_k_g = MODEL.addVars(K_index, G_index, vtype=GRB.BINARY, name='assign_k_g')

    dist_k_g = MODEL.addVars(K_index, G_index, vtype=GRB.CONTINUOUS, name='dist_k_g')
    dif_k_g = MODEL.addVars(K_index, G_index, 2, vtype=GRB.CONTINUOUS, name='dist_k_g')
    # prod_k_g = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'prod_k_g')

    dist_k_g_prime = MODEL.addVars(K_index, G_index, vtype=GRB.CONTINUOUS, name='dist_k_g_prime')
    dif_k_g_prime = MODEL.addVars(K_index, G_index, 2, vtype=GRB.CONTINUOUS, name='dist_k_g_prime')
    # prod_k_g_prime = MODEL.addVars(K_index, G_index, vtype = GRB.CONTINUOUS, name = 'prod_k_g_prime')

    dist_k_k = MODEL.addVars(K_index, K_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_k_k')
    dif_k_k = MODEL.addVars(K_index, K_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_k_k')
    # zkk = MODEL.addVars(K_index, K_index, vtype = GRB.BINARY, name = 'zkk')
    # pkk = MODEL.addVars(K_index, K_index, vtype = GRB.CONTINUOUS, lb = 0.0, name = 'pkk')

    dist_k = MODEL.addVars(K_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_k')
    dif_k = MODEL.addVars(K_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_k')

    C_k = MODEL.addVars(K_index, 2, vtype=GRB.CONTINUOUS, name='C_k')

    MODEL.update()

    # MODEL.addConstrs(assign_k_g.sum(k, '*') <= fleet_size for k in K_index)
    # MODEL.addConstrs(assign_k_g.sum('*', g) == 1 for g in G_index)

    for k in clusters.keys():
        for g in clusters[k]:
            MODEL.addConstr(assign_k_g[k, g] >= 0.5)
    # MODEL.addConstrs((prod_k_g[k, g] <= BigM * assign_k_g[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g[k, g] <= dist_k_g[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g[k, g] >= SmallM * assign_k_g[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g[k, g] >= dist_k_g[k, g] - BigM * (1 - assign_k_g[k, g])) for k, g in assign_k_g.keys())

    # MODEL.addConstrs((prod_k_g_prime[k, g] <= BigM * assign_k_g[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g_prime[k, g] <= dist_k_g_prime[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g_prime[k, g] >= SmallM * assign_k_g[k, g]) for k, g in assign_k_g.keys())
    # MODEL.addConstrs((prod_k_g_prime[k, g] >= dist_k_g_prime[k, g] - BigM * (1 - assign_k_g[k, g])) for k, g in assign_k_g.keys())

    MODEL.addConstrs((gp.quicksum(assign_k_g[k, g] * dist_k_g[k, g] for k in K_index) + paths[g - 1][2] + gp.quicksum(
        assign_k_g[k, g] * dist_k_g_prime[k, g] for k in K_index)) / drone_speed <= time_endurance for g in G_index)
    # MODEL.addConstrs((dist_k_k[k1, k2] / vC <= time_endurance for k1, k2 in dist_k_k.keys()))

    MODEL.addConstrs(
        (dif_k_g[k, g, dim] >= (C_k[k, dim] - paths[g - 1][1][0][dim]) * 14000 / 1e6 for k, g, dim in dif_k_g.keys()))
    MODEL.addConstrs(
        (dif_k_g[k, g, dim] >= (- C_k[k, dim] + paths[g - 1][1][0][dim]) * 14000 / 1e6 for k, g, dim in dif_k_g.keys()))
    MODEL.addConstrs(
        (dif_k_g[k, g, 0] * dif_k_g[k, g, 0] + dif_k_g[k, g, 1] * dif_k_g[k, g, 1] <= dist_k_g[k, g] * dist_k_g[k, g] for k, g in
         dist_k_g.keys()))

    MODEL.addConstrs((dif_k_g_prime[k, g, dim] >= (C_k[k, dim] - paths[g - 1][1][1][dim]) * 14000 / 1e6 for k, g, dim in
                      dif_k_g_prime.keys()))
    MODEL.addConstrs((dif_k_g_prime[k, g, dim] >= (- C_k[k, dim] + paths[g - 1][1][1][dim]) * 14000 / 1e6 for k, g, dim in
                      dif_k_g_prime.keys()))
    MODEL.addConstrs((dif_k_g_prime[k, g, 0] * dif_k_g_prime[k, g, 0] + dif_k_g_prime[k, g, 1] * dif_k_g_prime[k, g, 1] <=
                      dist_k_g_prime[k, g] * dist_k_g_prime[k, g] for k, g in dist_k_g_prime.keys()))

    MODEL.addConstrs((dif_k_k[k1, k2, dim] >= (C_k[k1, dim] - C_k[k2, dim]) * 14000 / 1e6 for k1, k2, dim in dif_k_k.keys()))
    MODEL.addConstrs((dif_k_k[k1, k2, dim] >= (-C_k[k1, dim] + C_k[k2, dim]) * 14000 / 1e6 for k1, k2, dim in dif_k_k.keys()))
    MODEL.addConstrs(
        gp.quicksum(dif_k_k[k1, k2, dim] * dif_k_k[k1, k2, dim] for dim in range(2)) <= dist_k_k[k1, k2] * dist_k_k[k1, k2] for k1, k2
        in dist_k_k.keys())

    MODEL.addConstrs((dif_k[k, dim] >= (C_k[k, dim] - origin[dim]) * 14000 / 1e6 for k, dim in dif_k.keys()))
    MODEL.addConstrs((dif_k[k, dim] >= (-C_k[k, dim] + origin[dim]) * 14000 / 1e6 for k, dim in dif_k.keys()))
    MODEL.addConstrs(gp.quicksum(dif_k[k, dim] * dif_k[k, dim] for dim in range(2)) <= dist_k[k] * dist_k[k] for k in dist_k.keys())

    # objective = gp.quicksum(prod_k_g[k, g] + prod_k_g_prime[k, g] for k, g in prod_k_g.keys()) + gp.quicksum(dist_k_k[k1, k2] for k1, k2 in dist_k_k.keys()) + gp.quicksum(dist_k[k] for k in dist_k.keys())
    objective = gp.quicksum(dist_k_k[k1, k2] for k1, k2 in dist_k_k.keys()) + gp.quicksum(
        dist_k[k] for k in dist_k.keys())  # + gp.quicksum(zk[k]*BigM for k in zk.keys())

    MODEL.Params.OutputFlag = 1
    MODEL.setObjective(objective, GRB.MINIMIZE)

    MODEL.update()

    MODEL.optimize()

    MODEL.update()

    # print(C_k)
    # print(assign_k_g)
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
