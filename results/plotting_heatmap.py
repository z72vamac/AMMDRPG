import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

pd.set_option('display.max_rows', 500)

datos = pd.read_csv('AMMDRPG_results_heatmap.csv')

print(datos)

valores = datos.pivot("Endurance", "Num_Drones", "ObjVal")
ax = sns.heatmap(valores, cmap="Greys")

# uniform_data = np.random.rand(10, 12)
# ax = sns.heatmap(uniform_data)

plt.show()

# datos = pd.read_table('results_MTZ.txt')
# datos2 = pd.read_table('results_MTZ_initval.txt')
# datos2
#
# datos3 = pd.read_table('results_DFJ_initval.txt')
# datos3.to_excel('results_DFJ_initval.xlsx')
# # datos.to_excel('results_MTZ.xlsx')
# # datos2.to_excel('results_MTZ_initval.xlsx')
#
# #datos.groupby(['Size']).plot(kind = 'bar', x = 'Mode', y = 'Opt. Time')
# #datos.unstack().plot(kind = 'bar')
# #datos.groupby(['Size']).plot(kind = 'bar', t = 'Opt. Time')
#
# g = sns.catplot(x = 'Radii', y = 'Opt. Time', hue = 'Mode', kind = 'bar', col = 'Size', data = datos, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Opt. Time', hue = 'Mode', kind = 'bar', col = 'Size', data = datos2, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Obj. Model', hue = 'Mode', kind = 'bar', col = 'Size', data = datos2, aspect = 1, sharey = False)
# g = sns.catplot(x = 'Radii', y = 'Obj. Heur.', hue = 'Mode', kind = 'bar', col = 'Size', data = datos2, aspect = 1, sharey = False)
#
#
# datos_sin = pd.read_table('results_MTZ.txt')
# datos_con = pd.read_table('results_MTZ_initval.txt')
# # datos_new = pd.read_table('results_MTZ_new.txt')
#
# # datos_new.to_csv('results_MTZ_new.txt', sep = '\t', index = False)
# # datos_con.to_excel('results_MTZ_initval.xlsx')
#
#
# comparador1 = pd.DataFrame()
# comparador1['Size'] = datos_sin['Size']
# comparador1['Radii'] = datos_sin['Radii']
# comparador1['Mode'] = datos_sin['Mode']
# comparador1['Opt. Time'] = np.log(datos_sin['Opt. Time'])
# comparador1['#Nodes'] = datos_sin['#Nodes']
# comparador1['Init. Val'] = 'NO'
#
# comparador2 = pd.DataFrame()
# comparador2['Size'] = datos_con['Size']
# comparador2['Radii'] = datos_con['Radii']
# comparador2['Mode'] = datos_con['Mode']
# comparador2['Opt. Time'] = np.log(datos_con['Opt. Time'])
# comparador2['#Nodes'] = datos_con['#Nodes']
# comparador2['Init. Val'] = 'SI'
# #comparador['Opt. Time Con'] = datos_con['Opt. Time']
#
#
# comparador = pd.concat([comparador1, comparador2])
#
# # comparador.groupby(['Mode', 'Radii']).plot(x = 'Size', y = ['Opt. Time Sin', 'Opt. Time Con'], kind = 'bar', figsize = (4, 4), stacked = False, grid = True, layout = ax)
#
# g = sns.catplot(x = 'Size', y = 'Opt. Time', hue = 'Init. Val', kind = 'bar', row = 'Mode', col = 'Radii', data = comparador, aspect = 0.3, sharey = True, legend = True)
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
# datos2


# datos_AMDRPG = pd.read_csv('results_init.csv', index_col=0)
# # datos_AMDRPG[datos_AMDRPG.isnull().any(axis=1)]
# datos_AMDRPG = datos_AMDRPG[datos_AMDRPG.notnull().any(axis=1)]
# datos_AMDRPG = datos_AMDRPG[datos_AMDRPG['Size'] == 10]
# # datos_AMDRPG[datos_AMDRPG['Opt. Time'] <= 100].head(60).shape
# # solved_MTZ10 = pd.DataFrame(np.array([[10, 20, 50, 100, 1800, 3600], [40, 45, 55, 60, 60, 60]]).T, columns = ['Time', '#Solved'])
# # solved_MTZ10['Type'] = 'MTZ'
#
# datos_AMDRPG[['Instance', 'List', 'Mode', 'Muestra']] = datos_AMDRPG[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# datos_AMDRPG
# datos_AMDRPG['Final Gap'] = 100*datos_AMDRPG['% Gap']
# datos_AMDRPG[datos_AMDRPG['Size'] == 10]
# #datos_AMDRPG['Opt. Time'] = np.log(datos_AMDRPG['Opt. Time'])
# datos_AMDRPG['#Nodes'] = datos_AMDRPG['#Nodes']
# datos_AMDRPG['Obj. Model'] = datos_AMDRPG[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# datos_AMDRPG['Improved Gap'] = 100 * (datos_AMDRPG['Obj. Heur.'] - datos_AMDRPG['Obj. Model']) / datos_AMDRPG['Obj. Heur.']
# datos_AMDRPG['Type'] = 'MTZ'
# datos_AMDRPG.to_excel('results_MTZ_initval.xlsx')
# solved_MTZ = pd.DataFrame(np.array([[10, 50, 100, 200, 450, 900, 1800, 3600, 7200],
#                                     [144, 172, 181, 193, 198, 211, 223, 235, 237]]).T, columns = ['Time', '#Solved'])
# solved_MTZ['Type']= 'MTZ'
#
# datos_AMDRPG_noinit = pd.read_csv('MTZ_noinit_results.csv', index_col=0).drop(['Obj. Heur.', 'Opt. Time Heur.'], axis = 1)
# datos_AMDRPG_noinit
# # datos_AMDRPG_noinit[datos_AMDRPG_noinit.isnull().any(axis=1)]
# datos_AMDRPG_noinit = datos_AMDRPG_noinit[datos_AMDRPG_noinit.notnull().any(axis=1)]
# datos_AMDRPG_noinit
# datos_AMDRPG_noinit[['Size', 'Radii', 'Mode', 'Muestra']] = datos_AMDRPG_noinit[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# datos_AMDRPG_noinit
# datos_AMDRPG_noinit['Final Gap'] = 100*datos_AMDRPG_noinit['% Gap']
# # datos_AMDRPG_noinit['Opt. Time'] = np.log(datos_AMDRPG_noinit['Opt. Time'])
# datos_AMDRPG_noinit['#Nodes'] = datos_AMDRPG_noinit['#Nodes']
# #datos_AMDRPG_noinit['Obj. Model'] = datos_AMDRPG_noinit[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# datos_AMDRPG_noinit['Type'] = 'MTZ_noinit'
# datos_AMDRPG_noinit.to_excel('results_MTZ_noinit.xlsx')
#
# datos_Benders_noinit = pd.read_csv('Benders_results.csv', index_col = 0)
# datos_Benders_noinit
# datos_Benders_noinit[datos_Benders_noinit['Opt. Time'] <= 1800].head(60).shape
# solved_Benders10 = pd.DataFrame(np.array([[10, 20, 50, 100, 1800, 3600], [6, 12, 19, 22, 27, 28]]).T, columns = ['Time', '#Solved'])
# solved_Benders10['Type'] = 'Benders'
#
# datos_Benders_noinit[['Size', 'Radii', 'Mode', 'Muestra']] = datos_Benders_noinit[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# datos_Benders_noinit['Final Gap'] = 100*datos_Benders_noinit['% Gap']
# datos_Benders_noinit['Type'] = 'Benders'
# tabla_Benders_noinit = datos_Benders_noinit.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time', ' #Cuts']].round(2).reset_index()
# tabla_Benders_noinit.to_csv('tabla_Benders_noinit.csv')
# comparador = pd.concat([datos_AMDRPG, datos_AMDRPG_noinit])
# comparador
# g = sns.catplot(x='Size', y='Final Gap', hue='Type', kind='box', row='Mode', col='Radii', data=comparador, aspect=1, sharey=True, legend=True)
# g.savefig('final_gap_MTZs.png')
#
# tabla_MTZ_noinit = datos_AMDRPG_noinit.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time']].round(2).reset_index()
#
# tabla_MTZ_noinit.to_csv('tabla_MTZ_noinit.csv')
#
#
# tabla_MTZ_init = datos_AMDRPG.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time']].round(2).reset_index()
# tabla_MTZ_init.head(60)
#
# tabla_MTZ_init.to_csv()
# datos_SEC = pd.read_csv('SEC_init_results.csv', index_col=0)
# # datos_SEC[datos_SEC.isnull().any(axis=1)]
# datos_SEC = datos_SEC[datos_SEC.notnull().any(axis=1)]
# datos_SEC[['Size', 'Radii', 'Mode', 'Muestra']] = datos_SEC[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
#
# datos_SEC
# datos_SEC['Final Gap'] = 100 * datos_SEC['% Gap']
# #datos_SEC['Opt. Time'] = np.log(datos_SEC['Opt. Time'])
# datos_SEC['#Nodes'] = datos_SEC['#Nodes']
# datos_SEC['Obj. Model'] = datos_SEC[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# datos_SEC['Improved Gap'] = 100 * \
#     (datos_SEC['Obj. Heur.'] - datos_SEC['Obj. Model']) / \
#     datos_SEC['Obj. Heur.']
# datos_SEC['Type'] = 'SEC'
# datos_SEC.to_excel('results_SEC_initval.xlsx')
# solved_SEC = pd.DataFrame(np.array([[10, 50, 100, 200, 450, 900, 1800, 3600, 7200],
#                                     [122, 148, 155, 163, 166, 170, 174, 179, 183]]).T, columns = ['Time', '#Solved'])
# solved_SEC['Type'] = 'SEC'
# solved_SEC
#
# datos_sSEC = pd.read_csv('sSEC_init_results.csv', index_col=0)
# datos_sSEC = datos_sSEC[datos_sSEC.notnull().any(axis=1)]
# datos_sSEC[['Size', 'Radii', 'Mode', 'Muestra']] = datos_sSEC[['Size', 'Radii', 'Mode', 'Muestra']].apply(np.int64)
# datos_sSEC
# datos_sSEC['Final Gap'] = 100 * datos_sSEC['% Gap']
# #datos_sSEC['Opt. Time'] = np.log(datos_sSEC['Opt. Time'])
# datos_sSEC['#Nodes'] = datos_sSEC['#Nodes']
# datos_sSEC['Obj. Model'] = datos_sSEC[['Obj. Model', 'Obj. Heur.']].min(axis=1)
# datos_sSEC['Improved Gap'] = 100 * \
#     (datos_sSEC['Obj. Heur.'] - datos_sSEC['Obj. Model']) / \
#     datos_sSEC['Obj. Heur.']
# datos_sSEC['Type'] = 'sSEC'
# datos_sSEC.to_excel('results_sSEC_initval.xlsx')
# datos_sSEC = datos_sSEC[datos_sSEC['Size'] == 10]
#
# datos_sSEC[datos_sSEC['Opt. Time'] <= 20].head(60).shape
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


# comparador = pd.concat([datos_AMDRPG, datos_SEC, datos_sSEC])
# comparador2 = pd.concat([datos_SEC, datos_sSEC])
#
# comparador
# tabla_SEC = datos_SEC.groupby(['Size', 'Radii', 'Mode']).mean()[['Final Gap', 'Opt. Time', 'Opt. Time Heur.', 'Improved Gap']].round(2).reset_index()
# tabla_SEC.to_csv('tabla_SEC.csv')

# g = sns.catplot(x='Size', y='#Sec', hue='Type', kind='box', row='Mode',
#                 col='Radii', data=comparador2, aspect=1, sharey=True, legend=True)
#
# # g = sns.catplot(x = 'Size', y = 'Improved Gap', hue = 'Type', kind = 'box', row = 'Mode', col = 'Radii', data = comparador, aspect = 0.6, sharey = True, legend = True)
#
# g.savefig('sec.png')
