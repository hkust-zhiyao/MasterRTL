import numpy as np
import pickle, json, time, re
from DG import Graph

def run_one_design(design_name, cmd, out_path):
        with open(f"../../example/feature/{design_name}_{cmd}_vec_area.json", 'r') as f:
            feat_vec = json.load(f)

        with open(f"../../example/verilog/toggle_rate/{design_name}_tc_sum_all.json", 'r') as f:
            tr_sum = json.load(f)
            feat_vec.append(tr_sum)
        
        with open(f"../../example/verilog/toggle_rate/{design_name}_tc_avr_all.json", 'r') as f:
            tr_avr = json.load(f)
            feat_vec.append(tr_avr) 

        ### ---- load the prediction of module level power 'pred_pwr' ---- ###
        pred_pwr = 0
        ######################################################################

        feat_vec.append(pred_pwr)

        print(feat_vec)
        vec_name = out_path + f'/{design_name}_{cmd}_vec_pwr.json'
        with open(vec_name, 'w') as f:
                json.dump(feat_vec, f)
             
if __name__ == '__main__':

        design_name = 'TinyRocket'
        cmd = 'sog'
        out_path = "../../example/feature"
        run_one_design(design_name, cmd, out_path)