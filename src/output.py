import sys
import os
from collections import namedtuple

Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

def getAllGenerationCost(algoType):
    dirName = "../output_eval/" + str(algoType)
    files = os.listdir(dirName)
    cost = []
    
    for i in range(len(files)):
        cost.append([])
        path = dirName + "/" + str(files[i])
        f = open(path, 'r')
        
        for line in f:
            c, l, s = line.split()
            cost[i].append(Cost(c, l, s))
        f.close()

    return cost

# cost = getAllGenerationCost("itlbo")
# print(len(cost[0]))