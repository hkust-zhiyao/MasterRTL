from DG import Graph
import re, json
from multiprocessing import Pool
from collections import defaultdict
import networkx as nx
import numpy as np
from graph_stat import cal_timing_type

class subNode:
    def __init__(self, name, type, width:None, delay:None):
        self.name = name
        self.type = type
        if width == None:
            width = 1
        self.width = width
        self.delay = delay
    
    def update_width(self, width):
        self.width = width
    
    def __repr__(self):
        return self.name

class subGraph:
    def __init__(self, name, children, type, width=None, delay=0):
        self.graph = defaultdict(list)
        self.node_dict = {}
        self.start = name
        self.end_set = set()
        self.add_decl_node(name, type, width, delay)
        for c in children:
            self.add_edge(name, c)

    def add_decl_node(self, name, type, width=None, delay=0):
        node = subNode(name, type, width, delay)
        self.node_dict[name] = node
    
    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        self.graph[u].append(v)

def get_path_feature(path, path_delay, node_dict):
    
    path_len = len(path) ## f1
    num_mux, num_and, num_or, num_not, num_xor = 0, 0, 0, 0, 0
    for node_name in path:
        node = node_dict[node_name]
        node_type = node.type
        if node_type in ['Operator', 'Mux', 'UnaryOperator']:
            op_temp = re.findall(r'([A-Z][a-z]*)(\d+)', node.name)
            op = op_temp[0][0]
            if op in ['Mux', 'Cond']:
                num_mux += 1
            elif op in ['And']:
                num_and += 1
            elif op in ['Or']:
                num_or += 1
            elif op in ['Ulnot', 'Unot']:
                num_not += 1
            elif op in ['Xor']:
                num_xor += 1
    path_feat_vec = [path_delay, path_len, num_mux,\
                    num_and, num_or, num_not, num_xor, 0]
    path_arr = np.array(path_feat_vec)


    return path_arr

class ProcessGraph:
    def __init__(self, g:Graph):
        self.g = g

    def Graph_STA(self, rfr, design_name):
        g_nx = nx.DiGraph(self.g.graph)
        topo_sort = list(nx.topological_sort(g_nx))
        for idx, n in enumerate(topo_sort):
            if '_CK_' in n:
                starti = idx
                break
        topo_sort = topo_sort[starti:]

        start_set, end_set = set(), set()

        visited_set = set()
        for node in topo_sort:
            if '_CK_' in node:
                start_set.add(node)
                self.g.node_dict[node].AT = self.g.node_dict[node].delay
                self.g.node_dict[node].path = [node]
            elif '_Q_' in node:
                end_set.add(node)
            
            if not hasattr(self.g.node_dict[node], 'AT'):
                self.g.node_dict[node].AT = self.g.node_dict[node].delay
                self.g.node_dict[node].path = [node]
                

            for successor in g_nx.successors(node):
                visited = False if successor not in visited_set else True
                self.g.node_dict[successor].update_AT(self.g.node_dict[node].AT, self.g.node_dict[node].path, visited)
                visited_set.add(successor)
        path_dict, AT_dict, feat_vec_dict = {}, {}, {}

        for n in end_set:
            pair, path, AT = self.g.node_dict[n].finish_AT()
            path_dict[pair] = path
            feat_vec_dict[pair] = get_path_feature(path, AT, self.g.node_dict)


        if len(feat_vec_dict) == 0:
            return
        feat_vec_lst = np.array(list(feat_vec_dict.values()))
        self.path_lst = rfr.predict(feat_vec_lst)

        for idx, pair in enumerate(feat_vec_dict.keys()):
            AT_dict[pair] = self.path_lst[idx]

        sorted_AT_dict_tmp = sorted(AT_dict.items(), key=lambda x:x[1], reverse=True)
        sorted_AT_dict = dict(sorted_AT_dict_tmp)
        
        pred_slack_lst = list(sorted_AT_dict.values())
        pred_slack_lst = cal_timing_type(pred_slack_lst, 'rr')
        pred_slack_lst = list(pred_slack_lst)
        # print(len(pred_slack_lst))

        with open(f'./pred_slack_lst/{design_name}_rf.json', 'w') as f:
            json.dump(pred_slack_lst, f)
 
        L_PATH_NUM = 100
        wns_heap = {}
        wns_pair = list(sorted_AT_dict.keys())[:L_PATH_NUM]

        for p in wns_pair:
            wns_heap[p] = sorted_AT_dict[p]

        return self.path_lst, wns_heap
