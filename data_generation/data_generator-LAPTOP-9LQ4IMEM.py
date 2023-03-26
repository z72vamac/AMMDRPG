"""
Created on Thu Nov  5 11:31:51 2020

@author: rafaelblanquero
"""

# import ujson
import pickle

from neighbourhood import *
from data import Data

seed = np.random.seed(2)
list_1 = [4, 6, 8, 10, 12]
list_2 = [4, 4, 6, 6, 8, 8, 10, 10, 12, 12]
list_3 = [4, 4, 4, 6, 6, 6, 8, 8, 8, 10, 10, 10, 12, 12, 12]
list_4 = [4, 4, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]

lists = [list_1, list_2, list_3, list_4]

instances = {}
# lista_deulonay = {}
# lista_ciclo = {}

r = 1
alpha_list = [True, False]
endurances = [20, 30, 40, 50, 60]
drones = [1, 2, 3]
grid = True
initialization = True

time_limit = 3600

for lista, j in zip(lists, range(len(lists))):
    for alpha in alpha_list:
        for c in endurances:
            for d in drones:
                for i in range(5):
                    graphs_number = len(lista)
                    grid_mode = True
                    data = Data([], graphs_number=graphs_number, grid_mode=grid_mode, time_limit=time_limit, alpha=alpha, fleet_size=d, time_endurance=c, seed=seed)
                    data.generate_grid()

                    data.generate_graphs(lista)

                    instances[(i, len(lista), alpha, c, d)] = data

            # grid = False+
            # data2= copy.copy(data)
            #
            # data2.grid = grid
            #
            # data2.generate_graphs(lista)
            # instances[(i, j, alpha, grid)] = data2

# print(instances)

# ciclos = Data([], m = 1, r = 6, grid = False, time_limit=120, alpha = True,
#                 initialization = True,
#                 show = True,
#                 seed = 2)
# ciclos.generar_ciclo()
#
# ciclo = ciclos.mostrar_data()[0]
# lista_ciclo[i] = ciclo
with open("instances.pickle", "wb") as pickle_out:
    pickle.dump(instances, pickle_out)

# with open("instancias_grid.pickle","wb") as pickle_out:
#     pickle.dump(lista_grid, pickle_out)
#
# with open("instancias_deulonay.pickle","wb") as pickle_out:
#     pickle.dump(lista_deulonay, pickle_out)
#
# with open("instancias_ciclos.pickle", "wb") as pickle_out:
#     pickle.dump(lista_ciclo, pickle_out)
