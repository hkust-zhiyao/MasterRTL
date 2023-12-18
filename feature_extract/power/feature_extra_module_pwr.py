import torch
import numpy as np
import pickle, json, time, re, sys, os
from DG import Graph, Node
import networkx as nx


def get_node_pwr(name, node:Node, g:nx.DiGraph, node_dict):
        fanout = g.in_degree(name)
        if not node.tr:
            node.tr = 0.2

        if node.type in ['Reg']:
            type_weight = 1
        elif node.type in ['Pointer', 'Partselect']:
            if g.node_dict[node.father].type in ['Reg']:
                type_weight = 1
        elif node.type in ['Operator', 'Mux', 'UnaryOperator']:
            op_temp = re.findall(r'([A-Z][a-z]*)(\d+)', name)
            op = op_temp[0][0]
            if op in ['Mux', 'Cond']:
                type_weight = 0.84
            elif op in ['And']:
                type_weight = 1
            elif op in ['Or']:
                type_weight = 1
            elif op in ['Ulnot', 'Unot']:
                type_weight = 0.58
            elif op in ['Xor']:
                type_weight = 0.79
        else:
             print(node.type)
             assert False
        
        if fanout > 20:
            fanout = 20
        elif fanout == 0:
            fanout = 1
        
        pred_dyn_pwr = node.tr*fanout*type_weight

        pred_dyn_pwr2 = node.tr*fanout
        
        return pred_dyn_pwr, pred_dyn_pwr2, fanout

def cal_oper_pwr(g:Graph):
        num_node = 0
        tr_sum = 0
        tr_io_sum = 0
        g_nx = nx.DiGraph(g.graph)
        pred_pwr1, pred_pwr2, fanout_sum = 0, 0, 0
        seq_num = 0
        comb_num = 0
        io_num = 0
        and_num, or_num, not_num, xor_num, mux_num= 0, 0, 0, 0, 0
        for name, node in g.node_dict.items():
            node_type = node.type
            width = node.width
            if not g_nx.has_node(name):
                continue
            if node_type in ['Reg']:
                seq_num += width
            elif node_type in ['Operator', 'UnaryOperator', 'Concat', 'Repeat']:
                op_temp = re.findall(r'([A-Z][a-z]*)(\d+)', name)
                op = op_temp[0][0]
                if op in ['And']:
                      and_num += 1
                      comb_num += 1
                elif op in ['Or']:
                      or_num += 1
                      comb_num += 1
                elif op in ['Ulnot', 'Unot']:
                      not_num += 1
                      comb_num += 1
                elif op in ['Xor']:
                      xor_num += 1
                      comb_num += 1
                elif op in ['Cond', 'Mux']:
                      mux_num += 1
                      comb_num += 1
            elif node_type in ['Output', 'Input', 'Inout']:
                  io_num += width
        for name, node in g.node_dict.items():
            if not g_nx.has_node(name):
                continue
            elif node.type in ['Wire', 'Constant', 'Concat']:
                continue
            elif node.type in ['Input', 'Output', 'Inout']:
                if not node.tr:
                    node.tr = 0.2
                tr_io_sum += node.tr
            elif node.type in ['Pointer', 'Partselect']:
                if node.father not in g.node_dict:
                    continue
                elif g.node_dict[node.father].type in ['Wire']:
                    continue
                elif g.node_dict[node.father].type in ['Input', 'Output', 'Inout']:
                    if not node.tr:
                        node.tr = 0.2
                    tr_io_sum += node.tr
            else:
                num_node += 1
                if not node.tr:
                    node.tr = 0.2
                tr_sum += node.tr
                pred_node_pwr, pred_node_pwr2, fanout = get_node_pwr(name, node, g_nx, g.node_dict)
                pred_pwr1 += pred_node_pwr
                pred_pwr2 += pred_node_pwr2
                fanout_sum += fanout
        total_cell_num = seq_num + comb_num + io_num
        if total_cell_num == 0:
            total_cell_num = 1 
        if num_node == 0:
            num_node = 1
        ret_vec = [pred_pwr1, pred_pwr2, fanout_sum, \
                    io_num, seq_num, comb_num, total_cell_num, io_num/total_cell_num,\
                    and_num, or_num, not_num, xor_num, mux_num, \
                    tr_io_sum, tr_sum, tr_sum/num_node]
        print(ret_vec)

        return ret_vec
        
def run_one_design(design_name, module_name, out_path):
        cmd = 'sog'

        folder_dir = f'../../example/module/{design_name}/'
        with open(f'{folder_dir}/{module_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        folder_dir = f'../../example/power_dag/'
        with open(f'{folder_dir}/{module_name}_{cmd}_node_dict_propagated.pkl', 'rb') as f:
                node_dict = pickle.load(f)

        g = Graph()
        g.init_graph(graph, node_dict)
        feat_vec = cal_oper_pwr(g)
        vec_name = out_path + f'/{design_name}_{cmd}_vec_module_pwr.json'
        with open(vec_name, 'w') as f:
                json.dump(feat_vec, f)



def run_all_hier(bench, design_name, out_path):
    
    design_hier_json = "../../example/verilog/design_hier.json"
    with open(design_hier_json, 'r') as f:
        design_hier_data = json.load(f)
        bench_data = design_hier_data[bench]
    for design in bench_data:
        k = list(design.keys())[0]
        k = design_name
        m_dict = design[k]
        m_lst = list(m_dict.keys())
        global design_dict
        design_dict = {}

        for m in m_lst:
            run_one_design(k,m,out_path)

if __name__ == '__main__':
        out_path = "../../example/feature"
        bench_list_all = ['chipyard']
        for bench in bench_list_all:
            run_all_hier(bench, 'TinyRocket', out_path)
        