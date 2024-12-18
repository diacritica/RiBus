import pygraphviz as pgv
import networkx as nx
import random
import json

class Mesh:

    def __init__(self, dotfile, jsonattrfile):

        gv = pgv.AGraph(dotfile, strict=False, directed=False)
        CG = nx.Graph(gv)
        self.graph = CG

        with open(jsonattrfile) as mesh_file:
            file_contents = mesh_file.read()
            meshattrdata = json.loads(file_contents)

        

        nx.set_node_attributes(self.graph, meshattrdata)


if __name__ == "__main__":

    dotfile = "../../utils/data/mesh_full_epsg3857.dot"
    jsonattrfile = "../../utils/data/students_epsg3857.json"
    m = Mesh(dotfile, jsonattrfile)
    print(m.graph.nodes["node_646"])