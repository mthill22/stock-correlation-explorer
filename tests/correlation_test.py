import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) #adding this to help run from command line

from src.correlation import (
    computing_daily_returns,
    pivot_returns,
    compute_and_save_summary_stats,
    orchestrate_daily_correlation_summary_stats
)

import pytest
import pandas as pd
import numpy as np
import tempfile
import shutil
from datetime import datetime, timedelta
import pickle
import dask

#creating some sample data
@pytest.fixture
def sample_price_data():
    
    #sample dates
    dates = pd.date_range(end=datetime.today(), periods=25)
    
    # sample tickers
    tickers = ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN", 
        "META", "NFLX", "NVDA", "JPM", "BAC", 
        "WMT", "PG", "JNJ", "V", "MA",
        "UNH", "HD", "PFE", "KO", "PEP",
        "ABBV", "MRK", "COST", "AVGO", "XOM"]
    
    data = []

    # sample price data using random price changes
    for ticker in tickers:
        price = 100.0
        for date in dates:
            price += np.random.normal(0, 1)
            data.append({"Ticker": ticker, "Date": date, "Price": price})

    return pd.DataFrame(data)

#Adding Unit Tests
@pytest.fixture
def temp_output_dir():
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)

"""Unit Tests"""
#Testing the daily returns are computed sensibly
def testing_computing_daily_returns(sample_price_data):
    df = computing_daily_returns(sample_price_data)
    
    # Check that Return column exists
    assert "Return" in df.columns, f"Expected 'Return' column not found. Available columns: {list(df.columns)}"
    
    # Should have no NaN values after dropna()
    null_count = df["Return"].isnull().sum()
    assert null_count == 0, f"Found {null_count} null values in Return column. This suggests dropna() didn't work properly."
    
    # Each ticker should have 24 returns (25 price points - 1 for pct_change)
    min_returns = df.groupby("Ticker").size().min()
    assert min_returns >= 24, f"Expected at least 24 returns per ticker, but minimum was {min_returns}. Check pct_change calculation."

#Testing the return DataFrame is pivoted correctly
def testing_pivot_returns(sample_price_data):
    df_returns = computing_daily_returns(sample_price_data)
    return_matrix = pivot_returns(df_returns)
    
    # Should return a DataFrame
    assert isinstance(return_matrix, pd.DataFrame), f"Expected DataFrame, got {type(return_matrix)}. Check pivot operation."
    
    # Should have 25 columns (one per ticker)
    actual_cols = return_matrix.shape[1]
    assert actual_cols == 25, f"Expected 25 columns (one per ticker), got {actual_cols}. Shape: {return_matrix.shape}"
    
    # All columns should be float32 for memory efficiency
    unique_dtypes = return_matrix.dtypes.nunique()
    assert unique_dtypes == 1, f"Expected all columns to have same dtype (float32), but found {unique_dtypes} different dtypes: {return_matrix.dtypes.unique()}"

#main calc test
def testing_compute_and_save_summary_stats_creates_file(sample_price_data, temp_output_dir):
    # Prepare test data
    df_returns = computing_daily_returns(sample_price_data)
    return_matrix = pivot_returns(df_returns)

    # Use first 20 days as window, 21st day as current date
    window_slice = return_matrix.iloc[:20]
    current_date = return_matrix.index[20]

    # Create delayed task and execute it
    task = compute_and_save_summary_stats(window_slice, current_date, temp_output_dir)
    dask.compute(task)

    # Verify file was created with expected naming convention
    expected_filename = os.path.join(temp_output_dir, f"correlation_summary_{current_date.strftime('%Y-%m-%d')}.pkl")
    assert os.path.exists(expected_filename), f"Expected file not created: {expected_filename}. Files in directory: {os.listdir(temp_output_dir)}"

    # Verify file contents have expected structure
    with open(expected_filename, "rb") as f:
        summary = pickle.load(f)
    
    # Check that key summary statistics are present
    assert "mean_correlation" in summary, f"Missing 'mean_correlation' key. Available keys: {list(summary.keys())}"
    assert "top_20_closest_to_zero" in summary, f"Missing 'top_20_closest_to_zero' key. Available keys: {list(summary.keys())}"
    
    # Top 20 list should not exceed 20 items (could be less if fewer pairs exist)
    top_20_count = len(summary["top_20_closest_to_zero"])
    assert top_20_count <= 20, f"Expected <= 20 items in top_20_closest_to_zero, got {top_20_count}"

#Testing the main pipeline
def testing_orchestrate_daily_correlation_summary_stats_end_to_end(sample_price_data, temp_output_dir):
    # Prepare test data
    df_returns = computing_daily_returns(sample_price_data)
    return_matrix = pivot_returns(df_returns)

    # Run the full pipeline with small batch size for testing
    orchestrate_daily_correlation_summary_stats(
        return_matrix=return_matrix,
        window=20,  # Use 20-day rolling window
        output_directory=temp_output_dir,
        batch_size=3  # Small batch size for testing
    )

    # Verify that output files were created
    saved_files = [f for f in os.listdir(temp_output_dir) if f.endswith(".pkl")]
    file_count = len(saved_files)
    expected_files = len(return_matrix.index) - 20  # Should have one file per day after 20-day window
    assert file_count > 0, f"No output files created. Directory contents: {os.listdir(temp_output_dir)}"
    
    # More detailed check - should have roughly the expected number of files
    assert file_count == expected_files, f"Expected {expected_files} files (one per day after 20-day window), got {file_count}. Files: {saved_files}"

    # Validate structure of one of the saved files
    test_file = os.path.join(temp_output_dir, saved_files[0])
    with open(test_file, "rb") as f:
        summary = pickle.load(f)

    # Verify the summary is a dictionary with expected keys
    assert isinstance(summary, dict), f"Expected summary to be dict, got {type(summary)}"
    assert "correlation_entropy" in summary, f"Missing 'correlation_entropy' key in summary. Available keys: {list(summary.keys())}"