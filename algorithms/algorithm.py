import os
import sys
import copy
import random
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
import utils.lib_commons as lib_commons
from utils.fitness import Fitness

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["general"]
min_coverage = cfg["min_coverage"]
max_sensor_rate = cfg["max_sensor_rate"]

class Algorithm:
    def __init__(self, population, data, outfile):
        self.outfile = outfile
        self.population = population
        self.indl_size = len(population[0])
        self.data = data
        self.pop_size = len(population)
        self.teachers = []
        self.fitness = Fitness(population, data)
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)
    
    def select_by_non_sorting_dominated(self, curr_pop, temp_pop):
        ## first non dominated sort
        total_student = curr_pop + temp_pop
        # print(len(total_student))
        # total_student = list(map(np.asarray, set(map(tuple, total_student))))
        # print(len(total_student))
        self.fitness.set_population(np.array(total_student))
        total_cost = self.fitness.getCost()
        total_rank = lib_commons.fast_non_dominated_sort(total_cost)
        
        new_pop = []
        current_size = 0
        for i in range(1, total_rank[-1]):
            current_rank_elem = []
            if current_size >= self.pop_size:
                break

            current_elem = list(filter(lambda elem: elem[1] == i, enumerate(total_rank)))
            for elem in current_elem:
                if total_cost[elem[0]][0] < min_coverage or total_cost[elem[0]][2] > max_sensor_rate * self.indl_size:
                    continue
                current_rank_elem.append(total_student[elem[0]])
            
            if total_rank.count(i) + current_size <= self.pop_size:
                new_pop.extend(current_rank_elem)
                current_size += len(current_rank_elem)
            else:
                for j in range(min(self.pop_size - current_size, len(current_rank_elem))):
                    new_pop.append(current_rank_elem[j])
                    current_size += 1
        
        if len(new_pop) == 0:
            for i in range(self.pop_size):
                index = np.random.randint(len(total_student))
                new_pop.append(total_student[index])
        if current_size < self.pop_size:
            stop = len(new_pop)
            for i in range(self.pop_size - current_size):
                new_pop.append(new_pop[random.randint(0, stop-1)])
        
        return new_pop
    
    def binary_selection(self):
        q_population = np.zeros((self.pop_size, self.indl_size))
        # binary selection
        for i in range(self.pop_size):
            if(i < 3):
                candicate_1 = random.randint(i+1, i+5)
                candicate_2 = random.randint(i+1, i+5)
            elif (i > self.pop_size - 3):
                candicate_1 = random.randint(i-5, i-1)
                candicate_2 = random.randint(i-5, i-1)
            else:
                candicate_1 = random.randint(i-2, i+2)
                candicate_2 = random.randint(i-2, i+2)

            if self.rank[candicate_1] < self.rank[candicate_2]:
                q_population[i] = self.population[candicate_2]
            else:
                q_population[i] = self.population[candicate_1]
        
        return q_population
    
    def uniform_crossover(self, q_population, crossover_rate):
        for i in range(int(self.pop_size / 2)):
            for j in range(self.indl_size):
                if(random.random() < crossover_rate):
                    temp = q_population[i][j]
                    q_population[i][j] = q_population[self.pop_size-i-1][j]
                    q_population[self.pop_size-i-1][j] = temp
        
        return q_population

    def random_mutation(self, q_population, mutation_rate):
        for i in range(self.pop_size):
            for j in range(self.indl_size):
                if(random.random() < mutation_rate):
                    q_population[i][j] = (q_population[i][j] + 1) % 2
        
        return q_population

    def one_point_crossover(self, p1, p2):
        size = len(p1)

        y = p1
        cut_point = random.randint(1, size)
        if np.random.randint(2) == 0:
            for i in range(cut_point, size):
                y[i] = p2[i]
        else:
            for i in range(cut_point):
                y[i] = p2[i]
        return y
    
    def mutation(self, indl, mutation_rate):
        size = len(indl)
        new_indl = indl.copy()
        for i in range(size):
            if random.random() < mutation_rate:
                new_indl[i] = (new_indl[i] + 1) % 2
        
        return new_indl
