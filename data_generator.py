"""
Created on Thu Nov  5 11:31:51 2020

@author: rafaelblanquero
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from data import *
from itertools import combinations
import auxiliar_functions as af
from data import *
from entorno import *
import csv
from entorno import *
import estimacion_M as eM
# import ujson
import json
import pickle
import copy

seed = np.random.seed(2)
lista_1 = [4, 6, 8, 10, 12]
lista_2 = [4, 4, 6, 6, 8, 8, 10, 10, 12, 12]
lista_3 = [4, 4, 4, 6, 6, 6, 8, 8, 8, 10, 10, 10, 12, 12, 12]
lista_4 = [4, 4, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]

listas = [lista_1, lista_2, lista_3, lista_4]

instancias = {}
# lista_deulonay = {}
# lista_ciclo = {}

r = 1
alpha_list = [True, False]
capacitys = [20, 30, 40, 50, 60]
drones = [1, 2, 3]
grid = True
init = True

tmax = 3600

for lista, j in zip(listas, range(len(listas))):
    for alpha in alpha_list:
        for c in capacitys:
            for d in drones:
                for i in range(5):
                    m = len(lista)
                    grid = True
                    datos = Data([], m = m, grid = grid, tmax = tmax, alpha = alpha, nD = d, capacity= c, seed = seed)
                    datos.generar_grid()
        
                    datos.generar_grafos(lista)
        
                    instancias[(i, len(lista), alpha, c, d)] = datos

            # grid = False+
            # datos2= copy.copy(datos)
            #
            # datos2.grid = grid
            #
            # datos2.generar_grafos(lista)
            # instancias[(i, j, alpha, grid)] = datos2

# print(instancias)

    # ciclos = Data([], m = 1, r = 6, grid = False, tmax=120, alpha = True,
    #                 init = True,
    #                 show = True,
    #                 seed = 2)
    # ciclos.generar_ciclo()
    #
    # ciclo = ciclos.mostrar_datos()[0]
    # lista_ciclo[i] = ciclo
with open("instancias.pickle","wb") as pickle_out:
    pickle.dump(instancias, pickle_out)


# with open("instancias_grid.pickle","wb") as pickle_out:
#     pickle.dump(lista_grid, pickle_out)
#
# with open("instancias_deulonay.pickle","wb") as pickle_out:
#     pickle.dump(lista_deulonay, pickle_out)
#
# with open("instancias_ciclos.pickle", "wb") as pickle_out:
#     pickle.dump(lista_ciclo, pickle_out)
