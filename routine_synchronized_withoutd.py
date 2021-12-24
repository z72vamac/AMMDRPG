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
from synchronous_version_withoutd import SYNCHRONOUS
from tsp_heuristic import heuristic
import csv
import pandas as pd
import pickle as pickle

instancias = pickle.load(open("instancias.pickle", "rb"))

init = False

if init:
    dataframe = pd.DataFrame(columns = ['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal'])
else:
    dataframe = pd.DataFrame(columns = ['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal']) #, 'HeurTime', 'HeurVal'])


for key, it in zip(instancias.keys(), range(len(instancias.keys()))):
    
    # if it >= 18:
        instance, size, alpha, capacity, nD = key
        datos = instancias[key]
        if init:
            datos.init = True
        else:
            datos.init = False
        # datos.tmax = 10
    
        print()
        print('--------------------------------------------')
        print('Instance: {a}'.format(a = instance))
        # print('--------------------------------------------')
        print()
        
        sol_Stages = SYNCHRONOUS(datos)
    
        if init:
            dataframe = dataframe.append(pd.Series([instance, size, alpha, capacity, nD, sol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3], sol_Stages[4], sol_Stages[5]], index=['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal']), ignore_index=True)
        
        else:
            dataframe = dataframe.append(pd.Series([instance, size, alpha, capacity, nD, sol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3]], index=['Instance', 'Size', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal']), ignore_index=True)
                    if init:
            dataframe.to_csv('./results/synchronous_results_with.csv', header = True, mode = 'w')
        else:
            dataframe.to_csv('./results/synchronous_results_without.csv', header = True, mode = 'w')
            
