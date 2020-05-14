import networkx as nx

import src.scraper.scraper

class Metadata():
  """Network repository metadata"""

  def __init__(self,
    name: str,
    metadata: dict,
    statistics: dict,
    data_url: str,
    ):
    
    self.name = name
    self.metadata = metadata
    self.statistics = statistics
    self.data_url = data_url

  _graph: nx.Graph = None
  def get_graph(self, force: bool = False) -> nx.Graph:
    """Get Networx graph object"""
    if not self._graph:
      self._graph = src.scraper.scraper.get_data(self, force)
    return self._graph
  
  def __getstate__(self):
    """Return state values to be pickled"""
    return {
      'name': self.name,
      'metadata': self.metadata,
      'statistics': self.statistics,
      'data_url': self.data_url
    }

  def __setstate__(self, state):
    """Restore state from the unpickled state values"""
    self.name = state['name']
    self.metadata = state['metadata']
    self.statistics = state['statistics']
    self.data_url = state['data_url']
