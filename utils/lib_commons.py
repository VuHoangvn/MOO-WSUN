import yaml
import numpy as np 

def read_yaml(filepath):
    '''
        Input a string filepath,
        output a `dict` containing the contents of the yaml file
    '''
    with open(filepath, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
    return data_loaded

def fast_non_dominated_sort(cost):
    size = len(cost)
    Sp = np.empty(size, dtype=np.object)
    F = np.empty(size + 1, dtype=np.object)
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

def find_bests(rank):
    p_best = []
    
    for i in range(len(rank)):
        if rank[i] == 1:
            p_best.append(i)
    
    return p_best

def write_to_file(filename, coverage, loss, squantity):
    f = open(filename, "a")
    f.write("{}     {}      {}\n".format(coverage, loss, squantity))
    f.close()