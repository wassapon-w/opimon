from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from imblearn.over_sampling import SMOTE

from matplotlib import pyplot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

methods = ["kedm", "autoreg", "lstm", "arima"]
target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

df_ddos = pd.read_csv("/Users/boom/Desktop/darpa_ts/ts_ddos_labeled_output_day1_norm.csv")

e = 9
tau = 3
tp = 1
m = 0

# print("E,tau,Tp,Acc.")

for m in range(0, 4):
# for e in range(1, 11):
#     for tau in range(1, 6):
#         for tp in range(1, 6):

    print(methods[m])

    pred_error = pd.DataFrame()
    for t in range(0, 18):
        # df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/kedm/ts_ddos_output_day1_kedm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        # df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/lstm/ts_ddos_output_day1_lstm_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        # df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/autoreg/ts_ddos_output_day1_autoreg_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        pred_error[target_list[t]] = abs(df["Observations"] - df["Predictions"])

    first_index = df["Time"][0]

    start_index = int(df_ddos.index[df_ddos['Time'] == first_index][0])
    ddos_label = df_ddos[start_index:].reset_index()["ddos_flag"]

    random_seed = 42
    oversample = SMOTE(random_state=random_seed)
    X_train, X_test, y_train, y_test = train_test_split(pred_error, ddos_label, test_size=0.9, random_state=random_seed)
    X_train, y_train = oversample.fit_resample(X_train, y_train)

    # print(len(X_train), len(X_test), len(y_train), len(y_test))

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    importance = model.feature_importances_

    # print(e, ",", tau, ",", tp, ",", metrics.accuracy_score(y_test, y_pred))

    print("Accuracy: ", metrics.accuracy_score(y_test, y_pred))
    print("F1-score: ", metrics.f1_score(y_test, y_pred))

    for i,v in enumerate(importance):
        print('Feature: %s, Score: %.5f' % (target_list[i],v))

    print("Confusion matrix:")
    print(metrics.confusion_matrix(y_test, y_pred))

    print("====================")

    # pyplot.bar([x for x in range(len(importance))], importance)
    # pyplot.show()