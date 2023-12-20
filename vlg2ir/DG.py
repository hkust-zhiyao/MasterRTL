
from collections import defaultdict
from multiprocessing import Pool
import sys, re, os
import numpy as np
import pickle
sys.setrecursionlimit(10000)

class Node:
    def __init__(self, name, type, width:None, father:None):
        self.name = name
        self.type = type
        self.width = width
        self.father = father
        self.path = []
        self.tr = None
        self.t1 = 0.5
    
    def update_width(self, width):
        self.width = width
    
    def update_delay(self, delay):
        self.delay = delay
        
    def update_fanout(self, fanout):
        self.fanout = fanout
    
    def update_feature(self, feat):
        self.feat = feat
    
    def update_AT(self, AT_delay, path, visited=False):
        if visited:
            # self.AT = max(self.AT-self.delay, AT_delay) + self.delay
            if self.AT-self.delay < AT_delay:
                self.AT = AT_delay
                self.path = path

        else:
            self.AT = AT_delay + self.delay
            path_copy = path.copy()
            path_copy.append(self.name)
            self.path = path_copy
    
    def update_AT_transformer(self, AT_delay, path, fanout_num,visited=False):
        if visited:
            # self.AT = max(self.AT-self.delay, AT_delay) + self.delay
            if self.AT-self.delay < AT_delay:
                self.AT = AT_delay
                self.path = path

        else:
            self.AT = AT_delay + self.delay
            path_copy = path.copy()
            path_copy.append(self.name)
            self.path = path_copy

    def finish_AT(self):
        if self.path[-1] != self.name:
            self.path.append(self.name)
            self.AT += self.delay
        p_s = re.sub(r'_CK_$', '', self.path[-1])
        p_s = re.sub(r'_Q_$', '', p_s)
        p_e = re.sub(r'_CK_$', '', self.path[0])
        p_e = re.sub(r'_Q_$', '', p_e)
        pair = (p_s, p_e)

        return pair, self.path, self.AT



    
    def add_tr(self, tr):
        self.tr = tr
    
    def add_t1(self, t1):
        self.t1 = t1
    
    def __repr__(self):
        return self.name

class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.node_dict = {}

    def init_graph(self, graph, node_dict):
        self.graph = graph
        self.node_dict = node_dict

    def add_decl_node(self, name, type, width=None, father=None):
        node = Node(name, type, width, father)
        self.node_dict[name] = node

    def graph2pkl(self, design_name, cmd, folder_dir):
        graph_name = folder_dir + f'{design_name}_{cmd}.pkl'
        node_dict_name = folder_dir + f'{design_name}_{cmd}_node_dict.pkl'
        with open(graph_name, 'wb') as f:
            pickle.dump(self.graph, f)
        with open(node_dict_name, 'wb') as f:
            pickle.dump(self.node_dict, f)
    

        

    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        self.graph[u].append(v)
    
    def remove_node(self, u):
        if u in self.graph.copy():
            del self.graph[u]
    
    def get_neighbors(self, u):
        return self.graph[u]
    
    def get_all_nodes(self):
        return self.graph.keys()
    
    def get_all_nodes2(self):
        all_nodes = set()
        for key, val_list in self.graph.items():
            all_nodes.add(key)
            for var in val_list:
                all_nodes.add(var)
        return all_nodes

    def load_node_dict(self, node_dict):
        self.node_dict = node_dict
    
    def cal_node_width(self):
        print('----- Calculating Operator Width -----')
        self.nowidth_set = set()
        
        for name, node in self.node_dict.items():
            if not node.width:
                self.nowidth_set.add(name)

        while(len(self.nowidth_set) != 0):
            ll_pre = len(self.nowidth_set)
            for n in self.nowidth_set.copy():
                # print(n)
                # assert n in self.graph.keys()
                if n in self.graph.keys():
                    neighbor = self.graph[n]
                    width = self.get_max_neighbor_wdith(neighbor)
                    self.node_dict[n].update_width(width)
                    if width:
                        self.nowidth_set.remove(n)
            ll_post = len(self.nowidth_set)
        #     if ll_pre == ll_post:
        #         break
        # print(ll_post)
        # print(self.nowidth_set)

    def get_max_neighbor_wdith(self, neighbor):
        width_list = []
        for n in neighbor:
            width_node = self.node_dict.get(n)
            if not width_node:
                return width_node
            else:
                width = width_node.width
                width_list.append(width)
        assert len(neighbor) == len(width_list)
        width = max(width_list)
        return width
    
    def get_stat(self):
        all_node = self.get_all_nodes2()
        self.seq_set = set()
        self.wire_set = set()
        self.comb_set = set()
        self.in_set = set()
        self.out_set = set()
        type_set = set()
        seq_num = 0
        comb_num = 0
        for name, node in self.node_dict.items():
            ntype = node.type
            if ntype == 'Reg':
                self.seq_set.add(name)
            elif ntype == 'Wire':
                self.wire_set.add(name)
            elif ntype in ['Operator', 'UnaryOperator', 'Concat', 'Repeat']:
                self.comb_set.add(name)
            elif ntype in ['Input']:
                self.in_set.add(name)
            elif ntype in ['Output']:
                self.in_set.add(name)

        for name, node in self.node_dict.items():
            father = node.father
            if father:
                if self.node_dict[father].type == 'Reg':
                    self.seq_set.add(name)
                elif self.node_dict[father].type == 'Wire':
                    self.wire_set.add(name)
                elif self.node_dict[father].type == 'Input':
                    self.in_set.add(name)
                elif self.node_dict[father].type == 'Output':
                    self.out_set.add(name)           
    
    def show_graph(self):
        self.get_stat()
        print('----- Writting Graph Visialization File -----')
        outfile_path = "../img/"
        outfile = outfile_path+"AST_graph.dot"
        top_name = 'test'
        node_set = self.get_all_nodes2()
        pair_set = set()
        for vertice in self.graph.keys():
            node_set.add(vertice)
            val_list = self.get_neighbors(vertice)
            for val in val_list:
                if val:
                    if vertice:
                        val = re.sub(r'\.|\[|\]|\\', r'_', val)
                        vertice = re.sub(r'\.|\[|\]|\\', r'_', vertice)
                        pair = '{0} -> {1}'.format(vertice, val)
                        pair_set.add(pair)

        with open (outfile, 'w') as f:
            line = "digraph {0} ".format(top_name)
            line = line + "{\n"
            f.write(line)
            reg_set = set()
            for node in node_set:
                if not node:
                    break
                n = self.node_dict[node]
                ntype = n.type
                node1 = re.sub(r'\.|\[|\]|\\', r'_', node)
                if node in self.seq_set:
                    line = "    {0} [style=filled, color=lightblue];\n".format(node1)
                elif node in self.wire_set:
                    line = "    {0} [style=filled, color=red];\n".format(node1)
                elif node in self.in_set:
                    line = "    {0} [style=filled, color=black];\n".format(node1)
                elif node in self.out_set:
                    line = "    {0} [style=filled, color=green];\n".format(node1)
                elif ntype == 'Constant':
                    line = "    {0} [style=filled, color=grey];\n".format(node1)
                elif node in self.comb_set:
                    line = "    {0} [style=filled, color=pink];\n".format(node1)

                else:
                    line = "    {0};\n".format(node1)
                f.write(line)
            for pair in pair_set:
                line = "    {0};\n".format(pair)
                f.write(line)
            
            f.write("}\n")
        
        print('Finish!\n')




                

