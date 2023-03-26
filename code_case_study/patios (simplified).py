# Incluimos primero los paquetes
import copy

import pandas as pd

import neighbourhood as e
# from AMMDRPGST import AMMDRPGST
from asynchronous_version import asynchronous
from data import *

data = []

for i in range(1, 7):
    puntos = pd.read_excel('./patios_breakpoints_simplified.xlsx', sheet_name='Ruta' + str(i))

    puntos['y'] = 200 - puntos['y']

    V = copy.copy(puntos.to_numpy())

    m = V.shape[0]

    Ar = np.zeros((m + 1, m + 1))

    if i == 1 or i == 2 or i == 5:
        for j in range(m):
            Ar[j, j + 1] = 1

    if i == 3:
        for j in range(13):
            Ar[j, j + 1] = 1

        Ar[2, 14] = 1
        Ar[14, 15] = 1

    if i == 4:
        for j in range(20):
            Ar[j, j + 1] = 1

        Ar[16, 21] = 1
        Ar[17, 22] = 1

    if i == 6:
        for j in range(19):
            Ar[j, j + 1] = 1

        Ar[2, 20] = 1
        Ar[20, 21] = 1
        Ar[11, 22] = 1
        Ar[12, 23] = 1

    data.append(e.Graph(V, Ar, 1))

data = Data(data, graphs_number=6, grid_mode=True, time_limit=5, alpha=False, fleet_size=2, time_endurance=0.123672786,
             initialization=False,
             show=True,
             truck_speed=30,
             drone_speed=43,
             origin=[0, 0],
             destination=[0, 0],
             seed=2)

print(sum([grafo.longitud for grafo in data]))  # *14000/1e6)

# velocities = np.linspace(1.5, 3, 16)

# for n in range(1, 4):
#     for cap in range(200, 205, 5):
#         for v in range(len(velocities)):
#             data = Data(data, m=6, grid = True, time_limit=1, alpha = False, fleet_size = n, time_endurance = cap,
#                         initialization=False,
#                         show=True,
#                         drone_speed = velocities[v],
#                         origin = [0, 0],
#                         destination = [0, 0],
#                         seed=2)
#
#             fig, ax = plt.subplots()
#
#             grafos = data.instances

# colors = ['blue', 'purple', 'cyan', 'orange', 'red', 'green']
# for g in range(1, 7):
# grafo = grafos[g-1]
# centroide = np.mean(grafo.V, axis = 0)
# nx.draw(grafo.G, grafo.pos, node_size=2, node_color=colors[g-1], alpha=1, width = 2, edge_color= colors[g-1])
# ax.annotate(g, xy = (centroide[0], centroide[1]+3.5))
# nx.draw_networkx_labels(grafo.G, grafo.pos, font_color = 'white', font_size=9)


asynchronous(data)

# plt.show()
