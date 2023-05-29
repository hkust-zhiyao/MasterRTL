from preprocess import *
import xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
import copy, time
import sys
sys.path.append('/data/user/masterRTL/')
sys.path.append('/data/user/masterRTL/utils')
sys.path.append('/data/user/masterRTL/utils/metrics.py')
from utils.metrics import MAPE_one_val

def run_xgb_label(x_train, y_train, x_test, y_test):

    x_train_stat = copy.copy(x_train)
    x_test_stat = copy.copy(x_test)
    x_train_stat.drop(x_train_stat.columns[[1,4,5,6,7,8,9,10, 11, 13, 14,15]], axis=1, inplace=True)
    x_test_stat.drop(x_test_stat.columns[[1,4,5,6,7,8,9,10, 11, 13, 14,15]], axis=1, inplace=True)


    x_train_dyn = copy.copy(x_train)
    x_test_dyn = copy.copy(x_test)
    x_train_dyn.drop(x_train_dyn.columns[[5,6,7,8,9,10,11,12,13,14,16]], axis=1, inplace=True)
    x_test_dyn.drop(x_test_dyn.columns[[5,6,7,8,9,10,11,12,13,14,16]], axis=1, inplace=True)




    n_est = 85
    man_d_num = 12

    # print('Training....')

    xgbr0 = xgb.XGBRegressor(n_estimators=n_est, max_depth=man_d_num, nthread=20)
    # xgbr0 = RandomForestRegressor(n_estimators= 100, max_depth=35)
    # xgbr0 = LinearRegression()
    xgbr0.fit(x_train_stat, y_train[4])

    xgbr1 = xgb.XGBRegressor(n_estimators=n_est, max_depth=man_d_num, nthread=20)
    xgbr1.fit(x_train_dyn, y_train[3])



    # y_pred_stat = np.array(x_test_stat)[:,0] 
    y_pred_stat = xgbr0.predict(x_test_stat)
    
    
    start_time = time.perf_counter()
    y_pred_dyn = xgbr1.predict(x_test_dyn) 
    end_time = time.perf_counter()
    runtime = round((end_time-start_time), 5)
    # print('Inference time: ', runtime)

    # y_pred_stat2 = np.array(x_train_stat)[:,0]
    y_pred_stat2 = xgbr0.predict(x_train_stat)
    y_pred_dyn2 = xgbr1.predict(x_train_dyn)

    y_pre_total = y_pred_stat + y_pred_dyn ## total area
    idx = 0
    for index, row in y_test.iterrows():

        dict_all[index] = {'pred_stat_pwr':y_pred_stat[idx], 'pred_dyn_pwr':y_pred_dyn[idx], 'pred_total_pwr':y_pre_total[idx],\
                            'real_total_pwr':row[5]}
        idx += 1
    
    


    return y_pred_stat, y_pred_stat2, y_pred_dyn, y_pred_dyn2, y_pre_total

def kFold_train(x, y, title):
        kf = KFold(n_splits=10, shuffle=True)
        kf.split(x, y)
        test_lst_stat, test_lst_dyn, test_lst_total = [],[],[]
        pred_lst_stat, pred_lst_dyn, pred_lst_total = [],[],[]
        train_lst_stat, train_lst_dyn= [],[]
        pred2_lst_stat, pred2_lst_dyn= [],[]
        test_all_arr_stat = np.array(test_lst_stat)
        pred_all_arr_stat = np.array(pred_lst_stat)
        train_all_arr_stat = np.array(train_lst_stat)
        pred2_all_arr_stat = np.array(pred2_lst_stat)

        test_all_arr_dyn = np.array(test_lst_dyn)
        pred_all_arr_dyn = np.array(pred_lst_dyn)
        train_all_arr_dyn = np.array(train_lst_dyn)
        pred2_all_arr_dyn = np.array(pred2_lst_dyn)



        test_all_arr_total = np.array(test_lst_total)
        pred_all_arr_total = np.array(pred_lst_total)
        # r_lst, r2_lst, mse_lst, rmse_lst = 0,0,0,0
        for k, (train, test) in enumerate(kf.split(x,y)):
            x_train = x.iloc[train]
            x_test = x.iloc[test]
            y_train = y.iloc[train]
            y_test = y.iloc[test]

            y_pred_stat, y_pred2_stat, y_pred_dyn, y_pred2_dyn, y_pred_total = run_xgb_label(x_train, y_train, x_test, y_test)
            test_all_arr_stat = np.append(test_all_arr_stat, np.array(y_test[4], dtype=np.float64))
            pred_all_arr_stat = np.append(pred_all_arr_stat, y_pred_stat)
            train_all_arr_stat = np.append(train_all_arr_stat, np.array(y_train[4], dtype=np.float64))
            pred2_all_arr_stat = np.append(pred2_all_arr_stat, y_pred2_stat)

            test_all_arr_dyn = np.append(test_all_arr_dyn, np.array(y_test[3], dtype=np.float64))
            pred_all_arr_dyn = np.append(pred_all_arr_dyn, y_pred_dyn)
            train_all_arr_dyn = np.append(train_all_arr_dyn, np.array(y_train[3], dtype=np.float64))
            pred2_all_arr_dyn = np.append(pred2_all_arr_dyn, y_pred2_dyn)


            test_all_arr_total = np.append(test_all_arr_total, np.array(y_test[5], dtype=np.float64))
            pred_all_arr_total = np.append(pred_all_arr_total, y_pred_total)


        draw_fig_kf('Stat. Power', test_all_arr_stat, pred_all_arr_stat, 'mix_kf_test', 'Test')
        draw_fig_kf('Dyn. Power', test_all_arr_dyn, pred_all_arr_dyn, 'mix_kf_test', 'Test')
        draw_fig_kf('Total Power', test_all_arr_total, pred_all_arr_total, 'mix_kf_test', 'Test')
        # return r, mape_val




if __name__ == '__main__':
    # while True:
    global dict_all
    dict_all = {}
    
    label_data, feat_data = load_data_sep()
    x = feat_data
    while True:
        kFold_train(x, label_data, 'Pwr')
        continue

        design_lst = ['SmallBoom', 'MediumBoom', 'LargeBoom', 'MegaBoom']
        for design in design_lst:
            print(design)
            d = dict_all[design]
            mape_val = MAPE_one_val(d['pred_total_pwr'], d['real_total_pwr'])
            print(mape_val)
        input()

    # with open ('./data/pred_pwr_dict.pkl', 'wb') as f:
    #     pickle.dump(dict_all, f)
    # if r > 0.85:
    #     exit()
