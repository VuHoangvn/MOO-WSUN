import sys
import os
import math
from collections import namedtuple
from operator import itemgetter

Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)
from output import getAllGenerationCost

def abs_distance(cost1, cost2):
    return abs(float(cost1[0]) - float(cost2[0])) + abs(float(cost1[1]) - float(cost2[1])) + abs(float(cost1[2]) - float(cost2[2]))

def distance(genCost):
    d = []
    for cost in genCost:
        di = min(abs_distance(cost, elem) for elem in genCost if abs_distance(cost, elem) != 0 )
        d.append(di) 
    
    return d

def spacing(all_cost):
    space = []
    for i, genCost in enumerate(all_cost):
        d = distance(genCost)
        mean = sum(di for di in d) / len(d)
        # if i == 1:
        #     print(mean)
        #     print(d)
        #     print("-----------------")
        s = math.sqrt(sum((di - mean)**2 for di in d)) / (len(d) - 1)
        space.append(s)
    
    return space

def maximum_spread(all_cost):
    MS = []
    max_obj = []
    min_obj = []
    for i, genCost in enumerate(all_cost):
        max_obj.append([])
        min_obj.append([])
        ms = 0
        for k in range(len(all_cost[0][0])):
            max_val = max(genCost, key = itemgetter(k))[k]
            min_val = min(genCost, key = itemgetter(k))[k]
            max_obj[i].append(max_val)
            min_obj[i].append(min_val)
            ms += abs(float(max_val) - float(min_val))

        ms = math.sqrt(ms)
        MS.append(ms)
    
    return MS

def dominate(cost1, cost2):
    # return true if 1 dominate 2
    return cost1[0] >= cost2[0] and cost1[1] <= cost2[1] and cost1[2] <= cost2[2] and (cost1[0] > cost2[0] or cost1[1] < cost2[1] or cost1[2] < cost2[2])

def coverage(all_result):
    algos = ["itlbo", "mode", "moea_d", "nsga_ii"]
    all_coverage = []
    for i in range(len(all_result[algos[0]])):
        all_coverage.append([])
        for j in range(len(algos)):
            all_coverage[i].append([])
            for k in range(len(algos)):
                if j == k:
                    all_coverage[i][j].append(0)
                num_dominate = 0
                for cost_j in all_result[algos[j]][i]:
                    for cost_k in all_result[algos[k]][i]:
                        if dominate(cost_k, cost_j):
                            num_dominate += 1
                            break
                all_coverage[i][j].append(num_dominate/len(all_result[algos[j]][i]))
    
    print(all_coverage[0])
                

def run():
    # read results
    algos = ["itlbo", "mode", "moea_d", "nsga_ii"]
    all_result = {}
    for algo in algos:
        all_result[algo] = getAllGenerationCost(algo)
        # space = spacing(all_result[algo])
        # print(algo, ":",space)
        # MS = maximum_spread(all_result[algo])
    coverage(all_result)

run()