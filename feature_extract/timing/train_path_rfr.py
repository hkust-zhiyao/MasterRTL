import pickle, random
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
def load_data():

    feat_data = f'/home/coguest5/MasterRTL/ML_model/saved_data/feat_all_lst.pkl'
    dc_label_data= f'/home/coguest5/MasterRTL/ML_model/saved_data/label_lst.pkl'

    # sample_lst = []
    # for idx in range(3000):
    #     random.randint(0, len())
    label_lst_samp = []
    feat_lst_samp = []

    with open(dc_label_data, 'rb') as f:
        label_lst = pickle.load(f)
    with open(feat_data, 'rb') as f:
        feat_lst = pickle.load(f)


    # for idx in range(len(label_lst)):
    #     if idx % 4 == 0:
    #         label_lst_samp.append(label_lst[idx])
    #         feat_lst_samp.append(feat_lst[idx])
    # label_lst = label_lst_samp
    # feat_lst = feat_lst_samp


    df1 = np.array(label_lst)
    df1 = pd.DataFrame(label_lst)
    
    df2 = pd.DataFrame(feat_lst)
    # print(df1.shape)
    # print(df2.shape)
    return df1, df2


def train_rfr():
    label_data, feat_data = load_data()
    x = feat_data
    y = label_data 
    X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=1)
    rfr = RandomForestRegressor(n_estimators= 50, max_depth=30, random_state=1)
    rfr.fit(X_train, y_train)

    return rfr

