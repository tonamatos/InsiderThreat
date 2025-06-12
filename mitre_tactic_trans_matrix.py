raise ValueError(
    "This module is deprecated and should no longer be used."
    "Please update your code to use 'config.py' instead."
)

MITRE_TACTICS = [
  "Initial Access", "Execution", "Persistence", "Privilege Escalation",
  "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
  "Collection", "Command and Control", "Exfiltration", "Impact"
]

# Copied Table 1 from page 6 of https://arxiv.org/pdf/2101.02573
TRANSITION_PROB = [
  [0.1, 0.8, 0.8, 0.8, 0.8, 0.8, 0.5, 0.5, 0.3, 0.3, 0.3, 0.3],
  [0.5, 0.1, 0.7, 0.7, 0.7, 0.7, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
  [0.5, 0.7, 0.1, 0.7, 0.7, 0.7, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
  [0.5, 0.7, 0.7, 0.1, 0.7, 0.7, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
  [0.5, 0.7, 0.7, 0.7, 0.1, 0.7, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
  [0.3, 0.5, 0.5, 0.5, 0.5, 0.1, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5],
  [0.3, 0.5, 0.5, 0.5, 0.5, 0.7, 0.1, 0.7, 0.8, 0.8, 0.8, 0.8],
  [0.3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.7, 0.1, 0.8, 0.8, 0.8, 0.8],
  [0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.7, 0.1, 0.7, 0.7, 0.7],
  [0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.7, 0.1, 0.7, 0.7],
  [0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.7, 0.7, 0.1, 0.7],
  [0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.5, 0.7, 0.7, 0.1, 0.1]
]

MITRE_TRANSITION = {
  from_tactic: {
    to_tactic: TRANSITION_PROB[i][j] for j, to_tactic in enumerate(MITRE_TACTICS)
  } for i, from_tactic in enumerate(MITRE_TACTICS)
}

if __name__=="__main__":
  # Example of usage

  p = MITRE_TRANSITION["Execution"]["Lateral Movement"]
  print(f"Probability of an attacker moving from Execution to Lateral Movement: {p}")