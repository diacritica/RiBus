import re
import click
import random
import copy
import json

import networkx as nx

import routescost
from mesh import Mesh


class Route:

    def create(self, all_schools, bus, dest_schools, nodes):

        # we ignore dest_schools

        self.id = bus["id"]
        self.bus_capacity = bus["capacity"]
        self.bus_available_capacity = bus["capacity"]

        self.orig_dest_schools = []
        self.active_dest_schools = []
        self.all_schools = all_schools

        self.taken_child_clusters_per_path_node = {}

        self.nodes = nodes
        self.path_setup(nodes)

        self.cost = 0
        self.total_served_children = 0

        self.covered_mesh_nodes = []
        self.mesh_nodes_by_path_node = {}

    def __repr__(self):

        out = {"id": self.id, "capacity": self.bus_capacity, "nodes": self.nodes, "total_served_children": self.total_served_children}
        return str(out)


    def traverseRoute(self, mesh):

        for index, path_node in enumerate(self.path):

            # We carry over clusters from previous node to the current one
            # before evaluating which new clusters are added
            if index > 0:
                self.path[index]["clusters"] = copy.deepcopy(self.path[index-1]["clusters"])

            for reachable_node in self.mesh_nodes_by_path_node[path_node["node_id"]]:

                pickups = []
                pickups = self.takeClustersFromNode(mesh, path_node, reachable_node)

                self.path[index]["clusters"] += pickups
                
                for cluster in pickups:
                    mesh.removeClusterFromNode(cluster["id"], reachable_node)

            # we check if we can leave clusters at school
            dest_schools_by_node = self.getSchoolsByNode(self.all_schools, path_node["node_id"])
            if dest_schools_by_node:
                for school in dest_schools_by_node:
                    pass
                    l = self.leaveClustersAtSchool(path_node["node_id"], school)




    def leaveClustersAtSchool(self, path_node, dest_school):

        # path_node in the form of path id
        freed_capacity = 0
        index = self.node_index[path_node]
        clusters = self.path[index]["clusters"]

        to_be_left = []

        for cluster in clusters:
            if cluster["school"] == dest_school:
                to_be_left.append(cluster)
                freed_capacity += cluster["count"]

        for cluster_to_be_left in to_be_left:
            self.path[index]["clusters"].remove(cluster_to_be_left)
        
        self.bus_available_capacity += freed_capacity
        return to_be_left

    def takeClustersFromNode(self, mesh, path_node, reachable_node):

        clusters = []

        mesh_node = mesh.graph.nodes[reachable_node]
        mesh_node_schools = set(mesh_node["schools"].keys())

        schools_intersection = set(self.active_dest_schools).intersection(mesh_node_schools)

        if schools_intersection:
            for school in schools_intersection:
                potential_clusters = mesh_node["schools"][school]
                for cluster in potential_clusters:
                    if self.bus_available_capacity >= cluster["count"]:
                       
                        self.taken_child_clusters_per_path_node[path_node["node_id"]].append(cluster)
                        self.total_served_children += cluster["count"]
                        self.bus_available_capacity -= cluster["count"]

                        clusters.append(cluster)
                        cluster["school"] = school

                    
        return clusters

        

    def get_reachable_mesh_nodes(self, mesh):

        for index, node in enumerate(self.path[:-1]):

            cur_node = self.path[index]
            next_node = self.path[index+1]

            
            cur_node_reachable_mesh_nodes = []
            cur_node_reachable_mesh_node_tuples = list(nx.dfs_edges(mesh.graph, cur_node["node_id"], depth_limit=2))

            for tuple in cur_node_reachable_mesh_node_tuples:
                cur_node_reachable_mesh_nodes.append(tuple[0])
                cur_node_reachable_mesh_nodes.append(tuple[1])
            cur_node_reachable_mesh_nodes = set(cur_node_reachable_mesh_nodes)

            next_node_reachable_mesh_nodes = []
            
            next_node_reachable_mesh_node_tuples = list(nx.dfs_edges(mesh.graph, next_node["node_id"], depth_limit=2))

            for tuple in next_node_reachable_mesh_node_tuples:
                next_node_reachable_mesh_nodes.append(tuple[0])
                next_node_reachable_mesh_nodes.append(tuple[1])
            next_node_reachable_mesh_nodes = set(next_node_reachable_mesh_nodes)


            intersection = cur_node_reachable_mesh_nodes.intersection(next_node_reachable_mesh_nodes)

            # CONVENTION: we give precedent path nodes preference over reachable mesh nodes

            cur_node["reachable_nodes"] = cur_node_reachable_mesh_nodes
            next_node["reachable_nodes"] = next_node_reachable_mesh_nodes - intersection

            # We populate auxiliary data structures

            self.mesh_nodes_by_path_node[cur_node["node_id"]] = cur_node["reachable_nodes"]
            self.mesh_nodes_by_path_node[next_node["node_id"]] = next_node["reachable_nodes"]

            self.covered_mesh_nodes += cur_node["reachable_nodes"]
            self.covered_mesh_nodes += next_node["reachable_nodes"]



    def path_setup(self, nodes):

        # CONVENTION: nodes order is final node first (typically includes a school)
        
        nodes_length = len(nodes)

        path = []
        node_index = {}

        for index, node in enumerate(nodes):

            self.taken_child_clusters_per_path_node[node] = []


            dest_schools_by_node = self.getSchoolsByNode(self.all_schools, node)

            if dest_schools_by_node:

                # CONVENTION We make sure ALL schools found in the route are added despite not being provided at instance creation time. This can be overriden by removing this FOR LOOP and sticking with instance creation
                for dest_school in dest_schools_by_node:
                    if dest_school not in self.active_dest_schools:
                        self.active_dest_schools.append(dest_school)

                path.append({"node_id": node, "schools": dest_schools_by_node, "clusters": [], "reachable_nodes": [],
                    "time": 2})     
                
                # we have to update orig_schools too!

            else:
                path.append({"node_id":node, "schools": [], 
                             "reachable_nodes": [], "clusters": [], "time": 0})     
                     
            # we create a reverse index to acount for the following path reverse
            # print('route["schools"]',route["schools"])
            node_index[node] = nodes_length - index -1

        self.orig_dest_schools = copy.deepcopy(self.active_dest_schools)
        self.path = path
        self.path.reverse()
        self.node_index = node_index


    def getSchoolsByNode(self, all_schools, node):
        schools = []
        for k, v in self.all_schools.items():
            if v["node"] == node:
                schools.append(k)
        return schools
    
    def evaluate_cost_by_path_node(self, node):
        pass

    def evaluate_cost_by_path(self):
        pass
    