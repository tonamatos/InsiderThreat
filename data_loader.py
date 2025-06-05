from collections import Counter
import json
import networkx as nx
import matplotlib.pyplot as plt

with open("security_data_assignment.json") as f:
  data = json.load(f)

G = nx.MultiDiGraph()

for event in data["events"]:
  G.add_node(event["id"], **event, node_type="event")

for entity in data["entities"]:
  G.add_node(entity["id"], **entity, node_type="entity")

for rel in data["relationships"]:
  G.add_edge(rel["source"], rel["target"], **rel)

print(f"Total nodes: {G.number_of_nodes()}")
print(f"Total edges: {G.number_of_edges()}")

event_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "event"]
entity_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "entity"]
print(f"Event nodes: {len(event_nodes)}")
print(f"Entity nodes: {len(entity_nodes)}")

def draw_graph_sample(G, sample_size=100):
  H = G.subgraph(list(G.nodes)[:sample_size])  # crude sampling
  pos = nx.spring_layout(H, seed=42)

  event_nodes = [n for n, d in H.nodes(data=True) if d.get("node_type") == "event"]
  entity_nodes = [n for n, d in H.nodes(data=True) if d.get("node_type") == "entity"]

  plt.figure(figsize=(12, 9))
  nx.draw_networkx_nodes(H, pos, nodelist=event_nodes, node_color='red', label='Events')
  nx.draw_networkx_nodes(H, pos, nodelist=entity_nodes, node_color='blue', label='Entities')
  nx.draw_networkx_edges(H, pos, alpha=0.3)
  nx.draw_networkx_labels(H, pos, font_size=8)
  plt.title("Sample of Global Graph (red = events, blue = entities)")
  plt.legend()
  plt.axis("off")
  plt.show()

draw_graph_sample(G)

entity_types = [entity["type"] for entity in data["entities"]]
type_counts = Counter(entity_types)

plt.figure(figsize=(8, 5))
plt.bar(type_counts.keys(), type_counts.values(), color='skyblue')
plt.title("Distribution of Entity Types")
plt.xlabel("Entity Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

weak_components = list(nx.weakly_connected_components(G))
print(f"Weakly connected components: {len(weak_components)}")

if __name__=="__main__":
  print()