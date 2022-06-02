import pandas as pd
import time

from sklearn.metrics import mean_squared_error, mean_absolute_error, matthews_corrcoef
from math import sqrt

# output_results = pd.read_csv('/work/wassapon-w/darpa_ts/ts_output_day1_norm.csv', header=0, index_col=0)
output_results = pd.read_csv('/Users/boom/Desktop/test/ts_output_day1_kedm_throughput_E1_rho1.csv', header=0, index_col=0)

rmae = sqrt(mean_absolute_error(output_results["Observations"], output_results["Predictions"]))
rmse = sqrt(mean_squared_error(output_results["Observations"], output_results["Predictions"]))
# corr = matthews_corrcoef(output_results["Observations"], output_results["Predictions"])

print("RMAE = ", rmae,  " : RMSE = ", rmse)