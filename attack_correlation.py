from mitre_tactic_trans_matrix import MITRE_TRANSITION
import networkx as nx
from itertools import combinations, product
from datetime import datetime

THRESHOLD = 0.4

# This dict may be defined by reading the description using an LLM,
# currently aboove my paygrade!
EVENT_TYPE_TO_MITRE = {"Authentication"     : ["Initial Access", "Credential Access"],
                       "Privilege Operation": ["Privilege Escalation", "Execution"],
                       "Data Access"        : ["Collection", "Discovery"],
                       "Exfiltration"       : ["Exfiltration"],
                       "Defense Evasion"    : ["Defense Evasion"]}

def alert_correlation_measure(vertex1, vertex2, data: dict, event_to_ips: dict) -> float:
  '''
  Args are nodes of a graph that correspond to events.
  Returns thee computed value C(vertex1, vertex2) as defined in (3),
  page 5 of https://arxiv.org/pdf/2101.02573.
  Yes, I KNOW this program is wildly inefficient and yes,
  I know how to make it faster, bear with me it works for now.
  '''
  event_lookup = {event["id"]: event for event in data["events"]}

  event1 = event_lookup[vertex1]
  event2 = event_lookup[vertex2]
  M_v       = EVENT_TYPE_TO_MITRE[event1["type"]]
  M_v_prime = EVENT_TYPE_TO_MITRE[event2["type"]]

  set_T_KC = [MITRE_TRANSITION[t][t_prime] for t, t_prime in product(M_v, M_v_prime)]
  
  ips1 = event_to_ips.get(vertex1, set())
  ips2 = event_to_ips.get(vertex2, set())
  shared_ips = ips1 & ips2  # set intersection
  set_C_IP = [1 if shared_ips else 0]

  return max(set_T_KC) * max(set_C_IP)

def attack_correlation(G: nx.Graph, data: dict, event_to_ips: dict) -> nx.Graph:
  event_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "event"]
  event_lookup = {event["id"]: event for event in data["events"]}

  attack_correlation_graph = nx.Graph()
  attack_correlation_graph.add_nodes_from((n, G.nodes[n]) for n in event_nodes)

  for u, v in combinations(event_nodes, 2):
    # Temporal logic:
    time_u = datetime.fromisoformat(event_lookup[u]["timestamp"])
    time_v = datetime.fromisoformat(event_lookup[v]["timestamp"])
    
    if time_u < time_v:
      score = alert_correlation_measure(u, v, data, event_to_ips)
      if score > 0.4:
        attack_correlation_graph.add_edge(u, v, weight=score)
    elif time_v < time_u:
      score = alert_correlation_measure(v, u, data, event_to_ips)
      if score > 0.4:
        attack_correlation_graph.add_edge(v, u, weight=score)

  return attack_correlation_graph