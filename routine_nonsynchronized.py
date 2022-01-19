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
from synchronous_version import SYNCHRONOUS
from asynchronous_version import ASYNCHRONOUS
from tsp_heuristic import heuristic
import csv
import pandas as pd
import pickle as pickle

instancias = pickle.load(open("instancias.pickle", "rb")) # antiguas
# instancias = pickle.load(open("instancias_init2.pickle", "rb"))

# instancias_deulonay = pickle.load(open("instancias_deulonay.pickle", "rb"))

init = True

if init:
    dataframe = pd.DataFrame(columns = ['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal'])
else:
    dataframe = pd.DataFrame(columns = ['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal']) #, 'HeurTime', 'HeurVal'])

# dataframe_h = pd.DataFrame(columns=['Obj', 'Time', 'Type'])
# [158, 162, 173, 179, 231, 238, 239, 248, 250]
# lista = [231, 238, 239, 248, 250]
# lista = [150, 151, 152, 154, 158, 188, 225, 227, 230, 236, 237]

for key, it in zip(instancias.keys(), range(len(instancias.keys()))):
    
    # if it in lista:
        instance, size, alpha, capacity, nD = key
        datos = instancias[key]
        if init:
            datos.init = True
        else:
            datos.init = False
        datos.tmax = 5
    
        print()
        print('--------------------------------------------')
        print('Instance: {a}'.format(a = instance))
        # print('--------------------------------------------')
        print()
        
        sol_Stages = ASYNCHRONOUS(datos)
    
        # sol_SEC = PDSEC(datos)
        if init:
            dataframe = dataframe.append(pd.Series([instance, size, alpha, capacity, nD, sol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3], sol_Stages[4], sol_Stages[5]], index=['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal']), ignore_index=True)
        
        else:
            dataframe = dataframe.append(pd.Series([instance, size, alpha, capacity, nD, sol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3]], index=['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal']), ignore_index=True)
            
        # dataframe = dataframe.append(pd.Series([sol_MTZ[0], sol_MTZ[1], sol_MTZ[2],sol_MTZ[3], sol_MTZ[4], sol_MTZ[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    
        # dataframe = dataframe.append(pd.Series([sol_SEC[0], sol_SEC[1], sol_SEC[2],sol_SEC[3], sol_SEC[4], sol_SEC[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
        if init:
            dataframe.to_csv('./results/asynchronous_results_with_timeandobjval.csv', header = True, mode = 'w')
        else:
            dataframe.to_csv('./results/asynchronous_results_without_corrected.csv', header = True, mode = 'w')
            

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Heuristic: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Grid"))
    # print('--------------------------------------------')
    # print()
    #
    # sol_h= heuristic(datos)
    #
    # dataframe_h = dataframe_h.append(pd.Series([sol_h[0], sol_h[1], sol_h[2]], index=['Obj', 'Time', 'Type']), ignore_index=True)
    #
    # dataframe_h.to_csv('Heuristic_results' + '.csv', header = True, mode = 'w')
    #
    # datos2 = instancias_deulonay[i]

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Stages: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_Stages = PDST(datos2)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-MTZ: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_MTZ = PDMTZ(datos2)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-SEC: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_SEC = PDSEC(datos2)

    # dataframe = dataframe.append(pd.Series([sol_Stages[0], sol_Stages[1], sol_Stages[2],sol_Stages[3], sol_Stages[4], sol_Stages[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    # dataframe.to_csv('AMDRPG_results' + '.csv', header = True, mode = 'w')

    # dataframe = dataframe.append(pd.Series([sol_MTZ[0], sol_MTZ[1], sol_MTZ[2],sol_MTZ[3], sol_MTZ[4], sol_MTZ[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)

    # dataframe = dataframe.append(pd.Series([sol_SEC[0], sol_SEC[1], sol_SEC[2],sol_SEC[3], sol_SEC[4], sol_SEC[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    # dataframe.to_csv('AMDRPG_results' + '.csv', header = True, mode = 'w')


    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Heuristic: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()
    #
    # sol_h= heuristic(datos2)
    #
    # dataframe_h = dataframe_h.append(pd.Series([sol_h[0], sol_h[1], sol_h[2]], index=['Obj', 'Time', 'Type']), ignore_index=True)
    #
    # dataframe_h.to_csv('Heuristic_results' + '.csv', header = True, mode = 'w')
