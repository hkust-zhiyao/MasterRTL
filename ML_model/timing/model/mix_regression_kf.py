from preprocess import *
import xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
import copy, time, pickle
def run_xgb_label(x_train, y_train, x_test, y_test):

    x_train_reg_pin = copy.copy(x_train)
    x_test_reg_pin = copy.copy(x_test)
    x_train_reg_pin.drop(x_train_reg_pin.columns[[0,1,2,3,4,5,6,7,9,10]], axis=1, inplace=True)
    x_test_reg_pin.drop(x_test_reg_pin.columns[[0,1,2,3,4,5,6,7,9,10]], axis=1, inplace=True)

    x_train_dyn = copy.copy(x_train)
    x_test_dyn = copy.copy(x_test)
    x_train_dyn.drop(x_train_dyn.columns[[0,1,2,8,10]], axis=1, inplace=True)
    x_test_dyn.drop(x_test_dyn.columns[[0,1,2,8,10]], axis=1, inplace=True)



    n_est = 45
    man_d_num = 8
    print('Training....')

    xgbr1 = xgb.XGBRegressor(n_estimators=n_est, max_depth=man_d_num, nthread=20)
    xgbr1.fit(x_train_dyn, y_train[1])


    
    y_pred_reg_pin = np.array(x_test_reg_pin)[:,0] ## seq area
    
    
    start_time = time.perf_counter()
    y_pred_dyn = xgbr1.predict(x_test_dyn) ## comb area
    end_time = time.perf_counter()
    runtime = round((end_time-start_time), 5)
    print('Inference time: ', runtime)

    y_pred_reg_pin2 = np.array(x_train_reg_pin)[:,0]  
    y_pred_dyn2 = xgbr1.predict(x_train_dyn)

    y_pred_total = y_pred_reg_pin + y_pred_dyn ## total area


    idx = 0
    for index, row in y_test.iterrows():
        dict_all[index] = {'pred_seq_area':y_pred_reg_pin[idx], 'pred_comb_area':y_pred_dyn[idx], 'pred_total_area':y_pred_total[idx],
                           'real_seq_area':row[0], 'real_comb_area':row[1], 'real_total_area':row[2]}
        idx += 1
    

    return y_pred_reg_pin, y_pred_reg_pin2, y_pred_dyn, y_pred_dyn2, y_pred_total

def kFold_train(x, y, title):
        kf = KFold(n_splits=10, shuffle=True)
        kf.split(x, y)
        test_lst_reg_pin, test_lst_dyn, test_lst_total = [],[],[]
        pred_lst_reg_pin, pred_lst_dyn, pred_lst_total = [],[],[]
        train_lst_reg_pin, train_lst_dyn= [],[]
        pred2_lst_reg_pin, pred2_lst_dyn= [],[]
        test_all_arr_reg_pin = np.array(test_lst_reg_pin)
        pred_all_arr_reg_pin = np.array(pred_lst_reg_pin)
        train_all_arr_reg_pin = np.array(train_lst_reg_pin)
        pred2_all_arr_reg_pin = np.array(pred2_lst_reg_pin)

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

            y_pred_reg_pin, y_pred2_reg_pin, y_pred_dyn, y_pred2_dyn, y_pred_total = run_xgb_label(x_train, y_train, x_test, y_test)
            test_all_arr_reg_pin = np.append(test_all_arr_reg_pin, np.array(y_test[0], dtype=np.float64))
            pred_all_arr_reg_pin = np.append(pred_all_arr_reg_pin, y_pred_reg_pin)
            train_all_arr_reg_pin = np.append(train_all_arr_reg_pin, np.array(y_train[0], dtype=np.float64))
            pred2_all_arr_reg_pin = np.append(pred2_all_arr_reg_pin, y_pred2_reg_pin)

            test_all_arr_dyn = np.append(test_all_arr_dyn, np.array(y_test[1], dtype=np.float64))
            pred_all_arr_dyn = np.append(pred_all_arr_dyn, y_pred_dyn)
            train_all_arr_dyn = np.append(train_all_arr_dyn, np.array(y_train[1], dtype=np.float64))
            pred2_all_arr_dyn = np.append(pred2_all_arr_dyn, y_pred2_dyn)


            test_all_arr_total = np.append(test_all_arr_total, np.array(y_test[2], dtype=np.float64))
            pred_all_arr_total = np.append(pred_all_arr_total, y_pred_total)


        draw_fig_kf('Seq. Area', test_all_arr_reg_pin, pred_all_arr_reg_pin, 'mix_kf_test', 'Test')
        draw_fig_kf('Comb. Area', test_all_arr_dyn, pred_all_arr_dyn, 'mix_kf_test', 'Test')
        draw_fig_kf('Total Area', test_all_arr_total, pred_all_arr_total, 'mix_kf_test', 'Test')





if __name__ == '__main__':
    global dict_all
    dict_all = {}
    label_data, feat_data = load_data_sep()
    x = feat_data
    kFold_train(x, label_data, 'Area')


    # print(dict_all)
    with open ('./data/pred_area_dict.pkl', 'wb') as f:
        pickle.dump(dict_all, f)
