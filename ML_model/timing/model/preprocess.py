import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json, pickle
from scipy.stats import stats


bench_type = "timing"
feat_type = "feat_timing"



def load_data():
    data_dir = "/data/user/masterRTL/ML_model/data"
    dc_label_data = f'{data_dir}/label/dc_label_{bench_type}.json'
    feat_data = f'{data_dir}/feature/{feat_type}_{bench_type}.json'
    # feat_data = f'/data/user/qor_predictor/ML_model/data/feature/feat_timing_mul_timing_70.json'
    with open(dc_label_data, 'r') as f:
        dc_data_dict = json.load(f)
    df1 = pd.DataFrame(dc_data_dict)
    df1 = df1.T
    
    with open(feat_data, 'r') as f:
        feat_dict = json.load(f)
    

    df2 = pd.DataFrame(feat_dict)
    df2 = df2.T
    print(df2.shape)
    print(type(df2))

    print(df2)
    # df2.drop(df2.columns[[8,9,10,11,12,13,14,17]], axis=1, inplace=True) ### for wns (#.xor + 3 wns)
    # df2.drop(df2.columns[[8,9,10,11,12,13,14,15,16]], axis=1, inplace=True) ### for tns (#. mux)



    ### for ablation study:
    ## wns
    # df2.drop(df2.columns[[8,9,10,11,12,13,14,15,16,17]], axis=1, inplace=True)
    # df2.drop(df2.columns[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,17]], axis=1, inplace=True)
    ## tns
    # df2.drop(df2.columns[[8,9,10,11,12,13,14,15,16,17]], axis=1, inplace=True)
    df2.drop(df2.columns[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]], axis=1, inplace=True)
    print(df2)

    return df1, df2



def draw_fig_kf(title, y_pred, y_test, method, train_test):
    pass