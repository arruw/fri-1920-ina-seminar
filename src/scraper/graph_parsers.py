import re

import networkx as nx


def read_mtx(file_path: str) -> nx.Graph:
  G = nx.Graph()
  
  with open(file_path, 'r') as f:

    skiped = False

    for l in f:
      # skip blank lines
      l = l.strip()
      if l == '': continue
      # skip comments
      if l[0] in ['#', '%']: continue

      # skip first non comment
      if not skiped:
        skiped = True
        continue

      i, j, *tail = re.split(' |,', l)
      if len(tail) == 1:
        G.add_edge(int(i), int(j), weight=float(tail[0]))
      else:
        G.add_edge(int(i), int(j))

  return G


def read_edges(file_path: str) -> nx.Graph:
  G = nx.Graph()

  with open(file_path, 'r') as f:
    for l in f:
      # skip blank lines
      l = l.strip()
      if l == '': continue
      # skip comments
      if l[0] in ['#', '%']: continue

      i, j, *tail = re.split(' |,', l)
      if len(tail) == 1:
        G.add_edge(int(i), int(j), weight=float(tail[0]))
      else:
        G.add_edge(int(i), int(j))

  return G



