from logicGraph import *
import pickle, json
from DG import Node
from graph_stat import cal_oper


 
def run_one_design(design_name, cmd, out_path):
        print('Current Design:', design_name)
        folder_dir = f'../../example/{cmd}'
        with open(f'{folder_dir}/{design_name}_{cmd}.pkl', 'rb') as f:
                graph = pickle.load(f)
        with open(f'{folder_dir}/{design_name}_{cmd}_node_dict.pkl', 'rb') as f:
                node_dict = pickle.load(f)
        g = Graph()
        g.init_graph(graph, node_dict)
        feat_vec = cal_oper(g)
        vec_name = out_path + f'/{design_name}_{cmd}_vec_area.json'
        with open(vec_name, 'w') as f:
                json.dump(feat_vec, f)



        
if __name__ == '__main__':
        design_name = 'TinyRocket'
        cmd = 'sog'
        out_path = "../../example/feature"
        run_one_design(design_name, cmd, out_path)
