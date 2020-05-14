import os
import requests
import networkx as nx
import zipfile
import pickle
import glob
from typing import List

import bs4

import src.scraper.metadata
import src.scraper.graph_parsers

BASE_URL = 'http://networkrepository.com'
TMP_DIR = '.tmp'

if not os.path.exists(TMP_DIR):
  os.mkdir(TMP_DIR)


def resolve_graph_file(content: List[str]) -> str:
  content = list(filter(src.scraper.graph_parsers.parser_exists, content))
  if len(content) != 1: return None
  return content[0]

def to_float(string):
  if string == '-' or not string:
    return None
  elif string[-1] == 'K':
    return float(string[:-1]) * 1000
  elif string[-1] == 'M':
    return float(string[:-1]) * 1000000
  elif string[-1] == 'B':
    return float(string[:-1]) * 1000000000
  else:
    return float(string)


def get_metadata(name: str, force: bool = False) -> src.scraper.metadata.Metadata:
  cache_path = os.path.join(TMP_DIR, f'{name}.metadata')

  # Load metadata from cache
  if os.path.exists(cache_path) and not force:
    with open(cache_path, 'rb') as pfd: 
      return pickle.load(pfd)

  # Download metadata
  print(f'Downloading metadata...')
  url = f'{BASE_URL}/{name}.php'
  res = requests.get(url)
  if res.status_code >= 400:
    raise Exception(f'Failed to load page "{url}" with status {res.status_code}')

  parser = bs4.BeautifulSoup(res.text, 'html.parser')

  download_el = parser.find('i', {'class': 'icon-cloud-download icon-large'}).parent
  if not download_el:
    raise Exception(f'Download link not found for the network "{name}".')

  metadata = dict()
  metadata_el = parser.find('table', {'summary': 'Dataset metadata'})
  if metadata_el:
    metadata = dict(map(lambda tr: (tr.contents[0].text, tr.contents[1].text), metadata_el.findAll('tr')))

  statistics_el = parser.find('table', {'summary': 'Network data statistics'})
  if not statistics_el:
    raise Exception(f'Statistics container not found for the network "{name}"".')
  statistics = dict(map(lambda tr: (tr.contents[0].text, to_float(tr.contents[1].text)), statistics_el.findAll('tr')))

  ret = src.scraper.metadata.Metadata(
    name=name,
    metadata = metadata,
    statistics = statistics,
    data_url=download_el.attrs['href']
  )

  # Cache loaded metadata
  with open(cache_path, 'ab') as pfd:
    pickle.dump(ret, pfd)

  return ret


def get_data(metadata: src.scraper.metadata.Metadata, force: bool = False) -> nx.Graph:
  zip_cache_path = os.path.join(TMP_DIR, metadata.data_url.split('/')[-1])
  cache_path = resolve_graph_file(glob.glob(os.path.join(TMP_DIR, f'{metadata.name}.*')))

  # Download zip file
  if not os.path.exists(zip_cache_path) or force:
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
  if not cache_path or force:
    print('Extracting *.edges file...')
    with zipfile.ZipFile(zip_cache_path) as zfd:
      graph_file = resolve_graph_file(zfd.namelist())
      if not graph_file:
        raise Exception(f'Failed to resolve graph file for the network "{metadata.name}"')
      zfd.extract(f'{graph_file}', path=TMP_DIR)
      cache_path = os.path.join(TMP_DIR, f'{metadata.name}{os.path.splitext(graph_file)[1]}')
      os.rename(os.path.join(TMP_DIR, os.path.basename(graph_file)), cache_path)

  # Parse graph file
  print(f'Parsing graph from "{cache_path}"...')
  return src.scraper.graph_parsers.GRAPH_PARSERS[os.path.splitext(cache_path)[1]](cache_path)
