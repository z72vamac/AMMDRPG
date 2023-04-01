import bigM_estimation as eM
from neighbourhood import *
from vns import *


# np.random.seed(394)
#
# lista = list(4*np.ones(1, int))
#
# graphs_number = len(lista)
# data = Data([], m=graphs_number, grid = True, time_limit=300, alpha = True, fleet_size = 1, capacgy = 10,
# ing=False,
# show=True,
# seed=2)
#
# data.generate_grid()
# data.generate_graphs(lista)
#
# graph = data.instances[0]
#
# print(graph.edges)

# 78.54 -> 300 sec

# seed = seed_function(data)

# Call the Function
# tiempo1 = time.time()
# lsvns = variable_neighborhood_search(data, cgy_tour = seed, max_attempts = 5, neighbourhood_size = 2, gerations = 10)
# tiempo2 = time.time()

# print('Tiempo total: {0}'.format(tiempo2-tiempo1))

def grafo_problem(graph, alpha, g):
    # graph = data.instances[0]

    # Creamos el modelo
    MODEL = gp.Model("PD-Stages")

    # Variable binaria zij = 1 si voy del segmento i al segmento j del graph g.
    zij_index = []
    si_index = []

    for i in graph.edges:
        si_index.append((i, g))
        for j in graph.edges:
            if i != j:
                zij_index.append((i, j, g))

    zij = MODEL.addVars(zij_index, vtype=GRB.BINARY, name='zigjg')
    si = MODEL.addVars(si_index, vtype=GRB.INTEGER, lb=0, ub=graph.edges_number - 1, name='sig')

    # Variable continua no negativa dij que indica la distancia entre los segmentos i j en el graph g.
    dij_index = zij_index

    dij = MODEL.addVars(dij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='digjg')
    difij = MODEL.addVars(dij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difigjg')

    # Variable continua no negativa pij = zij * dij
    pij_index = zij_index

    pij = MODEL.addVars(pij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pigjg')

    Ri_index = []
    rhoi_index = []

    for i in graph.edges:
        rhoi_index.append((i, g))
        for dim in range(2):
            Ri_index.append((i, g, dim))

    Ri = MODEL.addVars(Ri_index, vtype=GRB.CONTINUOUS, name='Rig')
    rhoi = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS,
                         lb=0.0, ub=1.0, name='rhoig')

    # Li: punto de lanzamiento del dron del segmento si
    Li_index = Ri_index
    landai_index = rhoi_index

    Li = MODEL.addVars(Li_index, vtype=GRB.CONTINUOUS, name='Lig')
    landai = MODEL.addVars(landai_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landaig')

    # Variables difiliares para modelar el valor absoluto
    mini = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='minig')
    maxi = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='maxig')
    entryi = MODEL.addVars(rhoi_index, vtype=GRB.BINARY, name='entryig')
    mui = MODEL.addVars(rhoi_index, vtype=GRB.BINARY, name='muig')
    pi = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='pig')
    alphai = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alphaig')

    MODEL.update()

    MODEL.addConstrs(zij.sum('*', j, g) == 1 for j, g in rhoi.keys())
    MODEL.addConstrs(zij.sum(i, '*', g) == 1 for i, g in rhoi.keys())

    MODEL.addConstrs(pi[i, g] >= mui[i, g] + alphai[i, g] - 1 for i, g in rhoi.keys())
    MODEL.addConstrs(pi[i, g] <= mui[i, g] for i, g in rhoi.keys())
    MODEL.addConstrs(pi[i, g] <= alphai[i, g] for i, g in rhoi.keys())

    for i in graph.edges[1:]:
        for j in graph.edges[1:]:
            if i != j:
                MODEL.addConstr(graph.edges_number - 1 >= (si[i, g] - si[j, g]) + graph.edges_number * zij[i, j, g])

    MODEL.addConstr(si[graph.edges[0], g] == 0)

    for i in graph.edges[1:]:
        MODEL.addConstr(si[i, g] >= 1)

    # for i, g in graph.edges:
    # MODEL.addConstr(si[i, g] >= 0)
    # MODEL.addConstr(si[i, g] <= graph.edges_number - 1)

    MODEL.addConstrs(
        (difij[i, j, g, dim] >= (Li[i, g, dim] - Ri[j, g, dim]) * 14000 / 1e6) for i, j, g, dim in difij.keys())
    MODEL.addConstrs(
        (difij[i, j, g, dim] >= (- Li[i, g, dim] + Ri[j, g, dim]) * 14000 / 1e6) for i, j, g, dim in difij.keys())

    MODEL.addConstrs(
        (difij[i, j, g, 0] * difij[i, j, g, 0] + difij[i, j, g, 1] * difij[i, j, g, 1] <= dij[i, j, g] * dij[i, j, g]
         for i, j, g in dij.keys()), name='difij')

    for i, j, g in zij.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100

        segm_i = Polygonal(
            np.array([[graph.V[first_i, 0], graph.V[first_i, 1]], [graph.V[second_i, 0], graph.V[second_i, 1]]]),
            graph.A[first_i, second_i])
        segm_j = Polygonal(
            np.array([[graph.V[first_j, 0], graph.V[first_j, 1]], [graph.V[second_j, 0], graph.V[second_j, 1]]]),
            graph.A[first_j, second_j])

        BigM_local = eM.estimate_local_U(segm_i, segm_j)
        SmallM_local = eM.estimate_local_L(segm_i, segm_j)

        # BigM_local = 10000
        # SmallM_local = 0
        MODEL.addConstr((pij[i, j, g] <= BigM_local * zij[i, j, g]))
        MODEL.addConstr((pij[i, j, g] <= dij[i, j, g]))
        MODEL.addConstr((pij[i, j, g] >= SmallM_local * zij[i, j, g]))
        MODEL.addConstr((pij[i, j, g] >= dij[i, j, g] - BigM_local * (1 - zij[i, j, g])))

    for i, g in rhoi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhoi[i, g] - landai[i, g] == maxi[i, g] - mini[i, g])
        MODEL.addConstr(maxi[i, g] + mini[i, g] == alphai[i, g])
        if alpha:
            MODEL.addConstr(pi[i, g] >= graph.A[first, second])
        MODEL.addConstr(maxi[i, g] <= 1 - entryi[i, g])
        MODEL.addConstr(mini[i, g] <= entryi[i, g])
        MODEL.addConstr(Ri[i, g, 0] == rhoi[i, g] * graph.V[first, 0] + (1 - rhoi[i, g]) * graph.V[second, 0])
        MODEL.addConstr(Ri[i, g, 1] == rhoi[i, g] * graph.V[first, 1] + (1 - rhoi[i, g]) * graph.V[second, 1])
        MODEL.addConstr(Li[i, g, 0] == landai[i, g] * graph.V[first, 0] + (1 - landai[i, g]) * graph.V[second, 0])
        MODEL.addConstr(Li[i, g, 1] == landai[i, g] * graph.V[first, 1] + (1 - landai[i, g]) * graph.V[second, 1])

    if not (alpha):
        MODEL.addConstr(gp.quicksum(
            pi[i, g] * graph.edges_length[i // 100 - 1, i % 100] for i in graph.edges) >= graph.alpha * graph.length)

    MODEL.update()

    objective = gp.quicksum(pij[i, j, g] for i, j, g in pij.keys()) + gp.quicksum(pi[i, g] * graph.edges_length[i // 100 - 1, i % 100] for i in graph.edges)

    MODEL.setObjective(objective, GRB.MINIMIZE)
    MODEL.Params.Threads = 8
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 60

    MODEL.update()

    MODEL.optimize()

    if MODEL.Status == 3:
        MODEL.computeIIS()
        MODEL.write('casa.ilp')

    # MODEL.write('./heuristic/graph' + str(g) + 'a.sol')

    vals_z = MODEL.getAttr('x', zij)
    selected_z = gp.tuplelist((i, j, g) for i, j, g in vals_z.keys() if vals_z[i, j, g] > 0.5)
    # print(selected_z)

    path_D = []

    index_i = graph.edges[0]
    count = 0

    limit = sum([1 for i1, j1, g in selected_z])

    path_D.append([Ri[index_i, g, 0].X, Ri[index_i, g, 1].X])
    path_D.append([Li[index_i, g, 0].X, Li[index_i, g, 1].X])

    path_edges = []

    while count < limit:
        for i, j, g in selected_z:
            if i == index_i:
                count += 1

                path_edges.append(index_i)
                index_i = j
                path_D.append([Ri[index_i, g, 0].X, Ri[index_i, g, 1].X])
                path_D.append([Li[index_i, g, 0].X, Li[index_i, g, 1].X])

    # path_edges.append(graph.edges[0])

    def possible_paths(path_edges):
        paths = []
        # path_edges = path_edges[-1]
        # print(path_edges)

        for a in range(len(path_edges)):
            path = list(np.roll(path_edges, a))
            points = (np.array([Li[path[-1], g, 0].X, Li[path[-1], g, 1].X]),
                      np.array([Ri[path[0], g, 0].X, Ri[path[0], g, 1].X]))
            distance_path = MODEL.ObjVal - np.linalg.norm(
                np.array([Li[path[-1], g, 0].X, Li[path[-1], g, 1].X]) - np.array(
                    [Ri[path[0], g, 0].X, Ri[path[0], g, 1].X])) - pi[path[-1], g].X * graph.edges_length[
                                path[-1] // 100 - 1, path[-1] % 100]  # dij[path[-1], path[0]].X
            paths.append([path, points, distance_path])

        return paths

    paths = possible_paths(path_edges)

    # print(paths)

    # fig, ax = plt.subplots()
    #
    # ax.add_artist(Polygon(path_D, fill=False, closed = True, lw = 2, alpha=1, color='red'))
    #
    # centroide = np.mean(graph.V, axis = 0)
    # nx.draw(graph.G, graph.pos, node_size=100, node_color='black', alpha=1, width = 1, edge_color='black')
    # ax.annotate('graph', xy = (centroide[0], centroide[1]))
    # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'red', font_size=9)
    #
    # plt.show()

    return paths[0]

# grafo_problem(data)
