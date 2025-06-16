# Largely based off of https://jessicastringham.net/2019/01/09/sum-product-message-passing/
from __future__ import annotations
from typing import List, Tuple, Dict
from datetime import datetime
import numpy as np

# our files
from data_loader import data_load_into_graph as load
from config import EVENT_TYPE_TO_MITRE, MITRE_TRANSITION, FALSE_INDICATION

MAX_ITER = 10 # Factor graph has cycles so need some way to stop the sumproduct algorithm

class Node:
    """
    Abstract class for factor and variable nodes

    Attributes:
    name (str): Name of node
    """
    def __init__(self, name: str | Tuple[str]):
        self.name = name
        self.neighbours = []

    def is_valid_neighbour(self, node: Node) -> bool:
        raise NotImplementedError

    def add_neighbour(self, node):
        if self.is_valid_neighbour(node):
            self.neighbours.append(node)


class VariableNode(Node):
    """
    Class for variable nodes in factor graphs.
    For us, these will hold the tactics in an incident.
    """
    def is_valid_neighbour(self, node: Node):
        return isinstance(node, FactorNode)


class FactorNode(Node):
    """
    Class for factor nodes in factor graphs.
    
    Attributes:
    distr (np.ndarray): Probability distribution for this node. Should only be 1x2 or 2x2 matrices in our case
    """
    # Any factor node should have at most 2 neighbours
    def is_valid_neighbour(self, node: Node):
        return isinstance(node, VariableNode)
    
    def __init__(self, name:str, distr: np.ndarray=None):
        super().__init__(name)
        self.distr = distr # will contain a numpy array corresponding to a probability distribution

    def set_distr(self, distr: np.ndarray):
        # For our cases, dist should be a 1x2 vector or 2x2 matrix
        self.distr = distr


class Messages:
    """
    Class to keep track of all the messages passing between nodes.
    Implements the sumproduct algorithm as outlined in https://vision.unipv.it/IA2/Factor%20graphs%20and%20the%20sum-product%20algorithm.pdf
    and section 5.1.2 of http://web4.cs.ucl.ac.uk/staff/D.Barber/textbook/180325.pdf.
    """
    def __init__(self):
        self.i = 0 # roughly keeps track of how many iterations have happened
        
    def variable_to_factor_message(self, variable: VariableNode, factor: FactorNode) -> np.ndarray:
        """ Computes messages from variable to factor.
        Formula given in (5) of the paper and Procedure 5.1 of Barber 
        """
        self.i += 1
        if self.i >= MAX_ITER:
            return np.array([1., 1.])
        
        incoming_messages = [
            self.factor_to_variable_message(factor2, variable)
            for factor2 in variable.neighbours
            if factor2.name != factor.name
        ]

        return np.prod(incoming_messages, axis=0)
    
    def factor_to_variable_message(self, factor: FactorNode, variable: VariableNode) -> np.ndarray:
        """
        Computes factor to variable messages for sum product algorithm.
        Formula given in (6) of paper and Procedure 5.1 of Barber
        Relies on the fact that a factor depends on at most 2 variables.
        """
        self.i += 1
        factor_distr = np.copy(factor.distr)
        var_index = factor.neighbours.index(variable) # variable should be a neighbour of factor. TODO: Check this?
        
        # This is the case of a factor leaf node, just push the distribution as is
        if len(factor.neighbours) == 1:
            return factor_distr
        
        if self.i >= MAX_ITER:
            return np.squeeze(np.sum(factor_distr, axis=1 - var_index))
        
        assert len(factor.neighbours) == 2 # Only other case. Code below assumes this is the case
        
        # pointwise product along appropriate axis
        incoming_message = self.variable_to_factor_message(factor.neighbours[1 - var_index], factor) # should be a 1x2 vector
        assert incoming_message.shape == (2,)
        
        factor_distr *= np.stack((incoming_message, incoming_message), axis=var_index) # This lines multiplies the variable messages with the appropriate axis

        return np.squeeze(np.sum(factor_distr, axis=1 - var_index)) # Here we sum over the variables (not including the given one)

    
    def marginal(self, variable: VariableNode) -> np.ndarray:
        """
        Computes distribution for given variable. Also given in Procedure 5.1 of Barber

        Returns:
        np.ndarray: array of shape (2,) corresponding to probabilty distribution of variable being active or inactive
        """
        self.i = 0
        unnorm_p = np.prod(
            [self.factor_to_variable_message(neighbour, variable) for neighbour in variable.neighbours],
            axis = 0
        )

        return unnorm_p / np.sum(unnorm_p)
    
    def marginals(self, fg):
        marginals_dict = dict()
        for variable in fg.variables:
            marginals_dict[variable] = float(self.marginal(fg.variables[variable])[1])
        return marginals_dict


class FactorGraph:
    """
    Class for constructing factor graphs to compute marginal probabilities of tactics given a list of alerts

    Parameters:
    alerts (List): A list of alerts from which factor graph is to be produced where each alert is dictionary-like.
                   Important: alert['type'] is assumed to be a MITRE tactic
    
    marginals (Dict[str, float]): A dictionary mapping MITRE tactics to their score/probability according to the factor graph
    """
    def __init__(self, alerts: List):
        tactics = list([EVENT_TYPE_TO_MITRE[alert['type']][0] for alert in alerts]) # TODO: Need to be translated to MITRE tactics
        self.variables = dict() # Use a dict to easily find the variable nodes for a given tactic
        self.factors = dict()
        
        self.marginals = None

        # Constructing variable nodes for the tactics
        for tactic in tactics:
            var_node = VariableNode(tactic)
            self.variables[tactic] = var_node
        
        # Constructing single-alert factor nodes
        for alert_a in alerts:
            # create factor node for alert_a
            fact_node = FactorNode(alert_a['id'])
            tactic = EVENT_TYPE_TO_MITRE[alert_a['type']][0]
            fact_node.add_neighbour(self.variables[tactic])
            self.variables[tactic].add_neighbour(fact_node)

            alert_score = alert_a['severity'] / 10.0
            fact_node.set_distr(np.array([1 - alert_score, alert_score]))

            # create pairwise factor nodes for tactics
            # Need to account for temporal data
            alert_a_time = datetime.fromisoformat(alert_a['timestamp'])
            alert_a_tactic = EVENT_TYPE_TO_MITRE[alert_a['type']][0]
            for alert_b in alerts:
                alert_b_tactic = EVENT_TYPE_TO_MITRE[alert_b['type']][0]
                if alert_a_tactic == alert_b_tactic: # Only connect distinct tactics
                    continue
                
                alert_b_time = datetime.fromisoformat(alert_b['timestamp'])
                factor_node_name = (alert_a_tactic, alert_b_tactic) # node name encodes the temporal data
                if alert_b_time < alert_a_time:
                    factor_node_name = (alert_b_tactic, alert_a_tactic)
                
                if factor_node_name in self.factors:
                    continue

                # Don't already have this factor node, need to create it
                fact_node = FactorNode(factor_node_name)
                mu = MITRE_TRANSITION[factor_node_name[0]][factor_node_name[1]] # TODO: Change mu so it takes into account temporal data
                fact_node.set_distr(np.array([[FALSE_INDICATION, 1 - mu], [1 - mu, mu]]))

                # add the edges
                ta_node = self.variables[alert_a_tactic]
                tb_node = self.variables[alert_b_tactic]
                
                fact_node.add_neighbour(ta_node)
                fact_node.add_neighbour(tb_node)
                ta_node.add_neighbour(fact_node)
                tb_node.add_neighbour(fact_node)

                # Add factor node to collection of nodes
                self.factors[factor_node_name] = fact_node
    
    def run_inference(self) -> Dict[str, np.ndarray]:
        """ Sets the marginals and returns it """
        m = Messages()
        self.marginals = m.marginals(self)
        return self.marginals
    
    # FactorGraphs should not be computing scores
    # This has been moved to ScoreCalculator in attack_scoring 
    #
    # def compute_score(self):
    #     """ Computes score as a weighted sum of the severity scores with weights given by the marginals. """
    #     if not self.marginals:
    #         raise ValueError("Marginals have not been computed yet.")
        
    #     score = 0
    #     for alert in self.alerts:
    #         score += alert['severity'] * self.marginals[EVENT_TYPE_TO_MITRE[alert['type']][0]][1]
    #     self.score = score / (10 * len(self.alerts)) # 10 * len(alerts) is the maximum possible score so normalise by that
    #     return self.score
    
    # def export_scores(self, incident_name: str, filename: str ="data/scores.txt"):
    #     """ Saves the scores to filename.
    #     Adds a newline to filename if it exists and creates filenames if not.
    #     This function only handles the export part. It should not be doing any computations.
    #     """
    #     if not self.marginals:
    #         raise ValueError("Marginals have not been computed yet.")
    #     if not self.score:
    #         raise ValueError("Score has not been computed yet.")
        
    #     with open(filename, mode='a') as f:
    #         marginal_output = [f'{tactic},{self.marginals[tactic][1]}' for tactic in self.marginals]
    #         marginal_output = ','.join(marginal_output)
    #         f.write(f"{incident_name},{marginal_output},Score,{self.score}\n")


if __name__ == "__main__":
    G, data = load()
    alerts = data['events'][:10]
    fg = FactorGraph(alerts)

    print(fg.run_inference())
