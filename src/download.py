import argparse
from src.scraper.scraper import get_metadata, get_data

def main(network: str):
  meta = get_metadata(network)
  graph = meta.get_graph()
  print('Done.')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Download and cache network from the networkrepository.com')
  parser.add_argument('network', type=str, help='Unique name of the network')

  args = parser.parse_args()
  main(**vars(args))
