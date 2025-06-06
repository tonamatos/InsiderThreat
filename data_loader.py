import json
import networkx as nx

def data_load_into_graph(filepath="security_data_assignment.json"):

  with open(filepath) as f:
    data = json.load(f)

  G = nx.MultiDiGraph()

  for event in data["events"]:
    G.add_node(event["id"], **event, node_type="event")

  for entity in data["entities"]:
    G.add_node(entity["id"], **entity, node_type="entity")

  for rel in data["relationships"]:
    G.add_edge(rel["source"], rel["target"], **rel)

  return G, data

if __name__=="__main__":
  # Example of usage
  
  G, data = data_load_into_graph()
  print(f"Total nodes: {G.number_of_nodes()}")
  print(f"Total edges: {G.number_of_edges()}")

  event_nodes  = [n for n, d in G.nodes(data=True) if d.get("node_type") == "event"]
  entity_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "entity"]
  print(f"Event nodes: {len(event_nodes)}")
  print(f"Entity nodes: {len(entity_nodes)}")