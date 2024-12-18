import re
import click
import random
import copy

import networkx as nx
import pygraphviz as pgv

import routescost


class Routesbuilder:

    def __init__(self):
        self.G = nx.Graph()

    def init(self, buses, avg_length_of_routes, delta_length, list_of_schools, bus_grid_filename, child_grid_filename):

        # list of schools comes as [{"school":"name of the school", "node_id": node_id}, {},{},]

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



    def getFreshRoute(self, bus):

        school = random.choice(self.list_of_schools)
        route = {"id":bus["id"], "bus_capacity":bus["capacity"], "schools":[school]}
        length = self.avg_length_of_routes - random.choice(range(self.delta_length))


        last_node = list(nx.dfs_edges(self.bus_grid, school["node_id"], depth_limit=length))[-1][-1]

        # we also need to make sure the path goes through 1 other school TBD. For now we pick one random
        connected_nodes = random.choice(list(nx.all_shortest_paths(self.bus_grid, school["node_id"], last_node)))

        path = []

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
        route["path"] = path

        return route
                    

    def initialize(self, letters, language, start, end):

        self.start = start
        self.end = end
        self.solution = {"solution":[], "cost":2000}
        self.temp_copy = {}
        self.best_solution = {"solution":[], "cost":2000}

        self.allwords = []

        if len(start) == len(end):
            letters = int(len(start))
        numletter = int(letters)
        wordpattern = "^"+"."*numletter+"$"
        wordsregex = re.compile(wordpattern)

        if language in ["es","en"]:
            with open('words_{}.txt'.format(language), "r") as wordsfile:
                allwords = list(filter(wordsregex.match, [i.strip() for i in wordsfile.readlines()]))

        self.allwords = allwords
        self.G.add_nodes_from(allwords)

        click.secho("Number of nodes/words "+str(self.G.number_of_nodes()),fg='white')

        click.secho("Creating edges between words. This might take a while...", blink=True, bold=True)
        for w in allwords:
            replacelist = []
            for i in range(numletter):
                replacelist.append(w.replace(w[i],".",3))
                #print(w, replacelist[i])

            r = re.compile("|".join(replacelist))
            listofnearbywords = list(filter(r.match, allwords))

            self.G.add_edges_from([(w,j) for j in listofnearbywords])

        click.echo("Number of edges "+str(self.G.number_of_edges()))
        self.createFirstSolution()

    def createFirstSolution(self):
        self.solution["solution"] = list(nx.all_shortest_paths(self.G,self.start,self.end))
        self.solution["cost"] = routescost.route_total_cost(self.solution["solution"])
        print("createFirstSolution finished", len(self.solution["solution"]), self.solution["cost"])
        print("FS",self.solution["solution"])

    def generateNeighbour(self):

        self.temp_copy = copy.copy(self.solution)

        random_route = random.choice(self.temp_copy["solution"])
        random_pos = random.randint(0, len(random_route)-3)
        random_cell_init = random_route[random_pos]
        random_cell_inter = random_route[random_pos+1]
        random_cell_final = random_route[random_pos+2]

#        self.G.remove_edge(random_cell_init, random_cell_inter)
#        self.G.remove_edge(random_cell_inter, random_cell_final)

        newnode = random.choice(self.allwords)

        self.G.add_edge(random_cell_init, newnode)
        self.G.add_edge(newnode, random_cell_final)
        random_route[random_pos+1] = newnode

        self.temp_copy["cost"] = routescost.route_total_cost(self.temp_copy["solution"])
#        print("generateNeighbour finished", len(self.temp_copy["solution"]), self.temp_copy["cost"])
#        print("NS",self.temp_copy["solution"])

        return self.temp_copy

    def acceptNeighbour(self):

        self.solution = self.temp_copy
        self.temp_copy = {}

    def undoNeighbour(self):

        self.temp_copy = self.solution


if __name__=="__main__":

    rb = Routesbuilder()
    rb.init([{"id":"A","capacity":55},{"id":"B","capacity":55}],30,5,[{"school":"C1", "node_id": "node_2614"},{"school":"C2", "node_id": "node_3102"}],"busgrid.dot","childrengrid.dot")
#    rb.generateNeighbour()