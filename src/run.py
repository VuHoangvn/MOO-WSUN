import sys
import os
from input import Input

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

from utils.population_generation import initialPopulation
from algorithms import ITLBO

def run(data_file):
    data = Input.from_file(data_file)
    sensor_quantity = data.num_of_sensors
    population = initialPopulation(sensor_quantity)

    itlbo = ITLBO(population, data)
    itlbo.run()
if __name__ == '__main__':
    run('../data/small_data/no-dem1_r25_1.in')