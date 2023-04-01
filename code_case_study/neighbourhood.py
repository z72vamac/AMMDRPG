# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:01:34 2019

@author: Carlos
"""

# Required packages
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx
from itertools import combinations

class Ellipsoid(object):
    def __init__(self, P, q, r):
        """
        Ellipsoid represented by x'Px + q'x + r <= 0
        """
        self.P = P
        self.invP = np.linalg.inv(P)
        self.q = q
        self.r = r
        self.num_landa = 0
        self.G = np.linalg.cholesky(P).T
        self.invG = np.linalg.inv(self.G).T
        self.center = np.array(
            [-0.5 * (float(self.q[0]) / self.P[0, 0]), -0.5 * (float(self.q[1]) / self.P[1, 1])])
        self.radii = np.sqrt(
            self.P[0, 0] * self.center[0] ** 2 + self.P[1, 1] * self.center[1] ** 2 - self.r)
        self.width = 2 * float(self.radii) / self.P[0, 0]
        self.height = 2 * float(self.radii) / self.P[1, 1]
        self.artist = mpatches.Ellipse(
            self.center, self.width, self.height, color='grey', alpha=0.5)

    def getPqr(self):
        print("P = \n" + str(self.P) + "\n"
              + "q = \n" + str(self.q) + "\n"
              + "r = \n" + str(self.r))

    def modify_radii(self, radii):
        self.radii = radii

    def modify_center(self, center):
        self.center = center

    def modify_figure(self):
        self.width = 2 * np.sqrt(float(self.radii) / self.P[0, 0])
        self.height = 2 * np.sqrt(float(self.radii) / self.P[1, 1])
        self.artist = mpatches.Ellipse(
            self.center, self.width, self.height, alpha=0.1)


class Point(object):
    def __init__(self, V):
        self.V = V


class Polygon(object):
    def __init__(self, V):
        """
        Polygon represented as the convex hull of its vertices
        V: Set of vertices
        """
        self.V = V
        self.barycenter = np.mean(self.V, axis=0)
        self.points_number = len(V)
        self.segments_number = self.points_number - 1
        self.path = []
        self.lengths = []

        for v in range(self.segments_number):
            self.lengths.append(np.linalg.norm(self.V[v] - self.V[v + 1]))

        self.length = sum(self.lengths)

        for s in V:
            self.path.append(s)
        self.artist = mpatches.Polygon(
            self.path, fill=False, facecolor=None)


class Polygonal(object):
    def __init__(self, V, alpha):
        """
        V: Set of vertices of the polygonal chain
        alpha: percentage of the length of the polygonal to traverse
        """
        self.V = V
        self.points_number = len(V)
        self.segments_number = self.points_number - 1
        self.alpha = alpha
        self.lengths = []

        for v in range(self.segments_number):
            self.lengths.append(np.linalg.norm(self.V[v] - self.V[v + 1]))

        self.length = sum(self.lengths)

        # self.artist = mlines.Line2D([self.V[i][0] for i in range(self.num_Points)], [
        #                               self.V[i][1] for i in range(self.num_Points)], color='k', alpha=0.1)
        self.artist = mpatches.Polygon(
            V, fill=False, facecolor=None)


class Graph(object):
    def __init__(self, V, A, alpha):
        """
        V: Set of the vertices of the graph
        A: Set of edges and percentage of traversing:
        If A(i, j) == 0: There is not edge
        Si 0 < A(i, j) < 1: There exists an edge and it must be traversed an A(i, j) of its total length.
        """
        self.V = V
        self.A = A
        self.points_number = len(V)
        self.edges_number = np.count_nonzero(self.A)
        self.edges = []

        self.edges_length = np.zeros_like(self.A)
        self.lengths = []

        length = 0

        for i, j in combinations(range(self.points_number), 2):
            if A[i, j] > 0:
                self.edges_length[i, j] = np.linalg.norm(self.V[i] - self.V[j])
                length += self.edges_length[i, j]
        self.length = length

        self.G = nx.Graph()

        for i in range(self.points_number):
            self.G.add_node(i, pos=V[i])

        for i, j in combinations(range(self.points_number), 2):
            if A[i, j] > 0:
                self.G.add_edge(i, j)
                self.edges.append(100 * (i + 1) + j)

        for e in self.edges:
            first = e // 100 - 1
            second = e % 100
            self.lengths.append(np.linalg.norm(self.V[first] - self.V[second]))

        self.alpha = alpha
        self.pos = nx.get_node_attributes(self.G, 'pos')

        # self.artist = nx.draw(G, self.pos, node_size=20)
