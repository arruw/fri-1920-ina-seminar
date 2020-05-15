import os
import requests
import networkx as nx
import zipfile
import pickle
import glob
from typing import List

import bs4

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


def get_graph(metadata: Metadata, force: bool = False) -> nx.Graph:
  """Get graph"""
  zip_cache_path = os.path.join(_TMP_DIR, metadata.data_url.split('/')[-1])
  cache_path = _resolve_graph_file(glob.glob(os.path.join(_TMP_DIR, f'{metadata.name}.*')))

  # Download zip file
  if not cache_path or force:
    print(f'Downloading the network "{metadata.name}" [. = 1MB]: ', end='', flush=True)
    res = requests.get(metadata.data_url, stream=True)
    if res.status_code >= 400:
      raise Exception(f'Failed to load page "{url}" with status {res.status_code}')
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
        raise Exception(f'Failed to resolve graph file for the network "{metadata.name}"')
      zfd.extract(f'{graph_file}', path=_TMP_DIR)
      cache_path = os.path.join(_TMP_DIR, f'{metadata.name}{os.path.splitext(graph_file)[1]}')
      os.rename(os.path.join(_TMP_DIR, os.path.basename(graph_file)), cache_path)
    
    # Cleanup
    os.remove(zip_cache_path)

  # Parse graph file
  print(f'Parsing graph from "{cache_path}"...')
  return _GRAPH_PARSERS[os.path.splitext(cache_path)[1]](cache_path)
