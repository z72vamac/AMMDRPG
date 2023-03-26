from vns import *
import neighbourhood as neigh


def grafo_problem(grafo, alpha, g):
    # grafo = data.instances[0]

    # Creamos el modelo
    model = gp.Model("PD-Stages")

    # Variable binaria zij = 1 si voy del segmento i al segmento j del grafo g.
    zij_index = []
    si_index = []

    for i in grafo.edges:
        si_index.append((i, g))
        for j in grafo.edges:
            if i != j:
                zij_index.append((i, j, g))

    zij = model.addVars(zij_index, vtype=GRB.BINARY, name='zigjg')
    si = model.addVars(si_index, vtype=GRB.INTEGER, lb=0, ub=grafo.edges_number - 1, name='sig')

    # Variable continua no negativa dij que indica la distancia entre los segmentos i j en el grafo g.
    dij_index = zij_index

    dij = model.addVars(dij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='digjg')
    difij = model.addVars(dij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difigjg')

    # Variable continua no negativa pij = zij * dij
    pij_index = zij_index

    pij = model.addVars(pij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pigjg')

    ri_index = []
    rhoi_index = []

    for i in grafo.edges:
        rhoi_index.append((i, g))
        for dim in range(2):
            ri_index.append((i, g, dim))

    ri = model.addVars(ri_index, vtype=GRB.CONTINUOUS, name='Rig')
    rhoi = model.addVars(rhoi_index, vtype=GRB.CONTINUOUS,
                         lb=0.0, ub=1.0, name='rhoig')

    # li: punto de lanzamiento del dron del segmento si
    li_index = ri_index
    landai_index = rhoi_index

    li = model.addVars(li_index, vtype=GRB.CONTINUOUS, name='Lig')
    landai = model.addVars(landai_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landaig')

    # Variables difiliares para modelar el valor absoluto
    mini = model.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='minig')
    maxi = model.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='maxig')
    entryi = model.addVars(rhoi_index, vtype=GRB.BINARY, name='entryig')
    mui = model.addVars(rhoi_index, vtype=GRB.BINARY, name='muig')
    pi = model.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='pig')
    alphai = model.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alphaig')

    model.update()

    model.addConstrs(zij.sum('*', j, g) == 1 for j, g in rhoi.keys())
    model.addConstrs(zij.sum(i, '*', g) == 1 for i, g in rhoi.keys())

    model.addConstrs(pi[i, g] >= mui[i, g] + alphai[i, g] - 1 for i, g in rhoi.keys())
    model.addConstrs(pi[i, g] <= mui[i, g] for i, g in rhoi.keys())
    model.addConstrs(pi[i, g] <= alphai[i, g] for i, g in rhoi.keys())

    for i in grafo.edges[1:]:
        for j in grafo.edges[1:]:
            if i != j:
                model.addConstr(grafo.edges_number - 1 >= (si[i, g] - si[j, g]) + grafo.edges_number * zij[i, j, g])

    model.addConstr(si[grafo.edges[0], g] == 0)

    for i in grafo.edges[1:]:
        model.addConstr(si[i, g] >= 1)

    # for i, g in grafo.edges:
    # model.addConstr(si[i, g] >= 0)
    # model.addConstr(si[i, g] <= grafo.edges_number - 1)

    model.addConstrs((difij[i, j, g, dim] >= li[i, g, dim] - ri[j, g, dim]) for i, j, g, dim in difij.keys())
    model.addConstrs((difij[i, j, g, dim] >= - li[i, g, dim] + ri[j, g, dim]) for i, j, g, dim in difij.keys())

    model.addConstrs(
        (difij[i, j, g, 0] * difij[i, j, g, 0] + difij[i, j, g, 1] * difij[i, j, g, 1] <= dij[i, j, g] * dij[i, j, g]
         for i, j, g in dij.keys()), name='difij')

    for i, j, g in zij.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = neigh.Polygonal(
            np.array([[grafo.V[first_i, 0], grafo.V[first_i, 1]], [grafo.V[second_i, 0], grafo.V[second_i, 1]]]),
            grafo.A[first_i, second_i])
        segm_j = neigh.Polygonal(
            np.array([[grafo.V[first_j, 0], grafo.V[first_j, 1]], [grafo.V[second_j, 0], grafo.V[second_j, 1]]]),
            grafo.A[first_j, second_j])

        big_m_local = eM.estimate_local_U(segm_i, segm_j)
        small_m_local = eM.estimate_local_L(segm_i, segm_j)

        model.addConstr((pij[i, j, g] <= big_m_local * zij[i, j, g]))
        model.addConstr((pij[i, j, g] <= dij[i, j, g]))
        model.addConstr((pij[i, j, g] >= small_m_local * zij[i, j, g]))
        model.addConstr((pij[i, j, g] >= dij[i, j, g] - big_m_local * (1 - zij[i, j, g])))

    for i, g in rhoi.keys():
        first = i // 100 - 1
        second = i % 100
        model.addConstr(rhoi[i, g] - landai[i, g] == maxi[i, g] - mini[i, g])
        model.addConstr(maxi[i, g] + mini[i, g] == alphai[i, g])
        if alpha:
            model.addConstr(pi[i, g] >= grafo.A[first, second])
        model.addConstr(maxi[i, g] <= 1 - entryi[i, g])
        model.addConstr(mini[i, g] <= entryi[i, g])
        model.addConstr(ri[i, g, 0] == rhoi[i, g] * grafo.V[first, 0] + (1 - rhoi[i, g]) * grafo.V[second, 0])
        model.addConstr(ri[i, g, 1] == rhoi[i, g] * grafo.V[first, 1] + (1 - rhoi[i, g]) * grafo.V[second, 1])
        model.addConstr(li[i, g, 0] == landai[i, g] * grafo.V[first, 0] + (1 - landai[i, g]) * grafo.V[second, 0])
        model.addConstr(li[i, g, 1] == landai[i, g] * grafo.V[first, 1] + (1 - landai[i, g]) * grafo.V[second, 1])

    if not alpha:
        model.addConstr(gp.quicksum(
            pi[i, g] * grafo.edges_length[i // 100 - 1, i % 100] for i in grafo.edges) >= grafo.alpha * grafo.longitud)

    model.update()

    objective = gp.quicksum(pij[i, j, g] for i, j, g in pij.keys()) + gp.quicksum(
        pi[i, g] * grafo.edges_length[i // 100 - 1, i % 100] for i in grafo.edges)

    model.setObjective(objective, GRB.MINIMIZE)
    model.Params.Threads = 8
    # model.Params.NonConvex = 2
    model.Params.TimeLimit = 120
    model.Params.MIPGap = 0.3
    model.update()

    model.optimize()

    if model.Status == 3:
        model.computeIIS()
        model.write('casa.ilp')

    model.write('./heuristic/graph' + str(g) + 'a.sol')

    vals_z = model.getAttr('x', zij)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    # print(selected_z)

    path_d = []

    index_i = grafo.edges[0]
    count = 0

    limit = sum([1 for i1, j1, g in selected_z])

    path_d.append([ri[index_i, g, 0].X, ri[index_i, g, 1].X])
    path_d.append([li[index_i, g, 0].X, li[index_i, g, 1].X])

    path_edges = []

    while count < limit:
        for i, j, g in selected_z:
            if i == index_i:
                count += 1

                path_edges.append(index_i)
                index_i = j
                path_d.append([ri[index_i, g, 0].X, ri[index_i, g, 1].X])
                path_d.append([li[index_i, g, 0].X, li[index_i, g, 1].X])

    # path_edges.append(grafo.edges[0])

    def possible_paths(path_edges):
        paths = []
        # path_edges = path_edges[-1]
        # print(path_edges)

        for a in range(len(path_edges)):
            path = list(np.roll(path_edges, a))
            points = (np.array([li[path[-1], g, 0].X, li[path[-1], g, 1].X]),
                      np.array([ri[path[0], g, 0].X, ri[path[0], g, 1].X]))
            distance_path = model.ObjVal - np.linalg.norm(
                np.array([li[path[-1], g, 0].X, li[path[-1], g, 1].X]) - np.array(
                    [ri[path[0], g, 0].X, ri[path[0], g, 1].X])) - pi[path[-1], g].X * grafo.edges_length[
                                path[-1] // 100 - 1, path[-1] % 100]  # dij[path[-1], path[0]].X
            paths.append([path, points, distance_path])

        return paths

    paths = possible_paths(path_edges)

    # print(paths)

    # fig, ax = plt.subplots()
    #
    # ax.add_artist(Polygon(path_d, fill=False, closed = True, lw = 2, alpha=1, color='red'))
    #
    # centroide = np.mean(grafo.V, axis = 0)
    # nx.draw(grafo.G, grafo.pos, node_size=100, node_color='black', alpha=1, width = 1, edge_color='black')
    # ax.annotate('grafo', xy = (centroide[0], centroide[1]))
    # nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'red', font_size=9)
    #
    # plt.show()

    return paths[0]

# grafo_problem(data)
