import networkx as nx
import pandas as pd
from random import choice, sample
from src.scraper.scraper import get_graph

def compute_auc(indexes, m, sampleSize):
	m1, m2 = 0, 0
	indexes = (list(indexes[0]), list(indexes[1])) # cast from generator to list
	for i in range(sampleSize):
		_,_,randLNs = choice(indexes[0])
		_,_,randLPs = choice(indexes[1])
		if randLPs > randLNs:
			m1 += 1
		elif randLPs == randLNs:
			m2 += 1
	return round((m1+m2/2)/(m/10), 3)

def evaluate_link_prediction_method(G: nx.Graph, method, negative, positive, sampleSize):
	indexes = compute_indexes(G, method, negative, positive)
	return compute_auc(indexes, G.number_of_edges(), sampleSize)

def compute_indexes(G: nx.Graph, method, negative, positive):
	if method == 'resource_allocation_index':
		return nx.resource_allocation_index(G,negative), nx.resource_allocation_index(G,positive)
	elif method == 'jaccard_coefficient':
		return nx.jaccard_coefficient(G,negative), nx.jaccard_coefficient(G,positive)
	elif method == 'adamic_adar_index':
		return nx.adamic_adar_index(G,negative), nx.adamic_adar_index(G,positive)
	elif method == 'preferential_attachment':
		return nx.preferential_attachment(G,negative), nx.preferential_attachment(G,positive)
	else:
		return -1

def compute_negative_and_positive_pairs(G: nx.Graph):
	m = G.number_of_edges()
	sampleSize = int(m * 0.1)
	negative = []
	pairs = 0
	nodes = list(G.nodes)
	while pairs < sampleSize:
		[rand1,rand2] = sample(nodes,2)
		if not connected(G,rand1,rand2) and (rand1,rand2) not in negative and (rand2,rand1) not in negative:
			negative.append((rand1,rand2))
			pairs += 1
	positive = sample(list(G.edges()),sampleSize)
	for edge in positive:
		G.remove_edge(edge[0],edge[1])
	return sampleSize, negative, positive

def connected(G: nx.Graph, u, v):
	return u in G.neighbors(v)

networks_df = pd.read_csv('data/precomputed.csv')
link_prediction_methods = ['resource_allocation_index',
													'jaccard_coefficient',
													'adamic_adar_index',
													'preferential_attachment']

for index, row in networks_df.iterrows():
	G = get_graph(row['name'], row['download_url'])
	scores = {}
	sampleSize, negative, positive = compute_negative_and_positive_pairs(G.copy())
	for method in link_prediction_methods:
		scores[method] = evaluate_link_prediction_method(G, method, negative, positive, sampleSize)
	print(row['name'], scores)