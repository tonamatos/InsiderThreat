from typing import List

import json
from json.decoder import JSONDecodeError

from factor_graph import FactorGraph
from config import EVENT_TYPE_TO_MITRE, DEFAULT_SCORES_PATH_TXT, DEFAULT_SCORES_PATH_JSON, WEIGHT_PARAMETERS

class ScoreCalculator:
    """ Class designed to compute scores given alerts and factor graph.
    Used a class so different 'types' of scores can be calculated if needed.
    Also allows for flexibility of exports.
    """
    def __init__(self, alerts: List, fg: FactorGraph):
        self.alerts = alerts
        self.fg = fg
        self.score = None
    
    def compute_weighted_score(self):
        if not self.fg.marginals:
            raise ValueError("Marginals have not been computed yet.")
        
        score = 0
        for alert in self.alerts:
            score += alert['severity'] * self.fg.marginals[EVENT_TYPE_TO_MITRE[alert['type']][0]][1] * WEIGHT_PARAMETERS[EVENT_TYPE_TO_MITRE[alert['type']][0]]
        self.score = score / (10 * len(self.alerts)) # 10 * len(alerts) is the maximum possible score so normalise by that
        return self.score
    
    def check_computations(self):
        """ Raises ValueError if scores, marginals, etc. have not been computed. """
        if not self.fg.marginals:
            raise ValueError("Marginals have not been computed yet.")
        if not self.score:
            raise ValueError("Score has not been computed yet.")
    
    def export_scores_txt(self, incident_name: str, filename: str =DEFAULT_SCORES_PATH_TXT):
        """ Saves the scores to filename.
        Adds a newline to filename if it exists and creates filenames if not.
        This function only handles the export part. It should not be doing any computations.
        """
        self.check_computations()

        with open(filename, mode='a') as file:
            marginal_output = [f"{tactic},{self.fg.marginals[tactic][1]}" for tactic in self.fg.marginals]
            marginal_output = ','.join(marginal_output)
            file.write(f"{incident_name},{marginal_output},Score,{self.score}\n")
    
    def export_scores_json(self, incident_name: str, filename: str=DEFAULT_SCORES_PATH_JSON):
        """ Exports the scores to json file """
        self.check_computations()
        formatted_marginals = {tactic: float(self.fg.marginals[tactic][1]) for tactic in self.fg.marginals}
        incident_export = {"name": incident_name,
                           "marginals": formatted_marginals, 
                           "score": float(self.score)}
        with open(filename, "r") as file:
            try:
                data = json.load(file)
            except JSONDecodeError:
                data = []
        
        data.append(incident_export)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)