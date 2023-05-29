import numpy as np
import pickle, json, time, re
from DG import Graph
import networkx as nx
from multiprocessing import Pool

bench_type = 'area_pwr'
design_json = f"/data/wenjifang/masterRTL/graph_data/design_{bench_type}.json"

def run_one_design(design_name):
        with open(f"/data/wenjifang/qor_predictor/dyn_pwr_ML/design_level/feat_all/{design_name}.json", 'r') as f:
            feat_vec = json.load(f)
        #feat_vec = [0: seq_num, 1: io_num, 2: comb_num, 3: total_num, 4: io_num/total_num, 
        #           5: and_num, 6: or_num, 7: not_num, 8: xor_num, 9: mux_num, 
        #           10: tr_sum_prop, 11: tr_sum/tr_num_prop, 12:stat pwr
        #           13: tr_sum_DC, 14: tr_sum/tr_num_DC
        #           15: pred_dyn_pwr 16:pred_stat_pwr
        # ]

        with open(f"/data/wenjifang/qor_predictor/feature_extraction/power_feature/data/toggle_rate/{design_name}_tc_sum_all.json", 'r') as f:
            tr_sum = json.load(f)
            feat_vec.append(tr_sum)
        
        with open(f"/data/wenjifang/qor_predictor/feature_extraction/power_feature/data/toggle_rate/{design_name}_tc_avr_all.json", 'r') as f:
            tr_avr = json.load(f)
            feat_vec.append(tr_avr) 

        
        ret_all_dict_path = '/data/wenjifang/qor_predictor/module_level/ML_model/output/all_dict_w_pred.pkl'
        with open(ret_all_dict_path, 'rb') as f:
            all_dict = pickle.load(f)
        
        for design, design_dict in all_dict.copy().items():
            if design != design_name:
                continue
            pred_pwr = 0
            for module_name, module_dict in design_dict.copy().items():
                pred_pwr += module_dict['pred']
        feat_vec.append(pred_pwr)

        feat_dir = "/data/wenjifang/masterRTL/feature_extract/feat_data/graph_stat"
        vec_name = feat_dir + f'/{design_name}_{cmd}_vec_graph_stat.json'
        with open(vec_name, 'r') as f:
                graph_stat = json.load(f)
        feat_vec.append(graph_stat[11])
        
 

        feat_dir = "/data/wenjifang/masterRTL/feature_extract/feat_data/pwr_feature"
        vec_name = feat_dir + f'/{design_name}_{cmd}_vec_pwr.json'
        with open(vec_name, 'w') as f:
                json.dump(feat_vec, f)
        



def run_all(bench, design_name=None):
    
    with open(design_json, 'r') as f:
        design_data = json.load(f   )
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

        global feat_all, label_all, idx
        idx = 0
        feat_all, label_all = [], []
        cmd = 'rtlil'
        design_name = ''
        # design_name = ''
        bench_list_all = ['iscas' ,'itc','opencores', 'VexRiscv', 'riscvcores', 'chipyard','NVDLA']
        # bench_list_all = ['chipyard','NVDLA']
        for bench in bench_list_all:
                run_all(bench, design_name)
                # run_all_parallel(bench)
