import yaml
import numpy as np 
from collections import namedtuple


MAX_NUM = 1e6
Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

def read_yaml(filepath):
    '''
        Input a string filepath,
        output a `dict` containing the contents of the yaml file
    '''
    with open(filepath, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded

def generate_lamda(size):
    lamda = np.zeros((size, 3))
    dis = round(1.0/(1.1*size), 3)
    for i in range(1, size+1):
        lamda[i-1][0] = round(abs(1 - dis * i), 2)
        lamda[i-1][1] = round(abs(1 - dis * (i + 1)), 2)
        lamda[i-1][2] = round(abs(1 - dis * (i + 2)), 2)
    return lamda

def is_dominate(cost1, cost2):
    # return true if 1 dominate 2
    return cost1[0] >= cost2[0] and cost1[1] <= cost2[1] and cost1[2] <= cost2[2] and (cost1[0] > cost2[0] or cost1[1] < cost2[1] or cost1[2] < cost2[2])

def get_mean_student(cost):
    pop_size = len(cost)
    mean_coverage = sum(c[0] for c in cost)/pop_size
    mean_loss = sum(c[1] for c in cost)/pop_size
    mean_squantity = sum(c[2] for c in cost)/pop_size
    return Cost(mean_coverage, mean_loss, mean_squantity)

def fast_non_dominated_sort(cost):
    size = len(cost)
    Sp = np.empty(size, dtype=np.object)
    F = np.empty(size + 2, dtype=np.object)
    for i in range(size):
        Sp[i] = []
        F[i] = []
    Np = [0] * size
    rank = [0] * (size+1)

    for i in range(size):
        for j in range(i+1, size):
            if(cost[i].coverage > cost[j].coverage and cost[i].loss < cost[j].loss) and cost[i].squantity < cost[j].squantity:
                Sp[i].append(j)
            else:
                if(cost[i].coverage <= cost[j].coverage and cost[i].loss >= cost[j].loss) and cost[i].squantity >= cost[j].squantity:
                    Sp[j].append(i)
                    Np[i] += 1
    for i in range(size):
        if Np[i] == 0:
            rank[i] = 1
            F[1].append(i)

    i = 1
    while F[i] != None and F[i] != []:
        Q = []
        for x in F[i]:
            for z in Sp[x]:
                Np[z] -= 1
                if Np[z] == 0:
                    rank[z] = i+1
                    Q.append(z)
        i += 1
        F[i] = Q
    rank[size] = i
    return rank

def crowding_distance_assignment(cost, size):
    l = len(cost)
    I = [0] * l
    coverage_sort = sorted(range(l), key=lambda k: cost[k][0])
    loss_sort = sorted(range(l), key=lambda k: cost[k][1])
    squantity_sort = sorted(range(l), key=lambda k: cost[k][2])

    I[coverage_sort[0]] = MAX_NUM    
    I[coverage_sort[-1]] = MAX_NUM
    I[loss_sort[0]] = MAX_NUM    
    I[loss_sort[-1]] = MAX_NUM
    I[squantity_sort[0]] = MAX_NUM
    I[squantity_sort[-1]] = MAX_NUM

    normalize_coverage = cost[coverage_sort[-1]][0] - cost[coverage_sort[0]][0]
    normalize_loss = cost[loss_sort[-1]][1] - cost[loss_sort[0]][1]
    normalize_squantity = cost[squantity_sort[-1]][2] - cost[squantity_sort[0]][2]

    if normalize_coverage == 0 or normalize_loss == 0 or normalize_squantity == 0:
        return range(size)

    for i in range(1, l-1):
        I[coverage_sort[i]] += (cost[coverage_sort[i+1]][0] - cost[coverage_sort[i-1]][0]) / normalize_coverage
        I[loss_sort[i]] += (cost[loss_sort[i+1]][1] - cost[loss_sort[i-1]][1]) / normalize_loss
        I[squantity_sort[i]] += (cost[squantity_sort[i+1]][2] - cost[squantity_sort[i-1]][2]) / normalize_squantity
    
    dist_sort = sorted(range(l), key=lambda k: I[k])
    extend_index = []
    for k in dist_sort:
        extend_index.append(k)
    
    return extend_index[:size]

def find_bests(rank):
    p_best = []
    
    for i in range(len(rank)):
        if rank[i] == 1:
            p_best.append(i)
    
    return p_best

def write_to_file(cost, filename):
    f = open(filename, "w")
    for i in range(len(cost)):
        f.write("{}     {}      {}\n".format(cost[i].coverage, cost[i].loss, cost[i].squantity))
    f.close()