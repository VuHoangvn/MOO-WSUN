import sys
import os
from input import Input

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

from utils.population_generation import initialPopulation
from algorithms import ITLBO, MODE, MOEA_D, NSGA_II

NUM_ITER = 30

def run(data_file, iteration):
    data = Input.from_file(data_file)
    sensor_quantity = data.num_of_sensors
    population = initialPopulation(sensor_quantity)

    # output_itlbo = "../output/itlbo/gen_" + str(iteration)
    output_nsga_ii = "../output/nsga_ii/gen_" + str(iteration)
    # output_mode = "../output/mode/gen_" + str(iteration)
    # output_moea_d = "../output/moea_d/gen_" + str(iteration)

    # itlbo = ITLBO(population, data, output_itlbo)
    # moea_d = MOEA_D(population, data, output_moea_d)
    nsga_ii = NSGA_II(population, data, output_nsga_ii)
    # mode = MODE(population, data, output_mode)
    
    # mode.run()
    # moea_d.run()
    nsga_ii.run()
    # itlbo.run()

    
if __name__ == '__main__':
    for iteration in range(NUM_ITER):
        print('---------------------------------------------')
        print('LOOP ', iteration)
        print('---------------------------------------------')
        run('../data/small_data/no-dem1_r25_1.in', iteration)