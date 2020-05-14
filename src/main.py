from src.scraper.scraper import get_metadata, get_data

def main():
  meta = get_metadata('bio-CE-CX')
  graph = meta.get_graph()
  print()

if __name__ == "__main__":
  main()
