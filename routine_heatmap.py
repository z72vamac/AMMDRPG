import pickle as pickle

import pandas as pd
from AMMDRPGST import AMMDRPGST

instances = pickle.load(open("instancias_heatmap.pickle", "rb"))
# instancias_deulonay = pickle.load(open("instancias_deulonay.pickle", "rb"))

dataframe = pd.DataFrame(columns=['Instance', 'time_endurance', 'fleet_size'GAP', 'Runtime', 'NodeCount', 'ObjVal'])
# dataframe_h = pd.DataFrame(columns=['Obj', 'Time', 'Type'])

for key, it in zip(instances.keys(), range(len(instances.keys()))):
    time_endurance, fleet_sizekey
    data = instances[key]

    print()
    print('--------------------------------------------')
    print('AMMDRPG-Stages-Heatmap: time_endurance: {d} - NumberOfDrones: {e}'.format(d=time_endurance, e=fleet_size
    print('--------------------------------------------')
    print()

    sol_Stages = AMMDRPGST(data)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-MTZ: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Grid"))
    # print('--------------------------------------------')
    # print()

    # sol_MTZ = PDMTZ(data)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-SEC: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Grid"))
    # print('--------------------------------------------')
    # print()

    # sol_SEC = PDSEC(data)
    dataframe = dataframe.append(pd.Series([time_endurance, fleet_sizeol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3]],
                                           index=['time_endurance', 'fleet_size'GAP', 'Runtime', 'NodeCount', 'ObjVal']),
                                 ignore_index=True)

    # dataframe = dataframe.append(pd.Series([sol_MTZ[0], sol_MTZ[1], sol_MTZ[2],sol_MTZ[3], sol_MTZ[4], sol_MTZ[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)

    # dataframe = dataframe.append(pd.Series([sol_SEC[0], sol_SEC[1], sol_SEC[2],sol_SEC[3], sol_SEC[4], sol_SEC[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    dataframe.to_csv('AMMDRPG_results_heatmap.csv', header=True, mode='w')

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Heuristic: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Grid"))
    # print('--------------------------------------------')
    # print()
    #
    # sol_h= heuristic(data)
    #
    # dataframe_h = dataframe_h.append(pd.Series([sol_h[0], sol_h[1], sol_h[2]], index=['Obj', 'Time', 'Type']), ignore_index=True)
    #
    # dataframe_h.to_csv('Heuristic_results' + '.csv', header = True, mode = 'w')
    #
    # data2 = instancias_deulonay[i]

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Stages: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_Stages = PDST(data2)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-MTZ: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_MTZ = PDMTZ(data2)

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-SEC: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()

    # sol_SEC = PDSEC(data2)

    # dataframe = dataframe.append(pd.Series([sol_Stages[0], sol_Stages[1], sol_Stages[2],sol_Stages[3], sol_Stages[4], sol_Stages[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    # dataframe.to_csv('AMDRPG_results' + '.csv', header = True, mode = 'w')

    # dataframe = dataframe.append(pd.Series([sol_MTZ[0], sol_MTZ[1], sol_MTZ[2],sol_MTZ[3], sol_MTZ[4], sol_MTZ[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)

    # dataframe = dataframe.append(pd.Series([sol_SEC[0], sol_SEC[1], sol_SEC[2],sol_SEC[3], sol_SEC[4], sol_SEC[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
    # dataframe.to_csv('AMDRPG_results' + '.csv', header = True, mode = 'w')

    # print()
    # print('--------------------------------------------')
    # print('AMDRPG-Heuristic: Iteration: {i} - Graphs: {j}'.format(i = i, j = "Delaunay"))
    # print('--------------------------------------------')
    # print()
    #
    # sol_h= heuristic(data2)
    #
    # dataframe_h = dataframe_h.append(pd.Series([sol_h[0], sol_h[1], sol_h[2]], index=['Obj', 'Time', 'Type']), ignore_index=True)
    #
    # dataframe_h.to_csv('Heuristic_results' + '.csv', header = True, mode = 'w')
