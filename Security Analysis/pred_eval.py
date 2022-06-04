import pandas as pd
import time
import sys

from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt

methods = ["kedm", "auto_regression", "lstm"]
target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]
lags = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]

m = int(sys.argv[1]) - 1

if m == 0:
    print("method,target,E,tau,Tp,MAE,RMSE")
    for t in range(0, 18):
        for e in range(1, 21):
            for tau in range(1,11):
                for tp in range(1, 6):
                    output_results = pd.read_csv("/work/wassapon-w/network_output/kedm/ts_output_day1_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0, index_col=0)

                    mae = mean_absolute_error(output_results["Observations"], output_results["Predictions"])
                    rmse = sqrt(mean_squared_error(output_results["Observations"], output_results["Predictions"]))

                    print(methods[m] + "," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(mae) + "," + str(rmse))
else:
    print("method,target,lags,MAE,RMSE")
    for t in range(0, 18):
        for l in range(0, 19):
            output_results = pd.read_csv('/work/wassapon-w/network_output/ts_output_day1_'+methods[m]+'_'+target_list[t]+'_'+str(lags[l])+'.csv', header=0, index_col=0)

            mae = mean_absolute_error(output_results["Observations"], output_results["Predictions"])
            rmse = sqrt(mean_squared_error(output_results["Observations"], output_results["Predictions"]))

            print(methods[m] + "," + target_list[t] + "," + str(lags[l]) + "," + str(mae) + "," + str(rmse))