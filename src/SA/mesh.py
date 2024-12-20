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

    def removeClusterFromNode(self, cluster_id, node_id, origin):
        n_schools = self.graph.nodes[node_id]["schools"]

        for s, cs in n_schools.items():
            for c in cs:
                if cluster_id == c["id"]:
                    n_schools[s].remove(c)
                    


if __name__ == "__main__":

    dotfile = "../../utils/data/mesh_full_epsg3857.dot"
    jsonattrfile = "../../utils/data/students_epsg3857.json"
    m = Mesh(dotfile, jsonattrfile)
    print(m.graph.nodes["node_468"])
    m.removeClusterFromNode("cluster_10143","node_468")
    print(m.graph.nodes["node_468"])
