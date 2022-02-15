from scapy.all import *

import sys
import time
import glob, os

import pandas as pd
import numpy as np

def pcap_process(pcap_name, csv_name):
    packets = PcapReader(pcap_name)
    with open(csv_name, 'w') as f:
        print("Time,Size,Ether.src,Ether.dst,IP.len,IP.proto,TCP.flags,IP.src,IP.dst,IP.sport,IP.dport", file=f)
        for i, p in enumerate(packets):
            # print(i)
            if IP in p:
                print(int(p.time), file=f, end=",") # Second
                print(len(p), file=f, end=",")
                print(p[Ether].src, file=f, end=",")
                print(p[Ether].dst, file=f, end=",")
                print(p[IP].len, file=f, end=",")
                if p[IP].proto == 6:
                    print("TCP", file=f, end=",")
                elif p[IP].proto == 1:
                    print("ICMP", file=f, end=",")
                elif p[IP].proto == 17:
                    print("UDP", file=f, end=",")
                if p[IP].proto == 6:
                    print(p[TCP].flags, file=f, end=",")
                else:
                    print("", file=f, end=",")
                print(p[IP].src, file=f, end=",")
                print(p[IP].dst, file=f, end=",")
                if (p[IP].proto == 6 or p[IP].proto == 17):
                    try:
                        print(p[IP].sport, file=f, end=",")
                        print(p[IP].dport, file=f)
                    except:
                        print("", file=f, end=",")
                        print("", file=f)
                else:
                    print("", file=f, end=",")
                    print("", file=f)

def clear_values():
    global packets_count, throughput, proto_set, proto_count_TCP, proto_count_UDP, proto_count_ICMP
    global flags_set, flags_count_PA, flags_count_FPA, flags_count_S, flags_count_SA, flags_count_A, flags_count_FA
    global IP_src_set, IP_dst_set, IP_sport_set, IP_dport_set, ddos_flag
    packets_count = 0
    throughput = 0
    proto_set = set()
    proto_count_TCP = 0
    proto_count_UDP = 0
    proto_count_ICMP = 0
    flags_set = set()
    flags_count_PA = 0
    flags_count_FPA = 0
    flags_count_S = 0
    flags_count_SA = 0
    flags_count_A = 0
    flags_count_FA = 0
    IP_src_set = set()
    IP_dst_set = set()
    IP_sport_set = set()
    IP_dport_set = set()
    ddos_flag = 0

def packet_counter(csv_name, ts_name):
    df = pd.read_csv(csv_name, skipinitialspace=True)

    global packets_count, throughput, proto_set, proto_count_TCP, proto_count_UDP, proto_count_ICMP
    global flags_set, flags_count_PA, flags_count_FPA, flags_count_S, flags_count_SA, flags_count_A, flags_count_FA
    global IP_src_set, IP_dst_set, IP_sport_set, IP_dport_set, ddos_flag
    clear_values()
    next_time = df["Time"][0] + 1

    with open(ts_name, 'w') as f:
        print("Time,throughput,packets_count,avg_size,proto_set,proto_count_TCP,proto_count_UDP,proto_count_ICMP,flags_set,flags_count_PA,flags_count_FPA,flags_count_S,flags_count_SA,flags_count_A,flags_count_FA,IP_src_set,IP_dst_set,IP_sport_set,IP_dport_set", file=f)

    # for Time,IP_proto,TCP_flag,IP_src,IP_dst,IP_sport,IP_dport,Event in zip(df["Time"],df["IP.proto"],df["TCP.flags"],df["IP.src"],df["IP.dst"],df["IP.sport"],df["IP.dport"],df["Event"]):
    for Time, Size, IP_proto, TCP_flag, IP_src, IP_dst, IP_sport, IP_dport in zip(df["Time"], df["Size"], df["IP.proto"], df["TCP.flags"], df["IP.src"], df["IP.dst"], df["IP.sport"], df["IP.dport"]):
        # print(Time)
        if(Time > next_time):
            with open(ts_name, 'a') as f:
                print(Time, file=f, end=",")
                print(throughput, file=f, end=",")
                print(packets_count, file=f, end=",")
                print(throughput/packets_count, file=f, end=",")
                print(len(proto_set), file=f, end=",")
                print(proto_count_TCP, file=f, end=",")
                print(proto_count_UDP, file=f, end=",")
                print(proto_count_ICMP, file=f, end=",")
                print(len(flags_set), file=f, end=",")
                print(flags_count_PA, file=f, end=",")
                print(flags_count_FPA, file=f, end=",")
                print(flags_count_S, file=f, end=",")
                print(flags_count_SA, file=f, end=",")
                print(flags_count_A, file=f, end=",")
                print(flags_count_FA, file=f, end=",")
                print(len(IP_src_set), file=f, end=",")
                print(len(IP_dst_set), file=f, end=",")
                print(len(IP_sport_set), file=f, end=",")
                print(len(IP_dport_set), file=f)
                # print(ddos_flag)
            clear_values()
            next_time += 1

        throughput += int(Size)
        packets_count += 1
        proto_set.add(IP_proto)
        if(IP_proto=="TCP"):
            proto_count_TCP += 1
        if(IP_proto=="UDP"):
            proto_count_UDP += 1
        if(IP_proto=="ICMP"):
            proto_count_ICMP += 1
        flags_set.add(TCP_flag)
        if(TCP_flag=="PA"):
            flags_count_PA += 1
        if(TCP_flag=="FPA"):
            flags_count_FPA += 1
        if(TCP_flag=="S"):
            flags_count_S += 1
        if(TCP_flag=="SA"):
            flags_count_SA += 1
        if(TCP_flag=="A"):
            flags_count_A += 1
        if(TCP_flag=="FA"):
            flags_count_FA += 1
        IP_src_set.add(IP_src)
        IP_dst_set.add(IP_dst)
        IP_sport_set.add(IP_sport)
        IP_dport_set.add(IP_dport)
        # if(Event=="ddos"):
        # 	ddos_flag=1

def sum_file():
    output_file = '/work/wassapon-w/data/network/DARPA_Scalable_Network_Monitoring-20091103/ts_output.csv'

    with open(output_file, 'w') as f:
        print("Time,throughput,packets_count,avg_size,proto_set,proto_count_TCP,proto_count_UDP,proto_count_ICMP,flags_set,flags_count_PA,flags_count_FPA,flags_count_S,flags_count_SA,flags_count_A,flags_count_FA,IP_src_set,IP_dst_set,IP_sport_set,IP_dport_set", file=f)

    for i in range(1,11):
        folder = glob.glob("/work/wassapon-w/data/network/DARPA_Scalable_Network_Monitoring-20091103/set"+str(i)+"/ts/*.csv") 
        for file in folder:
            df = pd.read_csv(file, skipinitialspace=True, header=0) 
            df.to_csv(output_file, mode='a', index=False, header=False)

def main():
    pcap_dir = sys.argv[1]
    csv_dir = sys.argv[1] + "csv/"
    ts_dir = sys.argv[1] + "ts/"

    print("Directory: " + str(sys.argv[1]))
    # print("File Number: " + str(sys.argv[2]) + " to " + str(sys.argv[3]))

    os.chdir(pcap_dir)
    pcap_file = glob.glob("*.pcap")

    # for i in range(int(sys.argv[2]), int(sys.argv[3])):
    #     print(str(i+1) + " / " + str(len(pcap_file)) + ": " + pcap_file[i])

    #     pcap_name = pcap_dir + pcap_file[i]
    #     csv_name = csv_dir + pcap_file[i] + ".csv"
    #     pcap_process(pcap_name, csv_name)

    #     ts_name = ts_dir + "ts_" + pcap_file[i] + ".csv"
    #     packet_counter(csv_name, ts_name)

    i = int(sys.argv[2]) - 1

    print(str(i+1) + " / " + str(len(pcap_file)) + ": " + pcap_file[i])

    pcap_name = pcap_dir + pcap_file[i]
    csv_name = csv_dir + pcap_file[i] + ".csv"
    pcap_process(pcap_name, csv_name)

    ts_name = ts_dir + "ts_" + pcap_file[i] + ".csv"
    packet_counter(csv_name, ts_name)

if __name__ == "__main__":
    main()