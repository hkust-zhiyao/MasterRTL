# from preprocess import *
from scipy import stats
import xgboost as xgb
import copy, time, os, json
from sklearn.metrics import accuracy_score, mean_squared_error
from xgboost import XGBClassifier
import numpy as np

import pickle

def load_data_sep():

    design_name = 'TinyRocket'
    feat_dir = f'../../example/feature/'

    with open(f'{feat_dir}{design_name}_sog_vec_timing.json', 'r') as f:
        feat_timing_lst = json.load(f)
    with open(f'{feat_dir}{design_name}_sog_vec_area.json', 'r') as f:
        feat_design_lst = json.load(f)
    test_feat_lst = []
    test_feat_lst.extend(feat_design_lst)
    test_feat_lst.extend(feat_timing_lst)
    test_label_lst = []


    test_x = np.array(test_feat_lst).reshape(1, -1)
    test_y = np.array(test_label_lst)
    return test_x, test_y

def calculate_r_mape_rrse(actual, predicted):

    r, _ = stats.pearsonr(actual, predicted)
    

    mean_actual = np.mean(actual)
    numerator = np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))
    denominator = np.sqrt(np.mean((np.array(actual) - mean_actual)**2))
    rrse = numerator / denominator

    percent_errors = [(abs(actual[i] - predicted[i]) / actual[i]) * 100 for i in range(len(actual))]
    percent_errors = [min(pe, 100) for pe in percent_errors]
    mape = sum(percent_errors) / len(percent_errors)
    return {'r': r, 'mape': mape, 'rrse': rrse}



if __name__ == '__main__':

    test_eval = 'tns'
    model_name = f'../saved_model/xgboost_{test_eval}_model.json'
    
    model = xgb.XGBRegressor()
    model.load_model(model_name)
    x_test, y_test = load_data_sep()
    # if test_eval == 'wns':
    #     y_true = y_test[:, 0]
    # else:
    #     y_true = y_test[:, 1]
    y_pred = model.predict(x_test)
    print(f"Predicted {test_eval}:", y_pred)
    # metric = calculate_r_mape_rrse(y_true, y_pred)
    # print(metric)




