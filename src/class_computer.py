import networkx as nx
import pandas as pd
import numpy as np

from cdlib.algorithms import leiden

from math import factorial
from random import choice
from itertools import combinations_with_replacement

from src.scraper.scraper import get_graph


N_OF_RUNS = 5

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
	return (m1+m2/2)/(m/10)

def evaluate_link_prediction_method(G: nx.Graph, m, method, negative, positive, sampleSize):
	indexes = compute_indexes(G, method, negative, positive)
	return compute_auc(indexes, m, sampleSize)

def compute_indexes(G: nx.Graph, method, negative, positive):
	if method == 'resource_allocation_index':
		return nx.resource_allocation_index(G,negative), nx.resource_allocation_index(G,positive)
	elif method == 'jaccard_coefficient':
		return nx.jaccard_coefficient(G,negative), nx.jaccard_coefficient(G,positive)
	elif method == 'adamic_adar_index':
		return nx.adamic_adar_index(G,negative), nx.adamic_adar_index(G,positive)
	elif method == 'preferential_attachment':
		return nx.preferential_attachment(G,negative), nx.preferential_attachment(G,positive)
	elif method == 'cn_soundarajan_hopcroft':
		return nx.cn_soundarajan_hopcroft(G,negative), nx.cn_soundarajan_hopcroft(G,positive)
	elif method == 'ra_index_soundarajan_hopcroft':
		return nx.ra_index_soundarajan_hopcroft(G,negative), nx.ra_index_soundarajan_hopcroft(G,positive)
	elif method == 'within_inter_cluster':
		return nx.within_inter_cluster(G,negative), nx.within_inter_cluster(G,positive)
	else:
		raise NameError('The given method is not supported')

def unconnected_pairs(G: nx.Graph):
	all_pairs = set(combinations_with_replacement(G.nodes, 2))		
	return list(all_pairs - set(G.edges))

def compute_negative_and_positive_pairs(G: nx.Graph):
	m = G.number_of_edges()
	sampleSize = int(m * 0.1)
	
	unconnected = np.array(unconnected_pairs(G))
	indexes = np.random.choice(len(unconnected), size=sampleSize, replace=False)
	negative = unconnected[indexes]
	
	connected = np.array(list(G.edges))
	indexes = np.random.choice(len(connected), size=sampleSize, replace=False)
	positive = connected[indexes]
	for edge in positive:
		G.remove_edge(edge[0],edge[1])
	return sampleSize, negative, positive

def connected(G: nx.Graph, u, v):
	return u in G.neighbors(v)

def community_index(G: nx.Graph, i, j, commLabels, comms):
	ci, cj = comms[i][0], comms[j][0]
	if ci != cj:
		return 0
	C = commLabels[ci]
	nc, mc = len(C), len(nx.subgraph(G,C))
	return mc/(factorial(nc)/(2*factorial(nc-2)))

networks_df = pd.read_csv('data/precomputed.csv')
link_prediction_methods = ['resource_allocation_index',
													'jaccard_coefficient',
													'adamic_adar_index',
													'preferential_attachment',]



for index, row in networks_df.iterrows():
	originalG = get_graph(row['name'], row['download_url'])
	# average scores
	scores = {method: 0 for method in link_prediction_methods}
	m = originalG.number_of_edges()
	
	for run in range(N_OF_RUNS):
		print(f'------- Run {run} -------')
		G = originalG.copy()
		sampleSize, negative, positive = compute_negative_and_positive_pairs(G)
		
		for method in link_prediction_methods:
			successful = False
			while not successful:
				try:
					scores[method] += evaluate_link_prediction_method(G, m, method, negative, positive, sampleSize) / N_OF_RUNS
					successful = True
				except: # division by 0 when computing adamic adar
					print(method, 'not successful...')
					# we compute negative and positive pairs again
					G = originalG.copy()
					sampleSize, negative, positive = compute_negative_and_positive_pairs(G)
		
	print(f'Network number {index}, scores: {[(method,round(score,3)) for method,score in scores.items()]}')
	