from DG import Graph
import json, re, os
import numpy as np
import networkx as nx

cwd = os.getcwd()


def cal_oper(g:Graph):
        g_nx = nx.DiGraph(g.graph)
        area_dict = "../../std_PPA.json"
        with open(area_dict, 'r') as f:
            std_data = json.load(f)

        all_node = g.get_all_nodes2()
        seq_set = set()
        comb_set = set()
        type_set = set()
        seq_num, comb_num, io_num, fanout_sum = 0, 0, 0, 0
        and_num, or_num, not_num, xor_num, mux_num= 0, 0, 0, 0, 0
        seq_area, comb_area, stat_pwr, dyn_pwr = 0, 0, 0, 0
        for name, node in g.node_dict.items():
            if not g_nx.has_node(name):
                continue
            type = node.type
            width = node.width
            type_set.add(type)
            # if type in ['Reg', 'Pointer', 'Partselect']:
            if type in ['Reg']:
                seq_set.add(name)
                fanout_sum += g_nx.in_degree(name)
                seq_num += width
                seq_area += std_data['area_seq']['DFF']*width
                stat_pwr += std_data['stat_pwr']['DFF']*width
                dyn_pwr += std_data['dyn_pwr']['DFF']*width
            elif type in ['Operator', 'UnaryOperator', 'Concat', 'Repeat']:
                comb_set.add(name)
                comb_num += width
                op_temp = re.findall(r'([A-Z][a-z]*)(\d+)', name)
                op = op_temp[0][0]
                if op in std_data['area_comb'].keys():
                    comb_area += std_data['area_comb'][op]*width
                    stat_pwr += std_data['stat_pwr'][op]*width
                    dyn_pwr += std_data['dyn_pwr'][op]*width
                else:
                    print(op)
                    assert False
                
                if op in ['And']:
                      and_num += 1
                elif op in ['Or']:
                      or_num += 1
                elif op in ['Ulnot', 'Unot']:
                      not_num += 1
                elif op in ['Xor']:
                      xor_num += 1
                elif op in ['Cond', 'Mux']:
                      mux_num += 1

            elif type in ['Output', 'Input', 'Inout']:
                  io_num += width
            elif type in ['Constant', 'Wire', 'Partselect', 'Pointer', 'Inout']:
                pass
            else:
                print(type)
                assert False
        #----- comb area -------
        seq_area = round(seq_area, 0)
        comb_area = round(comb_area, 0)
        total_area = seq_area+comb_area
        stat_pwr = round(stat_pwr, 0)
        dyn_pwr = round(dyn_pwr, 0)
        total_pwr = stat_pwr + dyn_pwr
        print('f0: #. DFF bits: %d\nf1: #. fanout: %d\nf2: #. IO bits: %d\nf3: #. AND: %d' %(seq_num, fanout_sum, io_num, and_num))
        print('f4: #. OR: %d\nf5: #. NOT: %d\nf6: #. XOR: %d\nf7: #. MUX: %d' %(or_num, not_num, xor_num, mux_num))
        print('f8: est. seq. area: %d\nf9: est. comb. area: %d\nf10: est. total area: %d\nf11: est. stat. pwr: %d' %(seq_area, comb_area, total_area, stat_pwr))
        print('f12: est. dyn. pwr: %d\nf13: est. total pwr: %d\n' %(dyn_pwr, total_pwr))

        ### 14 features
        feat_vec = [seq_num, fanout_sum, io_num,\
                    and_num, or_num, not_num, \
                    xor_num, mux_num, seq_area,\
                    comb_area, total_area, stat_pwr,\
                    dyn_pwr, total_pwr
                    ]

        return feat_vec


ppa_dict = "../../std_PPA.json"
with open(ppa_dict, 'r') as f:
    std_data = json.load(f)
t_data = std_data['timing']
freq = t_data['freq']
clk_unc = t_data['clk_unc']
lib_setup = t_data['lib_setup']
input_delay = t_data['input_delay']
output_delay = t_data['output_delay']
require_time = 1/freq - clk_unc - lib_setup

def cal_timing_type(delay_list, path_type):
        delay_sum = np.array(delay_list)

        if path_type == 'rr':
              input_delay_array = np.zeros(delay_sum.shape)
              output_delay_array = np.zeros(delay_sum.shape)
        elif path_type == 'ir':
              input_delay_array = np.ones(delay_sum.shape)*input_delay
              output_delay_array = np.zeros(delay_sum.shape)
        elif path_type == 'ro':
              input_delay_array = np.zeros(delay_sum.shape)
              output_delay_array = np.ones(delay_sum.shape)*output_delay
        elif path_type == 'io':
              input_delay_array = np.ones(delay_sum.shape)*input_delay
              output_delay_array = np.ones(delay_sum.shape)*output_delay

        require_time_array = np.ones(delay_sum.shape)*require_time - output_delay_array
        arrival_time_array = delay_sum + input_delay_array
        slack_array = require_time_array - arrival_time_array
        slack_array[slack_array>0] = 0
        return slack_array

def cal_timing(delay_list_all):
        slack_array_total = cal_timing_type(delay_list_all, 'rr')
        tns = np.sum(slack_array_total)
        wns = np.min(slack_array_total)

        feat_vec = [wns, tns]
        print('calculated tns:', tns)
        print('calculated wns:', wns)
        return feat_vec