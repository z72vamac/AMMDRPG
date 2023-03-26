import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

pd.set_option('display.max_rows', 500)

data = pd.read_csv('heatmap_results.csv')

print(data)

valores = data.pivot("time_endurance", "fleet_size"ObjVal")
ax = sns.heatmap(valores, cmap="Greys")

# uniform_data = np.random.rand(10, 12)
# ax = sns.heatmap(uniform_data)

plt.show()

# data = pd.read_table('results_MTZ.txt')
# data2 = pd.read_table('results_MTZ_initval.txt')
# data2
#
# data3 = pd.read_table('results_DFJ_initval.txt')
# data3.to_excel('results_DFJ_initval.xlsx')
# # data.to_excel('results_MTZ.xlsx')
# # data2.to_excel('results_MTZ_initval.xlsx')
#
# #data.groupby(['Size']).plot(kind = 'bar', x = 'Mode', y = 'Opt. Time')
# #data.unstack().plot(kind = 'bar')
# #data.groupby(['Size']).plot(kind = 'bar', t = 'Opt. Time')
#
# g = sns.catplot(x = 'Radii', y = 'Opt. Time', hue = 'Mode', kind = 'bar', col = 'Size', data = data, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Opt. Time', hue = 'Mode', kind = 'bar', col = 'Size', data = data2, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Obj. Model', hue = 'Mode', kind = 'bar', col = 'Size', data = data2, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Obj. Heur.', hue = 'Mode', kind = 'bar', col = 'Size', data = data2, aspect = 1, sharey = False)
#
#
# data_sin = pd.read_table('results_MTZ.txt')
# data_con = pd.read_table('results_MTZ_initval.txt')
# # data_new = pd.read_table('results_MTZ_new.txt')
#
# # data_new.to_csv('results_MTZ_new.txt', sep = '\t', index = False)
# # data_con.to_excel('results_MTZ_initval.xlsx')
#
#
# comparador1 = pd.DataFrame()
# comparador1['Size'] = data_sin['Size']
# comparador1['Radii'] = data_sin['Radii']
# comparador1['Mode'] = data_sin['Mode']
# comparador1['Opt. Time'] = np.log(data_sin['Opt. Time'])
# comparador1['#Nodes'] = data_sin['#Nodes']
# comparador1['initialization. Val'] = 'NO'
#
# comparador2 = pd.DataFrame()
# comparador2['Size'] = data_con['Size']
# comparador2['Radii'] = data_con['Radii']
# comparador2['Mode'] = data_con['Mode']
# comparador2['Opt. Time'] = np.log(data_con['Opt. Time'])
# comparador2['#Nodes'] = data_con['#Nodes']
# comparador2['initialization. Val'] = 'SI'
# #comparador['Opt. Time Con'] = data_con['Opt. Time']
#
#
# comparador = pd.concat([comparador1, comparador2])
#
# # comparador.groupby(['Mode', 'Radii']).plot(x = 'Size', y = ['Opt. Time Sin', 'Opt. Time Con'], kind = 'bar', figsize = (4, 4), stacked = False, grid = True, layout = ax)
#
# g = sns.catplot(x = 'Size', y = 'Opt. Time', hue = 'initialization. Val', kind = 'bar', row = 'Mode', col = 'Radii', data = comparador, aspect = 0.3, sharey = True, legend = True)
#
#
# g.savefig('resultados_MTZ2')
# # h = sns.heatmap(data = comparador[['Opt. Time Sin', 'Opt. Time Con']])
#
# fig.savefig('hola')
#
# dibujo[5].get_figures()
# fig.savefig('prueba')
#
# data2


# data_AMDRPG = pd.read_csv('results_init.csv', index_col=0)
# # data_AMDRPG[data_AMDRPG.isnull().any(axis=1)]
# data_AMDRPG = data_AMDRPG[data_AMDRPG.notnull().any(axis=1)]
# data_AMDRPG = data_AMDRPG[data_AMDRPG['Size'] == 10]
# # data_AMDRPG[data_AMDRPG['Opt. Time'] <= 100].head(60).shape
# # solved_MTZ10 = pd.DataFrame(np.array([[10, 20, 50, 100, 1800, 3600], [40, 45, 55, 60, 60, 60]]).T, columns = ['Time', '#Solved'])
# # solved_MTZ10['Type'] = 'MTZ'
#
# data_AMDRPG[['Instance', 'List', 'Mode', 'Muestra']] = data_AMDRPG[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# data_AMDRPG
# data_AMDRPG['Final Gap'] = 100*data_AMDRPG['% Gap']
# data_AMDRPG[data_AMDRPG['Size'] == 10]
# #data_AMDRPG['Opt. Time'] = np.log(data_AMDRPG['Opt. Time'])
# data_AMDRPG['#Nodes'] = data_AMDRPG['#Nodes']
# data_AMDRPG['Obj. Model'] = data_AMDRPG[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# data_AMDRPG['Improved Gap'] = 100 * (data_AMDRPG['Obj. Heur.'] - data_AMDRPG['Obj. Model']) / data_AMDRPG['Obj. Heur.']
# data_AMDRPG['Type'] = 'MTZ'
# data_AMDRPG.to_excel('results_MTZ_initval.xlsx')
# solved_MTZ = pd.DataFrame(np.array([[10, 50, 100, 200, 450, 900, 1800, 3600, 7200],
#                                     [144, 172, 181, 193, 198, 211, 223, 235, 237]]).T, columns = ['Time', '#Solved'])
# solved_MTZ['Type']= 'MTZ'
#
# data_AMDRPG_noinit = pd.read_csv('MTZ_noinit_results.csv', index_col=0).drop(['Obj. Heur.', 'Opt. Time Heur.'], axis = 1)
# data_AMDRPG_noinit
# # data_AMDRPG_noinit[data_AMDRPG_noinit.isnull().any(axis=1)]
# data_AMDRPG_noinit = data_AMDRPG_noinit[data_AMDRPG_noinit.notnull().any(axis=1)]
# data_AMDRPG_noinit
# data_AMDRPG_noinit[['Size', 'Radii', 'Mode', 'Muestra']] = data_AMDRPG_noinit[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# data_AMDRPG_noinit
# data_AMDRPG_noinit['Final Gap'] = 100*data_AMDRPG_noinit['% Gap']
# # data_AMDRPG_noinit['Opt. Time'] = np.log(data_AMDRPG_noinit['Opt. Time'])
# data_AMDRPG_noinit['#Nodes'] = data_AMDRPG_noinit['#Nodes']
# #data_AMDRPG_noinit['Obj. Model'] = data_AMDRPG_noinit[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# data_AMDRPG_noinit['Type'] = 'MTZ_noinit'
# data_AMDRPG_noinit.to_excel('results_MTZ_noinit.xlsx')
#
# data_Benders_noinit = pd.read_csv('Benders_results.csv', index_col = 0)
# data_Benders_noinit
# data_Benders_noinit[data_Benders_noinit['Opt. Time'] <= 1800].head(60).shape
# solved_Benders10 = pd.DataFrame(np.array([[10, 20, 50, 100, 1800, 3600], [6, 12, 19, 22, 27, 28]]).T, columns = ['Time', '#Solved'])
# solved_Benders10['Type'] = 'Benders'
#
# data_Benders_noinit[['Size', 'Radii', 'Mode', 'Muestra']] = data_Benders_noinit[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# data_Benders_noinit['Final Gap'] = 100*data_Benders_noinit['% Gap']
# data_Benders_noinit['Type'] = 'Benders'
# tabla_Benders_noinit = data_Benders_noinit.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time', ' #Cuts']].round(2).reset_index()
# tabla_Benders_noinit.to_csv('tabla_Benders_noinit.csv')
# comparador = pd.concat([data_AMDRPG, data_AMDRPG_noinit])
# comparador
# g = sns.catplot(x='Size', y='Final Gap', hue='Type', kind='box', row='Mode', col='Radii', data=comparador, aspect=1, sharey=True, legend=True)
# g.savefig('final_gap_MTZs.png')
#
# tabla_MTZ_noinit = data_AMDRPG_noinit.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time']].round(2).reset_index()
#
# tabla_MTZ_noinit.to_csv('tabla_MTZ_noinit.csv')
#
#
# tabla_MTZ_init = data_AMDRPG.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time']].round(2).reset_index()
# tabla_MTZ_init.head(60)
#
# tabla_MTZ_init.to_csv()
# data_SEC = pd.read_csv('SEC_init_results.csv', index_col=0)
# # data_SEC[data_SEC.isnull().any(axis=1)]
# data_SEC = data_SEC[data_SEC.notnull().any(axis=1)]
# data_SEC[['Size', 'Radii', 'Mode', 'Muestra']] = data_SEC[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
#
# data_SEC
# data_SEC['Final Gap'] = 100 * data_SEC['% Gap']
# #data_SEC['Opt. Time'] = np.log(data_SEC['Opt. Time'])
# data_SEC['#Nodes'] = data_SEC['#Nodes']
# data_SEC['Obj. Model'] = data_SEC[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# data_SEC['Improved Gap'] = 100 * \
#     (data_SEC['Obj. Heur.'] - data_SEC['Obj. Model']) / \
#     data_SEC['Obj. Heur.']
# data_SEC['Type'] = 'SEC'
# data_SEC.to_excel('results_SEC_initval.xlsx')
# solved_SEC = pd.DataFrame(np.array([[10, 50, 100, 200, 450, 900, 1800, 3600, 7200],
#                                     [122, 148, 155, 163, 166, 170, 174, 179, 183]]).T, columns = ['Time', '#Solved'])
# solved_SEC['Type'] = 'SEC'
# solved_SEC
#
# data_sSEC = pd.read_csv('sSEC_init_results.csv', index_col=0)
# data_sSEC = data_sSEC[data_sSEC.notnull().any(axis=1)]
# data_sSEC[['Size', 'Radii', 'Mode', 'Muestra']] = data_sSEC[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# data_sSEC
# data_sSEC['Final Gap'] = 100 * data_sSEC['% Gap']
# #data_sSEC['Opt. Time'] = np.log(data_sSEC['Opt. Time'])
# data_sSEC['#Nodes'] = data_sSEC['#Nodes']
# data_sSEC['Obj. Model'] = data_sSEC[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# data_sSEC['Improved Gap'] = 100 * \
#     (data_sSEC['Obj. Heur.'] - data_sSEC['Obj. Model']) / \
#     data_sSEC['Obj. Heur.']
# data_sSEC['Type'] = 'sSEC'
# data_sSEC.to_excel('results_sSEC_initval.xlsx')
# data_sSEC = data_sSEC[data_sSEC['Size'] == 10]
#
# data_sSEC[data_sSEC['Opt. Time'] <= 20].head(60).shape
# solved_sSEC10 = pd.DataFrame(np.array([[10, 20, 50, 100, 1800, 3600], [52, 60, 60, 60, 60, 60]]).T, columns = ['Time', '#Solved'])
# solved_sSEC10['Type'] = 'sSEC'
#
# solved = pd.concat([solved_Benders10, solved_MTZ10, solved_sSEC10])
# g = sns.relplot(x='Time', y='#Solved', hue='Type', data=solved, dashes = True, markers = True, kind = 'line', aspect=1, legend='full', style = 'Type')
# g.set(xscale="log");
# g.savefig('instances_solved_benders.png')


#
#
#
# solved_sSEC = pd.DataFrame(np.array([[10, 50, 100, 200, 450, 900, 1800, 3600, 7200],
#                                     [163, 179, 186, 192, 199, 205, 209, 212, 213]]).T, columns = ['Time', '#Solved'])
# solved_sSEC['Type'] = 'sSEC'
#
# solved = pd.concat([solved_MTZ, solved_SEC, solved_sSEC])
#
# g = sns.relplot(x='Time', y='#Solved', hue='Type', data=solved, dashes = True, markers = True, kind = 'line', aspect=1, legend='full', style = 'Type')
# g.set(xscale="log");
#
# g.savefig('instances_solved.png')
#
# resultados = pd.DataFrame([solved_MTZ, solved_SEC, solved_sSEC])
# resultados


# comparador = pd.concat([data_AMDRPG, data_SEC, data_sSEC])
# comparador2 = pd.concat([data_SEC, data_sSEC])
#
# comparador
# tabla_SEC = data_SEC.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time', 'Opt. Time Heur.', 'Improved Gap']].round(2).reset_index()
# tabla_SEC.to_csv('tabla_SEC.csv')

# g = sns.catplot(x='Size', y='#Sec', hue='Type', kind='box', row='Mode',
#                 col='Radii', data=comparador2, aspect=1, sharey=True, legend=True)
#
# # g = sns.catplot(x = 'Size', y = 'Improved Gap', hue = 'Type', kind = 'box', row = 'Mode', col = 'Radii', data = comparador, aspect = 0.6, sharey = True, legend = True)
#
# g.savefig('sec.png')
