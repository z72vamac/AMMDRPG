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
from AMMDRPGST import AMMDRPGST
from PDMTZ import PDMTZ
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

np.random.seed(123)

lista = list(4*np.ones(3, np.int))

nG = len(lista)
datos = Data([], m=nG, grid = True, tmax=90, alpha = True, nD = 1, capacity = 20,
             init=False,
             show=True,
             seed=2)

datos.generar_grid()
datos.generar_grafos(lista)

AMMDRPGST(datos)
