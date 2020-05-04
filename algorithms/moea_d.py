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
        self.weight_vectors = self.init_wvs_spread()
        self.B = self.init_neighborhood()
        self.Z = self.cost[0]
        self.lamda = lib_commons.generate_lamda(self.pop_size) 
        self.new_population = population
        self.EP = []

    def init_wvs_spread(self):
        lamda = np.zeros((self.pop_size, 3))
        dis = round(1.0/(1.1*self.pop_size), 3)
        for i in range(1, self.pop_size+1):
            lamda[i-1][0] = round(abs(1 - dis * i), 2)
            lamda[i-1][1] = round(abs(1 - dis * (i + 1)), 2)
            lamda[i-1][2] = round(abs(1 - dis * (i + 2)), 2)
        return lamda

    def init_neighborhood(self):
        B = np.empty([self.pop_size, T], dtype=int)
        for i in range(self.pop_size):
            wv = self.weight_vectors[i]
            euclidean_distances = np.empty([self.pop_size], dtype=float)
            for j in range(self.pop_size):
                euclidean_distances[j] = np.linalg.norm(wv - self.weight_vectors[j])
            B[i] = np.argsort(euclidean_distances)[:T]
        
        return B

    def opitmizer(self):
        self.Y = self.Y

    def reproduction(self):
        Y = np.empty([self.pop_size, self.indl_size])
        for i in range(self.pop_size):
            k = np.random.randint(0, len(self.B[i]))
            l = np.random.randint(0, len(self.B[i]) - 1)
            if l >= k:
                l += 1

            Y[i] = self.one_point_crossover(self.population[k], self.population[l])
            Y[i] = self.mutation(Y[i], mutation_rate)
        
        self.Y = Y

    def improvement(self):
        self.opitmizer()

    def update_Z(self):
        self.fitness.set_population(self.Y)
        y_cost = self.fitness.getCost()
        self.y_cost = y_cost
        for i in range(self.pop_size):
            if self.Z[0] < y_cost[i][0]:
                self.Z._replace(coverage=y_cost[i][0])
            if self.Z[1] > y_cost[i][1]:
                self.Z._replace(loss=y_cost[i][1])
            if self.Z[2] > y_cost[i][2]:
                self.Z._replace(squantity=y_cost[i][2])

    def g_te(self, cost_i, weight_vector):
        return max([weight_vector[j] * abs(cost_i[j] - self.Z[j]) for j in range(len(cost_i))])

    def update_neighborhood(self):
        for i in range(self.pop_size):
            for index in self.B[i]:
                wv = self.weight_vectors[index]
                if self.g_te(self.y_cost[index], wv) <= self.g_te(self.cost[index], wv):
                    self.population[index] = self.Y[index]
        
        self.fitness.set_population(self.population)
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)

    def updata_EP(self):
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
        self.reproduction()
        self.improvement()
        self.update_Z()
        self.update_neighborhood()
        self.updata_EP()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running MOEA_A...")
        for i in range(0, generations):
            print("MOEA_D step ", i, ":")
            self.next_generation()
        
        lib_commons.write_to_file(self.EP, self.outfile)