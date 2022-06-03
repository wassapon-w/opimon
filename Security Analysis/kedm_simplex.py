import kedm
import numpy as np
import pandas as pd
import time

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

print("method,target,E,tau,Tp,Time(Second)")
for t in range(0, 17):
    print(target_list[t])
    for e in range(1, 21):
        for tau in range(1,11):
            for tp in range(1, 6):
                start = time.time()

                time_series = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)
                # time_series = pd.read_csv('/Users/boom/Desktop/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)

                steps = 27817
                data_train = time_series[:-steps]
                data_test  = time_series[-steps:]
                simplex_result = kedm.simplex(data_train[target_list[t]].to_numpy(), data_test[target_list[t]].to_numpy(), e, tau, tp)

                shift = (e - 1) * tau + tp

                output = pd.DataFrame()
                output = pd.concat((pd.DataFrame(data_test[target_list[t]][shift:]), pd.DataFrame(simplex_result)[:-tp].set_index(data_test[shift:].index)), axis=1)
                output.columns = ["Observations", "Predictions"]

                output.to_csv("/work/wassapon-w/network_output/kedm/ts_output_day1_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", index=True, header=True)
                # output.to_csv("/Users/boom/Desktop/test/ts_output_day1_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+".csv", index=True, header=True)

                # np.savetxt("/home/boom/simplex_result.csv", simplex_result, delimiter=",")

                end = time.time()
                print("kEDM," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(end - start))