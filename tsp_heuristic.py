"""Tenemos un conjunto E de entornos y un conjunto de poligonales P de las que queremos recorrer un porcentaje alfa p . Buscamos
   un tour de mínima distancia que alterne poligonal-entorno y que visite todas las poligonales"""

# Incluimos primero los paquetes
from neighbourhood import *
from mtz import *


# np.random.seed(2)
# origin = [50, 50]
# destination = origin
#
# graphs_number = 20
# data = Data([], m=graphs_number, r=3, modo=4, time_limit=120, alpha = True,
#              initialization=True,
#              show=True,
#              seed=2)
# data.generate_graphs()
# graphs = data.graphs_numberostrar_data()
#
# T_index = range(data.graphs_number + 2)
# T_index_prima = range(1, data.graphs_number+1)
# T_index_primaprima = range(data.graphs_number+1)
#
# drone_speed = 2
#
# vC = 1

def heuristic(data):
    graphs = data.graphs_numberostrar_data()

    T_index = range(data.graphs_number + 2)
    T_index_prima = range(1, data.graphs_number + 1)
    T_index_primaprima = range(data.graphs_number + 1)

    origin = [50, 50]
    destination = origin

    first_time = time.time()
    results = []
    centroides = {}

    for g in T_index_prima:
        centroides[g] = np.mean(graphs[g - 1].V, axis=0)

    centros = []
    centros.append(origin)
    for g in centroides.values():
        centros.append(g)
    centros.append(destination)

    elipses = []

    radio = 2

    for c in centros:
        P = np.identity(2)
        q = -2 * np.array(c)
        r = c[0] ** 2 + c[1] ** 2 - radio ** 2
        elipse = Ellipsoid(P, q, r)
        elipses.append(elipse)

    elipse = Data(elipses, graphs_number=6, r=2, grid_mode=True, alpha=True, time_limit=1200, initialization=0, prepro=0, refor=0, show=True, seed=2)

    path_1, path_P, obj = mtz(elipse)

    # prim = path[1]
    # s_eg = path[2]
    # path[1] = s_eg
    # path[2] = prim

    z = af.path2matrix(path_1)

    xL, xR, obj = af.XPPNZ(data, z, origin, destination, 0)

    xL_dict = {}
    xR_dict = {}

    for g in T_index:
        xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
        xR_dict[g] = [xR[(g, 0)], xR[(g, 1)]]

    # points = list(xL_dict.values())
    #
    # elipses = []
    #
    # radio = 0.05
    # for c in points:
    #     P = np.identity(2)
    #     q = -2*np.array(c)
    #     r = c[0]**2 + c[1]**2 - radio**2
    #     elipse = Elipse(P, q, r)
    #     elipses.append(elipse)
    #
    # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
    # path, path_P, obj  = MTZ(elipse)
    # print(path)
    # path = tsp(points)

    # u_dict = {}
    # zgij_dict = {}
    # v_dict = {}
    #
    # for g in path[1:-1]:
    #     print('PROBLEMA del graph: ' + str(path[g]))
    #     vals_u, vals_zgij, vals_v, obj = af.XPPND(data, xL_dict[g], graphs[g-1], xL_dict[g+1])
    #     for key, value in vals_u.items():
    #         u_dict[(g, key)] = value
    #     for key, value in vals_zgij.items():
    #         zgij_dict[(g, key[0], key[1])] = value
    #     for key, value in vals_v.items():
    #         v_dict[(g, key)] = value
    #
    # print(u_dict)
    # iter = 0
    # z = af.path2matrix(path)
    # print(z)

    xL, xR, obj, path_2 = af.XPPNxl(data, xL_dict, xR_dict, origin, destination, 0)

    # print()
    # print('--------------------------------------------')
    # print('Exact Formulation: Fixing points. Iteration: 0')
    # print('--------------------------------------------')
    # print()

    print(path_1)

    path_app = path_1.copy()
    path_app.reverse()

    print(path_app)
    iter = 1
    while not (all([i == j for i, j in zip(path_1, path_2)]) or all([i == j for i, j in zip(path_app, path_2)])):
        path_1 = path_2

        z = af.path2matrix(path_1)

        # print()
        # print('--------------------------------------------')
        # print('Exact Formulation: Fixing w. Iteration: {i})'.format(i = iter))
        # print('--------------------------------------------')
        # print()

        xL, xR, obj = af.XPPNZ(data, z, origin, destination, 0)

        for g in T_index:
            xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
            xR_dict[g] = [xR[(g, 0)], xR[(g, 1)]]

        xL, xR, obj, path_2 = af.XPPNxl(data, xL_dict, xR_dict, origin, destination, 0)

        path_app = path_1.copy()
        path_app.reverse()
        # print(path_1)
        # print(path_2)
        # print(path_app)

        iter += 1

    second_time = time.time()
    runtime = second_time - first_time

    if data.initialization:
        z = af.path2matrix(path_2)

        for g in T_index:
            xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
            xR_dict[g] = [xR[(g, 0)], xR[(g, 1)]]

        results.append(obj)
        results.append(runtime)
        return z, xL_dict, xR_dict, results
    else:

        results.append(obj)
        results.append(runtime)
        if data.grid:
            results.append('Grid')
        else:
            results.append('Delauney')

        print(results)
        return results
# xL_dict = dict(sorted(xL_dict.items(), key=lambda x: x[0]))


# radio = 0.5
# elipses = []
# for c in xL_dict.values():
#     P = np.identity(2)
#     q = -2*np.array(c)
#     r = c[0]**2 + c[1]**2 - radio**2
#     elipse = Elipse(P, q, r)
#     elipses.append(elipse)
#
# elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)


# objective = []
# objective.append(10000)
#
# for i in range(1, 5):
#
#     xL_dict = {}
#
#     for g in T_index:
#         xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
#
#     xL_dict = dict(sorted(xL_dict.items(), key=lambda x: x[0]))
#
#     radio = 0.5
#     elipses = []
#     for c in xL_dict.values():
#         P = np.identity(2)
#         q = -2*np.array(c)
#         r = c[0]**2 + c[1]**2 - radio**2
#         elipse = Elipse(P, q, r)
#         elipses.append(elipse)
#
#     elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#
#     path, path_P, obj  = MTZ(elipse)
#
#     elipses = [elipses[a] for a in path]
#     graphs = [graphs[a-1] for a in path[1:-1]]
#     data = Data(graphs, m=graphs_number, r=3, modo=4, time_limit=120, alpha = True,
#                  initialization=True,
#                  show=True,
#                  seed=2)
#
#     #xL, xR, obj, path = af.XPPNe(data, origin, destination, elipses, i)
#
#     z = af.path2matrix(path)
#
#     # xL_dict = {}
#     #
#     # for g in T_index:
#     #     xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
#     #
#     # radio = 0.5
#     # elipses = []
#     # for c in xL_dict.values():
#     #     P = np.identity(2)
#     #     q = -2*np.array(c)
#     #     r = c[0]**2 + c[1]**2 - radio**2
#     #     elipse = Elipse(P, q, r)
#     #     elipses.append(elipse)
#     #
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#     #
#     # path, path_P, obj = MTZ(elipse)
#     # z = af.path2matrix(path)
#
#     # graphs = [graphs[a-1] for a in path[1:-1]]
#     # elipses = [elipses[a] for a in path]
#     #
#     # data = Data(graphs, m=graphs_number, r=3, modo=4, time_limit=120, alpha = True,
#     #              initialization=True,
#     #              show=True,
#     #              seed=2)
#
#
#
#     # xL_dict = dict(sorted(xL_dict.items(), key=lambda x: x[0]))
#     xL, xR, obj = af.XPPNZ(data, z, origin, destination, i, elipses)
#
#
#
#
#
#
#
#
#
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#
#
#     # radio = 3
#     # elipses = []
#     # for c in path_P:
#     #     P = np.identity(2)
#     #     q = -2*np.array(c)
#     #     r = c[0]**2 + c[1]**2 - radio**2
#     #     elipse = Elipse(P, q, r)
#     #     elipses.append(elipse)
#     #
#     # elipse = Data(elipses, m = 6, r = 2, modo = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#     #
#     # xL, xR, obj = af.XPPNZ(data, z, origin, destination, i+1, elipses)
#     #
#     #
#     # # print(xL)
#     # xL_dict = {}
#     #
#     # for g in T_index:
#     #     xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
#     #
#     # # xL_dict = dict(sorted(xL_dict.items(), key=lambda x: x[0]))
#     #
#     # radio = 3
#     # elipses = []
#     # for c in xL_dict.values():
#     #     P = np.identity(2)
#     #     q = -2*np.array(c)
#     #     r = c[0]**2 + c[1]**2 - radio**2
#     #     elipse = Elipse(P, q, r)
#     #     elipses.append(elipse)
#
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#
#     # path, path_P, obj = MTZ(elipse)
#
# #     xL_val = np.zeros((len(path)+1, 2))
# #     xR_val = np.zeros((len(path)+1, 2))
# #
# #     #
# #     for index in xL:
# #         xL_val[index] = xL[index]
# #         xR_val[index] = xR[index]
# #
# # #   xL_val = path_P
# #
# #     radio = 0.05
# #     elipses = []
# #     for c in xL_val:
# #         P = np.identity(2)
# #         q = -2*np.array(c)
# #         r = c[0]**2 + c[1]**2 - radio**2
# #         elipse = Elipse(P, q, r)
# #         elipses.append(elipse)
# #
# #     elipse = Data(elipses, m = 6, r = 2, modo = 4, alpha = True, time_limit = 1200, initialization = 0, prepro = 0, refor = 0, show = True, seed = 2)
#     if obj >= min(objective) and i >= 5:
#         objective.append(obj)
#         break
#     else:
#         objective.append(obj)
#
#
# print(objective)
#
# fig, ax = plt.subplots()
# plt.axis([0, 100, 0, 100])
#
# for g in T_index_prima:
#     graph = graphs[g-1]
#     nx.draw(graph.G, graph.pos, node_size=20,
#             node_color='black', alpha=0.3, edge_color='gray')
#     ax.annotate(g, xy = (centroides[g][0], centroides[g][1]))
#
#
# for c in centros:
#     plt.plot(c[0], c[1], 'ko', markersize=1, color='cyan')
#
# plt.show()
