# Largely based off of https://jessicastringham.net/2019/01/09/sum-product-message-passing/
import numpy as np
from typing import List
from mitre_tactic_trans_matrix import mitre_transition
from data_loader import data_load_into_graph as load

FALSE_INDICATION = 0.2
MAX_ITER = 500

class Node:
    """
    Abstract class for factor and variable nodes

    Attributes:
    name (str): Name of node
    """
    def __init__(self, name: str):
        self.name = name
        self.neighbours = []

    def is_valid_neighbour(self, node) -> bool:
        raise NotImplementedError

    def add_neighbour(self, node):
        if self.is_valid_neighbour(node):
            self.neighbours.append(node)


class VariableNode(Node):
    def is_valid_neighbour(self, node: Node):
        return isinstance(node, FactorNode)


class FactorNode(Node):
    """
    Class for factor nodes in factor graphs.
    
    Attributes:
    distr (np.ndarray): Probability distribution for this node. Should only be 1x2 or 2x2 matrices in our case
    """
    # Any factor node should have at most 2 neighbours
    def is_valid_neighbour(self, node):
        return isinstance(node, VariableNode)
    
    def __init__(self, name:str, distr: np.ndarray=None):
        super().__init__(name)
        self.distr = distr # will contain a numpy array corresponding to a probability distribution

    def set_distr(self, distr: np.ndarray):
        # For our cases, dist should be a 1x2 vector or 2x2 matrix
        self.distr = distr


class Messages:
    """
    Class to keep track of all the messages passing between nodes
    """
    def __init__(self):
        self.messages = dict() # keeps track of the messages on an edge. Means messages don't have to be recomputed
        self.i = 0
        

    def _variable_to_factor_message(self, variable: VariableNode, factor: FactorNode):
        """ Computes variable to factor messages as outlined in  """
        if self.i >= MAX_ITER:
            return 1
        
        incoming_messages = [
            self.factor_to_variable_message(factor2, variable)
            for factor2 in variable.neighbours
            if factor2 is not factor
        ]

        if len(incoming_messages) == 0:
            return 1

        # base case is also handled here
        # returns 1 on empty product
        return np.prod(incoming_messages, axis=0)

    def _factor_to_variable_message(self, factor: FactorNode, variable: VariableNode):
        """ Relies on the fact that a factor depends on at most 2 variables. """
        factor_distr = np.copy(factor.distr)
        var_index = factor.neighbours.index(variable) # variable should be a neighbour of factor. TODO: Check this?
        
        if len(factor.neighbours) == 1:
            return factor_distr
        
        assert len(factor.neighbours) == 2 # Only other case

        if self.i >= MAX_ITER:
            return np.squeeze(np.sum(factor_distr, axis=1 - var_index))
        
        # pointwise product along appropriate axis
        incoming_message = self.variable_to_factor_message(factor.neighbours[1 - var_index], factor) # should be a 1x2 vector
        assert incoming_message.shape == (2,)
        factor_distr *= np.stack((incoming_message, incoming_message), axis=var_index)

        return np.squeeze(np.sum(factor_distr, axis=1 - var_index))

    def variable_to_factor_message(self, variable: VariableNode, factor: FactorNode):
        self.i += 1
        if self.i == MAX_ITER:
            return 1
        message_name = (variable.name, factor.name)
        if message_name not in self.messages:
            self.messages[message_name] = self._variable_to_factor_message(variable, factor)
        return self.messages[message_name]
    
    def factor_to_variable_message(self, factor: FactorNode, variable: VariableNode):
        self.i += 1
        if self.i >= MAX_ITER:
            var_index = factor.neighbours.index(variable)
            return np.squeeze(np.sum(factor.distr, axis=1 - var_index))
        message_name = (factor.name, variable.name)
        if message_name not in self.messages:
            self.messages[message_name] = self._factor_to_variable_message(factor, variable)
        return self.messages[message_name]
    
    def marginal(self, variable: VariableNode) -> np.ndarray:
        """
        Computes distribution for given variable.

        Returns:
        np.ndarray: array of shape (2,) corresponding to probabilty distribution of variable being active or inactive
        """
        unnorm_p = np.prod(
            [self.factor_to_variable_message(neighbour, variable) for neighbour in variable.neighbours],
            axis = 0
        )

        return unnorm_p / np.sum(unnorm_p)


class FactorGraph:
    """
    Class for constructing factor graphs to compute marginal probabilities of tactics given a list of alerts

    Parameters:
    alerts (List): A list of alerts from which factor graph is to be produced where each alert is dictionary-like.
                   Important: alert['type'] is assumed to be a MITRE tactic
    """
    def __init__(self, alerts: List):
        tactics = list([alert['type'] for alert in alerts]) # TODO: Need to be translated to MITRE tactics
        self.variables = dict() # Use a dict to easily find the variable nodes for a given tactic
        self.factors = []
        
        # Constructing variable nodes for the tactics
        for tactic in tactics:
            var_node = VariableNode(tactic)
            self.variables[tactic] = var_node
        
        # Constructing single-alert factor nodes
        for alert in alerts:
            fact_node = FactorNode(alert['id'])
            tactic = alert['type']
            fact_node.add_neighbour(self.variables[tactic])
            self.variables[tactic].add_neighbour(fact_node)

            alert_score = alert['severity'] / 10.0
            fact_node.set_distr(np.array([1 - alert_score, alert_score]))

        # Constructing the pairwise factor nodes
        for tactic_a in tactics:
            for tactic_b in tactics:
                if tactic_a == tactic_b:
                    continue
                fact_node = FactorNode((tactic_a, tactic_b))
                ta_node = self.variables[tactic_a]
                tb_node = self.variables[tactic_b]
                
                fact_node.add_neighbour(ta_node)
                fact_node.add_neighbour(tb_node)
                ta_node.add_neighbour(fact_node)
                tb_node.add_neighbour(fact_node)

                mu = mitre_transition[tactic_a][tactic_b]
                fact_node.set_distr(np.array([[FALSE_INDICATION, 1 - mu], [1 - mu, mu]]))


if __name__ == "__main__":
    G, data = load()
    alerts = data['events'][:3]
    fg = FactorGraph(alerts)

    m = Messages()
    v = fg.variables["Privilege Escalation"]
    print(m.marginal(v))