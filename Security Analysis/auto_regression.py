from dbm.ndbm import library
import numpy as np
import pandas as pd
import time

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from skforecast.ForecasterAutoreg import ForecasterAutoreg
from skforecast.ForecasterAutoregCustom import ForecasterAutoregCustom
from skforecast.ForecasterAutoregMultiOutput import ForecasterAutoregMultiOutput
from skforecast.model_selection import grid_search_forecaster
from skforecast.model_selection import backtesting_forecaster

from joblib import dump, load

target_list = ["throughput", "packets_count", "avg_size,proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]
lags = [30, 60, 300, 600, 1800, 3600]

for t in range(0, 17):
    for l in range(0, 6):
        start = time.time()

        time_series = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)

        steps = 27817
        data_train = time_series[:-steps]
        data_test  = time_series[-steps:]

        forecaster = ForecasterAutoreg(regressor = RandomForestRegressor(random_state=123), lags = lags[l])
        forecaster.fit(y=data_train[target_list[t]])

        predictions = forecaster.predict(steps=steps)

        output = pd.DataFrame()
        output = pd.concat([data_test[target_list[t]], predictions.to_frame().set_index(data_test.index)], axis=1)
        output.columns = ["Observations", "Predictions"]

        output.to_csv('/work/wassapon-w/EDM/darpa_day1/ts_output_day1_auto_regression_'+target_list[t]+'.csv', index=True, header=True)

        end = time.time()
        print("Auto Regression : " + target_list[t] + " : " + str(end - start))

    # error_mse = mean_squared_error(
    #                 y_true = data_test['throughput'],
    #                 y_pred = predictions
    #             )

    # print(f"Test error (mse): {error_mse}")