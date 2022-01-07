from scapy.all import *

import time
import glob, os

import pandas as pd
import numpy as np

current_time = 0

throughput = {}
number_of_packet = {}
average_packet_size = {}
src_ip = {}
src_port = {}
dst_ip = {}
dst_port = {}

tcp_flag = {}

table_src_ip = []
table_src_port = []
table_dst_ip = []
table_dst_port = []

pcap_dir = "/Users/boom/Desktop/data/"
os.chdir(pcap_dir)
for pcap_file in glob.glob("*.pcap"):
    pcap_data = PcapReader(pcap_dir + pcap_file)

    for index, packet in enumerate(pcap_data):
        if int(packet.time) > current_time:
            current_time = int(packet.time)
            throughput[current_time] = 0
            number_of_packet[current_time] = 0

            src_ip[current_time] = 0
            src_port[current_time] = 0
            dst_ip[current_time] = 0
            dst_port[current_time] = 0

            tcp_flag[current_time] = {}

            table_src_ip = []
            table_src_port = []
            table_dst_ip = []
            table_dst_port = []

        # Count throughput
        throughput[current_time] += len(packet) # Byte
        number_of_packet[current_time] += 1

        # Count unique IP/port and number of packet of each TCP port
        if IP in packet:
            if packet[IP].src not in table_src_ip:
                table_src_ip.append(packet[IP].src)
                src_ip[current_time] += 1
            if packet[IP].sport not in table_src_port:
                table_src_port.append(packet[IP].sport)
                src_port[current_time] += 1
            if packet[IP].dst not in table_dst_ip:
                table_dst_ip.append(packet[IP].dst)
                dst_ip[current_time] += 1
            if packet[IP].dport not in table_dst_port:
                table_dst_port.append(packet[IP].dport)
                dst_port[current_time] += 1
            if packet[IP].proto == 6:
                if packet[TCP].flags not in tcp_flag[current_time].keys():
                    tcp_flag[current_time][packet[TCP].flags] = 0
                tcp_flag[current_time][packet[TCP].flags] += 1
        else:
            pass
            # print("Found not IP packet")

# Calculate average packet size
for current_time in number_of_packet.keys():
    average_packet_size[current_time] = throughput[current_time] / number_of_packet[current_time]

# print(throughput)
# print(src_ip)
# print(src_port)
# print(dst_ip)
# print(dst_port)
# print(tcp_flag)
# print(average_packet_size)

# Export to CSV
throughput_df = pd.DataFrame.from_dict(throughput, orient='index', columns=['throughput'])
number_of_packet_df = pd.DataFrame.from_dict(number_of_packet, orient='index', columns=['number_of_packet'])
average_packet_size_df = pd.DataFrame.from_dict(average_packet_size, orient='index', columns=['average_packet_size'])
src_ip_df = pd.DataFrame.from_dict(src_ip, orient='index', columns=['src_ip'])
src_port_df = pd.DataFrame.from_dict(src_port, orient='index', columns=['src_port'])
dst_ip_df = pd.DataFrame.from_dict(dst_ip, orient='index', columns=['dst_ip'])
dst_port_df = pd.DataFrame.from_dict(dst_port, orient='index', columns=['dst_port'])
tcp_flag_df = pd.DataFrame.from_dict(tcp_flag, orient='index')

dataset = pd.concat([throughput_df, number_of_packet_df, average_packet_size_df, src_ip_df, src_port_df, dst_ip_df, dst_port_df, tcp_flag_df], axis=1, join='inner')
dataset.fillna(0).apply(np.int64)

dataset.to_csv('/Users/boom/Desktop/data.csv')