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

class TLBO(Algorithm):
    def teacher_selection(self):
        candidate = [index for index in range(len(self.rank)) if self.rank[index] == 1]
        Tl_index = random.choice(candidate)
        self.Tl = self.cost[Tl_index]
        self.num_teachers = cfg['num_teachers']
        r2 = random.random()
        r3 = random.random()
        Ts2 = self.Tl
        Ts3 = self.Tl

        print(Ts2)

    def teacher_phase(self):
        pass
    
    def learner_phase(self):
        pass
    
    def next_generation(self):
        self.teacher_selection()
        self.teacher_phase()
        self.learner_phase()

    def run(self):
        self.next_generation()


