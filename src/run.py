import sys
import os
from input import Input

ROOT = os.path.dirname(os.path.abspath(__file__))+"/../"
sys.path.append(ROOT)

from utils.population_generation import initialPopulation
from algorithms import ITLBO, MODE, MOEA_D, NSGA_II

NUM_ITER = 30

def run(data_file, iteration, output_dir):
    data = Input.from_file(data_file)
    sensor_quantity = data.num_of_sensors
    population = initialPopulation(sensor_quantity)

    algos = ["itlbo", "nsga_ii", "mode", "moea_d"]
    output_file = []
    for algo in algos:
        file = output_dir + '/' + algo
        if not os.path.exists(file):
            os.makedirs(file)
        
        output_file.append(file)

    output_itlbo = output_file[0] + "/gen_" + str(iteration)
    output_nsga_ii = output_file[1] + "/gen_" + str(iteration)
    output_mode = output_file[2] + "/gen_" + str(iteration)
    output_moea_d = output_file[3] + "/gen_" + str(iteration)

    itlbo = ITLBO(population, data, output_itlbo)
    moea_d = MOEA_D(population, data, output_moea_d)
    nsga_ii = NSGA_II(population, data, output_nsga_ii)
    mode = MODE(population, data, output_mode)
    
    mode.run()
    moea_d.run()
    nsga_ii.run()
    itlbo.run()
       
if __name__ == '__main__':
    for i in range(1, 11):
        for j in range(25, 35, 5):
            input_file = '../data/small_data/no-dem{}_r{}_1.in'.format(i, j)
            output_dir = '../output/small_data/no-dem{}_r{}_1'.format(i, j)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            print('====================================================')
            print('====================================================')
            print('====================================================')
            print('Running on input data file: ', input_file)
            print('====================================================')
            print('====================================================')
            print('====================================================')

            for iteration in range(NUM_ITER):
                print('---------------------------------------------')
                print('LOOP ', iteration)
                print('---------------------------------------------')
                run(input_file, iteration, output_dir)