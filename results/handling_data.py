import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import matplotlib

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

synchronous_data_with = pd.read_csv('synchronous_withoutd_results_with.csv')

synchronous_objval = pd.read_csv('synchronous_results_with_timeandobjval')