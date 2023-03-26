# Auxiliar function used in some files of the project.

import numpy as np


def path2matrix(path):
    "Toma un camino y lo devuelve como matriz de adyacencia"
    m = len(path)
    zcc = np.zeros([m, m])
    for i in range(m - 1):
        zcc[path[i]][path[i + 1]] = 1
    zcc[path[m - 1]][path[0]] = 1
    return zcc


def matrix2path(matrix):
    " Toma una matriz y lo devuelve como camino "
    matrix = np.array(matrix, int)
    ind = 0
    path = []
    while ind not in path:
        path.append(ind)
        lista = matrix[ind]
        counter = 0
        for i in lista:
            if i == 1:
                ind = counter
                break
            counter += 1
    return path


def subtour(edges):
    "Genera un subtour de una lista de aristas"
    m = len(edges)
    unvisited = list(range(m))
    cycle = range(m + 1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


def subtours(edges):
    "Genera un subtour de una lista de aristas"
    m = len(edges)
    unvisited = edges
    cycle = range(m + 1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited] + [i for i, j in edges.select('*', current) if i in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle
