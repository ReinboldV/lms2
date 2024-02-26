import unittest
import networkx as nx
import os
from lms2.electric.graph_utils import read_json_graph, save_json_graph


class TestSaveGraph(unittest.TestCase):
    def setUp(self):
        # Créer un graphe pour les tests
        self.G = nx.Graph()
        self.G.add_nodes_from([1, 2, 3])
        self.G.add_edges_from([(1, 2), (2, 3)])
        self.file_name = os.path.realpath('./graph.json')

    def test_save_and_load_graph(self):
        # Enregistrer le graphe au format JSON
        save_json_graph(self.G, self.file_name)
        loaded_graph = read_json_graph(self.file_name)
        # Vérifier que les graphes sont égaux
        self.assertTrue(nx.is_isomorphic(self.G, loaded_graph))

    def tearDown(self):
        # Supprimer le fichier JSON de test après les tests
        os.remove(self.file_name)


def test_calc_edge_pq_matrix():
    # todo : créer un cas simple et vérifier le résultat avec qq chose de connu

    assert True

from pyomo.environ import *
from lms2.electric.network import network_3phases_lindistflow, cable_3_150_95
import networkx as nx
from pyomo.util.check_units import assert_units_consistent


class TestNetwork_3phases_lindistflow(unittest.TestCase):
    def setUp(self):
        edges = [(0, 1, {'length': 10, 'cable': cable_3_150_95}),
                 (1, 2, {'length': 20, 'cable': cable_3_150_95})]

        self.g = nx.from_edgelist(edges, create_using=nx.DiGraph())

    def test_lindistflow(self):
        m = ConcreteModel()
        m.time = RangeSet(bounds=(0, 1))
        m.net = Block(rule=lambda b: network_3phases_lindistflow(b, **{'time': m.time, 'graph': self.g}))
        assert_units_consistent(m)
        assert True


if __name__ == '__main__':
    unittest.main()



