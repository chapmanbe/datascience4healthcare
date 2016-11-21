
import networkx as nx
from collections import defaultdict
import urllib.request



# ### An OBO Parser

# In[6]:

"""

based on

http://techoverflow.net/blog/2013/11/18/a-geneontology-obo-v1.2-parser-in-python/

__author__    = "Uli Koehler"
__copyright__ = "Copyright 2013 Uli Koehler"
__license__   = "Apache v2.0"
"""

def addOBONode(graph,items):
    """
    In an object representing an OBO term, replace single-element lists with
    their only member.
    Returns the modified object as a dictionary.

    """
    ret = dict(items) #Input is a defaultdict, might express unexpected behaviour
    for key, value in ret.items():
        #key = key.replace(":","->")
        if len(value) == 1:
            ret[key] = value[0]
    _is = ret.pop('id').replace(":","->")

    try:
        _isa = ret.pop('is_a')
        if isinstance(_isa,str):
            _isa = [_isa]
    except KeyError:
        # this may be a root node
        if not ret.get('is_obsolete'):
            graph.graph["roots"].append(_is)
        _isa = []

    graph.add_node(_is,attr_dict=ret)
    if _isa:
        for isa in _isa:
            isa, sep, b = isa.partition("!")
            isa = isa.strip()

            graph.add_edge(isa.replace(":","->"),_is)

def parseOBO(filename):
    """
    Parses an OBO file
    """
    ontology = nx.DiGraph(roots=[])
    with urllib.request.urlopen(filename) as fin:
        lines = fin.read().decode("utf-8").split("\n")
    inTerm = False
    currentItems = defaultdict(list)
    while lines:

        line = lines.pop(0)
        line = line.strip()
        if not line:
            continue #Skip empty
        if line == "[Term]":
            if inTerm:
                addOBONode(ontology,currentItems)
                currentItems = defaultdict(list)
            else:
                inTerm = True
        elif line == "[Typedef]":
            #Skip [Typedef sections]
            currentItems = None
        else: #Not [Term]
            #Only process if we're inside a [Term] environment
            if currentItems is None:
                continue
            key, sep, val = line.partition(":")
            currentItems[key].append(val.strip())
    #Add last term
    if currentItems is not None:
        addOBONode(ontology,currentItems)
    return ontology



def hasNodeWithAttribute(g,attribute):
    for n in g.nodes(data=True):
        if n[1].get(attribute[0]) == attribute[1]:
            return n[0]
    else:
        return None



def getNodeFeature(graph,n,feature='name'):
    try:
        return graph.node[n][feature]
    except KeyError:
        return None



def getPathSubGraph(graph,root,target):
    path = nx.dijkstra_path(graph,root,target)
    subGraph = graph.subgraph(path)
    return subGraph


def getDescendantGraph(graph,root):
    descendantNodes = nx.descendants(graph,root)
    descendantGraph = graph.subgraph(descendantNodes)
    return descendantGraph
def drawOBOGraph(graph,feature='name'):

    labels = {}
    for n in graph.nodes(data=True):
        labels[n[0]] = n[1][feature]
    nx.draw_networkx_edges(graph,
                           pos=nx.nx_pydot.graphviz_layout(
                                be_copy(graph),
                                prog='dot',
                                root=graph.graph['roots'][0]))
    nx.draw_networkx_nodes(graph,alpha=0.4,
                           pos=nx.nx_pydot.graphviz_layout(
                                be_copy(graph),
                                prog='dot',
                                root=graph.graph['roots'][0]))
    nx.draw_networkx_labels(graph,
                            pos=nx.nx_pydot.graphviz_layout(
                                be_copy(graph),
                                prog='dot', font_size=8,
                                root=graph.graph['roots'][0]),
                            labels=labels)


def be_copy(g):
    return nx.DiGraph([(e[0],e[1]) for e in g.edges()])

def namedTraverse(graph,root, target):

        path = nx.dijkstra_path(graph,root,target)
        path.reverse()
        tabdepth = ""
        for p in path[:-1]:
            print (tabdepth+"'%s' which is a"%graph.node[p]['name'])
            tabdepth += " "
        print (tabdepth+"'%s'"%graph.node[path[-1]]['name'])



def getGraphRoot(graph,root=0):
    return graph.graph['roots'][root]


def findLowestCommonAncestor(graph,node1,node2):
    path1 = nx.dijkstra_path(graph,graph.graph['roots'][0],node1)
    path2 = nx.dijkstra_path(graph,graph.graph['roots'][0],node2)
    if len(path2) < len(path1):
        spath= path2
        lpath=path1
    else:
        spath = path1
        lpath = path2
    lpath.reverse()
    for np in lpath:
        if np in spath:
            return np




def copyAttributes(destGraph,sourceGraph):
    for node in destGraph.nodes():
        destGraph.node[node] = sourceGraph.node[node]
    return destGraph



def getOBO_pydot(graph,feature='name'):
    newGraph = nx.DiGraph()
    labels = {}
    for e in graph.edges():
        newGraph.add_edge(graph.node[e[0]][feature],graph.node[e[1]][feature])
    ag = nx.nx_pydot.to_pydot(newGraph)
    return ag
