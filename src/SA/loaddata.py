import pygraphviz as pgv
import networkx as nx


def returnBusGrid(filename):

    gv = pgv.AGraph(filename, strict=False, directed=True)
    BG = nx.DiGraph(gv)
    return BG

def returnChildrenGrid(filename):

    gv = pgv.AGraph(filename, strict=False, directed=True)
    CG = nx.DiGraph(gv)
    return CG

if __name__=="__main__":

    returnBusGrid("busgrid.dot")
    returnChildrenGrid("childrengrid.dot")