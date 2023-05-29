from train_path_rfr import train_rfr
from logicGraph import *
import pickle, json, time, os, sys
from DG import Node
sys.path.append('/data/user/AST_analyzer')
sys.path.append('/data/user/AST_analyzer/ML_model')
sys.path.append('/data/user/AST_analyzer/ML_model/MLP_model.py')
import numpy as np
import torch
from graph_stat import cal_timing


design_json = f"/data/user/masterRTL/graph_data/design_{bench_type}.json"


 
def run_one_design(design_name):
        cmd = 'rtlil'
        folder_dir = '/data/user/AST_analyzer/graph_data_timing'
        with open(f'{folder_dir}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'{folder_dir}/node_dict_update/{design_name}_{cmd}_node_dict_init.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        graph = nx.to_dict_of_lists(graph)

        g = Graph()
        g.init_graph(graph, node_dict)
        graphProc = ProcessGraph(g)
        start_time = time.perf_counter()
        delay_list_all, wns_list = graphProc.Graph_STA(rfr, design_name)
        end_time = time.perf_counter()
        runtime = round((end_time-start_time), 2)
        runtime_dict[design_name] = {'STA':runtime}
        
        feat_timing = cal_timing(delay_list_all)
        wns_pred = feat_timing[0]
        tns_pred = feat_timing[1]

        with open ("/data/user/masterRTL/ML_model/data/label/label_ori/DC_label_timing.json", 'r') as f:
               label_dict = json.load(f)
        wns_real = label_dict[design_name]['WNS']
        tns_real = label_dict[design_name]['TNS']

        wns_pred_lst.append(wns_pred)
        wns_real_lst.append(wns_real)
        tns_pred_lst.append(tns_pred)
        tns_real_lst.append(tns_real)

        print(wns_pred, wns_real)

        # feat_dir = "/data/user/masterRTL/feature_extract/feat_data/timing_feature"
        # vec_name = feat_dir + f'/{design_name}_{cmd}_vec_graph_STA.json'
        # with open(vec_name, 'w') as f:
        #         json.dump(feat_timing, f)




        # wns_path = f"/data/user/masterRTL/feature_extract/feat_data/wns_path/{design_name}_wns.pkl"
        # # print(wns_list)
        # with open(wns_path, 'wb') as f:
        #     pickle.dump(wns_list, f)
        
        print(design_name + ' Finish!')


        

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
        global runtime_dict
        runtime_dict = {}
        global rfr
        global wns_pred_lst, wns_real_lst, tns_pred_lst, tns_real_lst
        wns_pred_lst, wns_real_lst, tns_pred_lst, tns_real_lst = [], [], [], []
        # rfr = train_rfr()
        train_num = 2000
        suffix = "w_grtl"
        with open (f'./path_model/rfr_{train_num}_{suffix}.pkl', 'rb') as f:
                rfr = pickle.load(f)

        design_name = ''

        bench_list_all = ['iscas' ,'itc','opencores', 'VexRiscv', 'riscvcores', 'chipyard', 'NVDLA']
        for bench in bench_list_all:
                run_all(bench, design_name)
                # run_all_parallel(bench)
        
        # with open ('/data/user/masterRTL/runtime_stat/runtime_dict_STA.json', 'w') as f:
        #         json.dump(runtime_dict, f)

        with open (f'./grtl_save/wns_pred_{train_num}_{suffix}.json', 'w') as f:
                json.dump(wns_pred_lst, f)
        with open (f'./grtl_save/wns_real_{train_num}_{suffix}.json', 'w') as f:
                json.dump(wns_real_lst, f)
        with open (f'./grtl_save/tns_pred_{train_num}_{suffix}.json', 'w') as f:
                json.dump(tns_pred_lst, f)
        with open (f'./grtl_save/tns_real_{train_num}_{suffix}.json', 'w') as f:
                json.dump(tns_real_lst, f)