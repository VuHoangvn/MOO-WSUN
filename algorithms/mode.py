import sys
import os
import numpy as np
import random

from .algorithm import Algorithm

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from utils.fitness import Fitness
from utils.mutation import mutate

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["mode"]
pg = cfg["pg"]
pm = cfg["pm"]
pp = cfg["pp"]

min_coverage = cfg_all["general"]["min_coverage"]
max_sensor_rate = cfg_all["general"]["max_sensor_rate"]

class MODE(Algorithm):
    # def __init__(self, population, data):
    #     self.population = population
    #     self.indl_size = len(population)
    #     self.data = data
    #     self.pop_size = len(population)
    #     self.teachers = []
    #     self.fitness = Fitness(population, data)
    #     self.cost = self.fitness.getCost()

    def crossover(self):
        new_population = np.zeros((self.pop_size, self.indl_size))
        a = pg + pm
        b = pg + pm + pp
        for i in range(self.pop_size):
            for j in range(self.indl_size):
                rand = random.random()
                if rand <= pg:
                    new_population[i][j] = self.population[i][j]
                elif rand > pg and rand <= a:
                    r = random.randint(0, len(self.bests) - 1)
                    new_population[i][j] = self.population[self.bests[r]][j]
                elif rand > a and rand <= b:
                    r = random.randint(0, self.pop_size - 1)
                    new_population[i][j] = self.population[r][j]
                elif rand > b:
                    r = -1
                    while 1:
                        r = random.randint(0, self.pop_size - 1)
                        if r != i:
                            break
                    new_population[i][j] = self.population[r][j]
        
        # self.population = new_population
        self.fitness.set_population(new_population)
        new_cost = self.fitness.getCost()
        for i in range(self.pop_size):
            if new_cost[i][0] < min_coverage or new_cost[i][2] > max_sensor_rate*self.indl_size:
                continue
            self.population[i] = new_population[i]

    def selection(self):
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)

    def next_generation(self):
        self.crossover()
        self.selection()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running MODE...")
        for i in range(0, generations):
            print("MODE step ", i, ":")
            self.next_generation()
        
        result = []
        for i in self.bests:
            result.append(self.cost[i])
        lib_commons.write_to_file(result, self.outfile)