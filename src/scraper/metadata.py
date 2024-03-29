import networkx as nx

import src.scraper.scraper

class Metadata():
  """Network repository metadata"""

  def __init__(self,
    name: str,
    category: str,
    metadata: dict,
    statistics: dict,
    data_url: str,
    ):
    
    self.name = name
    self.category = category
    self.metadata = metadata
    self.statistics = statistics
    self.data_url = data_url


  def __getstate__(self):
    """Return state values to be pickled"""
    return {
      'name': self.name,
      'category': self.category,
      'metadata': self.metadata,
      'statistics': self.statistics,
      'data_url': self.data_url
    }


  def __setstate__(self, state):
    """Restore state from the unpickled state values"""
    self.name = state['name']
    self.category = state['category']
    self.metadata = state['metadata']
    self.statistics = state['statistics']
    self.data_url = state['data_url']
