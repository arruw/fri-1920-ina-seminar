import os
import requests
import networkx as nx
import zipfile
import pickle
import glob
from typing import List

import bs4
import pandas as pd

from src.scraper.metadata import Metadata
from src.scraper.graph_parsers import read_edges, read_mtx

_BASE_URL = 'http://networkrepository.com'

_TMP_DIR = '.tmp'
if not os.path.exists(_TMP_DIR):
  os.mkdir(_TMP_DIR)

_VALUE_TYPES = {
  'Nodes': int,
  'Edges': int,
  'Density': float,
  'Maximum degree': int,
  'Minimum degree': int,
  'Average degree': int,
  'Assortativity': float,
  'Number of triangles': int,
  'Average number of triangles': int,
  'Maximum number of triangles': int,
  'Average clustering coefficient': float,
  'Fraction of closed triangles': float,
  'Maximum k-core': int,
  'Lower bound of Maximum Clique': int,
}

_SUFFIXES = {
  'K': 1e3, # kilo
  'M': 1e6, # mega/million
  'G': 1e9, # giga
  'B': 1e9, # billion
  'T': 1e12,# tera
}

_NAN = {
  'NAN',
  None,
  '-',
  ''
}

_GRAPH_PARSERS = {
  '.edges': read_edges,
  '.mtx': read_mtx,
}

_STATISTICS_MAPPINGS = {
  2: {'name': 'n', 'type': int},
  3: {'name': 'm', 'type': int},
  4: {'name': 'd_max', 'type': int},
  5: {'name': 'd_avg', 'type': float},
  6: {'name': 'r', 'type': float},
  7: {'name': 't', 'type': int},
  8: {'name': 't_avg', 'type': float},
  9: {'name': 't_max', 'type': int},
  10: {'name': 'k_avg', 'type': float},
  11: {'name': 'k', 'type': float},
  12: {'name': 'max_kcore', 'type': int},
  13: {'name': 'wlb', 'type': int},
}

def _graph_parser_exists(file_path: str) -> bool:
  """Check if graph parser exists"""
  _, ext = os.path.splitext(file_path)
  return ext.lower() in _GRAPH_PARSERS.keys() 


def _resolve_graph_file(content: List[str]) -> str:
  """Resolve graph file"""
  content = list(filter(_graph_parser_exists, content))
  if len(content) != 1: return None
  return content[0]


def _convert(key: str, value: str):
  """Convert raw values"""
  if value.upper() in _NAN:
    return (key, None)
  elif key in _VALUE_TYPES:
    if value[-1] in _SUFFIXES:
      return (key, _VALUE_TYPES[key](float(value[:-1]) * _SUFFIXES[value[-1]]))
    else:
      return (key, _VALUE_TYPES[key](value))
  
  return (key, value)


def get_metadata(name: str, force: bool = False) -> Metadata:
  """Get graph metadata"""
  cache_path = os.path.join(_TMP_DIR, f'{name}.metadata')

  # Load metadata from cache
  if os.path.exists(cache_path) and not force:
    with open(cache_path, 'rb') as pfd: 
      return pickle.load(pfd)

  # Download metadata
  print(f'Downloading metadata...')
  url = f'{_BASE_URL}/{name}.php'
  res = requests.get(url)
  if res.status_code >= 400:
    raise Exception(f'Failed to load page "{url}" with status {res.status_code}')

  parser = bs4.BeautifulSoup(res.text, 'html.parser')

  download_el = parser.find('i', {'class': 'icon-cloud-download icon-large'}).parent
  if not download_el:
    raise Exception(f'Download link not found for the network "{name}".')
  
  category_el = parser.find('a', {'summary': 'network data category'})
  if not category_el:
    raise Exception(f'Category not found for the network "{name}".')
  category = category_el.text

  metadata = dict()
  metadata_el = parser.find('table', {'summary': 'Dataset metadata'})
  if metadata_el:
    metadata = dict(map(lambda tr: (tr.contents[0].text, tr.contents[1].text), metadata_el.findAll('tr')))

  statistics_el = parser.find('table', {'summary': 'Network data statistics'})
  if not statistics_el:
    raise Exception(f'Statistics container not found for the network "{name}"".')
  statistics = dict(map(lambda tr: _convert(tr.contents[0].text, tr.contents[1].text), statistics_el.findAll('tr')))

  ret = Metadata(
    name=name,
    category = category,
    metadata = metadata,
    statistics = statistics,
    data_url=download_el.attrs['href']
  )

  # Cache loaded metadata
  with open(cache_path, 'ab') as pfd:
    pickle.dump(ret, pfd)

  return ret


def get_graph(name: str, data_url: str, force: bool = False) -> nx.Graph:
  """Get graph"""
  zip_cache_path = os.path.join(_TMP_DIR, data_url.split('/')[-1])
  cache_path = _resolve_graph_file(glob.glob(os.path.join(_TMP_DIR, f'{name}.*')))

  # Download zip file
  if not cache_path or force:
    print(f'Downloading the network "{name}" [. = 1MB]: ', end='', flush=True)
    res = requests.get(data_url, stream=True)
    if res.status_code >= 400:
      raise Exception(f'Failed to load page "{data_url}" with status {res.status_code}')
    with open(zip_cache_path, 'wb') as fd:
      for chunk in res.iter_content(chunk_size=1000000):
        print(f'.', end='', flush=True)
        fd.write(chunk)
    print()

    # Extract graph file
    print('Extracting graph file...')
    with zipfile.ZipFile(zip_cache_path) as zfd:
      graph_file = _resolve_graph_file(zfd.namelist())
      if not graph_file:
        raise Exception(f'Failed to resolve graph file for the network "{name}"')
      zfd.extract(f'{graph_file}', path=_TMP_DIR)
      cache_path = os.path.join(_TMP_DIR, f'{name}{os.path.splitext(graph_file)[1]}')
      os.rename(os.path.join(_TMP_DIR, os.path.basename(graph_file)), cache_path)
    
    # Cleanup
    os.remove(zip_cache_path)

  # Parse graph file
  print(f'Parsing graph from "{cache_path}"...')
  return read_graph(cache_path)


def read_graph(graph_file: str) -> nx.Graph:
  return _GRAPH_PARSERS[os.path.splitext(graph_file)[1]](graph_file)


def get_list(force = False) -> pd.DataFrame:
  """Download list of networks from the Network Repository and return it as Pandas dataframe."""

  cache_path = os.path.join(_TMP_DIR, 'graphs.csv')
  if os.path.exists(cache_path) and not force:
    return pd.read_csv(cache_path)

  url = f'{_BASE_URL}/networks.php'
  res = requests.get(url)
  if res.status_code >= 400:
    raise Exception(f'Failed to load page "{url}" with status {res.status_code}')
  
  parser = bs4.BeautifulSoup(res.text, 'html.parser')

  table = []
  for row_el in parser.select('table#myTable > tbody > tr'):
    td = dict()
    try:
      for i, td_el in enumerate(row_el.select('td')):
        if i == 0:
          td['name'] = td_el.text.lstrip('\xa0 ')
        elif i == 1:
          td['category'] = td_el.text
        elif i == 14:
          td['download_size'] = int(td_el.attrs['class'][1].rstrip('}'))
        elif i == 15:
          td['download_url'] = td_el.select('a[href]')[0].attrs['href']
        elif td_el.text != '-' and i in _STATISTICS_MAPPINGS:
          key = _STATISTICS_MAPPINGS[i]['name']
          value = _STATISTICS_MAPPINGS[i]['type'](td_el.attrs['class'][1].rstrip('}'))
          td[key] = value
      table.append(td)
    except:
      print(f'WARNING: Parsing error for the network {td.get("name", "/")}')

  df = pd.DataFrame(table)
  df.to_csv(cache_path, index=False)

  return df
