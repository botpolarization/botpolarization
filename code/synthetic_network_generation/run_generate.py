from generate_fast_graph import generate_fast_graph
import networkx as nx
import numpy as np
erdos_renyi_prob = 0.25
init_num_nodes = 100
num_nodes = range(10000,200000,10000)
polarWeights = np.linspace(0.01,0.1,10)
print(polarWeights)
alpha = 0.34
beta = 0.33
gamma = 0.33
delta_in = 0.01
delta_out = 0.01
for num_node in num_nodes:
	for polarWeight in polarWeights:
		generate_fast_graph(erdos_renyi_prob,init_num_nodes,num_node,polarWeight,alpha,beta,gamma,delta_in,delta_out)
