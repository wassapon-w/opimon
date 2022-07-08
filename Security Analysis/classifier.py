from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold

from matplotlib import pyplot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

methods = ["kedm", "autoreg", "lstm", "arima"]
target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

df_ddos = pd.read_csv("/Users/boom/Desktop/darpa_ts/ts_ddos_labeled_output_day2_norm.csv")
# df_ddos = pd.read_csv("/work/wassapon-w/darpa_ts/ts_ddos_labeled_output_day1_norm.csv")

e = 6
tau = 1
tp = 1
m = 0

# print("E,tau,Tp,Acc.")

for m in range(0, 3):
# for e in range(1, 11):
#     for tau in range(1, 6):
#         for tp in range(1, 6):

    print(methods[m])

    sum_acc = 0
    sum_f1 = 0
    sum_score = [0] * len(target_list) * 2
    f = 0

    pred_error = pd.DataFrame()
    for t in range(0, len(target_list)):
        f += 1
        # df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/day2/ts_ddos_output_day2_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        pred_error[target_list[t]+"_Obs"] = df["Observations"]
    for t in range(0, len(target_list)):
        f += 1
        df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/day2/ts_ddos_output_day2_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
        pred_error[target_list[t]+"_Pre"] = df["Predictions"]
    # for t in range(0, len(target_list)):
    #     df = pd.read_csv("/Users/boom/Desktop/darpa_result/network_ddos_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+".csv", header=0)
    #     pred_error[target_list[t]+"_Err"] = df["Observations"] - df["Predictions"]

    # for t in range(0, 18):
    #     df = pd.read_csv("/work/wassapon-w/network_ddos_cross_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+"_cross"+str(i)+".csv", header=0)
    #     pred_error[target_list[t]+"_Obs"] = df["Observations"]
    # for t in range(0, 18):
    #     df = pd.read_csv("/work/wassapon-w/network_ddos_cross_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+"_cross"+str(i)+".csv", header=0)
    #     pred_error[target_list[t]+"_Pre"] = df["Predictions"]
    # for t in range(0, 18):
    #     df = pd.read_csv("/work/wassapon-w/network_ddos_cross_output/"+methods[m]+"/ts_ddos_output_day1_"+methods[m]+"_"+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+"_cross"+str(i)+".csv", header=0)
    #     pred_error[target_list[t]+"_Err"] = df["Observations"] - df["Predictions"]

    first_index = df["Time"][0]

    start_index = int(df_ddos.index[df_ddos['Time'] == first_index][0])
    ddos_label = df_ddos[start_index:start_index+len(pred_error)].reset_index()["ddos_flag"]
    # print(ddos_label.value_counts())

    random_seed = 42
    # oversample = SMOTE(random_state=random_seed)
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_seed)
    # X_train, X_test, y_train, y_test = train_test_split(pred_error, ddos_label, test_size=0.2, random_state=random_seed)
    # X_train, y_train = oversample.fit_resample(X_train, y_train)

    # print(len(X_train), len(X_test), len(y_train), len(y_test))
    
    pred_error = pred_error.to_numpy()
    ddos_label = ddos_label.to_numpy()

    for train_ix, test_ix in kfold.split(pred_error, ddos_label):
        X_train, X_test = pred_error[train_ix], pred_error[test_ix]
        y_train, y_test = ddos_label[train_ix], ddos_label[test_ix]

        model = RandomForestClassifier(random_state=random_seed)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        importance = model.feature_importances_

        # print(e, ",", tau, ",", tp, ",", metrics.accuracy_score(y_test, y_pred))

        print("Accuracy: ", metrics.accuracy_score(y_test, y_pred))
        print("F1-score: ", metrics.f1_score(y_test, y_pred))

        sum_acc += metrics.accuracy_score(y_test, y_pred)
        sum_f1 += metrics.f1_score(y_test, y_pred)

        for i, v in enumerate(importance):
            sum_score[i] += v
            # print('Feature: %s, Score: %.5f' % (target_list[i % 17],v))

        print("Confusion matrix:")
        print(metrics.confusion_matrix(y_test, y_pred))

        # print("Report:")
        # print(metrics.classification_report(y_test, y_pred))

        # print("====================")

        # pyplot.bar([x for x in range(len(importance))], importance)
        # pyplot.show()

    print("=========================")
    print("Average Accuracy:", sum_acc/5)
    print("Average F1:", sum_f1/5)
    # print(sum_score)
    # for i in range(0, f):
    #         print('Feature: %s, Score: %.5f' % (target_list[i % len(target_list)], sum_score[i]/5))
    print("=========================")