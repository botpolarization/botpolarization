import networkx as nx
import numpy as np
import pandas as pd

import pdb
import operator
import random
import copy
import pickle
import collections
import json
import sys

from collections import defaultdict
from scipy.stats import ttest_ind,ks_2samp

from RWC import getCentralUsers, randomWalkPolarity
random.seed(42)


expCount = 1000
rwc_iteration = 10000
rwc_walk = 2000

num_nodes = range(10000,200000,10000)
polarWeights = np.linspace(0.01,0.1,10)
results = {}
fw = open('parameter_vs_polar.csv','w',buffering=0)

for num_node in num_nodes:
	if num_node not in results:
		results[num_node] = defaultdict(list)
	for polarWeight in polarWeights:
		print(num_node,polarWeight)
		fi = 'graphs/' + str(num_node) + '_' + str(polarWeight) + '.pickle'
		try:
			G = nx.read_gpickle(fi)
		except Exception as e:
			print(e)
			continue
		userList = {}
		for i in range(G.number_of_nodes()):
			if i%2 == 1:
				userList[i] = 'left'
			elif i%2 == 0:
				userList[i] = 'right'
		for _ in range(expCount):
			rwc,_ = randomWalkPolarity(G,userList,rwc_iteration,rwc_walk)
			results[num_node][polarWeight].append(rwc)

		fw.write(str(num_node) + ',' + str(polarWeight) + ',')
		toWrite = ''
		for rwc in results[num_node][polarWeight]:
			toWrite += str(rwc) + ','
		toWrite = toWrite[0:-1]
		fw.write(toWrite + '\n')
fw.close()
