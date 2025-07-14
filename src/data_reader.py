import pandas as pd
import zipfile

""" 
The purpose of this function is to load data from a .zip folder of multlipe .csv files and load the data into a Pandas DataFrame

Each .csv file must contain the following columns: 

- "Ticker": cast as a category for memory efficiency.
- "Price": cast as float32 for memory efficiency.
- "Date": cast as datatime.

Arguments: The funciton takes one argument for the path for the data to be loaded

Return: Pandas DataFrame with rows of price sorted by Ticker and Date. NOTE: ALL ROWS CONTAINING MISSING PRICE DATA ARE DROPPED!
    
"""

def data_load_zip(zip_path: str) -> pd.DataFrame:
    data = [] # List to collect DataFrames from each CSV file
    
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = sorted(zip_ref.namelist()) #Open .zip

        for file_name in file_list:
            if not file_name.endswith('.csv'): 
                continue #skip anything not a .csv

            with zip_ref.open(file_name) as f:
                df = pd.read_csv(
                    f,
                    usecols=["Ticker", "Date", "Price"], #columns to load, 
                    dtype={"Ticker": "category", "Price": "float32"}, #data casting
                    parse_dates=["Date"] #date parsing
                )
                data.append(df) #add the DataFrame for the .csv file to the list


    full_df = pd.concat(data, ignore_index=True) #combine DataFrames in list into one DataFrame
    full_df = full_df.dropna(subset=["Price"]) #removes rows where price is NA

    return full_df.sort_values(["Ticker", "Date"])