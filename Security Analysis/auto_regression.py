import pandas as pd
import time
import sys

from matplotlib import pyplot
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_squared_error
from math import sqrt

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

t = int(sys.argv[1]) - 1
tp = 1

runtime_log = '/work/wassapon-w/network_output/runtime/runtime_day1_normal_autoreg_'+str(t)+'.csv'
# runtime_log = '/work/wassapon-w/network_ddos_output/runtime/runtime_day1_ddos_autoreg.csv'

with open(runtime_log, 'w') as f:
    print("method,target,E,tau,Tp,Train(Second),Predict(Second)")

# for t in range(0, 18):
for e in range(1, 21):
    for tau in range(1, 11):
        lags = (e-1)*tau
        if lags <= 0:
            lags = 1
        else:
            lags += 1

        time_series_day1 = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)
        time_series_day2_normal = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day2_norm.csv', header=0, index_col=0)
        time_series_day2_ddos = pd.read_csv('/work/wassapon-w/darpa_ts/ts_ddos_output_day2_norm.csv', header=0, index_col=0)

        # steps = 27817
        data_train = time_series_day1
        data_test  = time_series_day2_normal[30109:86393]
        # data_test  = time_series_day2_normal[30109:86393]

        train = data_train[target_list[t]].values
        test = data_test[target_list[t]].values

        start_train = time.time()
        model = AutoReg(data_train[target_list[t]], lags=lags)
        model_fit = model.fit()
        # predictions = model_fit.predict(start=len(data_train[target_list[t]])+lags, end=len(data_train[target_list[t]])+len(data_test[target_list[t]])-1, dynamic=True)
        coef = model_fit.params
        end_train = time.time()

        start_test = time.time()
        history = train[len(train)-lags:]
        history = [history[i] for i in range(len(history))]
        predictions = list()
        for s in range(len(test)):
            length = len(history)
            lag = [history[i] for i in range(length-lags,length)]
            yhat = coef[0]
            for d in range(lags):
                yhat += coef[d+1] * lag[lags-d-1]
            obs = test[s]
            predictions.append(yhat)
            history.append(obs)
        end_test = time.time()

        output = pd.DataFrame()
        output = pd.concat([data_test[target_list[t]][lags:], pd.DataFrame(predictions)[lags:].set_index(data_test[lags:].index)], axis=1)
        output.columns = ["Observations", "Predictions"]

        output.to_csv('/work/wassapon-w/network_output/autoreg/ts_output_day1_autoreg_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)
        # output.to_csv('/work/wassapon-w/network_ddos_output/autoreg/ts_ddos_output_day1_autoreg_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)
        
        end = time.time()
        with open(runtime_log, 'a') as f:
            print("AutoReg," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(end_train - start_train) + "," + str(end_test - start_test), file=f)
