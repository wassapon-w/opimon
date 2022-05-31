import pyEDM
import time

target_list = ["throughput", "packets_count", "avg_size,proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

for t in range(0, 17):
    print(target_list[t])
    for e in range(1, 21):
        for tau in range(-1,11):
            if tau == 0:
                continue

            start = time.time()
            pyEDM.Simplex( pathIn = "/work/wassapon-w/darpa_ts/", dataFile = "ts_output_day1_norm.csv", pathOut = "/work/wassapon-w/network_output/", predictFile = "ts_output_day1_"+target_list[t]+"_E"+str(e)+"_rho"+str(tau)+".csv", lib = "1 27817", pred = "27818 55634",  E = e, tau = tau, embedded = False, columns=target_list[t], target=target_list[t]) 
            end = time.time()
            print("E = " + str(e) + " tau = " + str(tau) + " : " + str(end - start))
    print("----------")