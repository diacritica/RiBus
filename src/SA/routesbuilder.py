import networkx as nx
import re
import click
import random
import copy

import routescost


route_structure = {"bus_capacity":55,"bus_real_capacity":53,
                   "path":[{"id":1,"school":0,"payload":10,"time":1,"local_clusters":[{"id":345,"n":5,"school":2},{"id":666,"n":2,"school":3}],
                            "nearby_clusters":[{"id":111,"n":2,"school":3},{"id":222,"n":1,"school":3}]},
                    {"id":3,"school":0,"payload":12,"time":1,"local_clusters":[{"id":444,"n":2,"school":2}],"nearby_clusters":[]},
                    {"id":7,"school":0,"payload":12,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":9,"school":0,"payload":19,"time":1,"local_clusters":[{"id":555,"n":3,"school":3},{"id":777,"n":2,"school":2}],
                            "nearby_clusters":[{"id":888,"n":1,"school":3},{"id":999,"n":1,"school":3}]},
                    {"id":20,"school":2,"payload":13,"time":2,"local_clusters":[],"nearby_clusters":[{"id":33,"n":2,"school":3},{"id":321,"n":1,"school":3}]},
                    {"id":23,"school":0,"payload":13,"time":0.60,"local_clusters":[],"nearby_clusters":[]},
                    {"id":12,"school":3,"payload":0,"time":2,"local_clusters":[],"nearby_clusters":[]}]}

class Routesbuilder:

    def __init__(self):
        self.G = nx.Graph()

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
    rb.initialize(6, "es", "cuñado", "tornar")
    rb.generateNeighbour()