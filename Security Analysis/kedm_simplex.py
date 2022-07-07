import kedm
import numpy as np
import pandas as pd
import time
import sys

from sklearn.model_selection import StratifiedKFold

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

t = int(sys.argv[1]) - 1

# runtime_log = '/work/wassapon-w/network_output/runtime/runtime_day2_normal_kedm_'+str(t)+'.csv'
runtime_log = '/work/wassapon-w/network_ddos_output/runtime/runtime_day2_ddos_kedm_'+str(t)+'.csv'

with open(runtime_log, 'w') as f:
    print("method,target,E,tau,Tp,Time(Second)")

# for t in range(0, 18):
for e in range(1, 21):
    for tau in range(1, 11):
        for tp in range(1, 2):
            time_series_day1 = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)
            time_series_day2_normal = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day2_norm.csv', header=0, index_col=0)
            time_series_day2_ddos = pd.read_csv('/work/wassapon-w/darpa_ts/ts_ddos_output_day2_norm.csv', header=0, index_col=0)

            # steps = 27817
            data_train = time_series_day1
            # data_test  = time_series_day2_normal[30109:86394]
            data_test  = time_series_day2_ddos[30109:86394]

            start = time.time()
            simplex_result = kedm.simplex(data_train[target_list[t]].to_numpy(), data_test[target_list[t]].to_numpy(), e, tau, tp)
            end = time.time()

            shift = (e - 1) * tau + tp
            output = pd.DataFrame()
            output = pd.concat((pd.DataFrame(data_test[target_list[t]][shift:]), pd.DataFrame(simplex_result)[:-tp].set_index(data_test[shift:].index)), axis=1)
            output.columns = ["Observations", "Predictions"]

            # output.to_csv("/work/wassapon-w/network_output/day2/ts_output_day2_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", index=True, header=True)
            output.to_csv("/work/wassapon-w/network_ddos_output/day2/ts_ddos_output_day2_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", index=True, header=True)

            with open(runtime_log, 'a') as f:
                print("kEDM," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(end - start), file=f)
