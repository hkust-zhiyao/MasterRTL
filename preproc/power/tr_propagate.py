
from logicGraph import *
import pickle, json, time
from DG import Node
import copy
import networkx as nx

def propagate_node_tr(name, node:Node, g:nx.DiGraph, node_dict):
        if not g.has_node(name):
            t1 = 0.5
            tc = 0.2
            node.add_tr(tc)
            node.add_t1(t1)
            node_dict[name] = node
            return tc, t1, node_dict
        # tc = node.tr
        if node.type in ['Operator', 'UnaryOperator']:
                fanin_lst = list(g.successors(name))

                switch_prop_lst = []
                for fanin_node in fanin_lst:
                    fanin_node = re.sub(r'_CK_$|_Q_$', '', fanin_node)
                    switch_prop_lst.append(node_dict[fanin_node].tr)
                op_temp = re.findall(r'([A-Z][a-z]*)(\d+)', name)
                op = op_temp[0][0]
                if op == 'Concat':
                    t1 = 0
                    tc = 0
                elif op in ['Mux', 'Cond']:
                    if len(switch_prop_lst) >3:
                        switch_prop_lst = switch_prop_lst[:3]
                    assert len(switch_prop_lst) in [2, 3]
                    if len(switch_prop_lst) == 2:
                        t1 = switch_prop_lst[0]*switch_prop_lst[1]
                    else:
                        t1 = switch_prop_lst[0]*switch_prop_lst[1] + (1-switch_prop_lst[0])*switch_prop_lst[2]
                    tc = t1*(1-t1)
                elif op in ['And']:
                    t1 = 1
                    for i in switch_prop_lst:
                        t1 *= i
                    tc = t1*(1-t1)
                elif op in ['Or']:
                    t1 = 1
                    for i in switch_prop_lst:
                        t1 *= (1-i)
                    tc = t1*(1-t1)
                elif op in ['Ulnot', 'Unot']:
                    if len(switch_prop_lst) >1:
                        switch_prop_lst = [switch_prop_lst[0]]
                    assert len(switch_prop_lst) == 1
                    t1 = 1 - switch_prop_lst[0]
                    tc = t1*(1-t1)
                elif op in ['Xor']:
                    assert len(switch_prop_lst) == 2
                    t1 = switch_prop_lst[0]*(1-switch_prop_lst[1]) + switch_prop_lst[1]*(1-switch_prop_lst[0])
                    tc = t1*(1-t1)
        elif node.type == 'Constant':
            t1 = 0
            tc = 0
        elif node.type in ['Pointer', 'Reg', 'Input', 'Output', 'Partselect', 'Concat','Wire']:
            t1 = 0.08
            tc = 0.08
        else:
            print(name)
            print(node.type)
            assert False
        if tc < 0:
            tc = 0
        node.add_tr(tc)
        node.add_t1(t1)
        node_dict[name] = node
        return tc, t1, node_dict

def update_node_dict(g:Graph):
    node_dict_ret =  copy.copy(g.node_dict)
    g_nx = nx.DiGraph(g.graph)
    topo_sort = list(nx.topological_sort(g_nx))
    topo_sort.reverse()
    for n in topo_sort:
        n = re.sub(r'_CK_$|_Q_$', '', n)
        node = g.node_dict[n]
        if not node.tr:
            tr, t1, node_dict_ret = propagate_node_tr(n, node, g_nx, node_dict_ret)

    return node_dict_ret

def run_one_design(design_name, module_name, out_path):
        print('Current Design:', design_name)
        print('Current Module:', module_name)   
        cmd = 'sog'
        global i
        folder_dir = f'../../example/module/{design_name}/'
        with open(f'{folder_dir}/{module_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        folder_dir = f'../../example/module/{design_name}_init_tr/'
        with open(f'{folder_dir}/{module_name}_{cmd}_node_dict_tr.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        graph = nx.to_dict_of_lists(graph)

        g = Graph()
        g.init_graph(graph, node_dict)
        start_time = time.perf_counter()
        node_dict_new = update_node_dict(g)
        end_time = time.perf_counter()
        rt = round((end_time-start_time), 2)
        global runtime
        runtime = max(rt, runtime)
        
        suffix = 'propagated'

 
        dir_name = f'{out_path}/{module_name}_{cmd}_node_dict_{suffix}.pkl'
        with open(dir_name, 'wb') as f:
                pickle.dump(node_dict_new, f)
        



def run_all_hier(bench, out_path):
    
    design_hier_json = "./design_hier.json"
    with open(design_hier_json, 'r') as f:
        design_hier_data = json.load(f)
        bench_data = design_hier_data[bench]
    for design in bench_data:
        k = list(design.keys())[0]
        m_dict = design[k]
        m_lst = list(m_dict.keys())
        global runtime
        runtime = 0
        for m in m_lst:
            run_one_design(k,m, out_path)

        
if __name__ == '__main__':
        global i, module_dict
        i = 0
        module_dict = defaultdict(list)
        bench_list_all = ['chipyard']

        out_path = "../../example/power_dag"

        for bench in bench_list_all:
            run_all_hier(bench, out_path)

