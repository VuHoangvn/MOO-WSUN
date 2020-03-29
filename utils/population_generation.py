import sys
import os
import numpy as np
import random

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from config.constant import Constants

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["general"]

def createSet(data):
    num_ss = data.num_of_sensors
    Y = int(num_ss * cfg.init_sensor_rate)
    individual = np.zeros(num_ss)
    i = Y
    while i > 0:
        rd = random.randint(0, num_ss-1)
        if individual[rd] == 0:
            individual[rd] = 1
            i -= 1
    
    return individual

def initialPopulation(data):
    population = []
    for _ in range(cfg.pop_size):
        population.append(createSet(data))
    
    return population