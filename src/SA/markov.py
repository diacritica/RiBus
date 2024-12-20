import random, math, json
from routesbuilder import Routesbuilder

total_attempts = 0
chain_length = 10
max_chains = 100
max_attempts = 30
min_value = 0
alpha = 0.95
min_cost = 0


initial_temperature = 250


# list of schools comes as [{"school":"name of the school", "node_id": node_id}, {},{},]

buses = [{"id":"A","capacity":55},{"id":"B","capacity":55},{"id":"C","capacity":55},{"id":"D","capacity":60},
        {"id":"E","capacity":55},{"id":"F","capacity":55},{"id":"G","capacity":55},{"id":"H","capacity":60},
        {"id":"I","capacity":55}]

avg_length_of_routes = 17
delta_length = 3
 
with open('../../utils/data/schools_epsg3857.json') as schools_file:
    file_contents = schools_file.read()
    list_of_schools = json.loads(file_contents)

bus_grid_filename = "../../utils/data/mesh_roads_epsg3857.dot"
child_grid_filename = "../../utils/data/mesh_full_epsg3857.dot"
jsonattrfile = "../../utils/data/students_epsg3857.json"
 



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
        n = rb.getNeighbourSolution()
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

        print("BS",rb.best_solution["cost"])
     
        temperature = temperature * alpha
    



if __name__ == "__main__":

    with open('../../utils/data/base.json') as base_routes_file:
        file_contents = base_routes_file.read()
        base_routes = json.loads(file_contents)

    # list of schools comes as [{"school":"name of the school", "node_id": node_id}, {},{},]

 
    with open('../../utils/data/schools_epsg3857.json') as schools_file:
        file_contents = schools_file.read()
        list_of_schools = json.loads(file_contents)

    bus_grid_filename = "../../utils/data/mesh_roads_epsg3857.dot"
    child_grid_filename = "../../utils/data/mesh_full_epsg3857.dot"
    jsonattrfile = "../../utils/data/students_epsg3857.json"
 

    rb = Routesbuilder( bus_grid_filename, child_grid_filename, jsonattrfile, list_of_schools)

    rb.best_solution = rb.solution

    cooling(initial_temperature)

    with open("out.json","w") as f:
        f.write(json.dumps(rb.solution))
    f.close()
    
    print("Solution cost:",rb.solution["cost"])
    print("Children:",rb.getAttendedChildren())


    