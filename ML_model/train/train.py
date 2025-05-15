from preprocess import *
import xgboost as xgb
from sklearn.model_selection import KFold
import pickle
def train(x_train, y_train):

    xgbr = xgb.XGBRegressor(n_estimators=25, max_depth=12, nthread=20)
    xgbr.fit(x_train, y_train)

    return xgbr


if __name__ == '__main__':
    ppa_tpe = "Area"
    ppa_tpe = "TNS"
    ppa_tpe = "WNS"
    ppa_tpe = "Power"



    x, y = load_data(ppa_tpe)

    trained_model = train(x, y)
    with open (f"../saved_model/xgboost_{ppa_tpe}_model.pkl", 'wb') as f:
        pickle.dump(trained_model, f)

