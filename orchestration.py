import os
import pandas as pd
import subprocess
import shutil

from src.data_reader import data_load_zip
from src.correlation import (
    computing_daily_returns,
    pivot_returns,
    orchestrate_daily_correlation_summary_stats
)

def orchestrate_pipeline(
    zip_path="stock_data.zip",
    window=20,
    output_correlations_dir="daily_correlations_summary_stats",
    overwrite=False,
    start_date=None,
    end_date=None
):
    
    if os.path.exists(output_correlations_dir) and not overwrite:
        print(f"Data already exists in {output_correlations_dir}.")
        user_input = input("Do you want to recalculate the data? (y/n): ").strip().lower()
        if user_input != "y":
            print("Skipping data recomputation.")
            print("Launching Streamlit dashboard...")
            subprocess.run(["streamlit", "run", "app/app.py"])
            return
        else:
            print("Recomputing rolling correlation summary...")
            shutil.rmtree(output_correlations_dir)

    
    print("Loading Stock Data...")
    df = data_load_zip(zip_path)

    print("Computing daily returns...")
    returns = computing_daily_returns(df)

    print("Pivoting returns matrix...")
    return_matrix = pivot_returns(returns)

    print("Running rolling correlation summary...")
    orchestrate_daily_correlation_summary_stats(
        return_matrix,
        window=window,
        output_directory=output_correlations_dir
    )

    print("Launching Streamlit dashboard...")
    subprocess.run(["streamlit", "run", "app/app.py"])

if __name__ == "__main__":
    orchestrate_pipeline()