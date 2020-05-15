from src.scraper.scraper import get_metadata, get_graph

def main(name):
  meta = get_metadata(name)
  graph = get_graph(meta)
  print('Done.')

if __name__ == "__main__":
  main('power-1138-bus')
