# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 21:39:29 2025

@author: Dana's PC
"""
import pandas as pd

from src.correlation import get_trailing_correlations
from src.data_reader import data_load_zip

#df = data_load_zip("tests/test_data.zip")
df = data_load_zip("stocks_data.zip")
rolling_corrs = get_trailing_correlations(df, window=5)

correlations_for_date = rolling_corrs[rolling_corrs['date'] == pd.Timestamp("2000-01-31 05:00:00")]

print(correlations_for_date)