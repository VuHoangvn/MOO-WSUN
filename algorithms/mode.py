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
        
        self.population = new_population
        self.fitness.set_population(new_population)

    def selection(self):
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)

        print('\n ', len(self.bests))
        for i in self.bests:
            print(self.cost[i])

    def next_generation(self):
        self.crossover()
        self.selection()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running ITLBO...")
        for _ in range(0, generations):
            self.next_generation()