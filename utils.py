import pickle
import networkx as nx

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