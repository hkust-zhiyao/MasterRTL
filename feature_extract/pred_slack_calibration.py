import pickle, json, re, os, sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


design_json = f"/data/user/masterRTL/graph_data/design_{bench_type}.json"


def get_wns_median_based_on_scale(pred_lst, seq_num):
    seq_num = seq_num/1000 ### k
    sorted_pred_lst = sorted(pred_lst, reverse=True)
    # print(sorted_pred_lst)
    # exit()
    if seq_num <= 3:
        idx = round(len(sorted_pred_lst)*0.1)
    elif 3< seq_num <= 5:
        idx = round(len(sorted_pred_lst)*0.5)
    elif seq_num > 5:
        idx = round(len(sorted_pred_lst)*0.9)
    ret_wns = sorted_pred_lst[idx]
    print('Pred Final WNS: ',ret_wns)
    return ret_wns

def get_mul_wns(pred_lst):
    sorted_pred_lst = sorted(pred_lst, reverse=True)

    idx = round(len(sorted_pred_lst)*0.1)
    ret_wns1 = sorted_pred_lst[idx]
    idx = round(len(sorted_pred_lst)*0.5)
    ret_wns2 = sorted_pred_lst[idx]
    idx = round(len(sorted_pred_lst)*0.9)
    ret_wns3 = sorted_pred_lst[idx]
    ret_lst = [ret_wns1, ret_wns2, ret_wns3]
    return ret_lst
        
def get_seq_num(node_dict):
    seq_num, comb_num, total_num = 0, 0, 0
    for name, node in node_dict.items():
        type = node.type
        width = node.width
        if type in ['Reg']:
            seq_num += width
        elif type in ['Operator', 'UnaryOperator', 'Concat', 'Repeat']:
            comb_num += width
    total_num = seq_num + comb_num
    return seq_num, total_num

def get_dc_lst(design_name,vec_len):
    slack_lst = []
    dc_rpt_dir = "/data/user/AST_analyzer/PPA_data/timing_rpt_DC"
    with open (f"{dc_rpt_dir}/{design_name}.rpt", 'r') as f:
          lines = f.readlines()
    for line in lines:
          slk = re.findall(r'(\s*)slack(\s*)\((\w+)\)(\s*)(.*)', line, re.IGNORECASE)
          slk2 = re.findall(r'(\s*)slack(\s*)\(VIOLATED: increase significant digits\)(\s*)(.*)', line, re.IGNORECASE)
          if 'slack' in line:
            if slk:
                    slack = float(slk[0][-1])
                    slack_lst.append(slack)
            elif slk2:
                    slack = float(slk2[0][-1])
                    slack_lst.append(slack)
            else:
                  print(line)

    ret_lst = slack_lst[:vec_len]
    return ret_lst

# def draw_fig(dc_lst, pred_lst_rf, pred_lst_trans,design_name):
#     plt.clf()
#     plt.hist(dc_lst, alpha = 1, label='DC')
#     plt.hist(pred_lst_rf, alpha = 0.4, label='Random Forest')
#     plt.hist(pred_lst_trans, alpha = 0.4, label='Transformer')
#     plt.legend(loc='upper left')
#     plt.savefig(f"/data/user/AST_analyzer/histogram/fig/{design_name}.png", dpi=300)
    
    
    

def run_one_design(design_name):
    cmd = 'rtlil'
    folder_dir = '/data/user/AST_analyzer/graph_data'
    with open(f'{folder_dir}/node_dict_update/{design_name}_{cmd}_node_dict_init.pkl', 'rb') as f:
            node_dict = pickle.load(f)
    seq_num, total_num = get_seq_num(node_dict)
    print(seq_num)

    global max_seq, min_seq
    max_seq = max(seq_num, max_seq)
    min_seq = min(seq_num, min_seq)


    vec_len = seq_num*0.02
    if vec_len>1000:
        vec_len = 1000
    elif vec_len < 10:
        vec_len = 100
    else:
        vec_len = round(vec_len)

    with open(f'/data/user/qor_predictor/ML_model/timing/data/pred_slack_lst/{design_name}_rf.json', 'r') as f:
        pred_slack_lst_rf = json.load(f)


    vec_len = min([vec_len, len(pred_slack_lst_rf)])
    dc_slack_lst = get_dc_lst(design_name, vec_len)
    pred_slack_lst_rf = pred_slack_lst_rf[:vec_len]
    



    print('Real WNS: ', max(dc_slack_lst))
    print('Pred Median WNS: ',np.median(pred_slack_lst_rf))
    dc_wns = min(dc_slack_lst)
    # pred_median_rf = np.median(pred_slack_lst_rf)
    pred_median_rf = get_wns_median_based_on_scale(pred_slack_lst_rf, seq_num)
    pred_mean_rf = np.mean(pred_slack_lst_rf)
    save_lst = [dc_wns, pred_median_rf, pred_mean_rf]
    save_list_all.append(save_lst)
    

    # draw_fig(dc_slack_lst, pred_slack_lst_rf, design_name)

    with open(f"/data/user/qor_predictor/ML_model/timing/data/wns_calibrated/{design_name}_rf.json", 'w') as f:
         json.dump([pred_median_rf], f)

    mul_wns_lst = get_mul_wns(pred_slack_lst_rf)
    with open(f"/data/user/qor_predictor/ML_model/timing/data/wns_calibrated/{design_name}_rf_mul.json", 'w') as f:
         json.dump(mul_wns_lst, f)





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


if __name__ == '__main__':
        global max_seq, min_seq, save_list_all
        save_list_all = []
        max_seq = 0
        min_seq = 1000000000000
        design_name = ''
        # design_name = ''
        bench_list_all = ['iscas','itc','opencores', 'VexRiscv', 'riscvcores', 'chipyard','NVDLA', 'NaxRiscv']
        for bench in bench_list_all:
                run_all(bench, design_name)

        with open (f"/data/user/qor_predictor/ML_model/timing/data/save_lst_{bench_type}_seq_200.json", 'w') as f:
            json.dump(save_list_all, f)