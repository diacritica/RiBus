import pygraphviz as pgv
import networkx as nx
import random


def returnBusGrid(filename):

    gv = pgv.AGraph(filename, strict=False, directed=True)
    BG = nx.DiGraph(gv)
    return BG

def returnChildrenGrid(filename):

    gv = pgv.AGraph(filename, strict=False, directed=True)
    CG = nx.DiGraph(gv)
    return CG

if __name__=="__main__":

    bg = returnBusGrid("busgrid.dot")
    cg = returnChildrenGrid("childrengrid.dot")

    for i in nx.dfs_edges(bg, "node_2614", depth_limit=5):
        print(i)

    last_node = list(nx.dfs_edges(bg, "node_2614", depth_limit=5))[-1][-1]

    for y in nx.all_shortest_paths(bg,"node_2614","node_2515"):
        print(y)

    for y in nx.all_shortest_paths(bg,"node_2614",last_node):
        print(y)

    print(random.choice(list(nx.all_shortest_paths(bg, "node_2614", last_node))))