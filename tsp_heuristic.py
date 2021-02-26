"""Tenemos un conjunto E de entornos y un conjunto de poligonales P de las que queremos recorrer un porcentaje alfa p . Buscamos
   un tour de mínima distancia que alterne poligonal-entorno y que visite todas las poligonales"""


# Incluimos primero los paquetes
import gurobipy as gp
import pdb
from gurobipy import GRB
import numpy as np
from itertools import product
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
from data import *
from entorno import *
import copy
import estimacion_M as eM
import networkx as nx
import auxiliar_functions as af
from MTZ import *

# np.random.seed(2)
# orig = [50, 50]
# dest = orig
#
# nG = 20
# datos = Data([], m=nG, r=3, modo=4, tmax=120, alpha = True,
#              init=True,
#              show=True,
#              seed=2)
# datos.generar_grafos()
# grafos = datos.mostrar_datos()
#
# T_index = range(datos.m + 2)
# T_index_prima = range(1, datos.m+1)
# T_index_primaprima = range(datos.m+1)
#
# vD = 2
#
# vC = 1

def heuristic(datos):

    grafos = datos.mostrar_datos()

    T_index = range(datos.m + 2)
    T_index_prima = range(1, datos.m+1)
    T_index_primaprima = range(datos.m+1)

    orig= [50,50]
    dest = orig

    first_time = time.time()
    results = []
    centroides = {}

    for g in T_index_prima:
        centroides[g] = np.mean(grafos[g-1].V, axis = 0)

    centros = []
    centros.append(orig)
    for g in centroides.values():
        centros.append(g)
    centros.append(dest)

    elipses = []

    radio = 2

    for c in centros:
        P = np.identity(2)
        q = -2*np.array(c)
        r = c[0]**2 + c[1]**2 - radio**2
        elipse = Elipse(P, q, r)
        elipses.append(elipse)

    elipse = Data(elipses, m = 6, r = 2, grid = True, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)

    path_1, path_P, obj  = MTZ(elipse)

    # prim = path[1]
    # seg = path[2]
    # path[1] = seg
    # path[2] = prim

    z = af.path2matrix(path_1)

    xL, xR, obj = af.XPPNZ(datos, z, orig, dest, 0)

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
    # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
    # path, path_P, obj  = MTZ(elipse)
    # print(path)
    # path = tsp(points)

    # u_dict = {}
    # zgij_dict = {}
    # v_dict = {}
    #
    # for g in path[1:-1]:
    #     print('PROBLEMA del Grafo: ' + str(path[g]))
    #     vals_u, vals_zgij, vals_v, obj = af.XPPND(datos, xL_dict[g], grafos[g-1], xL_dict[g+1])
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

    xL, xR, obj, path_2 = af.XPPNxl(datos, xL_dict, xR_dict, orig, dest, 0)

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
    while not(all([i == j for i, j in zip(path_1, path_2)]) or all([i == j for i, j in zip(path_app, path_2)])):
        path_1=path_2

        z = af.path2matrix(path_1)

        # print()
        # print('--------------------------------------------')
        # print('Exact Formulation: Fixing w. Iteration: {i})'.format(i = iter))
        # print('--------------------------------------------')
        # print()

        xL, xR, obj = af.XPPNZ(datos, z, orig, dest, 0)

        for g in T_index:
            xL_dict[g] = [xL[(g, 0)], xL[(g, 1)]]
            xR_dict[g] = [xR[(g, 0)], xR[(g, 1)]]


        xL, xR, obj, path_2 = af.XPPNxl(datos, xL_dict, xR_dict, orig, dest, 0)

        path_app = path_1.copy()
        path_app.reverse()
        # print(path_1)
        # print(path_2)
        # print(path_app)

        iter += 1

    second_time = time.time()
    runtime = second_time - first_time

    if datos.init:
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
        if datos.grid:
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
# elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)



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
#     elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
#
#     path, path_P, obj  = MTZ(elipse)
#
#     elipses = [elipses[a] for a in path]
#     grafos = [grafos[a-1] for a in path[1:-1]]
#     datos = Data(grafos, m=nG, r=3, modo=4, tmax=120, alpha = True,
#                  init=True,
#                  show=True,
#                  seed=2)
#
#     #xL, xR, obj, path = af.XPPNe(datos, orig, dest, elipses, i)
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
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
#     #
#     # path, path_P, obj = MTZ(elipse)
#     # z = af.path2matrix(path)
#
#     # grafos = [grafos[a-1] for a in path[1:-1]]
#     # elipses = [elipses[a] for a in path]
#     #
#     # datos = Data(grafos, m=nG, r=3, modo=4, tmax=120, alpha = True,
#     #              init=True,
#     #              show=True,
#     #              seed=2)
#
#
#
#     # xL_dict = dict(sorted(xL_dict.items(), key=lambda x: x[0]))
#     xL, xR, obj = af.XPPNZ(datos, z, orig, dest, i, elipses)
#
#
#
#
#
#
#
#
#
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
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
#     # elipse = Data(elipses, m = 6, r = 2, modo = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
#     #
#     # xL, xR, obj = af.XPPNZ(datos, z, orig, dest, i+1, elipses)
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
#     # elipse = Data(elipses, m = 6, r = 2, modo  = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
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
# #     elipse = Data(elipses, m = 6, r = 2, modo = 4, alpha = True, tmax = 1200, init = 0, prepro = 0, refor = 0, show = True, seed = 2)
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
#     grafo = grafos[g-1]
#     nx.draw(grafo.G, grafo.pos, node_size=20,
#             node_color='black', alpha=0.3, edge_color='gray')
#     ax.annotate(g, xy = (centroides[g][0], centroides[g][1]))
#
#
# for c in centros:
#     plt.plot(c[0], c[1], 'ko', markersize=1, color='cyan')
#
# plt.show()
