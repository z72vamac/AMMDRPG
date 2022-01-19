import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import matplotlib

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

synchronous_data_without = pd.read_csv('synchronous_withoutd_results_without.csv')
synchronous_data_with = pd.read_csv('synchronous_withoutd_results_with.csv')

synchronous_data_without = synchronous_data_without.rename(columns={'GAP':'Gap wi'})
synchronous_data_with = synchronous_data_with.rename(columns={'GAP':'Gap i', 'HeurTime': 'TimeH'})

# comparador = pd.concat([point_gurobi, polygonal_gurobi])
synchronous_data_without[['Size', 'Instance', 'Capacity', 'Num_Drones']] = synchronous_data_without[['Size', 'Instance', 'Capacity', 'Num_Drones']].apply(np.int64)
synchronous_data_with[['Size', 'Instance', 'Capacity', 'Num_Drones']] = synchronous_data_with[['Size', 'Instance', 'Capacity', 'Num_Drones']].apply(np.int64)

tabla_medias_without = synchronous_data_without.groupby(['Size', 'Capacity', 'Num_Drones', 'Alpha_e']).mean()[['Gap wi']].round(2).reset_index()
tabla_notnan_without = synchronous_data_without.groupby(['Size', 'Capacity', 'Num_Drones', 'Alpha_e']).count()[['Gap wi']].round(2).reset_index()

tabla_medias_with = synchronous_data_with.groupby(['Size', 'Capacity', 'Num_Drones', 'Alpha_e']).mean()[['Gap i', 'TimeH']].round(2).reset_index()

print(tabla_medias_with)
datos = pd.DataFrame()

datos['Size'] = tabla_medias_without['Size']
datos['Capacity'] = tabla_medias_without['Capacity']
datos['Num_Drones'] = tabla_medias_without['Num_Drones']
datos['Alpha_e'] = tabla_medias_without['Alpha_e']
datos['Gap wi'] = tabla_medias_without['Gap wi']
datos['Unsolved'] = 5 - tabla_notnan_without['Gap wi']
datos['TimeH'] = tabla_medias_with['TimeH']
datos['Gap i'] = tabla_medias_with['Gap i']

datos.pivot(index = ['Capacity'], columns = ['Size', 'Num_Drones', 'Alpha_e']).to_excel('table_synchronous.xlsx')
