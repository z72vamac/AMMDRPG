from AMMDRPGSTSINCPARTIAL import AMMDRPGSTSINCPARTIAL
from agglomerative_algorithm import agglomerative
from grafo_problem import grafo_problem
from vns import *


# # Primer paso: Generamos data
# np.random.seed(5)
#
# lista = list(4*np.ones(10, int))
#
# graphs_number = len(lista)
# data = Data([], m=graphs_number, grid = True, time_limit=60, alpha = True, fleet_size4, time_endurance = 30,
# initialization=False,
# show=True,
# seed=2)
#
# data.generate_grid() 
# data.generate_graphs(lista)

def heuristicSINC(data):
    # Segundo paso: Resolvemos utilizando graph problem 

    graphs_number = data.graphs_number

    paths = []

    for g in range(1, graphs_number + 1):
        path = grafo_problem(data.instances[g - 1], data.alpha)
        paths.append(path)

    print()
    print(paths)
    print()

    seeds = 20

    best_clusters = {}
    # best_Ck = {}
    best_uigtd = {}
    best_vigtd = {}
    best_objval = 100000
    best_path = []

    for i in range(seeds):
        np.random.seed(i)

        # Tercer paso: Algoritmo agglomerative para clustering_hard
        clusters = agglomerative(data, paths)

        objVal, uigtd, vigtd = AMMDRPGSTSINCPARTIAL(data, clusters)

        # # Cuarto paso: Resolvemos la localizacion de los puntos una vez formado el clustering_hard
        # C_k = clustering_easy(data, paths, clusters)
        #
        # path, objVal = tsp(C_k)
        #
        if objVal <= best_objval:
            best_clusters = clusters
            best_objval = objVal
            # best_Ck = C_k
            best_uigtd = uigtd
            best_vigtd = vigtd
            best_path = path

    uigtd_sol = best_uigtd
    vigtd_sol = best_vigtd

    # for i, t in zip(best_path, range(1, len(best_path)+1)):
    # for g, d in zip(best_clusters[i], range(len(best_clusters[i]))):
    # e1 = paths[g-1][0][0]
    # e2 = paths[g-1][0][-1]
    # uigtd_sol.append((e1, g, t, d))
    # vigtd_sol.append((e2, g, t, d))
    #
    # print(uigtd_sol)
    # print(vigtd_sol)

    print()
    print(best_clusters)
    print(best_objval)
    print(uigtd_sol)
    print(vigtd_sol)

    # print(best_path)

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

    return uigtd_sol, vigtd_sol
