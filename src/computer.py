import glob
import statistics
import os

import pandas as pd
import networkx as nx
import networkx.algorithms.approximation

from src.scraper.scraper import get_graph

networks_df = pd.read_csv('data/networks.csv')
precomputed_df = pd.read_csv('data/precomputed.csv') if os.path.exists('data/precomputed.csv') else pd.DataFrame(columns=['name'])

def c(row, key, valfn):
  """Compute or return previously computed metric"""
  if key in row.columns and len(row[key]) == 1:
    return (key, row[key].iloc[0])
  return (key, valfn())

data = []
for index, row in networks_df.iterrows():
  print(f'({index}) Calculating...')

  G = get_graph(row['name'], row['download_url'])
  existing = precomputed_df.loc[precomputed_df['name'] == row['name']]

  d = [
    c(existing, 'name', lambda: row['name']),
    c(existing, 'category', lambda: row['category']),
    c(existing, 'download_url', lambda: row['download_url']),
    c(existing, 'n', lambda: G.number_of_nodes()),
    c(existing, 'm', lambda: G.number_of_edges()),
    c(existing, 'density', lambda: nx.density(G)),
    c(existing, 'k_min', lambda: min(dict(G.degree()).values())),
    c(existing, 'k_avg', lambda: statistics.mean(dict(G.degree()).values())),
    c(existing, 'k_max', lambda: max(dict(G.degree()).values())),
    c(existing, 'r', lambda: nx.degree_assortativity_coefficient(G)),
    c(existing, 't', lambda: sum(dict(nx.triangles(G)).values())),
    c(existing, 't_min', lambda: min(dict(nx.triangles(G)).values())),
    c(existing, 't_avg', lambda: statistics.mean(dict(nx.triangles(G)).values())),
    c(existing, 't_max', lambda: max(dict(nx.triangles(G)).values())),
    c(existing, 'C_avg', lambda: nx.average_clustering(G)),
    c(existing, 'C', lambda: nx.transitivity(G)),
    c(existing, 'LCC', lambda: max(map(len, nx.connected_components(G)))/G.number_of_nodes()),
  ]

  data.append(dict(d))

df = pd.DataFrame(data)
df.to_csv('data/precomputed.csv', index=False)