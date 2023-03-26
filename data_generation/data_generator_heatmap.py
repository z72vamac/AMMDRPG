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

instances = {}

r = 1

endurances = [10, 20, 30, 40, 50, 60]
drones = [1, 2, 3]
grid = True

time_limit = 7200

graphs_number = len(list_1)
grid = True
data = Data([], graphs_number=graphs_number, grid=grid, initialization=False, time_limit=time_limit, seed=seed)

data.generate_grid()
data.generate_graphs(list_1)

# for lista, j in zip(lists, range(len(lists))):
# for alpha in alpha_list:
for c in endurances:
    for d in drones:
        # for i in range(5):
        data.time_endurance = c
        data.fleet_size = d

        instances[(c, d)] = data

with open("instancias_heatmap.pickle", "wb") as pickle_out:
    pickle.dump(instances, pickle_out)
