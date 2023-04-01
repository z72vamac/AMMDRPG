
############################################################################

# Created by: Prof. Valdecy Pereira, D.Sc.
# UFF - Universidade Federal Fluminense (Brazil)
# email:  valdecy.pereira@gmail.com
# Course: Metaheuristics
# Lesson: Variable Neighborhood Search

# Citation: 
# PEREIRA, V. (2018). Project: Metaheuristic-Local_Search-Variable_Neighborhood_Search, File: Python-MH-Local Search-Variable Neighborhood Search.py, GitHub repository: <https://github.com/Valdecy/Metaheuristic-Local_Search-Variable_Neighborhood_Search>

############################################################################

# Required Libraries
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
import auxiliar_functions as af

# Function: Tour Distance
def distance_calc(datos, city_tour):
    distance = 0
    for k in range(0, len(city_tour[0])-1):
        m = k + 1
        distance = distance + datos[city_tour[0][k]-1, city_tour[0][m]-1]            
    return distance

# Function: Euclidean Distance 
def euclidean_distance(x, y):
    distance = 0
    for j in range(0, len(x)):
        distance = (x[j] - y[j])**2 + distance   
    return distance**(1/2) 

# Function: Initial Seed
def seed_function(datos):
    
    data = datos.data[0]
    aristas = data.aristas
    sequence = aristas.copy()
    random.shuffle(sequence)
    
    seed = [[],float("inf")]
    
    # sequence = random.sample(list(range(1, num_aristas+1)), num_aristas)
    # sequence.append(sequence[0])
    seed[0] = sequence
    seed[1] = modelo(datos, seed[0])
    
    return seed

# Function: Build Distance Matrix
def build_distance_matrix(coordinates):
   a = coordinates
   b = a.reshape(np.prod(a.shape[:-1]), 1, a.shape[-1])
   return np.sqrt(np.einsum('ijk,ijk->ij',  b - a,  b - a)).squeeze()

# Function: Tour Plot
def plot_tour_distance_matrix (datos, city_tour):
    m = np.copy(datos)
    for i in range(0, datos.shape[0]):
        for j in range(0, datos.shape[1]):
            m[i,j] = (1/2)*(datos[0,j]**2 + datos[i,0]**2 - datos[i,j]**2)    
    w, u = np.linalg.eig(np.matmul(m.T, m))
    s = (np.diag(np.sort(w)[::-1]))**(1/2) 
    coordinates = np.matmul(u, s**(1/2))
    coordinates = coordinates.real[:,0:2]
    xy = np.zeros((len(city_tour[0]), 2))
    for i in range(0, len(city_tour[0])):
        if (i < len(city_tour[0])):
            xy[i, 0] = coordinates[city_tour[0][i]-1, 0]
            xy[i, 1] = coordinates[city_tour[0][i]-1, 1]
        else:
            xy[i, 0] = coordinates[city_tour[0][0]-1, 0]
            xy[i, 1] = coordinates[city_tour[0][0]-1, 1]
    plt.plot(xy[:,0], xy[:,1], marker = 's', alpha = 1, markersize = 7, color = 'black')
    plt.plot(xy[0,0], xy[0,1], marker = 's', alpha = 1, markersize = 7, color = 'red')
    plt.plot(xy[1,0], xy[1,1], marker = 's', alpha = 1, markersize = 7, color = 'orange')
    return

# Function: Tour Plot
def plot_tour_coordinates (coordinates, city_tour):
    xy = np.zeros((len(city_tour[0]), 2))
    for i in range(0, len(city_tour[0])):
        if (i < len(city_tour[0])):
            xy[i, 0] = coordinates[city_tour[0][i]-1, 0]
            xy[i, 1] = coordinates[city_tour[0][i]-1, 1]
        else:
            xy[i, 0] = coordinates[city_tour[0][0]-1, 0]
            xy[i, 1] = coordinates[city_tour[0][0]-1, 1]
    plt.plot(xy[:,0], xy[:,1], marker = 's', alpha = 1, markersize = 7, color = 'black')
    plt.plot(xy[0,0], xy[0,1], marker = 's', alpha = 1, markersize = 7, color = 'red')
    plt.plot(xy[1,0], xy[1,1], marker = 's', alpha = 1, markersize = 7, color = 'orange')
    return

# Function: Stochastic 2_opt
def stochastic_2_opt(datos, city_tour):
    best_route = copy.deepcopy(city_tour)      
    i, j  = random.sample(range(0, len(city_tour[0])-1), 2)
    if (i > j):
        i, j = j, i
    
    best_route[0][i:j+1] = list(reversed(best_route[0][i:j+1]))           
    # best_route[0][-1]  = best_route[0][0]        
    print(best_route)      
    best_route[1] = modelo(datos, best_route[0]) 
                        
    return best_route

# Function: Local Search
def local_search(datos, city_tour, max_attempts = 50, neighbourhood_size = 5):
    count = 0
    solution = copy.deepcopy(city_tour) 
    while (count < max_attempts): 
        for i in range(0, neighbourhood_size):
            candidate = stochastic_2_opt(datos, city_tour = solution)
        if candidate[1] < solution[1]:
            solution  = copy.deepcopy(candidate)
            count = 0
        else:
            count = count + 1                             
    return solution 

# Function: Variable Neighborhood Search
def variable_neighborhood_search(datos, city_tour, max_attempts = 20, neighbourhood_size = 5, iterations = 50):
    count = 0
    solution = copy.deepcopy(city_tour)
    best_solution = copy.deepcopy(city_tour)
    while (count < iterations):
        for i in range(0, neighbourhood_size):
            for j in range(0, neighbourhood_size):
                solution = stochastic_2_opt(datos, city_tour = best_solution)
            solution = local_search(datos, city_tour = solution, max_attempts = max_attempts, neighbourhood_size = neighbourhood_size )
            if (solution[1] < best_solution[1]):
                best_solution = copy.deepcopy(solution) 
                break
        count = count + 1
        print("Iteration = ", count, "-> Distance ", best_solution[1])
    return best_solution

def modelo(datos, path):

    grafo = datos.data[0]
    
    # Creamos el modelo
    MODEL = gp.Model("PD-Stages")
    
    # Variable binaria zij = 1 si voy del segmento i al segmento j del grafo g.
    zij_index = []
    si_index = []
    
    for i in grafo.aristas:
        si_index.append(i)
        for j in grafo.aristas:
            if i != j:
                zij_index.append((i, j))
    
    zij = MODEL.addVars(zij_index, vtype=GRB.BINARY, name='zij')
    si = MODEL.addVars(si_index, vtype=GRB.CONTINUOUS, lb=0, ub = grafo.num_aristas-1, name='si')
    
    # Variable continua no negativa dij que indica la distancia entre los segmentos i j en el grafo g.
    dij_index = zij_index
    
    dij = MODEL.addVars(dij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dij')
    difij = MODEL.addVars(dij_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='difij')
    
    # Variable continua no negativa pij = zij * dij
    pij_index = zij_index
    
    pij = MODEL.addVars(pij_index, vtype=GRB.CONTINUOUS, lb=0.0, name='pij')
    
    Ri_index = []
    rhoi_index = []
    
    for i in grafo.aristas:
        rhoi_index.append(i)
        for dim in range(2):
            Ri_index.append((i, dim))
    
    Ri = MODEL.addVars(Ri_index, vtype=GRB.CONTINUOUS, name='Ri')
    rhoi = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS,
                          lb=0.0, ub=1.0, name='rhoi')
    
    # Li: punto de lanzamiento del dron del segmento si
    Li_index = Ri_index
    landai_index = rhoi_index
    
    Li = MODEL.addVars(Li_index, vtype=GRB.CONTINUOUS, name='Li')
    landai = MODEL.addVars(landai_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='landai')
    
    # Variables difiliares para modelar el valor absoluto
    mini = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='mini')
    maxi = MODEL.addVars(rhoi_index, vtype=GRB.CONTINUOUS, lb=0.0, ub = 1.0, name='maxi')
    entryi = MODEL.addVars(rhoi_index, vtype=GRB.BINARY, name='entryi')
    mui = MODEL.addVars(rhoi_index, vtype = GRB.BINARY, name = 'mui')
    pi = MODEL.addVars(rhoi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'pi')
    alphai = MODEL.addVars(rhoi_index, vtype = GRB.CONTINUOUS, lb = 0.0, ub = 1.0, name = 'alphai')
    
    MODEL.update()
    
    MODEL.addConstrs(zij.sum('*', j) == 1 for j in rhoi.keys()) 
    MODEL.addConstrs(zij.sum(i, '*') == 1 for i in rhoi.keys()) 
    
    for p in range(len(path)-1):
        MODEL.addConstr(zij[path[p], path[p+1]] == 1)
        
    # for p in range(len(path)-1):
        # MODEL.addConstr(si[path[p]] == p)
    
    MODEL.addConstrs(pi[i] >= mui[i] + alphai[i] - 1 for i in rhoi.keys())
    MODEL.addConstrs(pi[i] <= mui[i] for i in rhoi.keys())
    MODEL.addConstrs(pi[i] <= alphai[i] for i in rhoi.keys())
    
    # MODEL.addConstrs(mui[i] == 1 for i in rhoi.keys())
    
    # for i in grafo.aristas[1:]:
        # for j in grafo.aristas[1:]:
            # if i != j:
                # MODEL.addConstr(grafo.num_aristas - 1 >= (si[i] - si[j]) + grafo.num_aristas * zij[i, j])
                #
    # MODEL.addConstr(si[grafo.aristas[0]] == 0)
    
    # for i in grafo.aristas[1:]:
        # MODEL.addConstr(si[i] >= 1)
    
    
    MODEL.addConstrs((difij[i, j, dim] >=   Li[i, dim] - Ri[j, dim]) for i, j, dim in difij.keys())
    MODEL.addConstrs((difij[i, j, dim] >= - Li[i, dim] + Ri[j, dim]) for i, j, dim in difij.keys())
    
    MODEL.addConstrs((difij[i, j, 0]*difij[i, j, 0] + difij[i, j, 1] * difij[i, j, 1] <= dij[i, j] * dij[i, j] for i, j in dij.keys()), name = 'difij')
    
    
    for i, j in zij.keys():
        first_i = i // 100 - 1
        second_i = i % 100
        first_j = j // 100 - 1
        second_j = j % 100
    
        segm_i = Poligonal(np.array([[grafo.V[first_i, 0], grafo.V[first_i, 1]], [
                           grafo.V[second_i, 0], grafo.V[second_i, 1]]]), grafo.A[first_i, second_i])
        segm_j = Poligonal(np.array([[grafo.V[first_j, 0], grafo.V[first_j, 1]], [
                           grafo.V[second_j, 0], grafo.V[second_j, 1]]]), grafo.A[first_j, second_j])
    
        BigM_local = eM.estima_BigM_local(segm_i, segm_j)
        SmallM_local = eM.estima_SmallM_local(segm_i, segm_j)
        
        BigM_local = 10000
        SmallM_local = 0
        MODEL.addConstr((pij[i, j] <= BigM_local * zij[i, j]))
        MODEL.addConstr((pij[i, j] <= dij[i, j]))
        MODEL.addConstr((pij[i, j] >= SmallM_local * zij[i, j]))
        MODEL.addConstr((pij[i, j] >= dij[i, j] - BigM_local * (1 - zij[i, j])))
        
    
    for i in rhoi.keys():
        first = i // 100 - 1
        second = i % 100
        MODEL.addConstr(rhoi[i] - landai[i] == maxi[i] - mini[i])
        MODEL.addConstr(maxi[i] + mini[i] >= alphai[i])
        if datos.alpha:
            MODEL.addConstr(pi[i] >= grafo.A[first, second])
        MODEL.addConstr(maxi[i] <= 1 - entryi[i])
        MODEL.addConstr(mini[i] <= entryi[i])
        MODEL.addConstr(Ri[i, 0] == rhoi[i] * grafo.V[first, 0] + (1 - rhoi[i]) * grafo.V[second, 0])
        MODEL.addConstr(Ri[i, 1] == rhoi[i] * grafo.V[first, 1] + (1 - rhoi[i]) * grafo.V[second, 1])
        MODEL.addConstr(Li[i, 0] == landai[i] * grafo.V[first, 0] + (1 - landai[i]) * grafo.V[second, 0])
        MODEL.addConstr(Li[i, 1] == landai[i] * grafo.V[first, 1] + (1 - landai[i]) * grafo.V[second, 1])
    
    if not(datos.alpha):
        MODEL.addConstr(gp.quicksum(pi[i]*grafo.longaristas[i // 100 - 1, i % 100] for i in grafo.aristas) >= grafo.alpha*grafo.longitud)
    
    MODEL.update()
    
    objective = gp.quicksum(pij[i, j] for i, j in pij.keys()) + gp.quicksum(pi[i]*grafo.longaristas[i // 100 - 1, i % 100] for i in grafo.aristas)
    
    MODEL.setObjective(objective, GRB.MINIMIZE)
    # MODEL.Params.Threads = 8
    MODEL.Params.OutputFlag = 1
    # MODEL.Params.NonConvex = 2
    MODEL.Params.timeLimit = 300
    
    MODEL.update()
    
    MODEL.optimize()
    
    return MODEL.ObjVal
######################## Part 1 - Usage ####################################

# Load File - A Distance Matrix (17 cities,  optimal = 1922.33)
#X = pd.read_csv('Python-MH-Local Search-Variable Neighborhood Search-Dataset-01.txt', sep = '\t')
#X = X.values
#
## Start a Random Seed
#seed = seed_function(X)
#
## Call the Function
#lsvns = variable_neighborhood_search(X, city_tour = seed, max_attempts = 25, neighbourhood_size = 5, iterations = 1000)
#
## Plot Solution. Red Point = Initial city; Orange Point = Second City # The generated coordinates (2D projection) are aproximated, depending on the data, the optimum tour may present crosses
#plot_tour_distance_matrix(X, lsvns)
#
######################### Part 2 - Usage ####################################
#
## Load File - Coordinates (Berlin 52,  optimal = 7544.37)
#Y = pd.read_csv('Python-MH-Local Search-Variable Neighborhood Search-Dataset-02.txt', sep = '\t')
#Y = Y.values
#
## Build the Distance Matrix
#X = buid_distance_matrix(Y)
#
## Start a Random Seed
#seed = seed_function(X)
#
## Call the Function
#lsvns = variable_neighborhood_search(X, city_tour = seed, max_attempts = 25, neighbourhood_size = 5, iterations = 1000)
#
## Plot Solution. Red Point = Initial city; Orange Point = Second City
#plot_tour_coordinates(Y, lsvns)