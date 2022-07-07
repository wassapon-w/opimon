from numpy import array
import pandas as pd
import time
import sys

from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense

target_list = ["throughput", "packets_count", "avg_size", "proto_set", "proto_count_TCP", "proto_count_UDP", "proto_count_ICMP", "flags_set", "flags_count_PA", "flags_count_FPA", "flags_count_S", "flags_count_SA", "flags_count_A", "flags_count_FA", "IP_src_set", "IP_dst_set", "IP_sport_set", "IP_dport_set"]

t = int(sys.argv[1]) - 1
tp = 1

def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		end_ix = i + n_steps
		if end_ix > len(sequence)-1:
			break
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

runtime_log = '/work/wassapon-w/network_output/runtime/runtime_day1_normal_lstm_'+str(t)+'.csv'
# runtime_log = '/work/wassapon-w/network_ddos_output/runtime/runtime_day1_ddos_lstm_'+str(t)+'.csv'

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


        start_train = time.time()
        x_train, y_train = split_sequence(data_train[target_list[t]].reset_index(drop=True).to_numpy(), lags)

        n_features = 1
        x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], n_features))

        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(lags, n_features)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        model.fit(x_train, y_train, epochs=1, verbose=0)
        end_train = time.time()

        start_test = time.time()
        # x_input = data_test[target_list[t]].reset_index(drop=True).to_numpy().reshape((1, n_steps, n_features))
        x_test, y_test = split_sequence(data_test[target_list[t]].reset_index(drop=True).to_numpy(), lags)
        predictions = model.predict(x_test, verbose=0)
        end_test = time.time()

        output = pd.DataFrame()
        output = pd.concat([data_test[target_list[t]][lags:], pd.DataFrame(predictions).set_index(data_test[lags:].index)], axis=1)
        output.columns = ["Observations", "Predictions"]

        output.to_csv('/work/wassapon-w/network_output/lstm/ts_output_day1_lstm_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)
        # output.to_csv('/work/wassapon-w/network_ddos_output/lstm/ts_ddos_output_day1_lstm_'+target_list[t]+"_E"+str(e)+"_tau"+str(tau)+"_tp"+str(tp)+'.csv', index=True, header=True)

        end = time.time()

        with open(runtime_log, 'a') as f:
            print("LSTM," + target_list[t] + "," + str(e) + "," + str(tau) + "," + str(tp) + "," + str(end_train - start_train) + "," + str(end_test - start_test), file=f)