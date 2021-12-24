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
from synchronous_version_withoutd import SYNCHRONOUS
# from synchronous_version import SYNCHRONOUS
from asynchronous_version import ASYNCHRONOUS
from heuristic import heuristic
from heuristicSINC import heuristicSINC

# from PDSEC import PDSEC
# from TDST import TDST
# from TDMTZ import TDMTZ
# from TDSEC import TDSEC
# from tsp_heuristic import heuristic

# Definicion de los datos
""" P: conjunto de poligonales a agrupar
    E: conjunto de entornos
    T: sucesion de etapas
    C(e): centro del entorno e
    R(e): radio del entorno e
    p: indice de las poligonales
    e: indice de los entornos
    t: indice de las etapas
    n: dimension del problema
"""

# np.random.seed(120310)
# np.random.seed(7)
np.random.seed(13)


# Experimento para ver diferencias
# datos = Data([], m=2, grid = True, tmax=600, alpha = False, nD = 2, capacity = 5.2,
#             init=False,
#             show=True, 
#             vD = 5.11,
#             orig = [0, 5],
#             dest = [20, 5],
#             seed=2)
#
# datos.generar_grafo_personalizado(1)


lista = list(4*np.ones(10, int))

nG = len(lista)

datos = Data([], m=nG, grid = True, tmax=3600, alpha = True, nD = 2, capacity = 30,
            init=True,
            show=True,
            vD = 2,
            orig = [0, 0],
            dest = [100, 0],
            seed=2)

datos.generar_grid()
datos.generar_grafos(lista)

# for g in datos.data:
#     print(g.V)

# np.random.seed(30)

# np.random.seed(6)
## 117.949

# lista = list(4*np.ones(2, int))
# nG = len(lista)
# datos = Data([], m=nG, grid = True, tmax=150, alpha = True, nD = 2,
#              orig = [0, 0],
#              dest = [100, 0],
#              vD = 1.3,
#              init=False,
#              show=True,
#              capacity = 46,
#              seed=2)
#
# datos.generar_grid()
#
# datos.generar_grafos(lista)

SYNCHRONOUS(datos)

# ASYNCHRONOUS(datos)
# AMMDRPGSTSINC(datos)


# result1 = AMMDRPGSTSINC(datos) # 153.82 a los 150 segundos
# Sin solucion inicial: 104.104 a los 600 segundos
# Con solucion inicial: 94.66
# result2 = synchronous_version(datos) # 195.7856
# heuristicSINC(datos)

# print([result1[-3], result2[-1]])
# print(result2[-1])
