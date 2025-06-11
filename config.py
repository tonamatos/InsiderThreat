import json

CORRELATION_THRESHOLD = 0.4
DATA_FILEPATH        = "security_data_assignment.json" # This file is gitignored

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
with open('prob_matrix.json', 'r') as f: TRANSITION_PROB = json.load(f)

with open('marginal_thresholds.json', 'r') as f: MARGINAL_THRESHOLDS = json.load(f)

MITRE_TRANSITION = {
  from_tactic: {
    to_tactic: TRANSITION_PROB[i][j] for j, to_tactic in enumerate(MITRE_TACTICS)
  } for i, from_tactic in enumerate(MITRE_TACTICS)
}