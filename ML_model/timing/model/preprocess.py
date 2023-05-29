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
import sys
from pathlib import Path
folder = Path(__file__).parent.parent.parent.parent
sys.path.append(str(folder))
from utils.statistics import *

import sys
sys.path.append('/data/user/masterRTL/')
sys.path.append('/data/user/masterRTL/utils')
sys.path.append('/data/user/masterRTL/utils/metrics.py')
from utils.metrics import get_metrics

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
    y_test = y_test*-1
    y_pred = y_pred*-1
    print(title)
    r = get_metrics(y_pred, y_test)

    if r < 0.95:
        exit()
        with open (f'../data/pred_{title}.pkl', 'wb') as f:
            pickle.dump(y_pred, f)
        with open (f'../data/real_{title}.pkl', 'wb') as f:
            pickle.dump(y_test, f)
        exit()
    else:
        return
    y_test = y_test*-1
    y_pred = y_pred*-1
    mse = metrics.mean_squared_error(normalization(y_test), normalization(y_pred), squared=True)
    mse = round(mse, 3)
    mspe = mspe_cal(y_test, y_pred)
    mspe = round(mspe, 3)
    rmse = metrics.mean_squared_error(normalization(y_test), normalization(y_pred), squared=False)
    rmse = round(rmse, 3)
    rmspe = rmspe_cal(y_test, y_pred)
    rmspe = round(rmspe, 3)
    mape_val = mape(y_pred, y_test)
    mape_val = round(mape_val)
    print("MAPE:", mape_val)
    print("RMSE:", rmse)
    r, p = stats.pearsonr(y_test, y_pred)
    r = round(r, 3)
    print("R:", r)
    r2 = metrics.r2_score(y_test, y_pred)
    r2 = round(r2, 3)
    print("R2:", r2)
    fig, ax = plt.subplots(tight_layout = True)
    if train_test == 'Train':
        ax.scatter(y_test, y_pred, c="b", alpha= 0.6)
    elif train_test == 'Test':
        ax.scatter(y_test, y_pred, c="orange", alpha= 0.6)
    else:
        assert False
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], ls="--", c='r', alpha = 0.2)
    ax.set_xlabel('Measured', fontproperties='Times New Roman', size=14)
    ax.set_ylabel('Predicted', fontproperties='Times New Roman', size=14)
    bbox = dict(boxstyle="round", fc='1', alpha=0.5)
    plt.text( 0.05, 0.75,  fontdict={'family':'Times New Roman'}, s=f'R = {r}\nMAPE = {mape_val}%\nRMSE = {rmse}', 
                    transform=ax.transAxes, size=14, bbox=bbox)
    if title != 'WNS':
        plt.xscale('log')
        plt.yscale('log')
    plt.title(f'{title} {train_test}', fontdict={'family':'Times New Roman', 'size':24})
    plt.xticks(fontproperties='Times New Roman', size=14)
    plt.yticks(fontproperties='Times New Roman', size=14)
    plt.show()
    plt.savefig(f"../fig/{method}_{title}.png", dpi=300)
