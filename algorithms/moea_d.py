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
cfg = cfg_all["moea_d"]
crossover_rate = cfg["crossover_rate"]
mutation_rate = cfg["mutation_rate"]
T = cfg["T"]
min_coverage = cfg_all["general"]["min_coverage"]
max_sensor_rate = cfg_all["general"]["max_sensor_rate"]

class MOEA_D(Algorithm):
    def __init__(self, population, data, outfile):
    #     self.population = population
    #     self.indl_size = len(population)
    #     self.data = data
    #     self.pop_size = len(population)
    #     self.teachers = []
    #     self.fitness = Fitness(population, data)
    #     self.cost = self.fitness.getCost()
        super().__init__(population, data, outfile)
        self.weight_vectors = self.init_wvs_spread(0)
        self.B = self.init_neighborhood()
        self.Z = self.cost[0]
        self.lamda = lib_commons.generate_lamda(self.pop_size) 
        self.new_population = population
        self.EP = []

    def init_wvs_spread(self, rand):
        wvs = []
        spread = self.pop_size - rand
        for i in np.arange(0, 1 + sys.float_info.epsilon, 1/(spread-1)):
            wvs.append([i, 1 - i])
        for _ in range(rand):
            alpha = random.random()
            wvs.append((alpha, 1 - alpha))

        return np.array(wvs)

    def g_te(self, indl, weight_vector):
        return np.max(weight_vector * np.abs())

    def init_neighborhood(self):
        B = np.empty([self.pop_size, T], dtype=int)
        for i in range(self.pop_size):
            wv = self.weight_vectors[i]
            euclidean_distances = np.empty([self.pop_size], dtype=float)
            for j in range(self.pop_size):
                euclidean_distances[j] = np.linalg.norm(wv - self.weight_vectors[j])
            B[i] = np.argsort(euclidean_distances)[:T]
        
        return B

    def generate_offspring(self):
        # selection
        q_population = self.binary_selection()

        # uniform cross over
        q_population = self.uniform_crossover(q_population, crossover_rate)

        # random mutate
        q_population = self.random_mutation(q_population, mutation_rate)

        self.q_population = q_population

    def update_Z(self):
        for i in range(self.pop_size):
            if(self.cost[i].coverage > self.Z[0]):
                self.Z[0] = self.cost[i].coverage
            if(self.cost[i].loss < self.Z[1]):
                self.Z[1] = self.cost[i].loss
            if(self.cost[i].squantity < self.Z[2]):
                self.Z[2] = self.cost[i].squantity

    def generate_new_population(self):
        self.fitness.set_population(self.q_population)
        off_cost = self.fitness.getCost()
        for i in range(self.pop_size):
            max_s = max(abs(self.lamda[i][0] * (self.cost[i].coverage - self.Z[0])), abs(self.lamda[i][1] * (self.cost[i].loss - self.Z[1])), abs(self.lamda[i][2] * (self.cost[i].squantity - self.Z[2])))
            max_off = max(abs(self.lamda[i][0] * (off_cost[i].coverage - self.Z[0])), abs(self.lamda[i][1] * (off_cost[i].loss - self.Z[1])), abs(self.lamda[i][2] * (off_cost[i].squantity-self.Z[2])))

            if (max_s < max_off):
                self.new_population[i] = self.q_population[i]

        self.fitness.set_population(self.new_population)
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)
    
    def update_EP(self):
        print(len(self.bests))
        if len(self.EP) == 0:
            for i in self.bests:
                self.EP.append(self.cost[i])
        
        else:
            for i in self.bests:
                if(self.cost[i][0] < min_coverage or self.cost[i][2] > max_sensor_rate*self.indl_size):
                    continue

                new_EP = []
                for k in range(len(self.EP)):
                    if (self.cost[i][0] >= self.EP[k][0] and self.cost[i][1] <= self.EP[k][1] and self.cost[i][2] <= self.EP[k][2]): 
                        continue
                    else:
                        new_EP.append(self.EP[k])
                
                self.EP = new_EP

                cnt = 0
                for k in range(len(self.EP)):
                    if self.cost[i][0] == self.EP[k][0] and self.cost[i][1] == self.EP[k][1] and self.cost[i][2] == self.EP[k][2]:
                        continue
                    if self.cost[i][0] >= self.EP[k][0] or self.cost[i][1] <= self.EP[k][1] or self.cost[i][2] <= self.EP[k][2]:
                        cnt += 1

                if cnt == len(self.EP):
                    self.EP.append(self.cost[i])

    def next_generation(self):
        pass
        # self.update_Z()
        # self.generate_offspring()
        # self.generate_new_population()
        # self.update_EP()
        # print(self.EP)

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running MOEA_A...")
        for i in range(0, generations):
            print("MOEA_D step ", i, ":")
            self.next_generation()
        
        lib_commons.write_to_file(self.EP, self.outfile)