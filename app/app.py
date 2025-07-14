import streamlit as st
import pandas as pd
import os
import pickle
from datetime import datetime

"""
Create GUI for visualizing rolling correlation summary statistics using Streamlit
"""

SUMMARY_DIR = "daily_correlations_summary_stats" #file of daily summar stat .csv files

#loading and caching data for Streamlit dashboard
@st.cache_data
def load_summary_data(summary_dir):
    all_summaries = []
    for fname in sorted(os.listdir(summary_dir)):
        if fname.endswith(".pkl"):
            with open(os.path.join(summary_dir, fname), "rb") as f:
                summary = pickle.load(f)
                all_summaries.append(summary)
    return pd.DataFrame(all_summaries).sort_values("Date")

#formatting summary cards helper function
def display_summary_card(title, value):
    st.metric(label=title, value=round(value, 4))
#formatting top ticker tables helper function    
def display_top_table(title: str, data: list):
    df = pd.DataFrame(data)
    df.insert(0, "Rank", range(1, len(df) + 1))
    st.markdown(f"##### {title}")
    st.dataframe(df[["Rank", "ticker_1", "ticker_2", "correlation"]])

#Building the dashboard
st.title("Stock 20 Rolling Correlation Summary Dashboard")

df = load_summary_data(SUMMARY_DIR)
df["Date"] = pd.to_datetime(df["Date"])

# Sidebar date selector
date_selected = st.sidebar.date_input("Select a date", value=df["Date"].max(), min_value=df["Date"].min(), max_value=df["Date"].max())

# Extract summary for selected date
row = df[df["Date"] == pd.to_datetime(date_selected)].squeeze()

if row.empty:
    st.warning("No data available for the selected date.") #some days don't have price data (markets closed)
else:
    st.subheader(f"Summary Stats for {date_selected.strftime('%Y-%m-%d')}")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Mean Correlation", value=round(row["mean_correlation"], 4))

    with col2:
        st.metric(label="Median Correlation", value=round(row["median_correlation"], 4))

    with col3:
        st.metric(label="Std Dev", value=round(row["std_correlation"], 4))

    with col4:
        st.metric(label="Percent > 0.7", value=round(row["pct_above_0.7"], 4))

    with col5:
        st.metric(
            label="Entropy",
            value=round(row["correlation_entropy"], 4),
            help="Measures the unpredictability or diversity of correlation values. Higher values (~5-6) mean more variation than lower values (~2-3)."
            )

    st.subheader("Top Rolling 20 Correlations (Selected Day)")
    #correlations of interest table
    display_top_table("Top 20 Closest to 0", row["top_20_closest_to_zero"])
    display_top_table("Top 20 Closest to ±1", row["top_20_closest_to_one"])
    display_top_table("Top 5 Most Negative", row["top_5_most_negative"])

# Plot time series of summary stats
st.subheader("Time Series Overview")

st.markdown("**Mean, Median, and Percent > 0.7 Correlations Over Time**")
st.line_chart(df.set_index("Date")[["mean_correlation", "median_correlation", "pct_above_0.7"]])

st.markdown("**Standard Deviation of Correlations Over Time**")
st.line_chart(df.set_index("Date")[["std_correlation"]])

st.markdown("**Correlation Entropy Over Time**")
st.line_chart(df.set_index("Date")[["correlation_entropy"]])