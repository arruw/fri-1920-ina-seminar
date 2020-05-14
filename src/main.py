from src.scraper.scraper import get_metadata, get_data

def main(name):
  meta = get_metadata(name)
  graph = meta.get_graph()
  print('Done.')

if __name__ == "__main__":
  main('bio-CE-CX')
