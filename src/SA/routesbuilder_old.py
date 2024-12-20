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

    def initialize(self, buses, avg_length_of_routes, delta_length, list_of_schools, bus_grid_filename, child_grid_filename, json_attr_filename):

        # list of schools comes as [{"id":"name of the school", "node": node_id}, {},{},]

        self.buses = buses
        self.avg_length_of_routes = avg_length_of_routes
        self.delta_length = delta_length
        self.list_of_schools = list_of_schools

        print("RoutesBuilder start")
        print("buses", self.buses)
        print("avg_length_of_routes", self.avg_length_of_routes)
        print("delta_length", self.delta_length)
        print("list_of_schools", self.list_of_schools)
        print("-----------------------------------------")

        self.routes = []

        # We first build the bus graph
        bgpg = pgv.AGraph(bus_grid_filename)
        self.bus_grid = nx.DiGraph(bgpg)

        # We also build the children clusters graph
        cgpg = pgv.AGraph(child_grid_filename)
        self.child_grid = nx.Graph(cgpg)

        for bus in buses:
            self.routes.append(self.getFreshRoute(bus))

        self.solution = {"solution":self.routes, "cost":10000}

        # We generate the global mesh with nodes and student data
        self.m = Mesh(child_grid_filename, json_attr_filename)

        self.original_mesh = copy.deepcopy(self.m)
        self.init_solution = copy.deepcopy(self.solution)

    def traverseRoute(self, route):
   
        for i, c in enumerate(route["path"]):
            dest_schools = set([s["id"] for s in route["schools"]])

            if i > 0:
                route["path"][i]["2cell"] = copy.deepcopy(route["path"][i-1]["2cell"])

            pickup = False


            cell2_explored_nodes = list(nx.dfs_edges(self.m.graph, c["node_id"], depth_limit=2))
            cell2_nodes = []
            for tuple in cell2_explored_nodes:
                cell2_nodes.append(tuple[0])
                cell2_nodes.append(tuple[1])
            cell2_nodes = set(cell2_nodes)

            #2-cell that includes 1-cell and 0-cell
            cell2_pickups = []
            for c2 in cell2_nodes:
                c2_mesh_node = self.m.graph.nodes[c2]
                cell2_pickups = self.takeSchoolClustersFromNode(route, dest_schools, c2_mesh_node, c, "2cell")
                for cell2 in cell2_pickups:
                    self.m.removeClusterFromNode(cell2["id"],c2,"cell2")
               

            if cell2_pickups: 
                route["path"][route["node_index"][c["node_id"]]]["time"] = 1
                pickup = True   


            if not pickup:
                route["path"][route["node_index"][c["node_id"]]]["time"] = 0.60
                route["cost"] += 50

            # We check if we can leave clusters at a school
            if c["school"]:
                school = c["school"][0]["id"]
                if(self.leaveClustersAtSchool(route, c, school)):
                    route["path"][route["node_index"][c["node_id"]]]["time"] = 2
        
        # we evaluate long trips
        final_school = route["orig_schools"][0]
        penultimate_node = route["path"][-2]
        dest_school_children = penultimate_node["2cell"]
        times = []
        for d_s_c in dest_school_children:
            cluster_time = 0
            for p in route["path"][:-1]:
                if d_s_c["school"] == final_school["id"]:
                    if d_s_c["id"] in [i["id"] for i in p["2cell"]]:
                        cluster_time += p["time"]
            times.append(int(cluster_time))
        route["cost"] += sum(times) #something very basic for now
                




    def leaveClustersAtSchool(self, route, c, dest_school):
        # we have to remove school from dest_schools from that route!

        #print("We leave people at school",dest_school)
        freed_capacity = 0

      
        cell2_clusters = c["2cell"]
        to_be_left = []
        for cell2_c in cell2_clusters:

            if cell2_c["school"] == dest_school:
                freed_capacity += cell2_c["count"]
                to_be_left.append(cell2_c)


        for tbl in to_be_left:
            cell2_clusters.remove(tbl)

        route["bus_available_capacity"] += freed_capacity
        route["schools"].remove(c["school"][0])

        return to_be_left


                
    def takeSchoolClustersFromNode(self, route, dest_schools, mesh_node, c, cell="0cell"):

        pickup = []
        mesh_node_schools = set(mesh_node["schools"])

        school_intersection = dest_schools.intersection(mesh_node_schools)

        if school_intersection:

            # from 0cell to 2cell clusters 
            for school in school_intersection:
                potential_clusters = mesh_node["schools"][school]
                for pc in potential_clusters:
                    if route["bus_available_capacity"] >= pc["count"]:
                       
                        c[cell].append(pc)
                        route["students"] += pc["count"]
                        route["bus_available_capacity"] -= pc["count"]

                        pickup.append(pc)
                        pc["school"] = school

                        c["time"] = 1
                        

                                    
                    
        return pickup
            


    def traverseAllRoutes(self, solution):
        solution["cost"] = 0
        for r in solution["solution"]:
            r["cost"] = 0
            self.traverseRoute(r)
            solution["cost"] += r["cost"]


    def getCustomRoute(self, bus, dest_school, nodes):

        school = dest_school
        route = {"id":bus["id"], "bus_capacity":bus["capacity"], "bus_available_capacity":bus["capacity"], "students":0, "orig_schools": [school], "schools":[school], "cost":0}
        length = len(nodes)
        nodes.reverse()
        connected_nodes = nodes

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
                schools_by_node = []
                sbn_list = self.getSchoolsByNode(node)

                # FIXME redundant
                for s in sbn_list:
                    schools_by_node.append(self.list_of_schools[s])

                if schools_by_node:
                    path.append({"node_id":node, "school": schools_by_node, "0cell": [], 
                        "1cell": [], 
                        "2cell":[], 
                        "payload": 0, "time": 2})     
                    if schools_by_node[0] not in route["orig_schools"]:
                        route["schools"] = route["schools"] + schools_by_node
                        route["orig_schools"] = route["orig_schools"] + schools_by_node

                else:
                    path.append({"node_id":node, "school": [], "0cell": [], 
                        "1cell": [], 
                        "2cell":[], 
                        "payload": 0, "time": 0})     
                     
            # we create a reverse index to acount for the following path reverse
            # print('route["schools"]',route["schools"])
            node_index[node] = connected_nodes_length - index -1

        route["path"] = path
        route["path"].reverse()
        route["node_index"] = node_index

        print("----------> custom route generated", route)
        return route


    def getFreshRoute(self, bus):

        school = self.list_of_schools[random.choice(list(self.list_of_schools))]
        route = {"id":bus["id"], "bus_capacity":bus["capacity"], "bus_available_capacity":bus["capacity"], "students":0, "orig_schools": [school], "schools":[school], "cost":0}
        length = self.avg_length_of_routes - random.choice(range(self.delta_length))
        connected_nodes = []

        # we take the last tuple, and then the second node, which has to be, by definition, a school node
        last_node = list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length))[-1][-1]

        # we also need to make sure the path goes through 1 other school TBD. For now we pick one random
        for path in nx.all_simple_paths(self.bus_grid, source=school["node"], target=last_node, cutoff=length):
            if len(path) >= int(length):
                connected_nodes = path
                break
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
                schools_by_node = []
                sbn_list = self.getSchoolsByNode(node)

                # FIXME redundant
                for s in sbn_list:
                    schools_by_node.append(self.list_of_schools[s])

                if schools_by_node:
                    path.append({"node_id":node, "school": schools_by_node, "0cell": [], 
                        "1cell": [], 
                        "2cell":[], 
                        "payload": 0, "time": 2})     
                    route["schools"] = route["schools"] + schools_by_node
                    route["orig_schools"] = route["orig_schools"] + schools_by_node

                else:
                    path.append({"node_id":node, "school": [], "0cell": [], 
                        "1cell": [], 
                        "2cell":[], 
                        "payload": 0, "time": 0})     
                     
            # we create a reverse index to acount for the following path reverse
            # print('route["schools"]',route["schools"])
            node_index[node] = connected_nodes_length - index -1

        route["path"] = path
        route["path"].reverse()
        route["node_index"] = node_index

        if len(route["orig_schools"]) > 2:
            route["cost"] += 10

        return route
    
    def getSchoolsByNode(self, node):
        schools = []
        for k, v in self.list_of_schools.items():
            if v["node"] == node:
                schools.append(k)
        return schools


    def getNeighbourSolution(self):

        # self.solution is in the form {"solution":[], "cost": int
        # self.setup = {"solution": copy.copy(self.solution), "original_mesh": copy.copy(self.original_mesh)}

        self.temp_copy = copy.deepcopy(self.init_solution)

        pos1 = random.choice(range(len(self.temp_copy["solution"])))

        pos2 = random.choice(range(len(self.temp_copy["solution"])))
        while pos1 == pos2:
            pos2 = random.choice(range(len(self.temp_copy["solution"])))

        random_route1 = copy.copy(self.temp_copy["solution"][pos1])
        random_route2 = copy.copy(self.temp_copy["solution"][pos2])

        self.temp_copy["solution"].remove(random_route1)
        self.temp_copy["solution"].remove(random_route2)

        self.temp_copy["solution"].insert(pos2, random_route1)
        self.temp_copy["solution"].insert(pos1, random_route2)

        self.m = self.original_mesh
        self.traverseAllRoutes(self.temp_copy)
        print("COSTE DE NEIGHBOUR",self.temp_copy["cost"])

        #self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])

        return self.temp_copy


    def getNeighbourSolutionNew(self):

        # self.solution is in the form {"solution":[], "cost": int
        # self.setup = {"solution": copy.copy(self.solution), "original_mesh": copy.copy(self.original_mesh)}

        self.temp_copy = copy.deepcopy(self.init_solution)

        pos = random.choice(range(len(self.temp_copy["solution"])))
        random_route = self.temp_copy["solution"][pos]

        nbus = {"id":random_route["id"],"capacity":random_route["bus_capacity"]}
        nschool = random_route["orig_schools"][0]


        node = random.choice(random_route["path"][1:-1])
        node_i = random_route["node_index"][node["node_id"]]
   
        node_post = random_route["path"][node_i-1]["node_id"]
        node_prev = random_route["path"][node_i+1]["node_id"]
     

        for path in nx.all_simple_paths(self.bus_grid, source=node_post, target=node_prev, cutoff=3):
            if len(path) >= 2:
                connected_nodes = path
                break
        

        first_part = [i["node_id"] for i in random_route["path"][:node_i-1]]
        last_part = [i["node_id"] for i in random_route["path"][node_i+2:]]
        cnodes =  first_part + connected_nodes + last_part


        cr = self.getCustomRoute(nbus, nschool, cnodes)
        
        #self.traverseRoute(cr)
        self.temp_copy["solution"][pos] = cr


        # We generate a completely new bus route for said bus

        self.m = self.original_mesh
        self.traverseAllRoutes(self.temp_copy)
        #print("COSTE DE NEIGHBOUR",self.temp_copy["cost"])

        #self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])

        return self.temp_copy

    def getNeighbourSolutionOld(self):

        # self.solution is in the form {"solution":[], "cost": int
        # self.setup = {"solution": copy.copy(self.solution), "original_mesh": copy.copy(self.original_mesh)}

        self.temp_copy = copy.deepcopy(self.init_solution)

        random_route = random.choice(self.temp_copy["solution"])
        self.temp_copy["solution"].remove(random_route)

        route = {"id":random_route["id"], "capacity":random_route["bus_capacity"], "bus_available_capacity":random_route["bus_capacity"], "schools":[], "cost":0}

        # We generate a completely new bus route for said bus
        nr = self.getFreshRoute(route)
        self.temp_copy["solution"].append(nr)
        self.m = self.original_mesh
        self.traverseAllRoutes(self.temp_copy)
        print("COSTE DE NEIGHBOUR",self.temp_copy["cost"])

        #self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])

        return self.temp_copy


    def acceptNeighbour(self):

        self.solution = self.temp_copy
        self.temp_copy = {}

    def undoNeighbour(self):

        self.temp_copy = self.solution

    def getAttendedChildren(self):

        total = 0
        for route in self.routes:
            total += route["students"]
    
        return total


if __name__=="__main__":


    with open('../../utils/data/base.json') as base_routes_file:
        file_contents = base_routes_file.read()
        base_routes = json.loads(file_contents)

    # list of schools comes as [{"school":"name of the school", "node_id": node_id}, {},{},]

    buses = [{"id":"A","capacity":55},{"id":"B","capacity":55},{"id":"C","capacity":55},{"id":"D","capacity":60},
             {"id":"E","capacity":55},{"id":"F","capacity":55},{"id":"G","capacity":55},{"id":"H","capacity":60},
             {"id":"I","capacity":55}]
    avg_length_of_routes = 15
    delta_length = 2
 
    with open('../../utils/data/schools_epsg3857.json') as schools_file:
        file_contents = schools_file.read()
        list_of_schools = json.loads(file_contents)

    bus_grid_filename = "../../utils/data/mesh_roads_epsg3857.dot"
    child_grid_filename = "../../utils/data/mesh_full_epsg3857.dot"
    jsonattrfile = "../../utils/data/students_epsg3857.json"
 

    rb = Routesbuilder()
    rb.initialize(buses, avg_length_of_routes, delta_length, list_of_schools, bus_grid_filename, child_grid_filename, jsonattrfile)
    #rb.traverseRoute(rb.routes[0])


    cnodes = ["node_427","node_468","node_511","node_512","node_513","node_555","node_556","node_557","node_558","node_517","node_475","node_434","node_392","node_351","node_309","node_310","node_311","node_354","node_355","node_397","node_439","node_481","node_482","node_525","node_526","node_568","node_611","node_653","node_695","node_694","node_735","node_777","node_818","node_871","node_913","node_914","node_915","node_958","node_959","node_1001","node_1002","node_1044","node_1086"]
    cschool = {"id":"CEM HIPATIA", "node": "node_427"}    
    cbus = {"id":"Z","capacity":55}
    #cr = rb.getCustomRoute(cbus, cschool, cnodes)
    #rb.traverseRoute(cr)

    #rb.routes.append(cr)

    rb.traverseAllRoutes(rb.solution)

    with open("out.json","w") as f:
        f.write(json.dumps(rb.solution))
    f.close()
    
    print("Solution cost:",rb.solution["cost"])
    print("Students:",sum([i["students"] for i in rb.solution["solution"]]))

    n = rb.getNeighbourSolution()
    n = rb.getNeighbourSolution()
    print("neighbour!")
    print("Solution cost:",n["cost"])
    print("Students:",sum([i["students"] for i in n["solution"]]))

    with open("out_n.json","w") as f:
        f.write(json.dumps(n))
    f.close()
    
