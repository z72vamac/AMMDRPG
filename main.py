# Incluimos primero los paquetes
# from synchronous_version import SYNCHRONOUS
from asynchronous_version import asynchronous
from neighbourhood import *
from data import *

# from PDSEC import PDSEC
# from TDST import TDST
# from TDMTZ import TDMTZ
# from TDSEC import TDSEC
# from tsp_heuristic import heuristic

# Definicion de los data
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
# data = Data([], m=2, grid = True, time_limit=600, alpha = False, fleet_size2, time_endurance = 5.2,
#             initialization=False,
#             show=True, 
#             drone_speed = 5.11,
#             origin = [0, 5],
#             destination = [20, 5],
#             seed=2)
#
# data.generar_grafo_personalizado(1)


# lista = list(4*np.ones(10, int))
#
# graphs_number = len(lista)
#
# data = Data([], m=graphs_number, grid = True, time_limit=3600, alpha = True, fleet_size2, time_endurance = 30,
#             initialization=True,
#             show=True,
#             drone_speed = 2,
#             origin = [0, 0],
#             destination = [100, 0],
#             seed=2)
#
# data.generate_grid()
# data.generate_graphs(lista)

# for g in data.instances:
#     print(g.V)

# np.random.seed(30)

np.random.seed(6)
## 117.949

lista = list(4 * np.ones(4, int))
graphs_number = len(lista)
data = Data([], graphs_number=graphs_number, grid_mode=True, time_limit=150, alpha=True, fleet_size
             origin=[0, 0],
             destination=[100, 0],
             drone_speed=1.3,
             initialization=True,
             time_endurance=46,
             seed=2)

data.generate_grid()

data.generate_graphs(lista)

# SYNCHRONOUS(data)

asynchronous(data)
# AMMDRPGSTSINC(data)


# result1 = AMMDRPGSTSINC(data) # 153.82 a los 150 segundos
# Sin solucion inicial: 104.104 a los 600 segundos
# Con solucion inicial: 94.66
# result2 = synchronous_version(data) # 195.7856
# heuristicSINC(data)

# print([result1[-3], result2[-1]])
# print(result2[-1])
