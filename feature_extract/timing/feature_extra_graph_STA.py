from train_path_rfr import train_rfr
from logicGraph import *
import pickle, json, time, os, sys
from DG import Node
from graph_stat import cal_timing




 
def run_one_design(design_name, cmd, out_path):
        folder_dir = '../../example/timing_dag'
        with open(f'{folder_dir}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'{folder_dir}/{design_name}_{cmd}_node_dict_init.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        graph = nx.to_dict_of_lists(graph)

        g = Graph()
        g.init_graph(graph, node_dict)
        graphProc = ProcessGraph(g)
        start_time = time.perf_counter()

        ### ---- load the path-level model 'rfr' ---- ###
        # with open('/home/coguest5/MasterRTL/ML_model/saved_model/rfr_model.pkl', 'rb') as f:
        #         rfr = pickle.load(f)
        rfr = train_rfr()
        ######################################################################

        delay_list_all, wns_list = graphProc.Graph_STA(rfr, design_name)
        end_time = time.perf_counter()
        runtime = round((end_time-start_time), 2)
        
        feat_timing = cal_timing(delay_list_all)
        wns_pred = feat_timing[0]
        tns_pred = feat_timing[1]

        with open(f'{out_path}/{design_name}_{cmd}_vec_timing.json', 'w') as f:
                json.dump(feat_timing, f)


        
        print(design_name + ' Finish!')



        
if __name__ == '__main__':
        design_name = 'TinyRocket'
        cmd = 'sog'
        out_path = "../../example/feature"
        run_one_design(design_name, cmd, out_path)