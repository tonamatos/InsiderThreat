import json

CORRELATION_THRESHOLD = 0.4
FALSE_INDICATION = 0.2 # used by factor graphs
DATA_FILEPATH         = "security_data_assignment.json" # This file is gitignored
DEFAULT_SCORES_PATH_TXT = "scores/scores.txt"
DEFAULT_SCORES_PATH_JSON = "scores/scores.json"

MITRE_TACTICS = [
  "Initial Access", "Execution", "Persistence", "Privilege Escalation",
  "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
  "Collection", "Command and Control", "Exfiltration", "Impact"
]

EVENT_TYPE_TO_MITRE = {"Authentication"     : ["Initial Access"],
                       "Privilege Operation": ["Privilege Escalation"],
                       "Data Access"        : ["Collection"],
                       "Exfiltration"       : ["Exfiltration"],
                       "Defense Evasion"    : ["Defense Evasion"]}

# Copied Table 1 from page 6 of https://arxiv.org/pdf/2101.02573
with open('prob_matrix.json', 'r') as f: trans_prob = json.load(f)

with open('marginal_thresholds.json', 'r') as f: MARGINAL_THRESHOLDS = json.load(f)

MITRE_TRANSITION = {
  from_tactic: {
    to_tactic: trans_prob[i][j] for j, to_tactic in enumerate(MITRE_TACTICS)
  } for i, from_tactic in enumerate(MITRE_TACTICS)
}

'''
Possibly better version of this for later updates:

EVENT_TYPE_TO_MITRE = {"Authentication"     : ["Initial Access", "Credential Access"],
                       "Privilege Operation": ["Privilege Escalation", "Execution"],
                       "Data Access"        : ["Collection", "Discovery"],
                       "Exfiltration"       : ["Exfiltration"],
                       "Defense Evasion"    : ["Defense Evasion"]}
'''