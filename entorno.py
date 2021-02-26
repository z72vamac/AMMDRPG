# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:01:34 2019

@author: Carlos
"""

import numpy as np
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import networkx as nx
from itertools import combinations
from data import *
import matplotlib.pyplot as plt


class Elipse(object):
    def __init__(self, P, q, r):
        """
        Elipse representada de la forma x'Px + q'x + r <= 0
        """
        self.P = P
        self.invP = np.linalg.inv(P)
        self.q = q
        self.r = r
        self.num_landa = 0
        self.G = np.linalg.cholesky(P).T
        self.invG = np.linalg.inv(self.G).T
        self.centro = np.array(
            [-0.5*(float(self.q[0])/self.P[0, 0]), -0.5*(float(self.q[1])/self.P[1, 1])])
        self.radio = np.sqrt(
            self.P[0, 0]*self.centro[0]**2 + self.P[1, 1]*self.centro[1]**2-self.r)
        self.width = 2*float(self.radio)/self.P[0, 0]
        self.height = 2*float(self.radio)/self.P[1, 1]
        self.artist = mpatches.Ellipse(
            self.centro, self.width, self.height, color='grey', alpha=0.5)

    def getPqr(self):
        print("P = \n" + str(self.P) + "\n"
              + "q = \n" + str(self.q) + "\n"
              + "r = \n" + str(self.r))

    def cambiar_radio(self, radio):
        self.radio = radio

    def cambiar_centro(self, centro):
        self.centro = centro

    def cambiar_figura(self):
        self.width = 2*np.sqrt(float(self.radio)/self.P[0, 0])
        self.height = 2*np.sqrt(float(self.radio)/self.P[1, 1])
        self.artist = mpatches.Ellipse(
            self.centro, self.width, self.height, alpha=0.1)

class Punto(object):
    def __init__(self, V):
        self.V = V

class Poligono(object):
    def __init__(self, V):
        """
        Poligono representado como envolvente convexa de sus vértices
        V: Conjunto de vértices del Poligono
        """
        self.V = V
        self.baricentro = np.mean(self.V, axis=0)
        self.num_puntos = len(V)
        self.num_segmentos = self.num_puntos - 1
        self.path = []
        self.longitudes = []

        for v in range(self.num_segmentos):
            self.longitudes.append(np.linalg.norm(self.V[v] - self.V[v+1]))

        self.longitud = sum(self.longitudes)

        for s in V:
            self.path.append(s)
        self.artist = mpatches.Polygon(
            self.path, fill = False, facecolor=None)


class Poligonal(object):
    def __init__(self, V, alpha):
        """
        V: Conjunto de vértices de la Poligonal
        alpha: porcentaje deseado de recorrido de la poligonal
        """
        self.V = V
        self.num_puntos = len(V)
        self.num_segmentos = self.num_puntos - 1
        self.alpha = alpha
        self.longitudes = []

        for v in range(self.num_segmentos):
            self.longitudes.append(np.linalg.norm(self.V[v] - self.V[v+1]))

        self.longitud = sum(self.longitudes)

        # self.artist = mlines.Line2D([self.V[i][0] for i in range(self.num_puntos)], [
        #                               self.V[i][1] for i in range(self.num_puntos)], color='k', alpha=0.1)
        self.artist = mpatches.Polygon(
                V, fill = False, facecolor=None)

class Grafo(object):
    def __init__(self, V, A, alpha):
        """
        V: Conjunto de vértices del Grafo
        A: Conjunto de aristas y su porcentaje de recorrido:
        Si A(i, j) == 0: No existe arista
        Si 0 < A(i, j) < 1: Existe la arista y se tiene que recorrer ese porcentaje
        """
        self.V = V
        self.A = A
        self.num_puntos = len(V)
        self.num_aristas = np.count_nonzero(self.A)
        self.aristas = []

        self.longaristas = np.zeros_like(self.A)
        self.longitudes = []

        longitud = 0

        for i, j in combinations(range(self.num_puntos), 2):
            if A[i, j] > 0:
                self.longaristas[i, j] = np.linalg.norm(self.V[i] - self.V[j])
                longitud += self.longaristas[i, j]
        self.longitud = longitud

        self.G = nx.Graph()

        for i in range(self.num_puntos):
            self.G.add_node(i, pos=V[i])

        for i, j in combinations(range(self.num_puntos), 2):
            if A[i, j] > 0:
                self.G.add_edge(i, j)
                self.aristas.append(100*(i+1) + j)

        for e in self.aristas:
            first = e // 100 - 1
            second = e % 100
            self.longitudes.append(np.linalg.norm(self.V[first] - self.V[second]))

        self.alpha = alpha
        self.pos = nx.get_node_attributes(self.G, 'pos')

        # self.artist = nx.draw(G, self.pos, node_size=20)
