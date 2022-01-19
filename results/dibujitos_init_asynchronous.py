import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import matplotlib

pd.set_option('display.max_rows', 500)


datos = pd.read_csv('asynchronous_results_with.csv')
datos = datos[['Size', 'Instance', 'Alpha_e', 'Capacity', 'Num_Drones', 'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal']]
# datos['Runtime'] = np.log(datos['Runtime'])


datos['Difference'] = (datos['HeurVal'] - datos['ObjVal'])/(datos['HeurVal']) * 100


import tikzplotlib


matplotlib.rcParams['axes.unicode_minus'] = False

tikzplotlib.save('gap_gurobi_asynchronous_results_with.tex', encoding = 'utf-8')

# plt.savefig('gap_gurobi_with_initialization.png')

datos[['Size', 'Instance', 'Capacity', 'Num_Drones']] = datos[['Size', 'Instance', 'Capacity', 'Num_Drones']].apply(np.int64)

sns.set(style="darkgrid")

g = sns.catplot(x = 'Size', y = 'Difference', kind = 'box', col = 'Num_Drones', hue = 'Alpha_e', data = datos, aspect = 1, sharey = True, legend = True)

tikzplotlib.save('gap_between_algorithms_asynchronous_withoutd.tex')
plt.savefig('gap_between_algorithms_asynchronous_withoutd.png')

