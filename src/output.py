import sys
import os
from collections import namedtuple

Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

def getAllGenerationCost(algoType, dir):
    
    dir_path = dir + '/' + str(algoType)
    files = os.listdir(dir_path)
    cost = []
    
    for i in range(len(files)):
        # cost.append([])
        path = dir_path + "/" + str(files[i])
        f = open(path, 'r')
        
        for line in f:
            c, l, s = line.split()
            cost.append(Cost(float(c), float(l), float(s)))
        f.close()
    
    return cost

# cost = getAllGenerationCost("itlbo")
# for key in cost.keys():
#     print(key)