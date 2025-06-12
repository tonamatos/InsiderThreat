import networkx as nx
from itertools import product
from datetime import datetime
from config import CORRELATION_THRESHOLD, MITRE_TRANSITION, EVENT_TYPE_TO_MITRE

def build_event_to_ips_map(G):
  '''
  Returns a dictionary that links event nodes in G
  to the set of all IPs addresses of hosts connected to the
  event in G.
  '''
  event_to_ips = {}

  for node in G.nodes:
    if G.nodes[node].get("node_type") == "event":
      # Collect IPs from all Host entities linked to this event
      ips = set()
      for neighbor in G.neighbors(node):
        nbr_data = G.nodes[neighbor]
        if nbr_data.get("node_type") == "entity" and nbr_data.get("type") == "Host":
          ip = nbr_data.get("properties", {}).get("ip_address")
          if ip:
            ips.add(ip)
      event_to_ips[node] = ips

  return event_to_ips

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

  return max(set_T_KC) * max(set_C_IP), shared_ips

def attack_correlation(G: nx.Graph, data: dict) -> nx.DiGraph:
  '''
  Returns the attack correlation graph corresponding to G, the graph with
  nodes consisting of all events and entities, as produces by the data_loader
  '''
  event_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "event"]
  event_lookup = {event["id"]: event for event in data["events"]}

  attack_correlation_graph = nx.DiGraph()
  attack_correlation_graph.add_nodes_from((n, G.nodes[n]) for n in event_nodes)

  event_to_ips = build_event_to_ips_map(G)
  for u, v in product(event_nodes, repeat=2):
    # Temporal logic:
    time_u = datetime.fromisoformat(event_lookup[u]["timestamp"])
    time_v = datetime.fromisoformat(event_lookup[v]["timestamp"])

    if time_u < time_v:
      score, shared_ips = alert_correlation_measure(u, v, data, event_to_ips)
      if score > CORRELATION_THRESHOLD:
        match_IP = ", ".join(shared_ips)
        attack_correlation_graph.add_edge(u, v, weight=score, match_IP=match_IP)

  return attack_correlation_graph