import random

def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))
            
            sensor1 = individual[swapped]
            sensor2 = individual[swapWith]
            
            individual[swapped] = sensor2
            individual[swapWith] = sensor1
    return individual