from itertools import chain, permutations, combinations

import gurobipy as gp
import numpy as np
from gurobipy import GRB


def tsp(C_k):
    """
    Input: Centroids C_k
    Output: Order
    """

    print()
    print('Resolviendo el TSP con los centroides del cluster generado')
    print()

    def powerset(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(2, len(s) + 1))

    K_index = []

    for k, i in C_k.keys():
        if i < 1:
            K_index.append(k)

    KK_index = []

    for k1 in K_index:
        for k2 in K_index:
            if k1 != k2:
                KK_index.append((k1, k2))

    MODEL = gp.Model("TSP")

    zkk = MODEL.addVars(KK_index, vtype=GRB.BINARY, name='zkk')

    MODEL.update()

    MODEL.addConstrs(zkk.sum('*', k) == 1 for k in K_index)
    MODEL.addConstrs(zkk.sum(k, '*') == 1 for k in K_index)

    restricciones = MODEL.addConstrs(
        gp.quicksum(zkk[v, w] for v, w in permutations(set, 2)) <= len(set) - 1 for set in list(powerset(K_index)) if
        len(set) < len(K_index))
    restricciones.Lazy = 3

    objective = gp.quicksum(
        np.linalg.norm(np.array([C_k[(k1, 0)], C_k[(k1, 1)]]) - np.array([C_k[(k2, 0)], C_k[(k2, 1)]])) * zkk[k1, k2] for
        k1, k2 in KK_index)

    MODEL.setObjective(objective, GRB.MINIMIZE)

    MODEL.Params.OutputFlag = 0

    MODEL.optimize()

    # MODEL.computeIIS()
    # MODEL.write('tsp_infeasible.ilp')

    vals_zkk = MODEL.getAttr('x', zkk)
    selected_zkk = gp.tuplelist((k1, k2) for k1, k2 in vals_zkk.keys() if vals_zkk[k1, k2] > 0.5)
    # print(selected_zkk)

    first_k = K_index[0]
    path = [first_k]

    while len(path) < len(K_index):
        for i, j in selected_zkk:
            if i == first_k:
                path.append(j)
                first_k = j
                break

    print('Path: ' + str(path))

    return path, MODEL.ObjVal
