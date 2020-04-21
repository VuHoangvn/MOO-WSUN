import sys
import os
import numpy as np
import random

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from utils.fitness import Fitness
from utils.mutation import mutate

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["itlbo"]
TF = cfg["teaching_factor"]
mutation_rate = cfg["mutation_rate"]
threshold = cfg["mean_threshold"]
subject = [0,1,2]   # coverage, loss, squantity


class ITLBO:
    def __init__(self, population, data):
        self.population = population
        self.indl_size = len(population[0])
        self.data = data
        self.pop_size = len(population)
        self.teachers = []
        self.fitness = Fitness(population, data)
        self.cost = self.fitness.getCost()

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

    def get_mean_student(self):
        mean_student = [0] * self.indl_size
        
        for indl in self.population:
            for i in range(self.indl_size):
                mean_student[i] += indl[i]/self.pop_size
        
        mean_student = [0 if x < threshold else 1 for x in mean_student]
        
        return mean_student

    def teacher_phase(self):
        mean_student = self.get_mean_student()

        ## get temporary value like midterm
        temp = []
        for i in range(self.pop_size):
            temp_indl = mean_student if random.random() > TF else mutate(self.population[i], mutation_rate)
            temp.append(temp_indl)

        ## calculate temporary cost
        self.fitness.set_population(np.array(temp))
        temp_cost = self.fitness.getCost()

        ## modify original itlbo by teaching each subject with its own teacher
        ## get difference_mean
        difference_mean = [[0]*self.indl_size]*self.pop_size
        
        for subject_id, teacher_id in zip(subject, self.teachers):
            teacher = self.population[teacher_id]
            for id in range(self.pop_size):
                if id == teacher_id:
                    continue
                for i in range(self.indl_size):
                    fitness_rate = (temp_cost[id][subject_id] /
                        (self.cost[teacher_id][subject_id] + temp_cost[id][subject_id]))
                    if random.random() < fitness_rate:
                        difference_mean[id][i] = teacher[i]
                    else:
                        difference_mean[id][i] = temp[id][i]
        self.fitness.set_population(np.array(difference_mean))
        difference_cost = self.fitness.getCost()
        
        ## student after teacher phase
        middle_students = [[0]*self.indl_size]*self.pop_size
        for subject_id in subject:
            for id in range(self.pop_size):
                for i in range(self.indl_size):
                    fitness_rate = (self.cost[id][subject_id] /
                        (self.cost[id][subject_id] + difference_cost[id][subject_id]))
                    if random.random() < fitness_rate:
                        middle_students[id][i] = self.population[id][i]
                    else:
                        middle_students[id][i] = difference_mean[id][i]
        
        self.middle_students = middle_students
       

    def learner_phase(self):
        interactive_threshold = cfg["interactive_threshold"]
        temp = [[0]*self.indl_size]*self.pop_size
        self.fitness.set_population(np.array(self.middle_students))
        middle_cost = self.fitness.getCost()
        print(len(middle_cost))
        ## temporary students interactives with each other
        ## each student can ask another student to improve knowledge
        for subject_id in subject:
            for i in range(self.pop_size):
                for j in range(self.pop_size):
                    if random.random() < interactive_threshold or i == j:
                        continue
                    mutation = mutate(self.middle_students[i], mutation_rate)
                    rand = random.random()
                    if rand > threshold:
                        temp[i] = mutation
                    elif rand < (middle_cost[i][subject_id] / (middle_cost[i][subject_id] + middle_cost[j][subject_id])):
                        temp[i] = self.middle_students[j]
                    else:
                        temp[i] = self.middle_students[i]
        
        ## final student obtain knowledge:
        self.fitness.set_population(temp)
        temp_cost = self.fitness.getCost()
        final_students = [[0]*self.indl_size]*self.pop_size
        for subject_id in subject:
            for i in range(self.pop_size):
                rand = random.random()
                if rand < (middle_cost[i][subject_id] / (temp_cost[i][subject_id] + middle_cost[j][subject_id])):
                    final_students[i] = self.middle_students[i]
                else:
                    final_students[i] = temp[i]

    def next_generation(self):
        self.teacher_selection()
        self.teacher_phase()
        self.learner_phase()

    def run(self):
        generations = cfg["generations"]
        print("[INFO] Running ITLBO...")
        # for _ in range(0, generations):
        self.next_generation()
        
        
            
