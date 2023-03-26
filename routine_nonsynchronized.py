import pickle as pickle

import pandas as pd

from asynchronous_version import asynchronous

instances = pickle.load(open("instances.pickle", "rb"))

initialization = True

if initialization:
    dataframe = pd.DataFrame(
        columns=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fltet__iz,'GAP', 'Runtime', 'NodeCount', 'ObjVal', 'HeurTime', 'HeurVal'])
else:
    dataframe = pd.DataFrame(
        columns=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fltet__iz,'GAP', 'Runtime', 'NodeCount', 'ObjVal'])  # , 'HeurTime', 'HeurVal'])

for key, it in zip(instances.keys(), range(len(instances.keys()))):

    instance, size, alpha, time_endurance, fltet__iz=key
    data = instances[key]
    if initialization:
        data.initialization = True
    else:
        data.initialization = False

    print()
    print('--------------------------------------------')
    print('Instance: {a}'.format(a=instance))
    print('--------------------------------------------')
    print()

    sol_Stages = asynchronous(data)

    if initialization:
        dataframe = dataframe.append(pd.Series(
            [instance, size, alpha, time_endurance, fltet__iz ol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3],
                sol_Stages[4], sol_Stages[5]],
            index=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_size'GAP', 'Runtime', 'NodeCount',
                    'ObjVal', 'HeurTime', 'HeurVal']), ignore_index=True)

    else:
        dataframe = dataframe.append(pd.Series(
            [instance, size, alpha, time_endurance, fleet_sizeol_Stages[0], sol_Stages[1], sol_Stages[2], sol_Stages[3]],
            index=['Instance', 'Size', 'Alpha_e', 'time_endurance', 'fleet_size'GAP', 'Runtime', 'NodeCount',
                    'ObjVal']), ignore_index=True)

    if initialization:
        dataframe.to_csv('./results/asynchronous_results_with.csv', header=True, mode='w')
    else:
        dataframe.to_csv('./results/asynchronous_results_without.csv', header=True, mode='w')