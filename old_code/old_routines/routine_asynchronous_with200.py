import pickle as pickle

import pandas as pd

from asynchronous_version import asynchronous

# instances = pickle.load(open("instances.pickle", "rb")) # antiguas
instances = pickle.load(open("instances.pickle", "rb"))

# instancias_deulonay = pickle.load(open("instancias_deulonay.pickle", "rb"))

initialization = True

if initialization:
    dataframe = pd.DataFrame(
        columns=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_sizeP', 'Runtime', 'NodeCount', 'ObjVal',
                 'HeurTime', 'HeurVal'])
else:
    dataframe = pd.DataFrame(
        columns=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_sizeP', 'Runtime', 'NodeCount',
                 'ObjVal'])  # , 'HeurTime', 'HeurVal'])

# dataframe_h = pd.DataFrame(columns=['Obj', 'Time', 'Type'])
# [158, 162, 173, 179, 231, 238, 239, 248, 250]
lista = [152, 154, 156, 158, 160, 161, 163, 175, 178, 179, 192]

for key, it in zip(instances.keys(), range(len(instances.keys()))):

    if it >= 101 and it <= 200 and it in lista:
        instance, size, alpha, time_endurance, fleet_size
        data = instances[key]
        if initialization:
            data.initialization = True
        else:
            data.initialization = False
        data.time_limit = 3600

        print()
        print('--------------------------------------------')
        print('Instance: {a}'.format(a=instance))
        # print('--------------------------------------------')
        print()

        sol_Stages = asynchronous(data)

        # sol_SEC = PDSEC(data)
        if initialization:
            dataframe = dataframe.append(pd.Series(
                [instance, size, alpha, time_endurance, fleet_sizeStages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3],
                 sol_Stages[4], sol_Stages[5]],
                index=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_sizeP', 'Runtime', 'NodeCount', 'ObjVal',
                       'HeurTime', 'HeurVal']), ignore_index=True)

        else:
            dataframe = dataframe.append(pd.Series(
                [instance, size, alpha, time_endurance, fleet_sizeStages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3]],
                index=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_sizeP', 'Runtime', 'NodeCount',
                       'ObjVal']), ignore_index=True)

        # dataframe = dataframe.append(pd.Series([sol_MTZ[0], sol_MTZ[1], sol_MTZ[2],sol_MTZ[3], sol_MTZ[4], sol_MTZ[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)

        # dataframe = dataframe.append(pd.Series([sol_SEC[0], sol_SEC[1], sol_SEC[2],sol_SEC[3], sol_SEC[4], sol_SEC[5]], index=['GAP', 'Time', 'Nodes', 'Obj', 'Type', 'Form']), ignore_index=True)
        if initialization:
            dataframe.to_csv('./results/asynchronous_results_with200_corrected.csv', header=True, mode='w')
        else:
            dataframe.to_csv('./results/asynchronous_results_without.csv', header=True, mode='w')

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
