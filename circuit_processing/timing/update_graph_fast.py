from feature_extract.area.logicGraph import *
import pickle, json, time, os, sys
from DG import Node
from tqdm import trange
import time, copy
import concurrent.futures

bench_type = 'pr'
bench_type = "timing"
design_json = f"/data/user/MatserRTL/design_{bench_type}.json"


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
            

 
def run_one_design(design_name):
        cmd = 'rtlil'
        # folder_dir = '/data/user/AST_analyzer/graph_data'
        folder_dir = "/data/user/qor_predictor/path_level/graph_data/"
        with open(f'{folder_dir}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'{folder_dir}/{design_name}_{cmd}_node_dict.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        
        g = Graph()
        g.init_graph(graph, node_dict)
        g_new, node_dict_new = graph_update(g)

        # graph_data_timing_dir = "/data/user/AST_analyzer/graph_data_timing/"
        graph_data_timing_dir = "/data/user/qor_predictor/path_level/graph_data_split/"

        with open(graph_data_timing_dir + f"{design_name}_{cmd}.pkl", 'wb') as f:
            pickle.dump(g_new, f)
        with open(graph_data_timing_dir + f"{design_name}_{cmd}_node_dict.pk", 'wb') as f:
            pickle.dump(node_dict_new, f)
        
        print(f'{design_name} Finish!')

        

def run_all(bench, design_name=None):
    
    with open(design_json, 'r') as f:
        design_data = json.load(f)
        bench_data = design_data[bench]
    for k, v in bench_data.items():
        if design_name:
                if k == design_name:
                        print('Current Design:', k)
                        run_one_design(k)
        else:
                print('Current Design:', k)
                run_one_design(k)

def run_all_parallel(bench):
      with open(design_json, 'r') as f:
            design_data = json.load(f)
            bench_data = design_data[bench]
      with Pool(20) as p:
            p.map(run_one_design, list(bench_data.keys()))
            p.close()
            p.join()
        
if __name__ == '__main__':

        cmd2 = 'rtlil'
        design_name = 'TinyRocket'
        design_name = ''
        bench_list_all1 = ['iscas' ,'itc','opencores', 'VexRiscv']
        bench_list_all2 = ['riscvcores', 'chipyard']
        bench_list_all3 = ['NVDLA']

        bench_list_all = ['iscas' ,'itc','opencores', 'VexRiscv', 'riscvcores', 'chipyard', 'NVDLA']
        bench_list_all = ['opencores', 'VexRiscv', 'riscvcores', 'chipyard', 'NVDLA']

        b1 = ['iscas']
        b2 = ['itc']
        b3 = ['opencores']
        b4 = ['VexRiscv']
        b5 = ['riscvcores']
        b6 = ['chipyard']
        b7 = ['NVDLA']

        # bench_list_all = ['NVDLA']
        # for bench in bench_list_all:
        #         run_all(bench, design_name)
                # run_all_parallel(bench)
        i = 0
        for idx in range(2501):
            d = f"path{idx}"
            if os.path.exists(f"/data/user/qor_predictor/path_level/graph_data/path{idx}_rtlil.pkl"):
                run_one_design(d)
                i += 1
        print(i)