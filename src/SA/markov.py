import random, math
from routesbuilder import Routesbuilder

total_attempts = 0
chain_length = 10
max_chains = 100
max_attempts = 30
min_value = 0
alpha = 0.95
min_cost = 0


initial_temperature = 250
    
rb = Routesbuilder()
rb.initialize(6, "es", "cuñado", "tornar")
rb.best_solution = rb.solution


finished_calculus = False


def end_condition():
    return False

def too_much_invested_time():
    return False

def markov_chain(temperature):

    attempts = 0
    accepted_attempts = 0

    while ( (accepted_attempts < chain_length) and (attempts < max_attempts)):
        # we might want to remove the attempts condition

        current = rb.solution
        n = rb.generateNeighbour()
        attempts += 1

        if not accept_neighbour(current, n, temperature):
            rb.undoNeighbour()
        else:
            rb.acceptNeighbour()
            accepted_attempts += 1

        print(".",end=" ")

def accept_neighbour(current, n, temperature):

    if n["cost"] <= current["cost"]:
        return True
    if ( random.random() < math.exp (-(n["cost"] - current["cost"])/temperature) ):
        return True
    
    return False



def cooling(initial_temperature):
    # main solution-space traversing process

    temperature = initial_temperature

    chains_without_improvement = 0
    attempts = 0
    previous_cost = 2000


    while ( (chains_without_improvement < max_chains) and (rb.best_solution["cost"] > min_cost) and (not finished_calculus)):

        markov_chain(temperature)
        if rb.solution["cost"] >= rb.best_solution["cost"]:
            chains_without_improvement += 1
        else:
            rb.best_solution = rb.solution
            attempts = max_chains*(attempts+chains_without_improvement)/(max_chains-chains_without_improvement+1)
            chains_without_improvement = 0

     
        temperature = temperature * alpha
    

    print("BS",rb.best_solution)


if __name__ == "__main__":

    cooling(initial_temperature)