import sys
import os
import numpy as np
import random

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from utils.fitness import Fitness

class Algorithm:
    def __init__(self, population, data):
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
        self.fitness.set_population(np.array(total_student))
        total_cost = self.fitness.getCost()
        total_rank = lib_commons.fast_non_dominated_sort(total_cost)
        
        new_pop = []
        current_size = 0
        for i in range(1, total_rank[-1]):
            current_rank_elem = []
            if current_size == self.pop_size:
                break

            current_elem = list(filter(lambda elem: elem[1] == i, enumerate(total_rank)))
            for elem in current_elem:
                current_rank_elem.append(total_student[elem[0]])
            
            if total_rank.count(i) + current_size <= self.pop_size:
                new_pop.extend(current_rank_elem)
                current_size += len(current_rank_elem)
            else:
                for j in range(self.pop_size - current_size):
                    new_pop.append(current_rank_elem[j])
                break
        
        return new_pop
