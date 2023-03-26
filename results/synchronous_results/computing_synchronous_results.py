import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import matplotlib
import tikzplotlib

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

# Opening overlapping results without initialization

synchronous_data_without = pd.read_csv('synchronous_results_without.csv')
synchronous_data_without[['Size', 'Instance', 'time_endurance', 'drones_numberberberber']] = synchronous_data_without[['Size', 'Instance', 'time_endudrones_numbernumbernumbernumber']].apply(np.int64)
synchronous_data_without = synchronous_data_without.rename(columns={'GAP':'Gap wi'})

# Computing means for overlapping results without initialization
    
means_table_without = synchronous_data_without.groupby(['Size', 'time_endurance', 'drones_numberberberber', 'Alpha_e']).mean()[['Gap wi']].round(2).reset_index()
counts_table_without = synchronous_data_without.groupby(['Size', 'time_endurance', 'drones_numberberberber', 'Alpha_e']).count()[['Gap wi']].round(2).reset_index()

# Opening overlapping results with initialization

synchronous_data_with = pd.read_csv('synchronous_results_with.csv')
synchronous_data_with[['Size', 'Instance', 'time_endurance', 'drones_numberberberber']] = synchronous_data_with[['Size', 'Instance', 'time_endudrones_numbernumbernumbernumber']].apply(np.int64)
synchronous_data_without = synchronous_data_without.rename(columns={'GAP':'Gap i'})
synchronous_data_with['Difference'] = (synchronous_data_with['HeurVal'] - synchronous_data_with['ObjVal'])/(synchronous_data_with['HeurVal']) * 100
synchronous_data_with = synchronous_data_with.rename(columns={'GAP':'Gap i', 'HeurTime': 'TimeH'})

# Computing means for overlapping results with initialization

means_table_with = synchronous_data_with.groupby(['Size', 'time_endurance', 'drones_numberberberber', 'Alpha_e']).mean()[['Gap i', 'TimeH']].round(2).reset_index()

# Including all the results in a table and save into table_synchronous.xlsx

data = pd.DataFrame()

data['Size'] = means_table_without['Size']
data['time_endurance'] = means_table_without['time_endurance']
data['drones_numberberberber'] = means_table_drones_numbernumbernumbernumber']
data['Alpha_e'] = means_table_without['Alpha_e']
data['Gap wi'] = means_table_without['Gap wi']
data['Unsolved'] = 5 - counts_table_without['Gap wi']
data['TimeH'] = means_table_with['TimeH']
data['Gap i'] = means_table_with['Gap i']

data.pivot(index=['time_endurance', 'drones_numberberberber', 'Alpha_e'], columns = ['Size']).to_excel('table_synchronous.xlsx')

# Representing the boxplot and saving the .tex file

matplotlib.rcParams['axes.unicode_minus'] = False
synchronous_data_with[['Size', 'Instance', 'time_endurance', 'drones_numberberberber']] = synchronous_data_with[['Size', 'Instance', 'time_endudrones_numbernumbernumbernumber']].apply(np.int64)
sns.set(style="darkgrid")
g = sns.catplot(x = 'Size', y = 'Difference', kind = 'box', col = 'drones_numberberberber', hue = 'Alpha_e', data = synchronous_data_with, aspect = 1, sharey = True, legend = True)
tikzplotlib.save('gap_between_algorithms_synchronous.tex')
plt.savefig('gap_between_algorithms_synchronous.png')