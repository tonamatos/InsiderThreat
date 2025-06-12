raise ValueError(
    "This module is deprecated and should no longer be used."
    "Please update your code to use 'utils.py' instead."
)

import networkx as nx
import matplotlib.pyplot as plt

def plot_graph(subgraph: nx.Graph, node_label="description") -> None:

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
  pos = nx.circular_layout(subgraph)

  nx.draw(
      subgraph, pos,
      labels=node_labels,
      with_labels=True,
      node_size=node_sizes,
      node_color='lightblue',
      edge_color='gray',
      width=edge_weights
  )

  plt.show()