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
        print(candidate)
    
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


