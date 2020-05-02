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
cfg = cfg_all["nsga_ii"]
crossover_rate = cfg["crossover_rate"]
mutation_rate = cfg["mutation_rate"]
min_coverage = cfg_all["general"]["min_coverage"]
max_sensor_rate = cfg_all["general"]["max_sensor_rate"]

class NSGA_II(Algorithm):
    def __init__(self, population, data, outfile):
        super().__init__(population, data, outfile)
        self.new_population = population
        self.result = []
    #     self.population = population
    #     self.indl_size = len(population)
    #     self.data = data
    #     self.pop_size = len(population)
    #     self.teachers = []
    #     self.fitness = Fitness(population, data)
    #     self.cost = self.fitness.getCost()

    def generate_offspring(self):
        q_population = np.zeros((self.pop_size, self.indl_size))
        # binary selection
        for i in range(self.pop_size):
            candicate_1 = random.randint(0, self.pop_size - 1)
            candicate_2 = random.randint(0, self.pop_size - 1)
            if self.rank[candicate_1] < self.rank[candicate_2]:
                q_population[i] = self.population[candicate_2]
            else:
                q_population[i] = self.population[candicate_1]
        # uniform cross over
        for i in range(int(self.pop_size / 2)):
            for j in range(self.indl_size):
                if(random.random() < crossover_rate):
                    temp = q_population[i][j]
                    q_population[i][j] = q_population[self.pop_size-1][j]
                    q_population[self.pop_size-1][j] = temp
        # random mutate
        for i in range(self.pop_size):
            for j in range(self.indl_size):
                if(random.random() < mutation_rate):
                    q_population[i][j] = (q_population[i][j] + 1) % 2

        self.q_population = q_population
    
    def selection(self):
        total_population = np.concatenate((self.population, self.q_population))
        # # calculate objective
        size = self.pop_size
        self.fitness.set_population(total_population)
        total_cost = self.fitness.getCost()
        total_rank = lib_commons.fast_non_dominated_sort(total_cost)
        current_num = 0     # current number of individuals in new population
        new_population = []
        self.result = []
        # print(total_rank)
        # print(total_rank[-1])
        for i in range(1, total_rank[-1]):
            new_individual = []
            new_element_cost = []
            if current_num >= size:
                break

            new_element = list(filter(lambda elem: elem[1] == i, enumerate(total_rank)))
            for elem in new_element:
                if total_cost[elem[0]][0] < min_coverage or total_cost[elem[0]][2] > max_sensor_rate * self.indl_size:
                    continue
                new_individual.append(total_population[elem[0]])
                new_element_cost.append(total_cost[elem[0]])

            if total_rank.count(i) + current_num <= size:
                new_population.extend(new_individual)
                current_num += len(new_individual)
                if i == 1:
                    self.result = new_element_cost
            else:    
                extend_index = lib_commons.crowding_distance_assignment(new_element_cost, size-current_num)
                for j in extend_index:
                    new_population.append(new_individual[j])
                    current_num += 1
                if i == 1:
                    print(i)
                    for j in extend_index:
                        self.result.append(new_element_cost[j])

                break
        self.population = new_population
        self.fitness.set_population(self.population)
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
    
    def next_generation(self):
        self.generate_offspring()
        self.selection()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running NSGA_II...")
        for i in range(0, generations):
            print("NSGA_II step ", i, ":")
            self.next_generation()
        
        lib_commons.write_to_file(self.result, self.outfile)