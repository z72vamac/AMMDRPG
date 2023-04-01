# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 00:16:23 2019

@author: carlo
"""

# Required packages
from neighbourhood import *
import numpy as np


def estimate_local_U(comp1, comp2):
    """
    Function that estimates the maximum distance between two pair of neighbourhoods.
    """
    maximum = 0
    if type(comp1) is Polygon or type(comp1) is Polygonal:
        if type(comp2) is Polygon or type(comp2) is Polygonal:
            maximum = max([np.linalg.norm(v - w) for v in comp1.V
                          for w in comp2.V])

        if type(comp2) is Ellipsoid:
            maximum = comp2.radii + max([np.linalg.norm(v - comp2.center) for v in comp1.V])

    if type(comp1) is Ellipsoid:
        if type(comp2) is Polygon or type(comp2) is Polygonal:
            maximum = comp1.radii + max([np.linalg.norm(comp1.center - w) for w in comp2.V])

        if type(comp2) is Ellipsoid:
            maximum = comp1.radii + np.linalg.norm(comp1.center - comp2.center) + comp2.radii

    return maximum


def estimate_local_L(comp1, comp2):
    """
    Function that estimates the minimum distance between two pair of neighbourhoods.
    """
    if type(comp1) is Polygon or type(comp1) is Polygonal:
        if type(comp2) is Polygon or type(comp2) is Polygonal:
            minimum = min([np.linalg.norm(v - w) for v in comp1.V
                          for w in comp2.V])

        if type(comp2) is Ellipsoid:
            minimum = - comp2.radii + min([np.linalg.norm(v - comp2.center) for v in comp1.V])

    if type(comp1) is Ellipsoid:
        if type(comp2) is Polygon or type(comp2) is Polygonal:
            minimum = -comp1.radii + min([np.linalg.norm(comp1.center - w) for w in comp2.V])

        if type(comp2) is Ellipsoid:
            minimum = -comp1.radii + np.linalg.norm(comp1.center - comp2.center) - comp2.radii

    return minimum


def estimate_inside_U(comp):
    """
    Function that estimates the maximum distance between two pairs of the same neighbourhood.
    """
    maximum = 0
    if type(comp) is Polygon:
        maximum = max([np.linalg.norm(v - w) for v in comp.V for w in comp.V])

    if type(comp) is Ellipsoid:
        maximum = 2 * comp.radii

    if type(comp) is Polygonal:
        maximum = comp.alpha * comp.length

    return maximum
