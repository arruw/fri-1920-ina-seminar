import networkx as nx
import pandas as pd
import numpy as np

from cdlib.algorithms import leiden, louvain

from math import factorial, isnan
from random import choice
from itertools import combinations_with_replacement

from src.scraper.scraper import get_graph

def compute_class(G: nx.Graph):
	# average scores
	scores = {method: 0 for method in link_prediction_methods}
	m = G.number_of_edges()

	for run in range(N_OF_RUNS):
		print(f'------- Run {run} -------')
		G_test = G.copy()
		sampleSize, negative, positive = compute_negative_and_positive_pairs(G_test)
		
		for method in link_prediction_methods:
			successful = False
			while not successful:
				try:
					scores[method] += compute_auc(G_test, m, method, negative, positive, sampleSize) / N_OF_RUNS
					successful = True
				except Exception as inst:
					print(f'{method} failed. {type(inst)}, {inst.args}')
					# we compute negative and positive pairs again
					G_test = G.copy()
					sampleSize, negative, positive = compute_negative_and_positive_pairs(G_test)
	
	print(f'Network {index}, scores: {[(method,round(score,3)) for method,score in scores.items()]} \n')
	# return class - index of the best method
	aucs = list(scores.values())
	return aucs.index(max(aucs))

def compute_auc(G:nx.Graph, m, method, negative, positive, sampleSize):
	neg_indexes, pos_indexes = compute_indexes(G, method, negative, positive)
	m1, m2 = 0, 0
	neg_indexes, pos_indexes = list(neg_indexes), list(pos_indexes)
	
	for i in range(sampleSize):
		_,_,rand_neg = choice(neg_indexes)
		_,_,rand_pos = choice(pos_indexes)
		if rand_pos > rand_neg:
			m1 += 1
		elif rand_pos == rand_neg:
			m2 += 1
	return (m1+m2/2)/(m/10)

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

def compute_indexes(G: nx.Graph, method, negative, positive):
	if method == 'resource_allocation':
		return nx.resource_allocation_index(G,negative), nx.resource_allocation_index(G,positive)
	elif method == 'jaccard_coefficient':
		return nx.jaccard_coefficient(G,negative), nx.jaccard_coefficient(G,positive)
	elif method == 'adamic_adar':
		return nx.adamic_adar_index(G,negative), nx.adamic_adar_index(G,positive)
	elif method == 'preferential_attachment':
		return nx.preferential_attachment(G,negative), nx.preferential_attachment(G,positive)
	elif method == 'sorensen_neighbours':
		return ([(u, v, sorensen_index(G, u, v)) for u, v in negative],
					  [(u, v, sorensen_index(G, u, v)) for u, v in positive])
	elif method == 'community':
		c = louvain(G)
		commLabels = c.communities
		comms = c.to_node_community_map()
		return ([(u, v, community_index(G, u, v, commLabels, comms)) for u, v in negative],
					  [(u, v, community_index(G, u, v, commLabels, comms)) for u, v in positive])
	else:
		raise NameError('The given method is not supported')



def community_index(G: nx.Graph, i, j, commLabels, comms):
	ci, cj = comms[i][0], comms[j][0]
	if ci != cj:
		return 0
	C = commLabels[ci]
	nc, mc = len(C), len(nx.subgraph(G,C))
	return mc/(factorial(nc)/(2*factorial(nc-2)))

def sorensen_index(G: nx.Graph, i, j):
	i_neighbourhood = set(G.neighbors(i))
	j_neighbourhood = set(G.neighbors(j))
	degreeSum = G.degree(i) + G.degree(j)
	if degreeSum == 0:
		return 0
	return len(i_neighbourhood.intersection(j_neighbourhood))/degreeSum



def unconnected_pairs(G: nx.Graph):
	all_pairs = set(combinations_with_replacement(G.nodes, 2))		
	return list(all_pairs - set(G.edges))

def connected(G: nx.Graph, u, v):
	return u in G.neighbors(v)

def remove_weights(G: nx.Graph):
	if nx.is_weighted(G):
		for edge in G.edges:
			del G.edges[edge]['weight']


link_prediction_methods = ['resource_allocation',
													 'jaccard_coefficient',
													 'adamic_adar',
													 'preferential_attachment',
													 'community',
													 'sorensen_neighbours']


N_OF_RUNS = 5
OVERWRITE = False # if we compute and overwrite class where its already been computed
SAVE_RATE = 20 # save every n networks

if __name__ == '__main__':
	networks_df = pd.read_csv('data/precomputed_with_classes.csv')

	for index, row in networks_df.iterrows():
		if isnan(row['Class']) or OVERWRITE:
			G = get_graph(row['name'], row['download_url'])
			remove_weights(G)
			classVariable = compute_class(G)
			networks_df.iloc[index, networks_df.columns.get_loc('Class')] = classVariable
		if index % SAVE_RATE == 0: # save every 20 networks
			networks_df.to_csv('data/precomputed_with_classes.csv', index=False)