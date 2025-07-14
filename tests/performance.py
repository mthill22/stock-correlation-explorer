# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 19:05:26 2025

@author: Dana's PC
"""

import timeit
import pandas as pd
from src.correlation import computing_rolling_correlations_dictionary, computing_rolling_correlations_dataframe
from src.data_reader import data_load_zip


df = data_load_zip("stocks_data.zip", start_date="2020-01-01", end_date="2023-01-01")
df = df.sort_values(["ticker", "date"])
df["return"] = df.groupby("ticker")["close"].pct_change().astype('float32')
df = df.dropna(subset=["return"])
return_matrix = df.pivot(index="date", columns="ticker", values="return").astype("float32")

# Define benchmark functions
def dictionary():
    computing_rolling_correlations_dictionary(return_matrix, window=20)

def dataframe():
    computing_rolling_correlations_dataframe(return_matrix, window=20)

# Benchmark using callables (best practice)
dictionary_performance = timeit.timeit(dictionary, number=5)
dataframe_performance = timeit.timeit(dataframe, number=5)

print(f"Dictionary Performance: {dictionary_performance} seconds")
print(f"Dataframe Performance: {dataframe_performance} seconds")

"""Results
Dictionary Performance: 53.59297179999703 seconds
Dataframe Performance: 1143.6696672000107 seconds"""