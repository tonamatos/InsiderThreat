import pickle
import networkx as nx
import matplotlib.pyplot as plt
import os

def save_graph(graph: nx.Graph, filename: str) -> None:
  """
  Saves a NetworkX graph object to a pickle file.
  """
  with open(filename, "wb") as f:
    pickle.dump(graph, f)

def load_graph(filename: str) -> nx.Graph:
  """
  Loads a NetworkX graph object from a pickle file.
  """
  with open(filename, "rb") as f:
    return pickle.load(f)

def plot_graph(subgraph: nx.Graph, node_label="description", save_path=None) -> None:

  # Get node severities and scale them (e.g., severity 1–10 becomes size 300–1000)
  node_severities = nx.get_node_attributes(subgraph, "severity")
  min_sev, max_sev = min(node_severities.values()), max(node_severities.values())
  node_sizes = [
    30 + 1000 * ((node_severities[n] - min_sev) / (max_sev - min_sev)) if max_sev > min_sev else 500
    for n in subgraph.nodes()
  ]

  # Node labels: use event description
  node_labels = {
      node: subgraph.nodes[node].get(node_label, "") 
      for node in subgraph.nodes
  }

  # Edge widths scaled from weights
  raw_weights = [d.get("weight", 0) for _, _, d in subgraph.edges(data=True)]
  min_w, max_w = min(raw_weights), max(raw_weights)
  edge_weights = [
    2 + 5 * ((w - min_w) / (max_w - min_w)) if max_w > min_w else 5
    for w in raw_weights
  ]

  plt.figure(figsize=(12, 8))
  pos = nx.spring_layout(subgraph)

  edge_labels = {
    (u, v): d.get("match_IP", "N/A").split(", ")  # Split in case it's a comma-separated string
    for u, v, d in subgraph.edges(data=True)}

  nx.draw(
      subgraph, pos,
      labels=node_labels,
      edge_labels=edge_labels,
      with_labels=True,
      node_size=node_sizes,
      node_color='lightblue',
      edge_color='gray',
      width=edge_weights
  )

  if save_path:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format="png")
    plt.close()
  else:
    plt.show()