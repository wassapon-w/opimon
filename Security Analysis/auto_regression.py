import pandas as pd
import time
from matplotlib import pyplot
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]
# lags = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
tp = 1

print("method,target,E,tau,Tp,Time(Second)")

for t in range(0, 18):
    for e in range(1, 21):
        for tau in range(1,11):
            lags = (e-1)*tau
            if lags <= 0:
                lags = 1
            else:
                lags += 1

            start = time.time()

            time_series = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)
            time_series_ddos = pd.read_csv('/work/wassapon-w/darpa_ts/ts_ddos_output_day1_norm.csv', header=0, index_col=0)

            steps = 27817
            data_train = time_series[:-steps]
            # data_test  = time_series[-steps:]
            data_test  = time_series_ddos[-steps:]

            model = AutoReg(data_train[target_list[t]], lags=lags)
            model_fit = model.fit()
            predictions = model_fit.predict(start=len(data_train[target_list[t]])+lags, end=len(data_train[target_list[t]])+len(data_test[target_list[t]])-1, dynamic=False)

            output = pd.DataFrame()
            output = pd.concat([data_test[target_list[t]][lags:], predictions.to_frame().set_index(data_test[lags:].index)], axis=1)
            output.columns = ["Observations", "Predictions"]

            # output.to_csv('/work/wassapon-w/network_output/autoreg/ts_output_day1_autoreg_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)
            output.to_csv('/work/wassapon-w/network_ddos_output/autoreg/ts_ddos_output_day1_autoreg_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)

            end = time.time()
            print("AutoReg," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(end - start))
