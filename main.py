import os
import json

from attack_correlation import *
from data_loader import data_load_into_graph as load
from utils import save_graph, load_graph, plot_graph, create_placeholder_graph
from factor_graph import *
from config import IMAGES_DIRECTORY, DEFAULT_SCORES_PATH_JSON
from attack_scoring import ScoreCalculator

# STEP 1: Load data as a graph and a dictionary
print("Loading data...")
G, data = load()

# STEP 2: Compute attack correlation graph or load cache
print("Finding attack correlation graph...")
cache_path = "cached_graphs/attack_correlation_graph.pkl"
if os.path.exists(cache_path):
  H = load_graph(cache_path)
  print("Loaded cached attack correlation graph.")
else:
  H = attack_correlation(G, data)
  save_graph(H, cache_path)
  print("Cached graph not found. New attack correlation graph created and cached.")

# STEP 3: Compute factor graphs and scoring for each connected component
# Extract components
components = list(nx.connected_components(H.to_undirected()))
components.sort(key=len, reverse=True)
print("There are", len(components), "subgraphs.")
print("Creating images...")

all_event_subgraphs = []
export_data = [] # this is the data that is saved DEFAULT_SCORES_PATH_JSON

for i, component in enumerate(components):
  subgraph = H.subgraph(component)
  alerts = [event for event in data['events'] if event['id'] in subgraph.nodes()]
  fg = FactorGraph(alerts)
  marginals = fg.run_inference()
  sc = ScoreCalculator(alerts, fg)
  score = sc.compute_weighted_score() # this can be exported to a txt or json file if we like
  # sc.export_scores_txt(f"incident{i}")
  # sc.export_scores_json(f"incident{i}")
  event_subgraph = {"Factor graph": fg,
                    "Marginals"   : marginals,
                    "Score"       : score,
                    "Index"       : i, # This index is sorted by subgraph size.
                    "Subgraph"    : subgraph}
  all_event_subgraphs.append(event_subgraph)

  event_data = {"Index": i,
                "Marginals": marginals,
                "Score": score}
  export_data.append(event_data)

export_data.sort(key=lambda x: x["Score"], reverse=True) # sort incidents by score
with open(DEFAULT_SCORES_PATH_JSON, mode="w") as file:
  json.dump(export_data, file, indent=4)

for event_subgraph in all_event_subgraphs:
  subgraph = event_subgraph["Subgraph"]

  # If you don't want 600+ images of a single node...
  if subgraph.number_of_edges() == 0:
    GRAPH_DISPLAY_CUTOFF = event_subgraph["Index"]
    break # since after this they all have zero edges

  index = event_subgraph["Index"]
  save_path = IMAGES_DIRECTORY + f"event_subgraph_{index}.png"
  #plot_graph(subgraph, node_label="description", save_path=save_path)

create_placeholder_graph()
print("Done creating images.")