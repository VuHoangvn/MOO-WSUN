import sys
import os
import numpy as np
import random
import copy
from operator import itemgetter

from .algorithm import Algorithm



ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from utils.fitness import Fitness
from utils.mutation import mutate

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["itlbo"]
TF = cfg["teaching_factor"]
mutation_rate = cfg["mutation_rate"]
interactive_threshold = cfg["interactive_threshold"] 
threshold = cfg["threshold"]
subject = [0,1,2]   # coverage, loss, squantity


class ITLBO(Algorithm):
    # def __init__(self, population, data):
    #     self.population = population
    #     self.indl_size = len(population[0])
    #     self.data = data
    #     self.pop_size = len(population)
    #     self.teachers = []
    #     self.fitness = Fitness(population, data)
    #     self.cost = self.fitness.getCost()

    def teacher_selection(self):
        max_coverage = max(self.cost, key=lambda k: k.coverage)
        min_loss = min(self.cost, key=lambda k: k.loss)
        min_squantity = min(self.cost, key=lambda k: k.squantity)
        coverage_teacher = self.cost.index(max_coverage)
        loss_teacher = self.cost.index(min_loss)
        squantity_teacher = self.cost.index(min_squantity)

        self.teachers.append(coverage_teacher)
        self.teachers.append(loss_teacher)
        self.teachers.append(squantity_teacher)


    def teacher_phase(self):
        mean_student = lib_commons.get_mean_student(self.cost)
        
        ## get temporary value like midterm
        temp = []
        for i in range(self.pop_size):
            if lib_commons.is_dominate(self.cost[i], mean_student):
                indl = self.population[i].copy()
                temp.append(indl)
            else:
                mutation = self.mutation(self.population[i], mutation_rate)
                temp.append(mutation)
        # calculate temporary cost
        self.fitness.set_population(np.array(temp))
        temp_cost = self.fitness.getCost()

        # modify original itlbo by teaching each subject with its own teacher
        ## get difference_mean
        all_difference_mean = []
        for subject_id, teacher_id in zip(subject, self.teachers):
            difference_mean = []
            teacher = self.population[teacher_id].copy()
            for id in range(self.pop_size):
                if id == teacher_id:
                    difference_mean.append(teacher)
                    continue
                
                fitness_rate = (temp_cost[id][subject_id] /
                    (self.cost[teacher_id][subject_id] + temp_cost[id][subject_id]))
                if random.random() < fitness_rate:
                    crossover = self.one_point_crossover(temp[id], teacher)
                    difference_mean.append(self.mutation(crossover, mutation_rate))
                else:
                    difference_mean.append(self.mutation(temp[id], mutation_rate))

            all_difference_mean += difference_mean
        
        after_study_student = self.select_by_non_sorting_dominated(temp, all_difference_mean)
        
        self.middle_students = self.select_by_non_sorting_dominated(self.population , after_study_student)
        self.population = self.middle_students
        self.fitness.set_population(self.population)
        self.cost = self.fitness.getCost()
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.best = lib_commons.find_bests(self.rank)
        # result = []
        # for i in self.bests:
        #     result.append(self.cost[i])
        # print(result)
        

    def learner_phase(self):
        self.fitness.set_population(np.array(self.middle_students))
        middle_cost = self.fitness.getCost()
        mean_student = lib_commons.get_mean_student(middle_cost)
        all_temp = []

        # temporary students interactives with each other
        ## each student can ask another student to improve knowledge
        for subject_id in subject:
            temp = []
            for i in range(self.pop_size):
                temp.append(np.zeros(self.indl_size))
            for i in range(self.pop_size):
                for j in range(self.pop_size):
                    if j < i:
                        continue
                    if random.random() < interactive_threshold:
                        mutation = self.mutation(self.middle_students[i], mutation_rate)
                        temp[i] = mutation
                    else:
                        temp[i] = self.one_point_crossover(self.middle_students[i], self.middle_students[j])
                        temp[i] = self.mutation(temp[i], mutation_rate)
            all_temp += temp

        interactive_student = self.select_by_non_sorting_dominated([], all_temp)

        final_students = self.select_by_non_sorting_dominated(self.middle_students, interactive_student)
        self.population = final_students
        self.fitness.set_population(self.population)
        self.cost = self.fitness.getCost()
        print("=================================================")
        self.rank = lib_commons.fast_non_dominated_sort(self.cost)
        self.bests = lib_commons.find_bests(self.rank)
        result = []
        for i in self.bests:
            result.append(self.cost[i])
        print(result)

    def next_generation(self):
        self.teacher_selection()
        self.teacher_phase()
        self.learner_phase()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running ITLBO...")
        for i in range(0, generations):
            print("ITLBO step ", i, ":")
            self.next_generation()
        result = []
        for i in self.bests:
            result.append(self.cost[i])
        lib_commons.write_to_file(result, self.outfile)
       

        
            
