import random
import operator
import pdb
import copy
import pickle
import sys
from collections import defaultdict

import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import numpy as np
import networkx as nx

from RWC import getCentralUsers, randomWalkPolarity

from scipy.stats import ttest_ind,ks_2samp
random.seed(42)

task = int(sys.argv[1])
parallelTask = 5
if task>=parallelTask:
	print('Provide task number less than',parallelTask)

## PARAMETERS
expCount = 1000 		#fixed
rwc_iteration = 10000	#fixed
rwc_walk = 2000			#fixed

num_nodes_ = range(10000,200000,10000)
polarWeights = np.linspace(0.01,0.1,10)
polarWeight_ = [polarWeights[i] for i in range(len(polarWeights)) if i%parallelTask == task]
print('Running these polarWeights:',polarWeight_)
remove_ratio_ = [0.005,0.01,0.05,0.1]

## GENERATE GRAPH
for num_nodes in num_nodes_:
	for polarWeight in polarWeight_:
		try:
			G = nx.read_gpickle('graphs/' + str(num_nodes) + '_' + str(polarWeight) + '.pickle')
		except IOError:
			print('not_found',
			continue
		userList = {}
		for i in range(num_nodes):
			if i%2 == 0:
				userList[i] = 'left'
			else:
				userList[i] = 'right'

		for remove_ratio in remove_ratio_:
			## RANDOM NODE REMOVAL TEST
			rwcs = []
			rwcs_reduced = []

			identifier = str(num_nodes) + '_' + str(polarWeight) + '_' + str(remove_ratio)
			for _ in range(expCount):
				if _ %100 ==0:
					print(_)
				rwc,_ = randomWalkPolarity(G,userList,rwc_iteration,rwc_walk)
				rwcs.append(rwc)
			for _ in range(expCount):
				if _ %100 ==0:
					print(_)
				G_reduced = nx.read_gpickle('graphs/' + str(num_nodes) + '_' + str(polarWeight) + '.pickle')
				userList_reduced = dict(userList)
				remove_comm1 = np.random.choice(range(0,num_nodes,2),int(num_nodes*remove_ratio)/2,replace=False)
				remove_comm2 = np.random.choice(range(1,num_nodes,2),int(num_nodes*remove_ratio)/2,replace=False)
				for node in remove_comm1:
					G_reduced.remove_node(node)
					del userList_reduced[node]
				for node in remove_comm2:
					G_reduced.remove_node(node)
					del userList_reduced[node]
				for node, deg in G_reduced.degree().iteritems():
					if deg == 0:
						G_reduced.remove_node(node)
						del userList_reduced[node]
				
				rwc,_ = randomWalkPolarity(G_reduced,userList_reduced,rwc_iteration,rwc_walk)
				rwcs_reduced.append(rwc)



			fullPol = np.mean(rwcs)
			randomRemovedPol = np.mean(rwcs_reduced)
			testScore = ks_2samp(rwcs,rwcs_reduced)
			
			## VISUALIZE
			data = pd.DataFrame({'GraphType':np.concatenate((['Without Random']*len(rwcs_reduced),['Full']*len(rwcs))),
								 'Polarization':np.concatenate((rwcs_reduced,rwcs))})
			
			target_0 = data.loc[data['GraphType'] == 'Without Random']
			target_1 = data.loc[data['GraphType'] == 'Full']
			sns.distplot(target_0[['Polarization']], label='Without Random', hist=False, rug=False,kde_kws={"shade": True})
			sns.distplot(target_1[['Polarization']], label='Full', hist=False, rug=False,kde_kws={"shade": True})

			plt.legend(loc = 'upper left')
			plt.title('Synthetic Network')
			if testScore.pvalue < 0.05:
				if randomRemovedPol < fullPol:
					plt.savefig('experiments/increase_'+ identifier + '.png',dpi=500)
				elif randomRemovedPol >= fullPol:
					plt.savefig('experiments/decrease_'+ identifier + '.png',dpi=500)
			else:
				plt.savefig('experiments/noeffect_' + identifier + '.png',dpi=500)

			plt.clf()

			## SAVE RESULTS
			with open('experiments/values/' + identifier +'_randomRemoval.pickle','wb') as fw:
				pickle.dump({'rwcs':rwcs,'rwcs_reduced':rwcs_reduced}, fw)
			print(ks_2samp(rwcs,rwcs_reduced))
			print(ttest_ind(rwcs,rwcs_reduced))
			print(fullPol,randomRemovedPol)
					
