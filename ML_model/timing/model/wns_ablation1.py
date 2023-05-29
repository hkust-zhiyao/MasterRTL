from preprocess import *
import xgboost as xgb
from sklearn.model_selection import KFold
import pickle
def run_xgb_label(x_train, y_train, x_test):



    # X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=1)
    # xgbr = xgb.XGBRegressor(n_estimators=35, max_depth=12, nthread=20)
    xgbr = xgb.XGBRegressor(n_estimators=45, max_depth=8, nthread=20)

    

    xgbr.fit(x_train, y_train)

    # print(rfr.intercept_)
    # print(rfr.coef_)

    importance = xgbr.feature_importances_
    # print(importance)
    # exit()

    y_pred = xgbr.predict(x_test)
    y_pred2 = xgbr.predict(x_train)

    idx = 0
    for index, row in x_test.iterrows():
        dict_all[index] = {'pred_wns':y_pred[idx]}
        idx += 1
    
    return y_pred, y_pred2

def kFold_train(x, y, title):
    kf = KFold(n_splits=10, shuffle=True)
    kf.split(x, y)
    test_lst = []
    pred_lst = []
    train_lst = []
    pred2_lst = []
    test_all_arr = np.array(test_lst)
    pred_all_arr = np.array(pred_lst)
    train_all_arr = np.array(train_lst)
    pred2_all_arr = np.array(pred2_lst)
    # r_lst, r2_lst, mse_lst, rmse_lst = 0,0,0,0
    for k, (train, test) in enumerate(kf.split(x,y)):
        x_train = x.iloc[train]
        x_test = x.iloc[test]
        y_train = y.iloc[train]
        y_test = y.iloc[test]
        y_pred, y_pred2 = run_xgb_label(x_train, y_train, x_test)
        test_all_arr = np.append(test_all_arr, np.array(y_test, dtype=np.float64))
        pred_all_arr = np.append(pred_all_arr, y_pred)
        train_all_arr = np.append(train_all_arr, np.array(y_train, dtype=np.float64))
        pred2_all_arr = np.append(pred2_all_arr, y_pred2)


    draw_fig_kf(title, test_all_arr, pred_all_arr, 'xgb_kf_test', 'Test')
    # draw_fig_kf(title, train_all_arr, pred2_all_arr, 'xgb_kf_train', 'Train')






if __name__ == '__main__':
    global dict_all
    dict_all = {}
    label_data, feat_data = load_data()
    x = feat_data

    while True:
        kFold_train(x, label_data[6], 'WNS')

    # with open ('./data/pred_wns_dict.pkl', 'wb') as f:
    #     pickle.dump(dict_all, f)