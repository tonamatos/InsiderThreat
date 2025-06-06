import networkx as nx
from networkx import Graph
from mitre_tactic_trans_matrix import *

class FactorGraph:
    """ FactorGraph class is used to compute marginal probabilities of tactics """
    def __init__(self, tactics, alerts):
        self.fg = Graph()
        for tactic in tactics:
            self.fg.add_node(tactic, type='variable') # using variable and factor types as in paper
                                                      # could potentially use something else as well

        for alert in alerts:
            self.fg.add_node(alert['id'], **alert, type='factor') # should have severity attribute
            self.fg.add_edge(alert['id'], alert['type'])

        for ta in tactic:
            for tb in tactics:
                transition_prob = mitre_transition[ta][tb]
                self.fg.add_node((ta, tb), severity=mitre_transition[ta][tb], type='factor') # TODO: Need to incorporate the active/inactive stuff
                self.fg.add_edge(ta, (ta, tb))
                self.fg.add_edge((ta, tb), tb)

    def run_inference():
        """ Run an inference algorithm to learn marginal probabilities for the tactics. """
        raise NotImplementedError

    def draw_graph():
        """ Visualise the factor graph """
        raise NotImplementedError