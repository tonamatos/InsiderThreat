from attack_correlation import *
from data_loader import data_load_into_graph as load
from utils import save_graph, load_graph
from factor_graph import *
import os

# STEP 1: Load data as a graph and a dictionary
G, data = load()

# STEP 2: Compute attack correlation graph or load cache
cache_path = "cached_graphs/attack_correlation_graph.pkl"
if os.path.exists(cache_path):
  H = load_graph(cache_path)
else:
  H = attack_correlation(G, data)
  save_graph(H, cache_path)

# STEP 3: Compute factor graphs and scoring for each connected component
# Extract components
components = list(nx.connected_components(H.to_undirected()))
components.sort(key=len, reverse=True)
print("There are", len(components), "subgraphs.")

all_event_subgraphs = []

for i, component in enumerate(components):
  subgraph = H.subgraph(component)
  alerts = [event for event in data['events'] if event['id'] in subgraph.nodes()]
  fg = FactorGraph(alerts)
  m = Messages()
  # v = fg.variables["Collection"]
  # # print(m.marginal(v))
  # # v = fg.variables["Credential Access"]
  # # print(m.marginal(v))
  marginals = m.marginals(fg)
  event_subgraph = {"Factor graph": fg,
                    "Marginals"   : marginals,
                    "Index"       : i, # This index is sorted by subgraph size.
                    "Subgraph"    : subgraph}
  all_event_subgraphs.append(event_subgraph)

print("Processed", len(all_event_subgraphs), "subgraphs!")