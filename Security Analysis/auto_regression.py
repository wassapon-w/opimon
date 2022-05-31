import pandas as pd
import time
from matplotlib import pyplot
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]
lags = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]

for t in range(0, 17):
    for l in range(0, 19):
        start = time.time()
        time_series = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)

        steps = 27817
        data_train = time_series[:-steps]
        data_test  = time_series[-steps:]

        model = AutoReg(data_train[target_list[t]], lags=lags[l])
        model_fit = model.fit()
        predictions = model_fit.predict(start=len(data_train[target_list[t]]), end=len(data_train[target_list[t]])+len(data_test[target_list[t]])-1, dynamic=False)

        output = pd.DataFrame()
        output = pd.concat([data_test[target_list[t]], predictions.to_frame().set_index(data_test.index)], axis=1)
        output.columns = ["Observations", "Predictions"]

        output.to_csv('/work/wassapon-w/network_output/ts_output_day1_auto_regression_'+target_list[t]+'_'+str(lags[l])+'.csv', index=True, header=True)

        end = time.time()
        print("Auto Regression : " + target_list[t] + " : lags : " + str(lags[l]) + " : " + str(end - start))

        # for i in range(len(predictions)):
        #     print('predicted=%f, expected=%f' % (predictions[i], test[i]))
        # rmse = sqrt(mean_squared_error(test, predictions))
        # print('Test RMSE: %.3f' % rmse)