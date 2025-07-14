# # Stock Rolling Correlation Analysis Dashboard

A Python application for analyzing rolling correlations between stock prices using a 20-day window, with an interactive Streamlit dashboard for visualization.

## Overview

This project computes rolling 20-day correlations between stock pairs and provides summary statistics to understand market behavior patterns. The analysis helps identify periods of high/low correlation, market stress indicators, and relationship patterns between different stocks.

Please save .Zip file of .csv stock data in main directory before proceeding with the rest of the instructions.

## Project Structure

```
├── app.py                 # Streamlit dashboard application
├── correlation.py         # Core correlation computation logic
├── data_reader.py        # Data loading utilities
├── helpers.py            # General utility functions
├── daily_correlations_summary_stats/  # Output directory for results
└── README.md
```

## Key Components

### 1. Data Processing Pipeline (`correlation.py`)
- **Daily Returns Calculation**: Computes percentage changes in stock prices
- **Data Pivoting**: Transforms data into a matrix format suitable for correlation analysis
- **Rolling Window Analysis**: Uses 20-day windows to compute correlations
- **Batch Processing**: Processes data in chunks to manage memory usage

### 2. Summary Statistics Computation
For each trading day, the system calculates:
- **Basic Stats**: Mean, median, standard deviation of all pairwise correlations
- **Threshold Analysis**: Percentage of correlations above 0.7 (high correlation indicator)
- **Entropy Measure**: Quantifies the diversity/unpredictability of correlation values
- **Top Correlations**: Identifies pairs closest to 0, ±1, and most negative correlations

### 3. Interactive Dashboard (`app.py`)
- **Date Selection**: Navigate through different time periods
- **Summary Cards**: Display key metrics for selected dates
- **Time Series Visualization**: Track correlation patterns over time
- **Top Pairs Tables**: Show specific stock pairs with notable correlations

## Technical Design Decisions

### Memory Optimization
- Used `float32` instead of `float64` to reduce memory footprint
- Implemented batch processing to handle large datasets
- Leveraged Dask for parallel computation of summary statistics

### Data Structure Choices
- **Categorical Data Types**: Used for ticker symbols to save memory
- **Pickle Serialization**: Chosen for complex nested data structures containing lists and dictionaries
- **Upper Triangle Extraction**: Only computed unique correlation pairs to avoid redundancy

### Performance Considerations
- **Caching**: Streamlit `@st.cache_data` for data loading
- **Vectorized Operations**: NumPy operations for statistical calculations
- **Lazy Evaluation**: Dask delayed execution for batch processing

## Mathematical Approach

### Correlation Entropy
The entropy measure quantifies how "spread out" correlation values are:
- Higher entropy (~5-6): More diverse correlation values
- Lower entropy (~2-3): Correlations clustered around specific values
- Calculated using: `entropy = -Σ(p_i * log2(p_i))` where p_i are histogram probabilities

### Rolling Window Logic
- Uses exactly 20 trading days for each correlation calculation
- Window slides daily, providing continuous correlation tracking
- Handles missing data by dropping NaN values before correlation computation

## Setup Instructions

### Environment Setup
This project uses conda for dependency management. To set up the environment:

1. **Clone the repository** (if applicable) or download the project files
2. **Create the conda environment** from the provided environment file:
   ```bash
   conda env create -f environment.yml
   ```
3. **Activate the environment**:
   ```bash
   conda activate correlation-analysis
   ```
4. Add .zip of csv file stock data
### Verify Installation
You can verify that all dependencies are installed correctly by running:
```bash
python -c "import pandas, numpy, streamlit, dask; print('All dependencies imported successfully')"
```

##Key Consideration
The data set is far too large to calculate and display all correlations data. This would exceed available memory, require ~100GB of disk space if saved locally, and would be infeasable to display in a GUI for performance reasons.

A summary approach was taken to pull out 1) Key ticker pairs of interest 2) Summary stats showing trends in the correlations across the stocks


###Key Challenges
- Data set size: 5000 stocks over ~5 years
- Context: There was limited context provided for what specific information the end user would like to see
- Correlation Matrix Datatype: Dictionary was more performant to build but long DataFrame is more performant to display
- Optimizing Parallelization: Getting batch sizes that would not exceed memory but still perform calcs performantly
- Machine Specs: Built on a machine with very limited memory, CPU, and disk space

## Usage

### Running the Project (Processing Data & Launching Dashboard)
Run orchestration.py from the project root folder. This will 

Make sure you have saved your .zip file of csv stock data
## Data Requirements

### Input Format
- **ZIP file** containing CSV files with columns: `Ticker`, `Date`, `Price`
- **Date format**: Should be parseable by pandas
- **Price data**: Numeric values, missing values will be dropped

### Output Format
- **Pickle files**: One per trading day with comprehensive statistics
- **Nested structure**: Contains both summary stats and detailed pair information

## Key Features

### Market Stress Detection
- High correlation periods often indicate market stress
- The `pct_above_0.7` metric helps identify these periods
- Entropy drops when correlations become more uniform

### Relationship Discovery
- Identifies consistently correlated stock pairs
- Tracks changes in correlation patterns over time
- Highlights negative correlations (potential hedging opportunities)

### Scalability
- Batch processing handles large datasets
- Configurable window sizes and batch sizes
- Memory-efficient data types throughout

## Potential Extensions

1. **Different Window Sizes**: Easy to modify the 20-day window
2. **Sector Analysis**: Group correlations by industry sectors
3. **Volatility Integration**: Combine with volatility measures
4. **Real-time Updates**: Add streaming data capabilities
5. **Statistical Testing**: Add significance tests for correlations
6. **Incremental Data Loading**: Adding ability to load new data vs. full load
7. **Correlation Mean Deviation Identification**: Identify potential correlation mean reversion bets
8. **Handling NA Strategy**: Consider strategies for deriving price if NA
- 

## Testing
- Unit tests available in Tests folder

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **streamlit**: Web dashboard framework
- **dask**: Parallel computing for batch processing
- **pickle**: Data serialization

## Performance Notes

- Processing time scales quadratically with number of stocks
- Memory usage depends on the number of trading days and stocks
- Batch processing helps manage memory for large datasets
- Consider using more powerful hardware for datasets with >1000 stocks

## Sources
- https://docs.dask.org/en/stable/dataframe.html
- https://docs.dask.org/en/stable/best-practices.html
- https://pandas.pydata.org/docs/reference/api/pandas.core.window.rolling.Rolling.corr.html
- https://stackoverflow.com/questions/44914845/rolling-mean-of-correlation-matrix
- https://www.linkedin.com/pulse/comparative-study-among-csv-feather-pickle-parquet-loyola-gonz%C3%A1lez
- https://rigtorp.se/2011/01/01/rolling-statistics-numpy.html
- https://matthewrocklin.com/blog/work/2015/03/16/Fast-Serialization
- https://docs.streamlit.io/develop/concepts/architecture/caching
- https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
- https://www.nature.com/articles/srep00752
- https://pandas.pydata.org/docs/user_guide/categorical.html
- https://www.nature.com/articles/s41598-019-47210-8
