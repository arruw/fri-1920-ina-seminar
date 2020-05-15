import pandas as pd

from src.scraper.scraper import get_graph

df = pd.read_csv('.tmp/graphs.csv')

no_missing_data = (df.isnull().any(axis=1) == False)
small_graph = (df['n'] <= 1e3) & (df['m'] <= 1e4) & (df['download_size'] <= 5e6)
sanity_checks = (
  (df['n']**2 >= df['m']) &
  (df['d_avg']-1 <= 2*df['m']/df['n']) &
  (df['d_avg']+1 >= 2*df['m']/df['n'])
)

dfx = df[no_missing_data & small_graph & sanity_checks]

for index, row in dfx.iterrows():
  try:
    print(f'({index}) Downloading graph data for "{row["name"]}" [{row["download_size"]} B] ...')
    get_graph(row['name'], row['download_url'])
  except:
    print('WARNING: Error while downloading graph')

exit()