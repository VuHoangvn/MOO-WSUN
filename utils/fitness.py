import sys
import os
import yaml
import numpy as np
from collections import namedtuple

Cost = namedtuple('Cost', ['coverage', 'loss', 'squantity'])

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

import utils.lib_commons as lib_commons
from config.constant import Constants

cfg_all = lib_commons.read_yaml(ROOT + "config/config.yaml")
cfg = cfg_all["general"]

class Fitness:
	def __init__(self, population, data):
		self.population = population
		self.pop_size = len(population)
		self.coverage = []
		self.loss = []
		self.no_sensors = []
		self.data = data

	def set_population(self, new_population):
		self.population = new_population
		self.pop_size = len(new_population)
		
	
	def get_coverage(self):
		m = self.data.num_of_relays
		k = cfg["sensor_coverages"]
		elem_cover = np.zeros((self.pop_size, m))
		ss_cover = self.data.sensor_coverage
		for s in range(self.pop_size):
			for i in range(m):
				for j in range(self.data.num_of_sensors):
					if self.population[s][j] == 1 and ss_cover[i][j] == 1:
						elem_cover[s][i] += 1

		sum_ss_cover = [0] * self.pop_size
		for s in range(self.pop_size):
			for i in range(m):
				if(elem_cover[s][i] >= k):
					sum_ss_cover[s] += 1.0/m
				else:
					sum_ss_cover[s] += float(elem_cover[s][i]) / (k*m)
		
		self.coverage = sum_ss_cover
		return self.coverage

	def get_max_loss(self):
		no_sensors = self.data.num_of_sensors
		sum_loss = [0 for _ in range(self.pop_size)]
		loss_matrix = self.data.comm_loss_matrix
		for s in range(self.pop_size):
			for i in range(no_sensors):
				for j in range(i+1, no_sensors):
					if self.population[s][i] == 1 and self.population[s][j] == 1:
						sum_loss[s] += loss_matrix[i][j]
		
		self.loss = sum_loss
		return self.loss

	def get_no_sensors(self):
		no_sensors = [99999] * self.pop_size
		for s in range(self.pop_size):
			no_sensors[s] = np.count_nonzero(self.population[s] == 1.0)
		
		self.no_sensors = no_sensors
		return self.no_sensors

	def getCost(self):
		coverage = self.get_coverage()
		loss = self.get_max_loss()
		squantity = self.get_no_sensors()

		return [Cost(c, l, s) for c, l, s in zip(coverage, loss, squantity)]
