import sys
import os
import math
import numpy as np
import statistics
from collections import namedtuple
from operator import itemgetter

Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)
from output import getAllGenerationCost
from utils import lib_commons

def abs_distance(cost1, cost2):
    return abs(float(cost1[0]) - float(cost2[0])) + abs(float(cost1[1]) - float(cost2[1])) + abs(float(cost1[2]) - float(cost2[2]))

def distance(genCost):
    d = []
    for cost in genCost:
        di = min(abs_distance(cost, elem) for elem in genCost if abs_distance(cost, elem) != 0 )
        d.append(di) 
    
    return d

def spacing(all_cost):
    # space = []
    # for i, genCost in enumerate(all_cost):
    # print(genCost)
    d = distance(all_cost)
    mean = sum(di for di in d) / len(d)
    s = math.sqrt(sum((di - mean)**2 for di in d)) / (len(d) - 1)
    # space.append(s)
    
    return round(s, 2)

def maximum_spread(all_cost):
    MS = []
    max_obj = []
    min_obj = []
    # for i, genCost in enumerate(all_cost):
    #     max_obj.append([])
    #     min_obj.append([])
    ms = 0
    for k in range(len(all_cost[0])):
        max_val = max(all_cost, key = itemgetter(k))[k]
        min_val = min(all_cost, key = itemgetter(k))[k]
        # max_obj[i].append(max_val)
        # min_obj[i].append(min_val)
        ms += abs(float(max_val) - float(min_val))

    ms = math.sqrt(ms)
        # MS.append(ms)
    
    return round(ms, 2)

def dominate(cost1, cost2):
    # return true if 1 dominate 2
    return cost1[0] >= cost2[0] and cost1[1] <= cost2[1] and cost1[2] <= cost2[2] and (cost1[0] > cost2[0] or cost1[1] < cost2[1] or cost1[2] < cost2[2])

def coverage(all_result, algos):
    # algos = ["itlbo", "mode", "moea_d", "nsga_ii"]
    
    all_coverage = []
    # for i in range(len(all_result[algos[0]])):
    #     all_coverage.append([])
    for i in range(len(algos)):
        all_coverage.append([])
        for k in range(len(algos)):
            if i == k:
                all_coverage[i].append(0)
                continue
            num_dominate = 0
            for cost_k in all_result[algos[k]]:
                for cost_i in all_result[algos[i]]:
                    if dominate(cost_i, cost_k):
                        num_dominate += 1
                        break
            all_coverage[i].append(round(num_dominate/len(all_result[algos[k]]), 2))
    return all_coverage

def find_pareto_all_generation(algo, dir_path):
    all_result = getAllGenerationCost(algo, dir_path)
    rank = lib_commons.fast_non_dominated_sort(all_result)
    bests = lib_commons.find_bests(rank)
    result = []
    for i in bests:
        result.append(all_result[i])
    return result

def get_spacing(all_sheets, algos):
    all_sheet_spacing = []
    for i in range(len(all_sheets)):
        space = {}
        for algo in algos:
            space[algo] = spacing(all_sheets[i][algo])
        all_sheet_spacing.append(space)
    
    return all_sheet_spacing

def get_maximum_spread(all_sheets, algos):
    all_sheet_ms = []
    for i in range(len(all_sheets)):
        ms = {}
        for algo in algos:
            ms[algo] = maximum_spread(all_sheets[i][algo])
        all_sheet_ms.append(ms)
    
    return all_sheet_ms

def get_coverage(all_sheets, algos):
    all_sheet_coverage = []
    for i in range(len(all_sheets)):
        cover = coverage(all_sheets[i], algos)
        all_sheet_coverage.append(cover)
    all_sheet_coverage = np.array(all_sheet_coverage)
    result = all_sheet_coverage[0]
    for i in range(1, len(all_sheet_coverage)):
        result += all_sheet_coverage[i]
    result = result / len(all_sheet_coverage)
    for i in range(len(result)):
        for j in range(len(result[0])):
            result[i][j] = round(result[i][j], 2)
    # print(result)
    return result

def get_all_sheet_result(algos, dirName):
    # read results
    
    # dirs = ['no-dem1_r25_1']
    dirs = os.listdir(dirName)
    all_sheets = []
    all_dir = []
    for dir in dirs:
        all_result = {}
        # all_space = {}
        # all_MS = {}
        dir_path = dirName + '/' + dir
        for algo in algos:
           all_result[algo] = find_pareto_all_generation(algo, dir_path)
        
        all_sheets.append(all_result)
        all_dir.append(dir)
        #    break
        #     space = spacing(all_result[algo])
        #     mean_space = statistics.mean(space)
        #     stdev_space = statistics.stdev(space)
        #     print(mean_space, stdev_space)
        #     all_space[algo] = space
        #     MS = maximum_spread(all_result[algo])
        #     all_MS[algo] = MS
        # coverage(all_result)
    return all_sheets, all_dir

def get_all_metrics(dirName):
    algos = ["itlbo", "mode", "moea_d", "nsga_ii"]
    all_sheets, all_dir = get_all_sheet_result(algos, dirName)
    all_sheet_spacing = get_spacing(all_sheets, algos)
    all_sheet_ms = get_maximum_spread(all_sheets, algos)
    all_coverage = get_coverage(all_sheets, algos)
    return all_sheet_spacing, all_sheet_ms, all_coverage, all_dir

# run()
# get_all_metrics("../outpyt/small_data/ga")
