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
import copy

import gurobipy as gp
from gurobipy import GRB

import bigM_estimation as eM
import neighbourhood as neigh
import random
import numpy as np
import matplotlib.pyplot as plt


# Function: Tour Distance
def distance_calc(data, city_tour):
    distance = 0
    for k in range(0, len(city_tour[0]) - 1):
        m = k + 1
        distance = distance + data[city_tour[0][k] - 1, city_tour[0][m] - 1]
    return distance


# Function: Euclidean Distance
def euclidean_distance(x, y):
    distance = 0
    for j in range(0, len(x)):
        distance = (x[j] - y[j]) ** 2 + distance
    return distance ** (1 / 2)


# Function: Initial Seed
def seed_function(data):
    data = data.instances[0]
    aristas = data.edges
    sequence = aristas.copy()
    random.shuffle(sequence)

    seed = [[], float("inf")]

    seed[0] = sequence
    seed[1] = model(data, seed[0])

    return seed


# Function: Build Distance Matrix
def build_distance_matrix(coordinates):
    a = coordinates
    b = a.reshape(np.prod(a.shape[:-1]), 1, a.shape[-1])
    return np.sqrt(np.einsum('ijk,ijk->ij', b - a, b - a)).squeeze()


# Function: Tour Plot
def plot_tour_distance_matrix(data, city_tour):
    m = np.copy(data)
    for i in range(0, data.shape[0]):
        for j in range(0, data.shape[1]):
            m[i, j] = (1 / 2) * (data[0, j] ** 2 + data[i, 0] ** 2 - data[i, j] ** 2)
    w, u = np.linalg.eig(np.matmul(m.T, m))
    s = (np.diag(np.sort(w)[::-1])) ** (1 / 2)
    coordinates = np.matmul(u, s ** (1 / 2))
    coordinates = coordinates.real[:, 0:2]
    xy = np.zeros((len(city_tour[0]), 2))
    for i in range(0, len(city_tour[0])):
        if (i < len(city_tour[0])):
            xy[i, 0] = coordinates[city_tour[0][i] - 1, 0]
            xy[i, 1] = coordinates[city_tour[0][i] - 1, 1]
        else:
            xy[i, 0] = coordinates[city_tour[0][0] - 1, 0]
            xy[i, 1] = coordinates[city_tour[0][0] - 1, 1]
    plt.plot(xy[:, 0], xy[:, 1], marker='s', alpha=1, markersize=7, color='black')
    plt.plot(xy[0, 0], xy[0, 1], marker='s', alpha=1, markersize=7, color='red')
    plt.plot(xy[1, 0], xy[1, 1], marker='s', alpha=1, markersize=7, color='orange')
    return


# Function: Tour Plot
def plot_tour_coordinates(coordinates, city_tour):
    xy = np.zeros((len(city_tour[0]), 2))
    for i in range(0, len(city_tour[0])):
        if (i < len(city_tour[0])):
            xy[i, 0] = coordinates[city_tour[0][i] - 1, 0]
            xy[i, 1] = coordinates[city_tour[0][i] - 1, 1]
        else:
            xy[i, 0] = coordinates[city_tour[0][0] - 1, 0]
            xy[i, 1] = coordinates[city_tour[0][0] - 1, 1]
    plt.plot(xy[:, 0], xy[:, 1], marker='s', alpha=1, markersize=7, color='black')
    plt.plot(xy[0, 0], xy[0, 1], marker='s', alpha=1, markersize=7, color='red')
    plt.plot(xy[1, 0], xy[1, 1], marker='s', alpha=1, markersize=7, color='orange')
    return


# Function: Stochastic 2_opt
def stochastic_2_opt(data, city_tour):
    best_route = copy.deepcopy(city_tour)
    i, j = random.sample(range(0, len(city_tour[0]) - 1), 2)
    if (i > j):
        i, j = j, i

    best_route[0][i:j + 1] = list(reversed(best_route[0][i:j + 1]))
    # best_route[0][-1]  = best_route[0][0]        
    print(best_route)
    best_route[1] = model(data, best_route[0])

    return best_route


# Function: Local Search
def local_search(data, city_tour, max_attempts=50, neighbourhood_size=5):
    count = 0
    solution = copy.deepcopy(city_tour)
    while (count < max_attempts):
        for i in range(0, neighbourhood_size):
            candidate = stochastic_2_opt(data, city_tour=solution)
        if candidate[1] < solution[1]:
            solution = copy.deepcopy(candidate)
            count = 0
        else:
            count = count + 1
    return solution


# Function: Variable Neighborhood Search
def variable_neighborhood_search(data, city_tour, max_attempts=20, neighbourhood_size=5, iterations=50):
    count = 0
    solution = copy.deepcopy(city_tour)
    best_solution = copy.deepcopy(city_tour)
    while (count < iterations):
        for i in range(0, neighbourhood_size):
            for j in range(0, neighbourhood_size):
                solution = stochastic_2_opt(data, city_tour=best_solution)
            solution = local_search(data, city_tour=solution, max_attempts=max_attempts,
                                    neighbourhood_size=neighbourhood_size)
            if (solution[1] < best_solution[1]):
                best_solution = copy.deepcopy(solution)
                break
        count = count + 1
        print("Iteration = ", count, "-> Distance ", best_solution[1])
    return best_solution


def model(data, path):
    graph = data.instances[0]

    # Initializing the model
    MODEL = gp.Model("PD-Stages")

    # Binary variable flow_e1_e2 = 1 if we travel from edge e1 to edge e2 of the graph.
    flow_e1_e2_index = []
    s_e_index = []

    for e in graph.edges:
        s_e_index.append(e)
        for e2 in graph.edges:
            if e != e2:
                flow_e1_e2_index.append((e, e2))

    flow_e1_e2 = MODEL.addVars(flow_e1_e2_index, vtype=GRB.BINARY, name='flow_e1_e2')
    s_e = MODEL.addVars(s_e_index, vtype=GRB.CONTINUOUS, lb=0, ub=graph.edges_number - 1, name='s_e')

    # Continuous variables that denotes the distance between e1 and e2.
    dist_e1_e2_index = flow_e1_e2_index

    dist_e1_e2 = MODEL.addVars(dist_e1_e2_index, vtype=GRB.CONTINUOUS, lb=0.0, name='dist_e1_e2')
    dif_e1_e2 = MODEL.addVars(dist_e1_e2_index, 2, vtype=GRB.CONTINUOUS, lb=0.0, name='dif_e1_e2')

    # Continuous variable that denotes the product prod_e1_e2 = d_e1_e2 * z_e1_e2. 
    prod_e1_e2_index = flow_e1_e2_index

    prod_e1_e2 = MODEL.addVars(prod_e1_e2_index, vtype=GRB.CONTINUOUS, lb=0.0, name='prod_e1_e2')

    R_e_index = []
    rho_e_index = []

    for e in graph.edges:
        rho_e_index.append(e)
        for dim in range(2):
            R_e_index.append((e, dim))

    R_e = MODEL.addVars(R_e_index, vtype=GRB.CONTINUOUS, name='R_e')
    rho_e = MODEL.addVars(rho_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='rho_e')

    # L_e: launching proint from segment e
    L_e_index = R_e_index
    lambda_e_index = rho_e_index

    L_e = MODEL.addVars(L_e_index, vtype=GRB.CONTINUOUS, name='Li')
    lambda_e = MODEL.addVars(lambda_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='lambda_e')

    # Auxiliar variables to model the absolute value.
    min_e = MODEL.addVars(rho_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='min_e')
    max_e = MODEL.addVars(rho_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='max_e')
    entry_e = MODEL.addVars(rho_e_index, vtype=GRB.BINARY, name='entry_e')
    mu_e = MODEL.addVars(rho_e_index, vtype=GRB.BINARY, name='mu_e')
    prod_e = MODEL.addVars(rho_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='prod_e')
    alpha_e = MODEL.addVars(rho_e_index, vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name='alpha_e')

    MODEL.update()

    MODEL.addConstrs(flow_e1_e2.sum('*', e2) == 1 for e2 in rho_e.keys())
    MODEL.addConstrs(flow_e1_e2.sum(e1, '*') == 1 for e1 in rho_e.keys())

    for p in range(len(path) - 1):
        MODEL.addConstr(flow_e1_e2[path[p], path[p + 1]] == 1)

    # for p in range(len(path)-1):
    # MODEL.addConstr(si[path[p]] == p)

    MODEL.addConstrs(prod_e[e] >= mu_e[e] + alpha_e[e] - 1 for e in rho_e.keys())
    MODEL.addConstrs(prod_e[e] <= mu_e[e] for e in rho_e.keys())
    MODEL.addConstrs(prod_e[e] <= alpha_e[e] for e in rho_e.keys())

    # MODEL.addConstrs(mui[i] == 1 for i in rhoi.keys())

    # for i in grafo.edges[1:]:
    # for j in grafo.edges[1:]:
    # if i != j:
    # MODEL.addConstr(grafo.edges_number - 1 >= (si[i] - si[j]) + grafo.edges_number * zij[i, j])
    #
    # MODEL.addConstr(si[grafo.edges[0]] == 0)

    # for i in grafo.edges[1:]:
    # MODEL.addConstr(si[i] >= 1)

    MODEL.addConstrs((dif_e1_e2[e1, e2, dim] >=   L_e[e1, dim] - R_e[e2, dim]) for e1, e2, dim in dif_e1_e2.keys())
    MODEL.addConstrs((dif_e1_e2[e1, e2, dim] >= - L_e[e1, dim] + R_e[e2, dim]) for e1, e2, dim in dif_e1_e2.keys())

    MODEL.addConstrs(
        (dif_e1_e2[e1, e2, 0] * dif_e1_e2[e1, e2, 0] + dif_e1_e2[e1, e2, 1] * dif_e1_e2[e1, e2, 1] <= dist_e1_e2[e1, e2] * dist_e1_e2[e1, e2] for e1, e2 in
         dist_e1_e2.keys()), name='dif_e1_e2')

    for e, e2 in flow_e1_e2.keys():
        first_e1 = e // 100 - 1
        second_e1 = e % 100
        first_e2 = e2 // 100 - 1
        second_e2 = e2 % 100

        segm_i = neigh.Polygonal(np.array([[graph.V[first_e1, 0], graph.V[first_e1, 1]], [
            graph.V[second_e1, 0], graph.V[second_e1, 1]]]), graph.A[first_e1, second_e1])
        segm_j = neigh.Polygonal(np.array([[graph.V[first_e2, 0], graph.V[first_e2, 1]], [
            graph.V[second_e2, 0], graph.V[second_e2, 1]]]), graph.A[first_e2, second_e2])

        local_U = eM.estimate_local_U(segm_i, segm_j)
        local_L = eM.estimate_local_L(segm_i, segm_j)

        local_U = 10000
        local_L = 0
        MODEL.addConstr((prod_e1_e2[e, e2] <= local_U * flow_e1_e2[e, e2]))
        MODEL.addConstr((prod_e1_e2[e, e2] <= dist_e1_e2[e, e2]))
        MODEL.addConstr((prod_e1_e2[e, e2] >= local_L * flow_e1_e2[e, e2]))
        MODEL.addConstr((prod_e1_e2[e, e2] >= dist_e1_e2[e, e2] - local_U * (1 - flow_e1_e2[e, e2])))

    for e in rho_e.keys():
        first = e // 100 - 1
        second = e % 100
        MODEL.addConstr(rho_e[e] - lambda_e[e] == max_e[e] - min_e[e])
        MODEL.addConstr(max_e[e] + min_e[e] >= alpha_e[e])
        if data.alpha:
            MODEL.addConstr(prod_e[e] >= graph.A[first, second])
        MODEL.addConstr(max_e[e] <= 1 - entry_e[e])
        MODEL.addConstr(min_e[e] <= entry_e[e])
        MODEL.addConstr(R_e[e, 0] == rho_e[e] * graph.V[first, 0] + (1 - rho_e[e]) * graph.V[second, 0])
        MODEL.addConstr(R_e[e, 1] == rho_e[e] * graph.V[first, 1] + (1 - rho_e[e]) * graph.V[second, 1])
        MODEL.addConstr(L_e[e, 0] == lambda_e[e] * graph.V[first, 0] + (1 - lambda_e[e]) * graph.V[second, 0])
        MODEL.addConstr(L_e[e, 1] == lambda_e[e] * graph.V[first, 1] + (1 - lambda_e[e]) * graph.V[second, 1])

    if not (data.alpha):
        MODEL.addConstr(gp.quicksum(prod_e[e] * graph.edges_length[e // 100 - 1, e % 100] for e in graph.edges) >= graph.alpha * graph.length)

    MODEL.update()

    objective = gp.quicksum(prod_e1_e2[e1, e2] for e1, e2 in prod_e1_e2.keys()) + gp.quicksum(
        prod_e[e] * graph.edges_length[e // 100 - 1, e % 100] for e in graph.edges)

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
# X = pd.read_csv('Python-MH-Local Search-Variable Neighborhood Search-Dataset-01.txt', sep = '\t')
# X = X.values
#
## Start a random seed
# seed = seed_function(X)
#
## Call the Function
# lsvns = variable_neighborhood_search(X, city_tour = seed, max_attempts = 25, neighbourhood_size = 5, iterations = 1000)
#
## Plot Solution. Red Point = Initial city; Orange Point = Second City # The generated coordinates (2D projection) are aproximated, depending on the data, the optimum tour may present crosses
# plot_tour_distance_matrix(X, lsvns)
#
######################### Part 2 - Usage ####################################
#
## Load File - Coordinates (Berlin 52,  optimal = 7544.37)
# Y = pd.read_csv('Python-MH-Local Search-Variable Neighborhood Search-Dataset-02.txt', sep = '\t')
# Y = Y.values
#
## Build the Distance Matrix
# X = buid_distance_matrix(Y)
#
## Start a Random Seed
# seed = seed_function(X)
#
## Call the Function
# lsvns = variable_neighborhood_search(X, city_tour = seed, max_attempts = 25, neighbourhood_size = 5, iterations = 1000)
#
## Plot Solution. Red Point = Initial city; Orange Point = Second City
# plot_tour_coordinates(Y, lsvns)
