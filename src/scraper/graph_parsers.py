import os
from typing import List

import networkx as nx

import src.scraper.metadata


def read_mtx(file_path: str) -> nx.Graph:
  with open(file_path, 'r') as f:
    lines = f.readlines()
  
  lines = list(
    map(lambda l: l.rstrip('\n'),
      filter(lambda l: not l.startswith('%') and not l.startswith('#'), lines)))[1:]

  G = nx.Graph()
  for l in lines:
    ijw = l.split()
    if len(ijw) == 2:
      i, j = ijw
      G.add_edge(int(i), int(j))
    elif len(ijw) == 3:
      i, j, w = ijw
      G.add_edge(int(i), int(j), weight=float(w))

  return G


def read_edges(file_path: str) -> nx.Graph:
  with open(file_path, 'r') as f:
    lines = f.readlines()
  
  lines = list(
    map(lambda l: l.rstrip('\n'),
      filter(lambda l: not l.startswith('%') and not l.startswith('#'), lines)))

  G = nx.Graph()
  for l in lines:
    ijw = l.split()
    if len(ijw) == 2:
      i, j = ijw
      G.add_edge(int(i), int(j))
    elif len(ijw) == 3:
      i, j, w = ijw
      G.add_edge(int(i), int(j), weight=float(w))

  return G

GRAPH_PARSERS = {
  '.edges': read_edges,
  '.mtx': read_mtx,
}


def parser_exists(file_path: str) -> bool:
  _, ext = os.path.splitext(file_path)
  return ext.lower() in GRAPH_PARSERS.keys() 
