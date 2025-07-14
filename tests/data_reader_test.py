import pandas as pd
import pytest
import os #lines 3-5 added to work around issue running pytest from command line
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_reader import data_load_zip

@pytest.fixture
def test_df():
    test_data = "stock_data.zip" #file path for test data, must be a .zip
    return data_load_zip(test_data)

def testing_is_df(test_df):
    assert isinstance(test_df, pd.DataFrame), "Expected a DataFrame - your data is not a DataFrame"

def test_ticker_col(test_df):
    assert "Ticker" in test_df.columns, "Missing 'Ticker' column in DataFrame"

    for Ticker in test_df["Ticker"].dropna().unique():
        assert len(Ticker) <= 5, f"Ticker too long: '{Ticker}'"
        assert Ticker.isalnum(), f"Ticker contains invalid characters: '{Ticker}'"
        assert len(Ticker) > 0, f"Ticker is empty: '{Ticker}'"
    
def testing_contains_req_cols(test_df):
    req_cols = {"Date", "Price"} #add any required columns here, note ticker is expected to be provided in file name
    assert req_cols.issubset(test_df.columns), f"Missing at least one required column: {req_cols - set(test_df.columns)}"

def testing_empty_df(test_df):
    assert len(test_df) > 0, "DataFrame is empty - no rows found"    
    

    #testing the data types of the date and returns columns
    #tesing the value of return and making sure it makes sense