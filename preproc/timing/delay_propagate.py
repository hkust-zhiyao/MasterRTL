from logicGraph import *
import pickle, json, time, os, sys
from DG import Node
from tqdm import trange
import time, copy
import concurrent.futures


def node_split(name, g_nx:nx.DiGraph):
    pred_nodes = g_nx.predecessors(name)
    add_pred_lst = []
    for n in pred_nodes:
        add_pred_lst.append((n, name + '_Q_'))
    g_nx.add_edges_from(add_pred_lst)
    succ_nodes_lst = list(g_nx.successors(name))
    add_succ_lst = []
    for n in succ_nodes_lst:
        add_succ_lst.append((name + '_CK_', n))
    g_nx.add_edges_from(add_succ_lst)
    g_nx.remove_node(name)
    return g_nx


def graph_update(g:Graph):
        g_nx_tmp = nx.DiGraph(g.graph)
        g_nx = nx.DiGraph(g.graph)
        node_dict = g.node_dict
        ret_node_dict = copy.deepcopy(node_dict)
        

        split_node_dict = {}
        for name, node in node_dict.items():
            if node.type in ['Reg', 'Input', 'Output']:
                if g_nx_tmp.has_node(name):
                    split_node_dict[name] = node
            elif node.type in ['Pointer', 'Partselect']:
                if node_dict[node.father].type in ['Reg', 'Input', 'Output']:
                    if g_nx_tmp.has_node(name):
                        split_node_dict[name] = node

        for name, node in split_node_dict.items():
            if node.father:
                f_ck = node.father+"_CK_"
                f_q = node.father+"_Q_"
            else:
                f_ck = node.father
                f_q = node.father
            ret_node_dict[name + '_CK_'] = Node(name + '_CK_', node.type, node.width, f_ck)
            ret_node_dict[name + '_Q_'] = Node(name + '_Q_', node.type, node.width, f_q)
            g_nx = node_split(name, g_nx)
        
        print(nx.is_directed_acyclic_graph(g_nx))
        assert nx.is_directed_acyclic_graph(g_nx)
        return g_nx, ret_node_dict
            

 
def run_one_design(design_name, cmd, out_path):
        with open(f'../../example/{cmd}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'../../example/{cmd}/{design_name}_{cmd}_node_dict.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        
        g = Graph()
        g.init_graph(graph, node_dict)
        g_new, node_dict_new = graph_update(g)

        with open(out_path + f"{design_name}_{cmd}.pkl", 'wb') as f:
            pickle.dump(g_new, f)
        with open(out_path + f"{design_name}_{cmd}_node_dict.pkl", 'wb') as f:
            pickle.dump(node_dict_new, f)
        
        print(f'{design_name} Finish!')

        

        
if __name__ == '__main__':


        design_name = 'TinyRocket'
        cmd = 'sog'
        out_path = '../../example/timing_dag/'
        run_one_design(design_name, cmd, out_path)
