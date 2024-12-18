import re
import click
import random
import copy
import json

import networkx as nx
import pygraphviz as pgv

import routescost
from mesh import Mesh



class Routesbuilder:

    def __init__(self):
        self.G = nx.Graph()

    def init(self, buses, avg_length_of_routes, delta_length, list_of_schools, bus_grid_filename, child_grid_filename, json_attr_filename):

        # list of schools comes as [{"id":"name of the school", "node": node_id}, {},{},]

        self.buses = buses
        self.avg_length_of_routes = avg_length_of_routes
        self.delta_length = delta_length
        self.list_of_schools = list_of_schools

        self.routes = []
        bgpg = pgv.AGraph(bus_grid_filename)
        self.bus_grid = nx.DiGraph(bgpg)

        cgpg = pgv.AGraph(child_grid_filename)
        self.child_grid = nx.Graph(cgpg)


        for bus in buses:
            self.routes.append(self.getFreshRoute(bus))

        self.solution = {"solution":self.routes, "cost":10000}

        # We generate the global mesh with nodes and student data
        self.m = Mesh(child_grid_filename, json_attr_filename)


    def traverseRoute(self, route):
        dest_schools = set([s["id"] for s in route["schools"]])
     
        for c in route["path"]:
           # we first go for 0cell

            mesh_node = self.m.graph.nodes[c["node_id"]]
            mesh_node_schools = set(mesh_node["schools"])
            #print(">>>>>mesh_node_schools",mesh_node_schools)
            school_intersection = dest_schools.intersection(mesh_node_schools)
            #print(">>> school intersection", school_intersection)
            if school_intersection:
                # there's a 0cell cluster
                for school in school_intersection:
                    for mns in mesh_node_schools:
                        if school == mns:
                            potential_clusters = mesh_node["schools"][school] 
                            for pc in potential_clusters:
                                if route["bus_available_capacity"] >= pc["count"]:
                                    route["path"][route["node_index"][c["node_id"]]]["0cell"].append(pc)
                                    route["bus_available_capacity"] -= pc["count"]

                                    self.m.removeClusterFromNode(pc["id"],c["node_id"])
                        else:
                            pass

    def traverseAllRoutes(self):
        for r in self.routes:
            self.traverseRoute(r)

    def getFreshRoute(self, bus):

        school = self.list_of_schools[random.choice(list(self.list_of_schools))]
        route = {"id":bus["id"], "bus_capacity":bus["capacity"], "bus_available_capacity":bus["capacity"], "schools":[school], "cost":0}
        length = self.avg_length_of_routes - random.choice(range(self.delta_length))
        connected_nodes = []
        print("LENGTH", length)

        # we take the last tuple, and then the second node, which has to be, by definition, a school node
        #simple_paths_for_bus = list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length))
        #print(">>>>>>dfsedges",school["node"],list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length)))
        last_node = list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length))[-1][-1]

        # we also need to make sure the path goes through 1 other school TBD. For now we pick one random
        for path in nx.all_simple_paths(self.bus_grid, source=school["node"], target=last_node, cutoff=length):
            if len(path) >= int(length*0.9):
                connected_nodes = path
                print("CONNECTED NODES to", school["id"], school["node"], connected_nodes)
                break
        #connected_nodes = random.choice(list(nx.all_simple_paths(self.bus_grid, school["node"], last_node)))
        connected_nodes_length = len(connected_nodes)

        path = []
        node_index = {}

        for index, node in enumerate(connected_nodes):
            if index == 0:
                path.append({"node_id":node, "school": [school], "0cell": [], 
                    "1cell": [], 
                    "2cell":[], 
                    "payload": 0, "time": 2})
            else:
                path.append({"node_id":node, "school": [], "0cell": [], 
                    "1cell": [], 
                    "2cell":[], 
                    "payload": 0, "time": 0})      
            # we create a reverse index to acount for the following path reverse
            node_index[node] = connected_nodes_length - index -1

        route["path"] = path
        route["path"].reverse()
        route["node_index"] = node_index

        return route
    
    def getNeighbourSolution(self):

        # self.solution is in the form {"solution":[], "cost": int}
        self.temp_copy = copy.copy(self.solution)

        # We take a random route and we keep the original bus
        random_route = self.temp_copy["solution"].pop()
        bus = {"id":random_route["id"],"bus_capacity":random_route["capacity"]}

        # We generate a completely new bus route for said bus
        self.temp_copy["solution"].append(self.getFreshRoute(bus))

        self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])

        return self.temp_copy


    def acceptNeighbour(self):

        self.solution = self.temp_copy
        self.temp_copy = {}

    def undoNeighbour(self):

        self.temp_copy = self.solution


if __name__=="__main__":


    # list of schools comes as [{"school":"name of the school", "node_id": node_id}, {},{},]

    buses = [{"id":"A","capacity":55},{"id":"B","capacity":55},{"id":"C","capacity":55},{"id":"D","capacity":60},
             {"id":"E","capacity":55},{"id":"F","capacity":55},{"id":"G","capacity":55},{"id":"H","capacity":60},
             {"id":"I","capacity":55}]
    avg_length_of_routes = 18
    delta_length = 2
 
    with open('../../utils/data/schools_epsg3857.json') as schools_file:
        file_contents = schools_file.read()
        list_of_schools = json.loads(file_contents)

    #print("list_of_schools",list_of_schools)

    bus_grid_filename = "../../utils/data/mesh_roads_epsg3857.dot"
    child_grid_filename = "../../utils/data/mesh_full_epsg3857.dot"
    jsonattrfile = "../../utils/data/students_epsg3857.json"
 

    rb = Routesbuilder()
    rb.init(buses,avg_length_of_routes,delta_length,list_of_schools,bus_grid_filename,child_grid_filename, jsonattrfile)
    
    rb.traverseAllRoutes()
    with open("out.json","w") as f:
        f.write(json.dumps(rb.solution))
    f.close()

#    rb.generateNeighbour()

