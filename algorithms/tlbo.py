import os
import sys
import copy
import random
import numpy as np
from operator import itemgetter
from .algorithm import Algorithm

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from utils.fitness import Fitness

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["tlbo"]

def add(arr1, arr2):
    res_list = [] 
    for i in range(0, len(arr1)): 
        res_list.append(arr1[i] + arr2[i])

    return res_list 

class TLBO(Algorithm):
    def teacher_selection(self):
        candidate = [index for index in range(len(self.rank)) if self.rank[index] == 1]
        self.T1_index = random.choice(candidate)
        self.T1 = self.cost[self.T1_index]
        self.num_teachers = cfg['num_teachers']
        r2 = random.random() * 0.5
        self.ri = [1, r2, r2*1.5]
        r3 = r2 * 1.5
        T2 = self.T1
        T3 = self.T1
        T2 = T2._replace(coverage=T2.coverage - r2 * self.T1.coverage)
        T2 = T2._replace(loss=T2.loss + r2*self.T1.loss)
        T2 = T2._replace(squantity=T2.squantity + r2 * self.T1.squantity)
        
        T3 = T3._replace(coverage=T3.coverage - r3 * self.T1.coverage)
        T3 = T3._replace(loss=T3.loss + r3*self.T1.loss)
        T3 = T3._replace(squantity=T3.squantity + r3 * self.T1.squantity)

        self.T2 = T2
        self.T3 = T3

    def assign_group(self):
        self.groups = [[], [], [], []]
        for idx in range(len(self.cost)):
            if lib_commons.is_dominate(self.T1, self.cost[idx]) and lib_commons.is_dominate(self.cost[idx], self.T2):
                self.groups[0].append(idx)
            elif lib_commons.is_dominate(self.T2, self.cost[idx]) and lib_commons.is_dominate(self.cost[idx], self.T3):
                self.groups[1].append(idx)
            elif lib_commons.is_dominate(self.T3, self.cost[idx]):
                self.groups[2].append(idx)
            else:
                self.groups[3].append(idx)

    def get_mean(self, group):
        mean = self.population[group[0]]
        for idx in range(1, len(group)):
            # print(self.population[group[idx]])
            mean += self.population[group[idx]]
        mean = mean / len(group)
        return mean

    def teacher_phase(self):
        teacher_phase_groups = []
        for idx in range(len(self.groups) - 1):
            if len(self.groups[idx]) == 0:
                teacher_phase_groups.append([])
                continue
            mean = self.get_mean(self.groups[idx])
            print(self.groups[0])
            new_group = self.groups[idx].copy()
            TF = random.random()
            ri = random.random()
            for st in range(len(new_group)):
                # print(new_group[st])
                # print(self.population[self.T1_index])
                new_group[st] = new_group[st] + ri*add(new_group[st], -TF*mean) + ri*add(new_group[st], - self.ri[idx] * self.population[self.T1_index])
                new_group[st] = [0 if elem < 3 else 1 for elem in new_group[st]]
                # print(new_group[st])
            teacher_phase_groups.append(new_group)
        self.TP_groups = teacher_phase_groups
    
    def learner_phase(self):
        pass
    
    def next_generation(self):
        self.teacher_selection()
        self.assign_group()
        self.teacher_phase()
        # self.learner_phase()

    def run(self):
        self.next_generation()


