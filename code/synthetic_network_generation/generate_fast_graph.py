import networkx as nx
import random
import operator
import pdb
from collections import defaultdict
import numpy as np
import pickle
random.seed(42)

## erdos_renyi_prob:0.33
## init_num_nodes:100
## num_nodes: how many nodes you want in your polarized network in total
## polarWeight: inverse polarization parameter. Lower is more polarized, higher is less polarized.
## alpha, beta, gamm: read the paper at; https://www.microsoft.com/en-us/research/uploads/prod/2016/11/Directed-scale-free-graphs.pdf
## alpha: 0.33, beta:0.33, gamma: 0.33
## delta_in, delta_out: 0.1,0.1

def generate_fast_graph(erdos_renyi_prob,init_num_nodes,num_nodes,polarWeight,\
							alpha,beta,gamma,\
							delta_in,delta_out):

	identifier  = str(num_nodes) + '_' + str(polarWeight)
	## ERDOS RENYI CORES OF TWO POLARIZED COMMUNITIES
	G = nx.DiGraph()
	for i in range(init_num_nodes):
		G.add_node(i)

	for i in range(0,init_num_nodes,2):
		for j in range(0,init_num_nodes,2):
			if random.random() < erdos_renyi_prob:
				G.add_edge(i,j,weight=1)
	for i in range(1,init_num_nodes,2):
		for j in range(1,init_num_nodes,2):
			if random.random() < erdos_renyi_prob:
				G.add_edge(i,j,weight=1)
	
	new_node_index = init_num_nodes
	degreeOut = G.out_degree().values()
	degreeIn = G.in_degree().values()
	
	degreeInCamp1 = np.array([(degreeIn[i]+delta_in)*polarWeight if i%2 == 0 else degreeIn[i] + delta_in \
												for i in range(len(degreeIn))])
	sum_degreeInCamp1 = float(np.sum(degreeInCamp1))
	degreeInCamp1 = degreeInCamp1/sum_degreeInCamp1
	
	degreeInCamp2 = np.array([(degreeIn[i]+delta_in)*polarWeight if i%2 == 1 else degreeIn[i] + delta_in \
											for i in range(len(degreeIn))])
	sum_degreeInCamp2 = float(np.sum(degreeInCamp2))
	degreeInCamp2 = degreeInCamp2/sum_degreeInCamp2
	
	degreeOutCamp1 = np.array([(degreeOut[i]+delta_out)*polarWeight if i%2 == 0 else degreeOut[i] + delta_out \
											for i in range(len(degreeOut))])
	sum_degreeOutCamp1 = float(np.sum(degreeOutCamp1))
	degreeOutCamp1 = degreeOutCamp1/sum_degreeOutCamp1
	
	degreeOutCamp2 = np.array([(degreeOut[i]+delta_out)*polarWeight if i%2 == 1 else degreeOut[i] + delta_out \
											for i in range(len(degreeOut))])
	sum_degreeOutCamp2 = float(np.sum(degreeOutCamp2))
	degreeOutCamp2 = degreeOutCamp2/sum_degreeOutCamp2
	
	while G.number_of_nodes() < num_nodes:
		dice = random.random()
		selectA,selectB,selectC = False, False, False
		if dice < alpha:
			selectA = True
			#print('A')
		elif dice < (alpha + beta):
			selectB = True
			#print('B')
		elif dice < (alpha + beta + gamma):
			selectC =True
			#print('C')
		else:
			print('Something wrong with alpha,beta,gamma')
			return
		
		if selectA:
			# Add a new vertex and an edge from the new to an old one
			G.add_node(new_node_index)
			if new_node_index%2 == 1: # new node belongs to camp1
				old_node = np.random.choice(range(len(degreeInCamp1)),1,p = degreeInCamp1)[0]
				
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1 = np.append(degreeOutCamp1, 1+delta_out)
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2 = np.append(degreeOutCamp2, (1+delta_out)*polarWeight)
				
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1 = np.append(degreeInCamp1, 0 + delta_in)
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2 = np.append(degreeInCamp2, (0 + delta_in)*polarWeight)
				
				sum_degreeOutCamp1 += 1.0 + delta_out
				sum_degreeOutCamp2 += (1.0 + delta_out)*polarWeight
				degreeOutCamp1 /= sum_degreeOutCamp1
				degreeOutCamp2 /= sum_degreeOutCamp2
				
				if old_node%2 == 1: #old node belongs to camp1
					degreeInCamp1[old_node] += 1
					degreeInCamp2[old_node] += polarWeight
					sum_degreeInCamp1 += delta_in + 1
					sum_degreeInCamp2 += (delta_in + 1)*polarWeight
				elif old_node%2 == 0: #old node belongs to camp2
					degreeInCamp1[old_node] += polarWeight
					degreeInCamp2[old_node] += 1
					sum_degreeInCamp1 += delta_in + polarWeight
					sum_degreeInCamp2 += delta_in*polarWeight + 1
				
				degreeInCamp1 /= sum_degreeInCamp1
				degreeInCamp2 /= sum_degreeInCamp2
				
			elif new_node_index%2 == 0:# new node belongs to camp2
				old_node = np.random.choice(range(len(degreeInCamp2)),1,p = degreeInCamp2)[0]
				
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1 = np.append(degreeOutCamp1, (1+delta_out)*polarWeight)
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2 = np.append(degreeOutCamp2, 1+delta_out)
				
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1 = np.append(degreeInCamp1, (0 + delta_in)*polarWeight)
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2 = np.append(degreeInCamp2, 0 + delta_in)
				
				sum_degreeOutCamp1 += (1.0 + delta_out)*polarWeight
				sum_degreeOutCamp2 += 1.0 + delta_out
				degreeOutCamp1 /= sum_degreeOutCamp1
				degreeOutCamp2 /= sum_degreeOutCamp2
				
				if old_node%2 == 1: #old node belongs to camp1 
					degreeInCamp1[old_node] += 1
					degreeInCamp2[old_node] += polarWeight
					sum_degreeInCamp1 += delta_in*polarWeight + 1
					sum_degreeInCamp2 += delta_in + polarWeight
				elif old_node%2 == 0: #old node belongs to camp2
					degreeInCamp1[old_node] += polarWeight
					degreeInCamp2[old_node] += 1
					sum_degreeInCamp1 += (1+delta_in)*polarWeight
					sum_degreeInCamp2 += delta_in + 1
					
				degreeInCamp1 /= sum_degreeInCamp1
				degreeInCamp2 /= sum_degreeInCamp2
				
			G.add_edge(new_node_index, old_node, weight = 1)
			new_node_index += 1
			
		elif selectB:
			# Add a new edge between two existing nodes
			sideDice = 0 if random.random() < 0.5 else 1
			if sideDice == 1:
				old_node1 = np.random.choice(range(len(degreeOutCamp1)),1,p = degreeOutCamp1)[0]
				old_node2 = np.random.choice(range(len(degreeInCamp1)),1,p = degreeInCamp1)[0]
			elif sideDice == 0:
				old_node1 = np.random.choice(range(len(degreeOutCamp2)),1,p = degreeOutCamp2)[0]
				old_node2 = np.random.choice(range(len(degreeInCamp2)),1,p = degreeInCamp2)[0]
			
			if old_node1%2 == 1: #old_node1 belongs to camp1
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1[old_node1] += 1
				sum_degreeOutCamp1 += 1.0
				degreeOutCamp1 /= sum_degreeOutCamp1
				
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2[old_node1] += polarWeight
				sum_degreeOutCamp2 += polarWeight
				degreeOutCamp2 /= sum_degreeOutCamp2
			elif old_node1%2 == 0: #old_node1 belongs to camp2
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1[old_node1] += polarWeight
				sum_degreeOutCamp1 += polarWeight
				degreeOutCamp1 /= sum_degreeOutCamp1
				
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2[old_node1] += 1
				sum_degreeOutCamp2 += 1.0
				degreeOutCamp2 /= sum_degreeOutCamp2
			
			if old_node2%2 == 1: #old_node2 belongs to camp1
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1[old_node2] += 1
				sum_degreeInCamp1 += 1.0
				degreeInCamp1 /= sum_degreeInCamp1
				
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2[old_node2] += polarWeight
				sum_degreeInCamp2 += polarWeight
				degreeInCamp2 /= sum_degreeInCamp2
			elif old_node2%2 == 0: #old_node2 belongs to camp2
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1[old_node2] += polarWeight
				sum_degreeInCamp1 += polarWeight
				degreeInCamp1 /= sum_degreeInCamp1
				
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2[old_node2] += 1
				sum_degreeInCamp2 += 1.0
				degreeInCamp2 /= sum_degreeInCamp2
				
			if old_node1 in G and old_node2 in G[old_node1]:
				G.add_edge(old_node1, old_node2, weight = G[old_node1][old_node2]['weight'])
			else:
				G.add_edge(old_node1, old_node2, weight = 1)
			
		elif selectC:
			# Add a new vertex and an edge from an old node to the new one
			G.add_node(new_node_index)
			if new_node_index%2 == 1: # new node belongs camp1
				#print('C,1')
				old_node = np.random.choice(range(len(degreeOutCamp1)),1,p = degreeOutCamp1)[0]
				
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1 = np.append(degreeInCamp1,1+delta_in)
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2 = np.append(degreeInCamp2, (1+delta_in)*polarWeight)
				
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1 = np.append(degreeOutCamp1, 0 + delta_out)
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2 = np.append(degreeOutCamp2,(0 + delta_out)*polarWeight)
				
				sum_degreeInCamp1 += 1.0 + delta_in
				sum_degreeInCamp2 += (1.0 + delta_in)*polarWeight
				degreeInCamp1 /= sum_degreeInCamp1
				degreeInCamp2 /= sum_degreeInCamp2
				
				if old_node%2 == 1: #old node belongs to camp1
					degreeOutCamp1[old_node] += 1
					degreeOutCamp2[old_node] += polarWeight
					sum_degreeOutCamp1 += delta_out + 1
					sum_degreeOutCamp2 += (delta_out + 1)*polarWeight
				elif old_node%2 == 0: #old node belongs to camp2
					degreeOutCamp1[old_node] += polarWeight
					degreeOutCamp2[old_node] += 1
					sum_degreeOutCamp1 += delta_out + polarWeight
					sum_degreeOutCamp2 += delta_out*polarWeight + 1
				
				degreeOutCamp1 /= sum_degreeOutCamp1
				degreeOutCamp2 /= sum_degreeOutCamp2
			elif new_node_index%2 == 0: # new_node belongs to camp2
				#print('C,2')
				old_node = np.random.choice(range(len(degreeOutCamp2)),1,p = degreeOutCamp2)[0]
				
				degreeInCamp1 *= sum_degreeInCamp1
				degreeInCamp1 = np.append(degreeInCamp1,(1+delta_in)*polarWeight)
				degreeInCamp2 *= sum_degreeInCamp2
				degreeInCamp2 = np.append(degreeInCamp2,1+delta_in)
				
				degreeOutCamp1 *= sum_degreeOutCamp1
				degreeOutCamp1 = np.append(degreeOutCamp1,(0 + delta_out)*polarWeight)
				degreeOutCamp2 *= sum_degreeOutCamp2
				degreeOutCamp2 = np.append(degreeOutCamp2,0 + delta_out)
				
				sum_degreeInCamp1 += (1.0 + delta_out)*polarWeight
				sum_degreeInCamp2 += 1.0 + delta_out
				degreeInCamp1 /= sum_degreeInCamp1
				degreeInCamp2 /= sum_degreeInCamp2
				
				if old_node%2 == 1: #old node belongs to camp1 
					degreeOutCamp1[old_node] += 1
					degreeOutCamp2[old_node] += polarWeight
					sum_degreeOutCamp1 += delta_out*polarWeight + 1
					sum_degreeOutCamp2 += delta_out + polarWeight
				elif old_node%2 == 0: #old node belongs to camp2
					degreeOutCamp1[old_node] += polarWeight
					degreeOutCamp2[old_node] += 1
					sum_degreeOutCamp1 += (1+delta_out)*polarWeight
					sum_degreeOutCamp2 += delta_out + 1
					
				degreeOutCamp1 /= sum_degreeOutCamp1
				degreeOutCamp2 /= sum_degreeOutCamp2
			G.add_edge(old_node,new_node_index, weight = 1)
			
			new_node_index += 1
			
		#print(np.sum(degreeInCamp1),np.sum(degreeInCamp2),np.sum(degreeOutCamp1),np.sum(degreeOutCamp2))
	nx.write_gpickle(G,'graphs/' + identifier + '.pickle')
	with open('graphs/' + identifier + '_edges.csv','w') as fw:
		fw.write('Source,Target,Weight\n')
		for u1 in G:
			for u2 in G[u1]:
				fw.write(str(u1) + ',' + str(u2) + ',' + str(G[u1][u2]['weight']) + '\n')
	with open('graphs/' + identifier + '_nodes.csv','w') as fw:
		fw.write('Id,Label,Modularity Class\n')
		for i in range(num_nodes):
			if i%2 == 0:
				fw.write(str(i) + ',0,0\n')
			else:
				fw.write(str(i) + ',1,1\n')
	return G
