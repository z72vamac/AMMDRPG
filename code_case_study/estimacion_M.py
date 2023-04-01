# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 00:16:23 2019

@author: carlo
"""
from gurobipy import *
import numpy as np
from entorno import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


# def estima_BigM(data):
#
#     m = len(data)
#     BigM = 0
#
#     for i in range(m):
#         for j in range(m):
#             if i != j:
#                 comp1 = data[i]
#                 comp2 = data[j]
#
#                 if type(comp1) is Poligono or Poligonal:
#                     if type(comp2) is Poligono:
#                         maximo = max([np.linalg.norm(v-w) for v in comp1.V
#                                                           for w in comp2.V])
#
#                     if type(comp2) is Elipse:
#                         maximo = comp2.radio + max([np.linalg.norm(v-comp2.centro) for v in comp1.V])
#
#                 if type(comp1) is Poligonal:
#                     if type(comp2) is Poligono or Poligonal:
#                         maximo = max([np.linalg.norm(w-v) for w in comp2.V
#                                                           for v in comp1.V])
#
#                     if type(comp2) is Elipse:
#                         caso1 = comp2.radio + np.linalg.norm(comp1.P-comp2.centro)
#                         caso2 = comp2.radio + np.linalg.norm(comp1.Q-comp2.centro)
#                         maximo = max(caso1, caso2)
#
#                 if type(comp1) is Elipse:
#                     if type(comp2) is Poligono or Poligonal:
#                         maximo = comp1.radio + max([np.linalg.norm(comp1.centro-w) for w in comp2.V])
#
#                     if type(comp2) is Elipse:
#                         maximo = comp1.radio + np.linalg.norm(comp1.centro-comp2.centro) + comp2.radio
#
#                 if maximo >= BigM:
#                     BigM = maximo
#
#     return BigM


def estima_BigM_local(comp1, comp2):
        maximo = 0
        if type(comp1) is Poligono or type(comp1) is Poligonal:
            if type(comp2) is Poligono or type(comp2) is Poligonal:
                maximo = max([np.linalg.norm(v-w)*14000/1e6 for v in comp1.V
                                                  for w in comp2.V])

            if type(comp2) is Elipse:
                maximo = comp2.radio*14000/1e6 + max([np.linalg.norm(v-comp2.centro)*14000/1e6 for v in comp1.V])

        if type(comp1) is Elipse:
            if type(comp2) is Poligono or type(comp2) is Poligonal:
                maximo = comp1.radio*14000/1e6 + max([np.linalg.norm(comp1.centro-w)*14000/1e6 for w in comp2.V])

            if type(comp2) is Elipse:
                maximo = comp1.radio*14000/1e6 + np.linalg.norm(comp1.centro-comp2.centro)*14000/1e6 + comp2.radio*14000/1e6

        return maximo

def estima_SmallM_local(comp1, comp2):
        if type(comp1) is Poligono or type(comp1) is Poligonal:
            if type(comp2) is Poligono or type(comp2) is Poligonal:
                minimo = min([np.linalg.norm(v-w)*14000/1e6 for v in comp1.V
                                                  for w in comp2.V])

            if type(comp2) is Elipse:
                minimo = - comp2.radio*14000/1e6 + min([np.linalg.norm(v-comp2.centro)*14000/1e6 for v in comp1.V])

        if type(comp1) is Elipse:
            if type(comp2) is Poligono or type(comp2) is Poligonal:
                minimo = -comp1.radio*14000/1e6 + min([np.linalg.norm(comp1.centro-w)*14000/1e6 for w in comp2.V])

            if type(comp2) is Elipse:
                minimo = -comp1.radio*14000/1e6 + np.linalg.norm(comp1.centro-comp2.centro)*14000/1e6 - comp2.radio*14000/1e6

        return minimo

def estima_max_inside(comp):
        maximo = 0
        if type(comp) is Poligono:
            maximo = max([np.linalg.norm(v-w)*14000/1e6 for v in comp.V for w in comp.V])

        if type(comp) is Elipse:
            maximo = 2*comp.radio*14000/1e6

        if type(comp) is Poligonal:
            maximo = comp.alpha * comp.longitud*14000/1e6

        return maximo
