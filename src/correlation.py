import pandas as pd
import numpy as np
import os
from src.helpers import pickle_save
import dask
from dask import delayed

"""
The purpose of this file is to calculate rolling 20 day corrleations for stock data and calculate summary statistics at the daily level
Both memory and computation time were constrained due to the size of the intended data set (5000 stocks over ~5 years)
Dask was used to help work around these constraints by running calculations in parallel

The steps to achieve this were:
1. Computing daily percentage returns per stock
2. Pivoting data into a return matrix
3. Calculating rolling correlation matrices
4. Calculating and saving summary statistics
"""

#Computes daily percentage returns for each stock. Pandas DataFrame[Ticker, Date, Price] -> Pandas DataFrame[Ticker, Date, Price, Returns]
def computing_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.sort_values(["Ticker", "Date"])#.copy()
    df["Return"] = df.groupby("Ticker", observed=True)["Price"].pct_change().astype('float32')
    #print(df.dropna(subset=["return"]).head)
    return df.dropna(subset=["Return"])

#Pivoting dataframe to rows of dates and columns of ticker, returns
def pivot_returns(df_returns: pd.DataFrame) -> pd.DataFrame:
    #print(df_returns.pivot(index="date", columns="ticker", values="return").astype('float32'))
    return df_returns.pivot(index="Date", columns="Ticker", values="Return").astype('float32')

"""
    For a given window of stock returns:
    - Computes correlation matrix
    - Extracts upper triangle of correlations
    - Computes summary stats (mean, median, std, entropy, etc.)
    - Identifies interesting ticker pairs (high/low/zero correlation)
    - Saves results as a pickle file with the date in the filename
    
    Delayed is used to hold execution until dask has optimized the calculations for performance reasons
    """
    
@delayed
def compute_and_save_summary_stats(
    window_slice: pd.DataFrame,
    current_date: pd.Timestamp,
    output_directory: str
) -> None:
    # Calculate correlation matrix
    corr_matrix = window_slice.corr().astype('float32')
    
    # Get upper triangle values
    tickers = corr_matrix.columns.to_numpy()
    n = len(tickers)
    upper_indices = np.triu_indices(n, k=1)
    corr_values = corr_matrix.values[upper_indices].astype('float32')
    
    # Map back to ticker pairs
    ticker_pairs = list(zip(tickers[upper_indices[0]], tickers[upper_indices[1]]))

    # Basic summary stats
    mean_corr = np.mean(corr_values)
    median_corr = np.median(corr_values)
    std_corr = np.std(corr_values)
    pct_above_0_7 = np.mean(np.abs(corr_values) > 0.7)

    # Correlation entropy
    hist, _ = np.histogram(corr_values, bins=50, range=(-1, 1))
    probabilities = hist / hist.sum()
    probabilities = probabilities[probabilities > 0]
    entropy = -np.sum(probabilities * np.log2(probabilities))

    # Get top N indices
    def get_top_pairs(indices):
        return [
            {
                "ticker_1": ticker_pairs[i][0],
                "ticker_2": ticker_pairs[i][1],
                "correlation": float(corr_values[i])
            }
            for i in indices
        ]
    
    #get the index of each correlation of interest, so ticker pairs can be assigned to the value
    abs_corr = np.abs(corr_values)
    closest_to_zero_idx = np.argpartition(abs_corr, 20)[:20]
    closest_to_one_idx = np.argpartition(-abs_corr, 20)[:20]
    most_negative_idx = np.argpartition(corr_values, 5)[:5]

    #Summary dictionary
    summary = {
        "Date": current_date.strftime('%Y-%m-%d'),
        "mean_correlation": float(mean_corr),
        "median_correlation": float(median_corr),
        "std_correlation": float(std_corr),
        "pct_above_0.7": float(pct_above_0_7),
        "correlation_entropy": float(entropy),
        "top_20_closest_to_zero": get_top_pairs(closest_to_zero_idx),
        "top_20_closest_to_one": get_top_pairs(closest_to_one_idx),
        "top_5_most_negative": get_top_pairs(most_negative_idx),
    }
    
    #save the summary file with pickle
    filename = os.path.join(output_directory, f"correlation_summary_{current_date.strftime('%Y-%m-%d')}.pkl")
    pickle_save(summary, filename)

"""
Orchestrates the rolling correlation analysis over a DataFrame of stock returns.
For each date, takes a trailing window and computes correlation stats.
Uses Dask to process in parallel. Increasing batch_size will decrease run time but increase the memory usage
"""

def orchestrate_daily_correlation_summary_stats(
    return_matrix: pd.DataFrame,
    window: int = 20,
    output_directory: str = "daily_correlations_summary_stats",
    batch_size: int = 50  #Increasing this will increase memory usage and decrease run time
):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory) #create output directory (where one doesn't exist)
    
    dates_to_process = return_matrix.index[window:] #getting list of dates
    
    # Process batches
    for i in range(0, len(dates_to_process), batch_size):
        batch_dates = dates_to_process[i:i + batch_size]
        tasks = []
        
        for current_date in batch_dates:
            #setting window for rolling corrleation calc
            window_start_date_idx = return_matrix.index.get_loc(current_date) - window
            window_slice = return_matrix.iloc[window_start_date_idx : return_matrix.index.get_loc(current_date)]
            #Adding Dask delayed task
            task = compute_and_save_summary_stats(window_slice, current_date, output_directory)
            tasks.append(task)
        
        print(f"Processing batch {i//batch_size + 1}/{(len(dates_to_process) + batch_size - 1)//batch_size}...")
        dask.compute(*tasks) #execute the delayed tasks
        print(f"Completed batch {i//batch_size + 1}")