# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 08:31:09 2020

En este documento generamos los data segÃºn las configuraciones detalladas
en el documento xpp_segmentos2.

@author: Carlos
"""

import math
import random
from copy import copy
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
# Paquetes
import numpy as np
from scipy.spatial import Delaunay

import neighbourhood as e


class Data(object):

    def __init__(self, instances, graphs_number, grid_mode=True, time_limit=100, alpha=False, initialization=True, drone_speed = 3, truck_speed = 1,
                 origin=[50, 50], destination=[50, 50], fleet_size time_endurance=30, scale=1, seed=0):
        self.instances = instances
        self.graphs_number = graphs_number
        self.grid_mode = grid_mode
        self.time_limit = time_limit
        self.alpha = alpha
        self.initialization = initialization
        self.drone_speed = drone_speed
        self.truck_speed = truck_speed
        self.origin = origin
        self.destination = destination
        self.fleet_sizeflefleet_size
        self.time_endurance = time_endurance
        self.scale = scale
        self.grid_list = []
        random.seed(seed)

    def generate_customized_graph(self, mode=0):

        self.mode = mode

        if self.mode == 1:
            # Mode 1: Arbol
            A = [11, 20]
            B = [11, 20.00001]
            # C = [11, 51]
            # D = [11, 50]
            # E = [70, 30]
            # F = [70, 70]

            # V = np.array([A, B, C, D])
            V = np.array([A, B])

            Ar = np.zeros((len(V), len(V)))

            Ar[0, 1] = 1
            # Ar[1, 2] = 1
            # Ar[2, 3] = 1
            # Ar[0, 3] = 1
            # Ar[3, 5] = 1

            # self.origin = A
            # self.destination = F

            self.instances.append(e.Graph(V, Ar, 1e-6))

            A = [13, 20]
            B = [13, 20.00001]
            # C = [21, 51]
            # D = [21, 50]
            # E = [70, 30]
            # F = [70, 70]

            # V = np.array([A, B, C, D])
            V = np.array([A, B])

            Ar = np.zeros((len(V), len(V)))

            Ar[0, 1] = 1
            # Ar[1, 2] = 1
            # Ar[2, 3] = 1
            # Ar[0, 3] = 1
            # Ar[3, 5] = 1

            # self.origin = A
            # self.destination = F

            self.instances.append(e.Graph(V, Ar, 1e-6))

        if self.mode == 2:
            # Mode 2: Triangulo
            A = [30, 30]
            B = [70, 30]
            C = [50, 70]
            D = [50, 50]

            V = np.array([A, B, C, D])

            Ar = np.zeros((len(V), len(V)))

            Ar[0, 1] = 1
            Ar[0, 2] = 1
            Ar[0, 3] = 1
            Ar[1, 2] = 1
            Ar[1, 3] = 1
            Ar[2, 3] = 1

            self.origin = A
            self.destination = D

            self.instances.append((e.Graph(V, Ar, 1)))

        if self.mode == 3:
            # Mode 3: Estrella hexagonal
            A = [30, 20]
            B = [60, 20]
            C = [75, 46]
            D = [60, 72]
            E = [30, 72]
            F = [15, 46]
            G = [45, 46]

            V = np.array([A, B, C, D, E, F, G])

            Ar = np.zeros((len(V), len(V)))

            Ar[0, 6] = 1
            Ar[1, 6] = 1
            Ar[2, 6] = 1
            Ar[3, 6] = 1
            Ar[4, 6] = 1
            Ar[5, 6] = 1

            self.origin = G
            self.destination = G

            self.instances.append((e.Graph(V, Ar, 1)))

    def generate_grid(self):
        div = 10

        grid_list = []

        for graph_number in range(self.graphs_number):
            a = np.random.randint(0, div)
            b = np.random.randint(0, div)
            if (a, b) not in grid_list:
                self.grid_list.append((a, b))


    def generate_graphs(self, nV_list=[]):

        self.instances = []

        div = 10
        x = np.linspace(0, 100, div + 1)
        y = np.linspace(0, 100, div + 1)

        if self.grid_mode:
            # Grid
            for nV, tuple in zip(nV_list, self.grid_list):
                a, b = tuple
                nsg_x = (x[a + 1] - x[a]) / nV
                nsg_y = (y[b + 1] - y[b]) / nV

                V1x = np.random.uniform(x[a], x[a] + nsg_x, 1)
                V1y = np.random.uniform(y[b], y[b] + nsg_y, 1)

                V2x = np.random.uniform(x[a + 1] - nsg_x, x[a + 1], 1)
                V2y = np.random.uniform(y[b + 1] - nsg_y, y[b + 1], 1)

                lista = []
                for i in range(2, nV - 1):
                    if nV % i == 0:
                        lista.append(i)

                flag = np.random.randint(0, len(lista))

                n_row = int(lista[flag])
                n_col = int(nV / lista[flag])

                Vx = np.linspace(V1x, V2x, n_col)
                Vy = np.linspace(V1y, V2y, n_row)

                nVx = len(Vx)
                nVy = len(Vy)

                width_x = (Vx[1] - Vx[0]) / 3
                width_y = (Vy[1] - Vy[0]) / 3

                lista = []
                for i in range(n_row):
                    for j in range(n_col):
                        lista.append([Vx[j], Vy[i]])

                V = np.array(lista)

                V = np.reshape(V, (nV, 2))

                edges = []

                coordinates = [(i, j) for i in range(n_row) for j in range(n_col)]

                for tuple1 in coordinates:
                    for tuple2 in coordinates:
                        if (abs(tuple1[0] - tuple2[0]) + abs(tuple1[1] - tuple2[1]) == 1) & (
                                n_col * tuple1[0] + tuple1[1] > n_col * tuple2[0] + tuple2[1]):
                            edges.append((n_col * tuple2[0] + tuple2[1], n_col * tuple1[0] + tuple1[1]))

                per_x = np.random.uniform(-width_x, width_x, nV)
                per_y = np.random.uniform(-width_y, width_y, nV)

                for v in range(nV):
                    V[v][0] = V[v][0] + per_x[v]
                    if (V[v][0] <= 0):
                        V[v][0] = 0
                    elif (V[v][0] >= 100):
                        V[v][0] = 100
                    V[v][1] = V[v][1] + per_y[v]
                    if (V[v][1] <= 0):
                        V[v][1] = 0
                    elif (V[v][1] >= 100):
                        V[v][1] = 100

                G = nx.Graph()

                for v in range(nV):
                    G.add_node(v)

                for edge in edges:
                    G.add_edge(edge[0], edge[1])

                alpha = np.random.rand(nV, nV)

                A = np.zeros((nV, nV))

                for i, j in combinations(range(nV), 2):
                    if (i, j) in G.edges:
                        A[i, j] = alpha[i, j]

                alpha = np.random.rand()

                self.instances.append(e.Graph(V, A, alpha))
        else:
            # Delaunay
            for nV, tuple in zip(nV_list, self.grid_list):
                a, b = tuple
                Vx = np.random.uniform(x[a], x[a + 1], nV)
                Vy = np.random.uniform(y[b], y[b + 1], nV)

                V = np.array([[xi, yi] for xi, yi in zip(Vx, Vy)])

                tri = Delaunay(V)

                G = nx.Graph()

                for v in range(nV):
                    G.add_node(v)

                for path in tri.simplices:
                    nx.add_path(G, path)

                alpha = np.random.rand(nV, nV)

                A = np.zeros((nV, nV))

                for i, j in combinations(range(nV), 2):
                    if (i, j) in G.edges:
                        A[i, j] = alpha[i, j]

                alpha = np.random.rand()

                self.instances.append(e.Graph(V, A, alpha))

    def show_data(self):
        return self.instances

    # def imprimir_data(self):
    #     for i in self.instances:
    #         print(i)

    def change_initiliazation(self):
        if self.initialization:
            self.initialization = False
        else:
            self.initialization = True

    # def generar_punto(self):
    #     P = np.random.uniform(0, 100, 2)
    #     self.data.append(e.Punto(P))

    # def generar_ciclo(self):
    #     # genero radio en funcion del tamaÃ±o
    #     radio = 5 * np.random.uniform(self.r - 1, self.r)
    #     V = []
    #     # genero un centro en el cuadrado [0, 100]
    #     P = np.random.uniform(radio, 100 - radio, 2)
    #     nV = np.random.randint(4, 7)
    #     theta = np.linspace(0, 2 * math.pi, nV + 1)
    #     x = P[0] + radio * np.cos(theta)
    #     y = P[1] + radio * np.sin(theta)

    #     V = np.array([[i, j] for i, j in zip(x, y)])

    #     self.data.append(e.Polygonal(V, 1))

    # def generar_muestra(self):
    #     if self.modo == 1:
    #         for i in range(self.m):
    #             self.generar_elipse()
    #     if self.modo == 2:
    #         for i in range(self.m):
    #             self.generar_poligono()
    #     if self.modo == 3:
    #         for i in range(self.m):
    #             self.generar_poligonal()
    #     if self.modo == 4:
    #         for i in range(self.m):
    #             self.generar_grafo()
    #     if self.modo == 5:
    #         for i in range(self.m):
    #             self.generar_punto()
    #     if self.modo == 6:
    #         for i in range(self.m):
    #             flag = np.random.randint(1, 5)
    #             if flag == 1:
    #                 self.generar_elipse()
    #             elif flag == 2:
    #                 self.generar_poligono()
    #             elif flag == 3:
    #                 self.generar_poligonal()
    #             elif flag == 4:
    #                 self.generar_grafo()
    #             else:
    #                 self.generar_punto()

    # def dibujar_muestra(self):
    #     if self.initialization:
    #         ax2 = plt.gca()
    #         # ax2 = fig.add_subplot(111)

    #         min_x = []
    #         max_x = []
    #         min_y = []
    #         max_y = []

    #         for c in range(self.m):
    #             dato = self.instances[c]
    #             if type(dato) is e.Ellipsoid:
    #                 min_x.append(dato.center[0] - dato.width)
    #                 max_x.append(dato.center[0] + dato.width)
    #                 min_y.append(dato.center[1] - dato.height)
    #                 max_y.append(dato.center[1] + dato.height)
    #                 ax2.annotate(s=str(c), xy=(dato.center[0], dato.center[1]))
    #             if type(dato) is e.Polygon:
    #                 min_x.append(min(P[0] for P in dato.V))
    #                 max_x.append(max(P[0] for P in dato.V))
    #                 min_y.append(min(P[1] for P in dato.V))
    #                 max_y.append(max(P[1] for P in dato.V))
    #                 ax2.annotate(s=str(c), xy=(
    #                     dato.barycenter[0], dato.barycenter[1]))

    #             ax2.add_artist(dato.artist)
    #             # dato = self.olddata[c]
    #             # if type(dato) is e.Elipse:
    #             #     min_x.append(dato.centro[0] - dato.width)
    #             #     max_x.append(dato.centro[0] + dato.width)
    #             #     min_y.append(dato.centro[1] - dato.height)
    #             #     max_y.append(dato.centro[1] + dato.height)
    #             #     ax2.annotate(s = str(c), xy=(dato.centro[0], dato.centro[1]))
    #             # if type(dato) is e.Poligonal or type(dato) is e.Poligono:
    #             #     min_x.append(min(P[0] for P in dato.V))
    #             #     max_x.append(max(P[0] for P in dato.V))
    #             #     min_y.append(min(P[1] for P in dato.V))
    #             #     max_y.append(max(P[1] for P in dato.V))
    #             #     ax2.annotate(s = str(c), xy=(dato.baricentro[0], dato.baricentro[1]))
    #             # ax2.add_artist(dato.artist)

    #         # ax2.autoscale_view()
    #         ax2.axis([0, 100, 0, 100])
    #         # ax2.axis([min(min_x)-1, max(max_x)+1, min(min_y)-1, max(max_y)+1])
    #         ax2.set_aspect('equal')
    #         self.initialization = False

    #     if not (self.initialization):
    #         fig = plt.gcf()

    #     return fig