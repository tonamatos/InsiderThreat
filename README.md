# Insider Threat Detection Dashboard (RANK + MITRE)

>Collaborators: Sean Griswold, Tonatiuh Matos, Rishibh Prakash

This prototype tool presents a graphical dashboard for security analysts to monitor and interpret potential insider threats. It uses factor graphs and the RANK framework to correlate system alerts with known attack patterns from the MITRE ATT&CK framework.

## Overview

- Alerts are ingested and scored based on severity using custom heuristics.
- Related events are grouped and visualized as a graph to reflect attack progression.
- The system is designed to help analysts triage high-risk behavior by showing connections between alerts.
- Tested on a synthetic dataset simulating insider threat scenarios.

## Technologies

- Python
- NetworkX
- Custom scoring heuristics (RANK-inspired)
- MITRE ATT&CK framework mappings

## Features

- Graph-based visualization of security alerts
- Severity scoring system to prioritize analysis
- Factor-graph logic to link related activity
- Extensible and modular design for future data sources

## Status

This is a working prototype developed during the Fields Institute InfoSec specialization program. While tested on synthetic data, it provides a foundation for future development or academic study.
