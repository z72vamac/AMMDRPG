import numpy as np
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

synchronous_data_without = pd.read_csv('synchronous_withoutd_results_without.csv')
synchronous_data_with = pd.read_csv('synchronous_withoutd_results_with.csv')

synchronous_data_without = synchronous_data_without.rename(columns={'GAP': 'Gap wi'})
synchronous_data_with = synchronous_data_with.rename(columns={'GAP': 'Gap i', 'HeurTime': 'TimeH'})

# comparador = pd.concat([point_gurobi, polygonal_gurobi])
synchronous_data_without[['Size', 'Instance', 'time_endurance', 'fleet_size']] = synchronous_data_without[
    ['Size', 'Instance', 'time_endurance', 'fleet_size']].apply(np.int64)
synchronous_data_with[['Size', 'Instance', 'time_endurance', 'fleet_size']] = synchronous_data_with[
    ['Size', 'Instance', 'time_endurance', 'fleet_size']].apply(np.int64)

tabla_medias_without = synchronous_data_without.groupby(['Size', 'time_endurance', 'fleet_size', 'Alpha_e']).mean()[
    ['Gap wi']].round(2).reset_index()
tabla_notnan_without = synchronous_data_without.groupby(['Size', 'time_endurance', 'fleet_size', 'Alpha_e']).count()[
    ['Gap wi']].round(2).reset_index()

tabla_medias_with = synchronous_data_with.groupby(['Size', 'time_endurance', 'fleet_size', 'Alpha_e']).mean()[
    ['Gap i', 'TimeH']].round(2).reset_index()

data = pd.DataFrame()

data['Size'] = tabla_medias_without['Size']
data['time_endurance'] = tabla_medias_without['time_endurance']
data['fleet_size'] = tabla_medias_without['fleet_size']
data['Alpha_e'] = tabla_medias_without['Alpha_e']
data['Gap wi'] = tabla_medias_without['Gap wi']
data['Unsolved'] = 5 - tabla_notnan_without['Gap wi']
data['TimeH'] = tabla_medias_with['TimeH']
data['Gap i'] = tabla_medias_with['Gap i']

data.pivot(index=['time_endurance'], columns=['Size', 'fleet_size', 'Alpha_e']).to_excel('table_synchronous.xlsx')

# data = data.pivot(index=['Size', 'Alpha_e', 'fleet_size'], columns = ['time_endurance'])
# data.groupby(['Size', 'time_endurance', 'fleet_size', 'Alpha_e']).to_excel('table_synchronous.xlsx')
