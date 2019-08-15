from collections import defaultdict
import operator
import numpy as np
import random
eps = np.finfo(float).eps
def getCentralUsers(G,userList,ratio):
    central_users = {}
    groups = defaultdict(list)
    for u in userList:
        groups[userList[u]].append(u)
    for group in groups:
        degs = G.in_degree(groups[group])
        degs = sorted(degs.iteritems(), key = operator.itemgetter(1), reverse = True)
        central_users.update({c:group for c,d in degs[0:int(len(degs)*ratio)]})
    return central_users


def randomWalkPolarity(G, userList, iterC, walkStep):

    central_users = getCentralUsers(G,userList,0.01)

    nodeIndices = {} #screen_name -> adjacency matrix row index
    nodes = {} #adj.matrix row index-> screen_name
    index = 0
    for node in userList:
        nodeIndices[node] = index
        nodes[index] = node
        index += 1

    #iterC = 1000
    inner = 0.0
    cross = 0.0
    ll = 0.0
    lr = 0.0
    rl = 0.0
    rr = 0.0
    #print('Traversal Starts...')
    while iterC > 0:
        # 1- Choose random node
        start_node_ind = random.randint(0, len(nodeIndices)-1)
        start_label = userList[nodes[start_node_ind]]
        visited = {}
        node = nodes[start_node_ind]
        walkStepIt = walkStep
        while walkStepIt > 0:
            neighbors = G.neighbors(node)
            if len(neighbors) == 0:
                walkStepIt = 0 # walk failed
                break
            i = random.randint(0,len(neighbors)-1)
            node = neighbors[i]
            if node in central_users:
                #print('\tHit the center...')
                break
            walkStepIt -= 1
        if walkStepIt > 0:
            if start_label == 'left' and userList[node] == 'left':
                ll += 1
                inner += 1
            elif start_label == 'left' and userList[node] == 'right':
                lr += 1
                cross += 1
            elif start_label == 'right' and userList[node] == 'left':
                rl += 1
                cross += 1
            elif start_label == 'right' and userList[node] == 'right':
                rr += 1
                inner += 1

            iterC -= 1
    e1 = ll*1.0/(ll+rl+eps)
    e2 = lr*1.0/(lr+rr+eps)
    e3 = rl*1.0/(ll+rl+eps)
    e4 = rr*1.0/(lr+rr+eps)

    involvement = 0
    rwc = e1*e4 - e2*e3
    polarization = float(inner)/float(cross+inner+eps)
    
    return (rwc,polarization)
