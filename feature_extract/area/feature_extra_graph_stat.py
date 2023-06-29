from logicGraph import *
import pickle, json, time, os, sys
from DG import Node
from circuit_processing.area.graph_stat import cal_oper
import numpy as np
import time


design_json = f"/data/user/masterRTL/graph_data/design_{bench_type}.json"

 
def run_one_design(design_name):
        print('Current Design:', design_name)
        cmd = 'rtlil'
        folder_dir = '/data/user/AST_analyzer/graph_data'
        with open(f'{folder_dir}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'{folder_dir}/{design_name}_{cmd}_node_dict.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        g = Graph()
        g.init_graph(graph, node_dict)


        ## 2. estimation feature
        start_time = time.perf_counter()
        feat_vec = cal_oper(g)
        end_time = time.perf_counter()
        feat_dir = "/data/user/masterRTL/feature_extract/feat_data/graph_stat"
        vec_name = feat_dir + f'/{design_name}_{cmd}_vec_graph_stat.json'
        runtime = round((end_time-start_time), 2)
        runtime_dict[design_name] = {'graph_stat':runtime}
        with open(vec_name, 'w') as f:
                json.dump(feat_vec, f)



def run_all(bench, design_name=None):
    
    with open(design_json, 'r') as f:
        design_data = json.load(f)
        bench_data = design_data[bench]
    for k, v in bench_data.items():
        if design_name:
                if k == design_name:
                        run_one_design(k)
        else:
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
        global runtime_dict
        runtime_dict = {}

        cmd = 'rtlil'
        design_name = ''
        bench_list_all = ['iscas' ,'itc','opencores', 'VexRiscv', 'riscvcores', 'chipyard','NVDLA']
        for bench in bench_list_all:
                run_all(bench, design_name)
                # run_all_parallel(bench)
        
        print(runtime_dict)

        with open ('/data/user/masterRTL/runtime_stat/runtime_dict_graph_stat.json', 'w') as f:
                json.dump(runtime_dict, f)