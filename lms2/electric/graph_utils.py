import json
import numpy as np
from pyomo.environ import *
import networkx as nx
from json import JSONEncoder
from lms2.electric.network import Cable


class NumpyArrayEncoder(JSONEncoder):
    """
    Specific encoder to handle numpy arrays and Cable objects.
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Cable):
            return obj.__dict__
        return JSONEncoder.default(self, obj)


def save_json_graph(g, file_path, indent=4):
    """
    Save a networkx as a json file
    consider using indent=None for big graphes, memory saving or if readability is not an issue.

    @param g: networkx graph
    @param file_path: path to save the file to
    @param indent: number of spaces to add
    @return:
    """
    graph_data = nx.node_link_data(g)

    # Enregistrer le dictionnaire au format JSON
    with open(file_path, 'w') as f:
        json.dump(graph_data, f, cls=NumpyArrayEncoder, indent=indent)


def read_json_graph(file_path):
    with open(file_path, 'r') as f:
        graph_data = json.load(f)

    # Créer un graphe à partir des données chargées
    # les listes des données sont castées en np.array()
    edges = graph_data['links']
    for i, d in enumerate(edges):
        for k, v in d.items():
            if isinstance(v, list):
                edges[i][k] = np.asarray(v)

    graph_data.update({'link': edges})
    graph = nx.node_link_graph(graph_data)
    return graph


def calc_edge_pq_matrix(g):
    """
    Calculate P and Q matrix for each branch of the graph graphe.

    graphe needs to store some data, such as l, rmatrix and xmatrix, respectively, the lenth in km,
    and the real and imaginary parts of the impedance (Ohm/km).

    @param graphe: DiGraphe that describe the distribution network.
    @return:
    """
    #g = graphe.copy()

    for n1, n2, data in g.edges(data=True):
        l = data['length']
        r = data['cable'].r
        x = data['cable'].x

        pmatrix = np.zeros(r.shape)
        qmatrix = np.zeros(r.shape)

        pmatrix[0, 0] = - 2 * r[0, 0] * l
        pmatrix[2, 2] = - 2 * r[2, 2] * l
        pmatrix[1, 1] = - 2 * r[1, 1] * l
        pmatrix[1, 0] = r[1, 0] * l + sqrt(3) * x[1, 0] * l
        pmatrix[2, 1] = r[2, 1] * l - sqrt(3) * x[2, 1] * l
        pmatrix[0, 1] = r[0, 1] * l - sqrt(3) * x[0, 1] * l
        pmatrix[2, 1] = r[2, 1] * l + sqrt(3) * x[2, 1] * l
        pmatrix[0, 2] = r[0, 2] * l + sqrt(3) * x[0, 2] * l
        pmatrix[1, 2] = r[1, 2] * l - sqrt(3) * x[1, 2] * l

        qmatrix[0, 0] = - 2 * x[0, 0] * l
        qmatrix[2, 2] = - 2 * x[2, 2] * l
        qmatrix[1, 1] = - 2 * x[1, 1] * l
        qmatrix[1, 0] = x[1, 0] * l - sqrt(3) * r[1, 0] * l
        qmatrix[2, 1] = x[2, 1] * l + sqrt(3) * r[2, 1] * l
        qmatrix[0, 1] = x[0, 1] * l + sqrt(3) * r[0, 1] * l
        qmatrix[2, 1] = x[2, 1] * l - sqrt(3) * r[2, 1] * l
        qmatrix[0, 2] = x[0, 2] * l - sqrt(3) * r[0, 2] * l
        qmatrix[1, 2] = x[1, 2] * l + sqrt(3) * r[1, 2] * l

        g[n1][n2]['qmatrix'] = qmatrix
        g[n1][n2]['pmatrix'] = pmatrix
    return g


def radial_network(net, **kwargs):
    """
    Creates a radial distribution network
    Nd : number of dwellings in the network (specified by the user)
    Nb : number of buses in the network

    radial network :
            3      5     7
            |     |     |
     0--1---2-----4-----6


    :param net
    :param Nd, Nb
    """
    Nb = kwargs.pop('Nb', None)
    Nd = kwargs.pop('Nd', None)

    if Nb is None :
        Nb = 2 * Nd + 1
    if Nb < 2 * Nd + 1:
        raise ValueError('Wrong number of buses')
    if Nd is None :
        raise ValueError('User needs to specify the number of dwellings')
    else:
        net.graph = nx.Graph()
        for k in range(0, Nb + 1):
            net.graph.add_node(k)
        for k in range(0, 2):
            net.graph.add_edge(k, k + 1)
        for k in range(0, floor(Nb / 2) + 1):
            net.graph.add_edge(2 * k, 2 * k + 1)
        for k in range(1, floor(Nb / 2)):
            net.graph.add_edge(2 * k, 2 * (k + 1))
        net.graph = nx.dfs_tree(net.graph)


def radial_graph(Nd):
    # Nd: number of dwellings
    Nb = 2 * Nd + 1
    graph = nx.Graph()
    for k in range(0, Nb + 1):
        graph.add_node(k)
    for k in range(0, 2):
        graph.add_edge(k, k + 1)
    for k in range(0, floor(Nb / 2) + 1):
        graph.add_edge(2 * k, 2 * k + 1)
    for k in range(1, floor(Nb / 2)):
        graph.add_edge(2 * k, 2 * (k + 1))
    graph = nx.dfs_tree(graph)
    return graph


def full_island(dict_feeder):
    graph = nx.DiGraph()
    for fee in dict_feeder.keys():
        if fee == 'f_interest':
            Nd = dict_feeder[fee]
            Nb = 2 * Nd + 1
            for k in range(0, Nb + 1):
                graph.add_node(str(k))
            for k in range(0, 2):
                graph.add_edge(str(k), str(k + 1), data ={'feeder':fee, 'node':k+1})
            for k in range(0, floor(Nb / 2) + 1):
                graph.add_edge(str(2 * k), str(2 * k + 1), data ={'feeder':fee, 'node':2 * k+1})
            for k in range(1, floor(Nb / 2)):
                graph.add_edge(str(2 * k), str(2 * (k + 1)), data ={'feeder':fee, 'node':2 * (k+1)})
        else:
            Nd = dict_feeder[fee]
            Nb = 2 * Nd + 1
            for k in range(2, Nb + 1):
                graph.add_node(str(k) + fee)
            for k in range(1, 2):
                graph.add_edge(str(k), str(k + 1) + fee, data ={'feeder':fee, 'node':k+1})
            for k in range(1, floor(Nb / 2) + 1):
                graph.add_edge(str(2 * k) + fee, str(2 * k + 1) + fee, data ={'feeder':fee, 'node':2 * k+1})
            for k in range(1, floor(Nb / 2)):
                graph.add_edge(str(2 * k) + fee, str(2 * (k + 1)) + fee, data ={'feeder':fee, 'node':2 * (k+1)})
    # graph = nx.dfs_tree(graph)
    return graph


if __name__ == "__main__":

    net = ConcreteModel()
    Nd = 3
    Nb = 2 * Nd + 1
    graph_dict = {'Nd': Nd, 'Nb': Nb}
    radial_network(net, **graph_dict)
    edges = net.graph.edges()
    nodes = net.graph.nodes()

    #dict_feeder = {'f_interest': 15, 'f1': 30}
    radial_network(net, **{'Nd':4})



