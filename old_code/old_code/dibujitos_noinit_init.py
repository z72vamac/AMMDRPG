import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option('display.max_rows', 500)

point_cplex = pd.read_csv('results_point_cplex_without_initialization.csv')
point_cplex = point_cplex[['Size', 'Instance', 'time_endurance', 'GAP', 'NodeCount', 'Runtime', 'ObjVal']]
# point_cplex['Runtime'] = np.log(point_cplex['Runtime'])
point_cplex['Type'] = 'Point cplex'
point_cplex['Type2'] = 'Without'

point_cplex_with = pd.read_csv('results_point_cplex_with_initialization.csv')
point_cplex_with = point_cplex_with[
    ['Size', 'Instance', 'time_endurance', 'GAP', 'NodeCount', 'Runtime', 'ObjVal', 'HeurTime', 'HeurVal']]
# point_cplex['Runtime'] = np.log(point_cplex['Runtime'])
point_cplex_with['Type'] = 'Point cplex'
point_cplex_with['Type2'] = 'With'

polygonal_cplex = pd.read_csv('results_polygonal_cplex_without_initialization.csv')
polygonal_cplex = polygonal_cplex[['Size', 'Instance', 'time_endurance', 'GAP', 'NodeCount', 'Runtime', 'ObjVal']]
# point_cplex['Runtime'] = np.log(point_cplex['Runtime'])
polygonal_cplex['Type'] = 'Polygonal cplex'
polygonal_cplex['Type2'] = 'Without'

polygonal_cplex_with = pd.read_csv('results_polygonal_cplex_with_initialization.csv')
polygonal_cplex_with = polygonal_cplex_with[
    ['Size', 'Instance', 'time_endurance', 'GAP', 'NodeCount', 'Runtime', 'ObjVal', 'HeurTime', 'HeurVal']]
# point_cplex['Runtime'] = np.log(point_cplex['Runtime'])
polygonal_cplex_with['Type'] = 'Polygonal cplex'
polygonal_cplex_with['Type2'] = 'With'

# polygonal_cplex_with = pd.read_csv('results_polygonal_cplex_with_initialization.csv')
# polygonal_cplex_with = polygonal_cplex_with[['Size', 'Instance', 'time_endurance', 'GAP', 'NodeCount', 'Runtime', 'ObjVal', 'HeurTime', 'HeurVal']]
# # polygonal_cplex['Runtime'] = np.log(polygonal_cplex['Runtime'])
# polygonal_cplex_with['Type'] = 'Polygonal_cplex_With'

todo = pd.concat([point_cplex, polygonal_cplex])  # , point_cplex_with, polygonal_cplex_with])
todo = pd.concat([point_cplex_with, polygonal_cplex_with])
todo[['Size', 'Instance', 'time_endurance']] = todo[['Size', 'Instance', 'time_endurance']].apply(np.int64)

# sns.set(style="whitegrid")
# fig = plt.figure()
# ax = fig.gca()
# ax.set_xticks(np.arange(0, 1, 0.1))
sns.set(style="darkgrid")
g = sns.catplot(x='Size', y='GAP', kind='box', hue='Type', col='Type2', data=todo, aspect=2, sharey=True, legend=True)
# plt.legend(title='Smoker', loc='upper left', labels=['Hell Yeh', 'Nah Bruh'])


# plt.show()
import tikzplotlib

# plt.show()
matplotlib.rcParams['axes.unicode_minus'] = False
tikzplotlib.save('gap_cplex.tex', encoding='utf-8')

plt.savefig('gap_cplex.png')

# tabla_comparadora = comparador.groupby(['Type', 'Size', 'time_endurance']).describe()[['GAP', 'Runtime', 'HeurTime', 'HeurVal']].round(2).reset_index()
