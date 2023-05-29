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

bench_type = "area_pwr"
feat_type = "feat_area"



def load_data():
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
    df2.drop(df2.columns[[0,1,2,8,10]], axis=1, inplace=True) ### for comb cell
    

    return df1, df2


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

    return df1, df2


def draw_fig_kf(title, y_pred, y_test, method, train_test):
    print(title)
    r = get_metrics(y_pred, y_test)
    if title != 'Total Area':
        return
    if r > 0.97:
        pass
    #     with open ('../data/pred.pkl', 'wb') as f:
    #         pickle.dump(y_pred, f)
    #     with open ('../data/real.pkl', 'wb') as f:
    #         pickle.dump(y_test, f)
    #     exit()
    # else:
    #     return
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
    plt.savefig(f"/data/user/masterRTL/figures/{method}_{title}.png", dpi=300)
