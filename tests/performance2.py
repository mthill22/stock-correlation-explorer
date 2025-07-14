"""Performance testing of runtime with dictionary vs. upper trinagle dictionary"""

import timeit
import pandas as pd
from src.correlation import computing_rolling_correlations_dictionary, computing_rolling_correlations_dictionary_sliced
from src.data_reader import data_load_zip


df = data_load_zip("stocks_data.zip", start_date="2020-01-01", end_date="2023-01-01")
df = df.sort_values(["ticker", "date"])
df["return"] = df.groupby("ticker")["close"].pct_change().astype('float32')
df = df.dropna(subset=["return"])
return_matrix = df.pivot(index="date", columns="ticker", values="return").astype("float32")

# Define benchmark functions
def dictionary():
    computing_rolling_correlations_dictionary(return_matrix, window=20)

def dictionary_sliced():
    computing_rolling_correlations_dictionary_sliced(return_matrix, window=20)

# Benchmark using callables (best practice)
dictionary_performance = timeit.timeit(dictionary, number=5)
dictionary_sliced_performance = timeit.timeit(dictionary_sliced, number=5)

print(f"Standard Dictionary Performance: {dictionary_performance} seconds")
print(f"Dictionary Sliced Performance: {dictionary_sliced_performance} seconds")

"""Results: Standard Dictionary Performance: 73.78329409999424 seconds
Dictionary Sliced Performance: 2987.624476900004 seconds"""