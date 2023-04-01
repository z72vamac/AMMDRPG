from vns import *


def agglomerative(data, paths):

    """
    data: problem data,
    paths: list of (path_g, points_g, cost_g) associated to the graph g
    """
    
    fleet_size = data.fleet_size
    graphs_number = data.graphs_number
    scale = data.scale

    def can_be_joined(list):
        """ 
        Receives a list and print if possible to link having account the time_endurance constraint
        """

        print('Solving the feasibility problem for clusters {0} and {1}'.format(list[0], list[1]))

        paths_problem = []

        for i in list:
            for g in clusters[i]:
                paths_problem.append(paths[g - 1])

        cluster_size = len(paths_problem)

        if cluster_size > fleet_size:
            print('The number of available drones is greater than the num')
            print()
            return False

        MODEL = gp.Model('Can be joined')

        # Centroid
        centroid = MODEL.addVars(2, vtype=GRB.CONTINUOUS, name='centroid')

        dist_R_graph = MODEL.addVars(cluster_size, vtype=GRB.CONTINUOUS, name='dist_R_graph')
        dif_R_graph = MODEL.addVars(cluster_size, 2, vtype=GRB.CONTINUOUS, name='dif_R_graph')

        dist_L_graph = MODEL.addVars(cluster_size, vtype=GRB.CONTINUOUS, name='dist_L_g')
        dif_L_g = MODEL.addVars(cluster_size, 2, vtype=GRB.CONTINUOUS, name='dif_L_g')

        MODEL.update()

        MODEL.addConstrs(dif_L_g[g, dim] >= (paths_problem[g][1][1][dim] - centroid[dim]) * scale for g, dim in dif_L_g.keys())
        MODEL.addConstrs(dif_L_g[g, dim] >= (-paths_problem[g][1][1][dim] + centroid[dim]) * scale for g, dim in dif_L_g.keys())
        MODEL.addConstrs(gp.quicksum(dif_L_g[g, dim] * dif_L_g[g, dim] for dim in range(2)) <= dist_L_graph[g] * dist_L_graph[g] for g in dist_L_graph.keys())

        MODEL.addConstrs(dif_R_graph[g, dim] >= (paths_problem[g][1][0][dim] - centroid[dim]) * scale for g, dim in dif_R_graph.keys())
        MODEL.addConstrs(dif_R_graph[g, dim] >= (-paths_problem[g][1][0][dim] + centroid[dim]) * scale for g, dim in dif_R_graph.keys())
        MODEL.addConstrs(gp.quicksum(dif_R_graph[g, dim] * dif_R_graph[g, dim] for dim in range(2)) <= dist_R_graph[g] * dist_R_graph[g] for g in dist_L_graph.keys())

        MODEL.addConstrs((dist_L_graph[g] + paths_problem[g][2] + dist_R_graph[g]) / data.drone_speed <= data.time_endurance for g in dist_L_graph.keys())

        objective = 1

        MODEL.setObjective(objective, GRB.MINIMIZE)

        MODEL.update()
        MODEL.Params.OutputFlag = 0

        MODEL.optimize()

        MODEL.update()

        if MODEL.Status == GRB.INFEASIBLE:
            return False

        if MODEL.Status == GRB.OPTIMAL:
            print('The problem is feasible for these clusters.')
            print('Joining cluster {0} and cluster {1}'.format(list[0], list[1]))
            print()
            return True

    graphs_index = range(1, graphs_number + 1)

    clusters = {}

    for g in graphs_index:
        clusters[g] = [g]

    iter_number = 15

    for i in range(iter_number):

        if len(list(clusters.keys())) > 2:
            clusters_list = random.sample(list(clusters.keys()), 2)
        else:
            break

        representative = min(clusters_list)
        removed = max(clusters_list)

        if can_be_joined(clusters_list):

            cluster_graphs = []

            for i in clusters_list:
                for g in clusters[i]:
                    cluster_graphs.append(g)

            clusters[representative] = cluster_graphs

            del clusters[removed]
        else:
            print('The problem is feasible for these clusters')
            print()

    return clusters
