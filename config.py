import json

MITRE_TACTICS = [
  "Initial Access", "Execution", "Persistence", "Privilege Escalation",
  "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
  "Collection", "Command and Control", "Exfiltration", "Impact"
]

prob_matrix_file = open('prob_matrix.json','r')
TRANSITION_PROB = json.load(prob_matrix_file)
prob_matrix_file.close()

marginal_thresholds_file = open('marginal_thresholds.json','r')
MARGINAL_THRESHOLDS = json.load(marginal_thresholds_file)
marginal_thresholds_file.close()