import sys
from src.scraper.scraper import get_metadata, get_data

def main(name):
  meta = get_metadata(name)
  graph = meta.get_graph()
  print('Done.')

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('First argument should be network name.')
    exit(1)
  main(sys.argv[1])
