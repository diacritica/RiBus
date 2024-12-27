import re
import click
import random
import copy
import json

import networkx as nx
import pygraphviz as pgv

import routescost
from mesh import Mesh
from route import Route

class RouteManager:

    def __init__(self, bus_grid_filename, child_grid_filename, json_attr_filename, base_routes, all_schools):

        self.all_schools = all_schools

        self.bus_grid_filename = bus_grid_filename
        self.child_grid_filename = child_grid_filename
        self.json_attr_filename = json_attr_filename

         # We first build the bus graph.
         # This is the graph that represents available streets for buses (which are more restricted than simply cars)
         # This is necessarily a directed graph since there are one-way parts of the routes
        bgpg = pgv.AGraph(self.bus_grid_filename)
        self.bus_grid = nx.DiGraph(bgpg)

        self.initial_mesh = Mesh(self.child_grid_filename, self.json_attr_filename)    

        first_solution_setup = self.getSolutionSetup(base_routes)

        self.solutions = {"current": [first_solution_setup, None], "neighbour": [None, None]}

        processed_solution_setup = self.processSolutionSetup(self.solutions["current"][0])

        self.solutions["current"][1] = processed_solution_setup



    def getSolutionSetup(self, base_routes):


        # We generate the global mesh with nodes and student data
        # We "hydrate" the child graph with extra information to get our real global mesh
        mesh = copy.deepcopy(self.initial_mesh)    

        asolution_setup = {"routes": [], "total_cost": 0, "total_children": 0, "mesh": mesh}
 
        asolution_setup["base_routes"] = base_routes

        for base_route in base_routes:
            cr = self.getCustomRoute(self.all_schools, base_route["bus"], base_route["schools"], base_route["path"])
            asolution_setup["routes"].append(cr)

        return asolution_setup


    def getCustomRoute(self, all_schools, bus, dest_schools, nodes):

        aroute = Route()
        aroute.create(all_schools, bus, dest_schools, nodes)

        return aroute


    def processSolutionSetup(self, asolution_setup):

        asolution = copy.deepcopy(asolution_setup)

        asolution["total_cost"] = 0

        for route in asolution["routes"]:
        
            route.cost = 0
            route.get_reachable_mesh_nodes(asolution["mesh"])
            route.traverseRoute(asolution["mesh"])        
            
            asolution["total_cost"] += route.cost
        
        asolution["total_children"] = - sum([i.total_served_children for i in asolution["routes"]])

        return asolution

    def getNeighbourBaseRoutes(self, bus_grid_filename, child_grid_filename, json_attr_filename, asolution_setup):

        # We pick a random route
        pos = random.choice(range(len(asolution_setup["base_routes"])))
        random_route = asolution_setup["base_routes"][pos]

        nbus = {"id":random_route["bus"]["id"],"capacity":random_route["bus"]["capacity"]}
        nschools = [random_route["schools"][0]] # list of one final school

        node_i = random.choice(range(len(random_route["path"][1:-1]))) +1
        node = random_route["path"][node_i]
   
        node_post = random_route["path"][node_i-1]
        node_prev = random_route["path"][node_i+1]
     
        connected_nodes = [node_prev, node, node_post]
        for path in nx.all_simple_paths(self.bus_grid, source=node_post, target=node_prev, cutoff=3):
            if len(path) >= 2:
                connected_nodes = path
                break

        first_part = random_route["path"][:node_i-1]
        last_part = random_route["path"][node_i+2:]
        cnodes =  first_part + connected_nodes + last_part

        base_routes = copy.deepcopy(asolution_setup["base_routes"])

        base_routes[pos] = {"bus": nbus, "path": cnodes, "schools": nschools}

        return base_routes

    def getNeighbourSolutionSetup(self, asolution_setup):

        # We pick a random route
        pos = random.choice(range(len(asolution_setup["base_routes"])))
        random_route = asolution_setup["base_routes"][pos]

        nbus = {"id":random_route["bus"]["id"],"capacity":random_route["bus"]["capacity"]}
        nschools = [random_route["schools"][0]] # list of one final school

        node_i = random.choice(range(len(random_route["path"][1:-1]))) +1
        node = random_route["path"][node_i]
   
        node_post = random_route["path"][node_i-1]
        node_prev = random_route["path"][node_i+1]
     
        connected_nodes = [node_prev, node, node_post]
        for path in nx.all_simple_paths(self.bus_grid, source=node_post, target=node_prev, cutoff=3):
            if len(path) >= 2:
                connected_nodes = path
                break

        first_part = random_route["path"][:node_i-1]
        last_part = random_route["path"][node_i+2:]
        cnodes =  first_part + connected_nodes + last_part

        base_routes = copy.deepcopy(asolution_setup["base_routes"])

        base_routes[pos] = {"bus": nbus, "path": cnodes, "schools": nschools}

        n_solution_setup = self.getSolutionSetup(base_routes)

        return n_solution_setup


    def acceptNeighbour(self):

        self.solutions["current"] = self.solutions["neighbour"]
        self.solutions["neighbour"] = [None, None]


    def undoNeighbour(self):

        self.solutions["neighbour"] = [None, None]


if __name__=="__main__":


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
 

    rb = RouteManager(bus_grid_filename, child_grid_filename, jsonattrfile, base_routes, list_of_schools)

    fss = rb.solutions["current"][0]
    fsp = rb.solutions["current"][1]

    fsp = rb.processSolutionSetup(fss)
 

    with open("out.json","w") as f:
        f.write("\n".join([r.__repr__() for r in fsp["routes"]]))
    f.close()
    
    print("Solution cost:",fsp["total_cost"])
    #students_total = sum([i.total_served_children for i in rb.solution["routes"]])
    print("Students:", fsp["total_children"])

    for i in range(20):

        print(">>>> We build neighbour solution")

        nss = rb.getNeighbourSolutionSetup(fss)
        nsp = rb.processSolutionSetup(nss)
        fss = nss

        print("Neighbour Students:", nsp["total_children"])


    with open("out_final.json","w") as f:
        f.write("\n".join([r.__repr__() for r in nsp["routes"]]))
    f.close()
