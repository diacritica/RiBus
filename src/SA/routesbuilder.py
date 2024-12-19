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
        self.original_mesh = copy.copy(self.m)


    def traverseRoute(self, route):
        dest_schools = set([s["id"] for s in route["schools"]])
        if route["id"] == "A":
            print("Route A dest_schools", dest_schools)
        #print("Bus Route",route["id"],"towards schools",dest_schools)
     
        for c in route["path"]:

            local_pickup = False
            pickup = False
            #0-cell
            mesh_node = self.m.graph.nodes[c["node_id"]]

            local_pickup = self.takeSchoolClustersFromNode(route, dest_schools, mesh_node, c)
            if local_pickup: pickup = True

            #1-cell
            # cell1_nodes = mesh_node["edges"]
            # for c1 in cell1_nodes:
            #     c1_mesh_node = self.m.graph.nodes[c1]
            #     cell1_pickup = self.takeSchoolClustersFromNode(route, dest_schools, c1_mesh_node, c, "1cell")
            #     if cell1_pickup: pickup = True

            cell2_explored_nodes = list(nx.dfs_edges(self.m.graph, c["node_id"], depth_limit=2))
            cell2_nodes = []
            for tuple in cell2_explored_nodes:
                cell2_nodes.append(tuple[0])
                cell2_nodes.append(tuple[1])
            cell2_nodes = set(cell2_nodes)
            if route["id"] == "A":
                print("Route A for node", c["node_id"], "has", len(cell2_nodes)," nodes")

            #2-cell that includes 1-cell
            for c2 in cell2_nodes:
                c2_mesh_node = self.m.graph.nodes[c2]
                cell2_pickup = self.takeSchoolClustersFromNode(route, dest_schools, c2_mesh_node, c, "2cell")
                if cell2_pickup: pickup = True            

            if not pickup:
                route["path"][route["node_index"][c["node_id"]]]["time"] = 0.60
                route["cost"] += 10

            
            # We check if we can leave clusters at a school
            if c["school"]:
                school = c["school"][0]["id"]
                self.leaveClustersAtSchool(route, c, school)


    def leaveClustersAtSchool(self, route, c, dest_school):
        # we have to remove school from dest_schools from that route!

        #print("We leave people at school",dest_school)
        freed_capacity = 0

        cell0_clusters = c["0cell"]
        for cell0_c in cell0_clusters:
            if cell0_c["school"] == dest_school:
                freed_capacity += cell0_c["count"]
                cell0_clusters.remove(cell0_c)
        cell1_clusters = c["1cell"]
        for cell1_c in cell1_clusters:
            if cell1_c["school"] == dest_school:
                freed_capacity += cell1_c["count"]
                cell1_clusters.remove(cell1_c)
        
        cell2_clusters = c["2cell"]
        for cell2_c in cell2_clusters:
            if cell2_c["school"] == dest_school:
                freed_capacity += cell2_c["count"]
                cell2_clusters.remove(cell2_c)

        if route["id"] == "A":
            print("Route", route["id"], "leaves", freed_capacity, "students at",dest_school, "at node",c["node_id"])
            print("Previous capacity",route["bus_available_capacity"])
            route["bus_available_capacity"] += freed_capacity
            print("New capacity",route["bus_available_capacity"])
        else:
            route["bus_available_capacity"] += freed_capacity

                
    def takeSchoolClustersFromNode(self, route, dest_schools, mesh_node, c, cell="0cell"):

        local_pickup = False
        mesh_node_schools = set(mesh_node["schools"])

        school_intersection = dest_schools.intersection(mesh_node_schools)

        if school_intersection:

            # from 0cell to 2cell clusters 
            for school in school_intersection:
                for mns in mesh_node_schools:
                    if school == mns:
                        potential_clusters = mesh_node["schools"][school] 
                        for pc in potential_clusters:
                            if route["bus_available_capacity"] >= pc["count"]:
                                pc["school"] = school
                                route["path"][route["node_index"][c["node_id"]]][cell].append(pc)
                                route["bus_available_capacity"] -= pc["count"]

                                self.m.removeClusterFromNode(pc["id"],c["node_id"])

                                route["path"][route["node_index"][c["node_id"]]]["time"] = 1

                                #print("+",pc["id"],"to",school,"for",dest_schools)
                                local_pickup = True

                                    
                    else:
                        pass

        return local_pickup
            


    def traverseAllRoutes(self, solution):
        solution["cost"] = 0
        for r in self.routes:
            r["cost"] = 0
            self.traverseRoute(r)
            solution["cost"] += r["cost"]

    def getFreshRoute(self, bus):

        school = self.list_of_schools[random.choice(list(self.list_of_schools))]
        route = {"id":bus["id"], "bus_capacity":bus["capacity"], "bus_available_capacity":bus["capacity"], "schools":[school], "cost":0}
        length = self.avg_length_of_routes - random.choice(range(self.delta_length))
        connected_nodes = []
        
        # we take the last tuple, and then the second node, which has to be, by definition, a school node
        #simple_paths_for_bus = list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length))
        #print(">>>>>>dfsedges",school["node"],list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length)))
        last_node = list(nx.dfs_edges(self.bus_grid, school["node"], depth_limit=length))[-1][-1]

        # we also need to make sure the path goes through 1 other school TBD. For now we pick one random
        for path in nx.all_simple_paths(self.bus_grid, source=school["node"], target=last_node, cutoff=length):
            if len(path) >= int(length*0.9):
                connected_nodes = path
                #print("Creating initial bus route for bus:",bus["id"])
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
                sbns = []
                sbn_list = self.getSchoolsByNode(node)
                for s in sbn_list:
                    sbns.append(self.list_of_schools[s])
                if sbns:
                    path.append({"node_id":node, "school": sbns, "0cell": [], 
                        "1cell": [], 
                        "2cell":[], 
                        "payload": 0, "time": 2})     
                    route["schools"] = route["schools"] +sbns
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

        return route
    
    def getSchoolsByNode(self, node):
        schools = []
        for k, v in self.list_of_schools.items():
            if v["node"] == node:
                schools.append(k)
        return schools

    def getNeighbourSolution(self):

        # self.solution is in the form {"solution":[], "cost": int}
        self.temp_copy = copy.copy(self.solution)

        # We take a random route and we keep the original bus
        random_route = random.choice(self.temp_copy["solution"])

        self.temp_copy["solution"].remove(random_route)
        route = {"id":random_route["id"], "capacity":random_route["bus_capacity"], "schools":[], "cost":0}

        # We generate a completely new bus route for said bus
        self.temp_copy["solution"].append(self.getFreshRoute(route))
        self.m = self.original_mesh
        self.traverseAllRoutes(self.temp_copy)

        #self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])

        return self.temp_copy


    def acceptNeighbour(self):

        self.solution = self.temp_copy
        self.temp_copy = {}

    def undoNeighbour(self):

        self.temp_copy = self.solution

    def getAttendedChildren(self, routes=None):

        children = 0
        if routes:
            for route in routes["solution"]:
                c = route["bus_capacity"] - route["bus_available_capacity"]
                children += c
        else:
            for route in self.solution["solution"]:
                c = route["bus_capacity"] - route["bus_available_capacity"]
                children += c
        return children


if __name__=="__main__":


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
    rb.init(buses,avg_length_of_routes,delta_length,list_of_schools,bus_grid_filename,child_grid_filename, jsonattrfile)
    
    rb.traverseAllRoutes(rb.solution)
    with open("out.json","w") as f:
        f.write(json.dumps(rb.solution))
    f.close()
    print("Solution cost:",rb.solution["cost"])
    print("Children:",rb.getAttendedChildren())


