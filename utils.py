import pickle
import networkx as nx
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def create_placeholder_graph() -> None:
  # Create a blank white image
  width, height = 600, 400
  placeholder = Image.new("RGB", (width, height), color="white")
  draw = ImageDraw.Draw(placeholder)

  text = "Single node graph -\nno image generated."

  font = ImageFont.truetype("arial.ttf", size=48)

  bbox = draw.textbbox((0, 0), text, font=font)
  text_width = bbox[2] - bbox[0]
  text_height = bbox[3] - bbox[1]
  text_position = ((width - text_width) // 2, (height - text_height) // 2)

  # Draw text
  draw.text(text_position, text, fill="gray", font=font)

  # Save to correct path
  os.makedirs("graph_plots", exist_ok=True)
  placeholder.save("graph_plots/placeholder.png")

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

  # Node labels: use event label (e.g. description or type)
  node_labels = {
      node: subgraph.nodes[node].get(node_label, "") 
      for node in subgraph.nodes
  }

  # Edge widths scaled from weights
  raw_weights = [d.get("weight", 0) for _, _, d in subgraph.edges(data=True)]
  min_w, max_w = min(raw_weights + [1]), max(raw_weights + [0])
  edge_weights = [
    2 + 5 * ((w - min_w) / (max_w - min_w)) if max_w > min_w else 5
    for w in raw_weights
  ]

  plt.figure(figsize=(12, 8))
  pos = nx.circular_layout(subgraph)
  #pos = {k: v * 0.15 for k, v in pos.items()}

  pos = {k: v * 0.8 for k, v in pos.items()}

  

  edge_labels = {}
  for u, v, d in subgraph.edges(data=True):
    raw = d.get("match_IP", "")
    if isinstance(raw, str):
      ip_list = [ip.strip() for ip in raw.split(",") if ip.strip()]
      edge_labels[(u, v)] = "\n".join(ip_list)  # Multiple lines

  wrapped_node_labels = {
    node: "\n".join(textwrap.wrap(label, width=20))
    for node, label in node_labels.items()}


  nx.draw(
      subgraph, pos,
      labels=wrapped_node_labels,
      with_labels=True,
      node_size=node_sizes,
      node_color='lightblue',
      edge_color='gray',
      width=edge_weights,
      font_size=8
  )

  nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=8)

  if save_path:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format="png")
  else:
    plt.show()
  plt.close()

if __name__ == "__main__":
  create_placeholder_graph()