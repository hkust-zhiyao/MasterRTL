import numpy as np
import pandas as pd
# import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json, pickle
from scipy.stats import stats

bench_type = "area_pwr"
feat_type = "feat_pwr"



def load_data_sep():
    data_dir = "/data/user/masterRTL/ML_model/data"
    dc_label_data = f'{data_dir}/label/dc_label_{bench_type}.json'
    feat_data = f'{data_dir}/feature/{feat_type}_{bench_type}.json'
    with open(dc_label_data, 'r') as f:
        dc_data_dict = json.load(f)
    df1 = pd.DataFrame(dc_data_dict)
    df1 = df1.T
    


    with open(feat_data, 'r') as f:
        feat_dict = json.load(f)

    df2 = pd.DataFrame(feat_dict)
    df2 = df2.T
    print(df1.shape)
    print(df2.shape)

    # dc_label_data = f'/data/user/qor_predictor/ML_model/data/label/dc_label_pr_pwr.json'
    # with open(dc_label_data, 'r') as f:
    #     dc_data_dict1 = json.load(f)
    # print(dc_data_dict1)
    # exit()
    print(df2)


    return df1, df2


def draw_fig_kf(title, y_pred, y_test, method, train_test):
    pass