import logging
import pandas as pd
import os
import sys

# Set the random seed from CL or system clock
if len(sys.argv) > 1:
    SEED = int(sys.argv[1])
else:
    from datetime import datetime
    SEED = int(datetime.now().timestamp())
FILENAME = f"dtlz_mpi_logs-AC/results_seed{SEED}.csv"

# Set default problem parameters
PROB_NUM = "1"
BB_BUDGET = 10000 # 10K eval budget
NDIMS = 8 # 8 vars
NOBJS = 3 # 3 objs

# Set DTLZ problem environment variables
os.environ["DEEPHYPER_BENCHMARK_NDIMS"] = str(NDIMS)
os.environ["DEEPHYPER_BENCHMARK_NOBJS"] = str(NOBJS)
os.environ["DEEPHYPER_BENCHMARK_DTLZ_PROB"] = PROB_NUM # DTLZ2 problem
os.environ["DEEPHYPER_BENCHMARK_DTLZ_OFFSET"] = "0.5" # [x_o, .., x_d]*=0.5

# Load DTLZ benchmark suite
import deephyper_benchmark as dhb
dhb.load("DTLZ")
from deephyper_benchmark.lib.dtlz import hpo

# Load results
results = pd.read_csv("dtlz_mpi_logs-AC/results.csv")

# Gather performance stats
from deephyper_benchmark.lib.dtlz.metrics import PerformanceEvaluator
import numpy as np

# Extract objective values from dataframe
obj_vals = np.asarray([results["objective_0"].values, results["objective_1"].values, results["objective_2"].values]).T

# Initialize performance arrays
rmse_vals = []
npts_vals = []
hv_vals = []
bbf_num = []
# Create a performance evaluator for this problem and loop over budgets
perf_eval = PerformanceEvaluator()
for i in range(100, BB_BUDGET, 100):
    hv_vals.append(perf_eval.hypervolume(obj_vals[:i, :]))
    rmse_vals.append(perf_eval.rmse(obj_vals[:i, :]))
    npts_vals.append(perf_eval.numPts(obj_vals[:i, :]))
    bbf_num.append(i)
# Don't forget final budget
hv_vals.append(perf_eval.hypervolume(obj_vals))
rmse_vals.append(perf_eval.rmse(obj_vals))
bbf_num.append(BB_BUDGET)

# Dump results to csv file
import csv
with open(FILENAME, "w") as fp:
    writer = csv.writer(fp)
    writer.writerow(bbf_num)
    writer.writerow(hv_vals)
    writer.writerow(rmse_vals)
