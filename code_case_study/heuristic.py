import time

from agglomerative_algorithm import agglomerative
from clustering_easy import clustering_easy
from grafo_problem import grafo_problem
from tsp import tsp
from vns import *


# # Primer paso: Generamos data
# np.random.seed(5)
#
# lista = list(4*np.ones(10, int))
#
# graphs_number = len(lista)
# data = Data([], m=graphs_number, grid = True, time_limit=60, alpha = True, fleet_size = 4, time_endurance = 30,
# initialization=False,
# show=True,
# seed=2)
#
# data.generate_grid() 
# data.generate_graphs(lista)

def heuristic(data):
    # Segundo paso: Resolvemos utilizando graph problem 

    first_time = time.time()

    graphs_number = data.graphs_number

    paths = []

    for g in range(1, graphs_number + 1):
        path = grafo_problem(data.instances[g - 1], data.alpha, g)
        paths.append(path)

    print()
    print(paths)
    print()

    seeds = 20

    best_clusters = {}
    best_Ck = {}
    best_objval = 100000
    best_path = []

    for i in range(seeds):
        np.random.seed(i)

        # Tercer paso: Algoritmo agglomerative para clustering_hard
        clusters = agglomerative(data, paths)

        # Cuarto paso: Resolvemos la localizacion de los puntos una vez formado el clustering_hard
        C_k = clustering_easy(data, paths, clusters)

        if C_k == None:
            continue

        path, objVal = tsp(C_k)

        if objVal <= best_objval:
            best_clusters = clusters
            best_objval = objVal
            best_Ck = C_k
            best_path = path

    uigtd_sol = []
    vigtd_sol = []

    for i, t in zip(best_path, range(1, len(best_path) + 1)):
        for g in best_clusters[i]:
            e1 = paths[g - 1][0][0]
            e2 = paths[g - 1][0][-1]
            uigtd_sol.append((e1, g, t))
            vigtd_sol.append((e2, g, t))

    print(uigtd_sol)
    print(vigtd_sol)

    with open('solution_heuristic.txt', 'a') as f:

        f.write('Coordinates of the graphs squares. V[')

        for g, it in zip(data.instances, range(len(data.instances))):
            for i, it2 in zip(g.V, range(len(g.V))):
                f.write('V[{0}, {1}] = {2}\n'.format(it2, it, i))

        f.write('Centroids: ' + str(best_Ck) + '\n')
        f.write('Clusters labels: ' + str(best_clusters) + '\n')
        f.write('Path labels: ' + str(best_path) + '\n')

    z_sol = []

    for lista, it in zip(paths, range(1, len(paths) + 1)):
        for i in range(len(lista[0]) - 1):
            z_sol.append((lista[0][i], lista[0][i + 1], it))

    # with open('./case_study/z.')
    # f.close('solution_heuristic.txt', 'a')

    # f.write(best_Ck)

    print(best_Ck)
    print(best_clusters)
    # print(best_objval)
    print(paths)
    print(z_sol)
    print(best_path)

    # fig, ax = plt.subplots()
    #
    # for g in range(1, data.graphs_number+1):
    # graph = data.instances[g-1]
    # centroide = np.mean(graph.V, axis = 0)
    # nx.draw(graph.G, graph.pos, node_size=100, node_color='black', alpha=1, width = 1, edge_color='black')
    # ax.annotate(g, xy = (centroide[0], centroide[1]))
    # nx.draw_networkx_labels(graph.G, graph.pos, font_color = 'red', font_size=9)
    #
    # colores = ['blue', 'green', 'red', 'purple', 'black', 'yellow', 'brown']
    #
    # for (k, i) in zip(best_clusters.keys(), range(len(best_clusters.keys()))):
    # plt.plot(best_Ck[(k, 0)], best_Ck[(k, 1)], 'ko', color = colores[i])
    # ax.annotate(k, xy = (best_Ck[(k, 0)], best_Ck[(k, 1)]))
    #
    # plt.show()

    second_time = time.time()

    heuristic_time = second_time - first_time

    return uigtd_sol, vigtd_sol, z_sol, heuristic_time
