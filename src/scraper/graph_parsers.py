import networkx as nx


def read_mtx(file_path: str) -> nx.Graph:
  G = nx.Graph()
  
  with open(file_path, 'r') as f:

    skiped = False

    for l in f:
      # skip comments
      if l.startswith('%') or l.startswith('#'): continue

      # skip first non comment
      if not skiped:
        skiped = True
        continue

      ijw = l.rstrip('\n').split()
      if len(ijw) == 3:
        i, j, w = ijw
        G.add_edge(int(i), int(j), weight=float(w))
      else:
        i, j = ijw
        G.add_edge(int(i), int(j))

  return G


def read_edges(file_path: str) -> nx.Graph:
  G = nx.Graph()

  with open(file_path, 'r') as f:
    for l in f:
      # skip comments
      if l.startswith('%') or l.startswith('#'): continue

      ijw = l.rstrip('\n').split()
      if len(ijw) == 3:
        i, j, w = ijw
        G.add_edge(int(i), int(j), weight=float(w))
      else:
        i, j = ijw
        G.add_edge(int(i), int(j))

  return G



