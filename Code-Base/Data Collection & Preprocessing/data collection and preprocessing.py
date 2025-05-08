import yfinance as yf
import pandas as pd
import time
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

 # Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from the environment variable
database_url = os.getenv("DATABASE_URL")

# Create the engine using the environment variable
engine = create_engine(database_url)

# --- PostgreSQL connection ---
# engine = create_engine('postgresql://akilfiros:@127.0.0.1:5432/postgres')

# --- Data Collection ---
tickers = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOG", "GOOGL", "META", "TSLA", "PEP", "AVGO",
    "COST", "CSCO", "ADBE", "NFLX", "CMCSA", "AMD", "QCOM", "INTC", "HON",
    "INTU", "AMGN", "SBUX", "AMAT", "MDLZ", "ADI", "ISRG", "BKNG", "LRCX", "GILD",
    "ADP", "VRTX", "MU", "REGN", "KLAC", "MRVL", "SNPS", "PANW", "CDNS",
    "CSX", "MELI", "MNST", "LULU", "FTNT", "NXPI", "KDP", "ORLY", "MAR",
    "CTAS", "PAYX", "EXC", "ODFL", "TEAM", "XEL", "FAST", "BIIB", "ROST", "CTSH",
    "CHTR", "DLTR", "PCAR", "VRSK", "WBD", "AEP", "IDXX", "MCHP", "AZN", "EA",
    "ANSS", "ALGN", "KHC", "BKR", "CDW", "DDOG", "CPRT", "CRWD", "DXCM",
    "ZS", "CEG", "GFS", "PLTR", "MSTR", "AXON", "ARM", "SMCI", "APP",
    "GEHC", "ON", "TTWO", "PDD", "RIVN", "WBA", "ILMN", "LCID", "OKTA", "NTES",
    "BIDU", "DOCU", "MTCH", "VRSN", "TCOM"
]

start_date = "2020-01-01"
end_date = "2025-05-07"

# Function to fetch data in batches with exponential backoff
def fetch_data_with_backoff(tickers, start_date, end_date, max_retries=5, base_delay=60):
    all_data = []
    failed_tickers = []
    
    for ticker in tickers:
        delay = base_delay
        for attempt in range(max_retries):
            try:
                print(f"Downloading: {ticker} (Attempt {attempt + 1})")
                data = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=True)
                if data.empty:
                    print(f"⚠ Warning: No data received for {ticker}.")
                    failed_tickers.append(ticker)
                else:
                    all_data.append(data)
                break  # Exit retry loop if successful
            except yf.YFRateLimitError:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        else:
            print(f"❌ Failed to fetch data for {ticker} after {max_retries} attempts.")
            failed_tickers.append(ticker)
    
    if all_data:
        return pd.concat(all_data, axis=1), failed_tickers
    else:
        raise Exception("No data fetched due to rate limits.")

# Fetch data with exponential backoff
data, failed_tickers = fetch_data_with_backoff(tickers, start_date, end_date)
print(f"Failed tickers: {failed_tickers}")

# Print columns to verify structure
print("Columns before processing:", data.columns)

# --- Fix MultiIndex Problem ---
data.reset_index(inplace=True)  # Ensure 'Date' is a column
data = data.copy()  # Fix fragmentation warning

# Remove duplicate columns
data = data.loc[:, ~data.columns.duplicated()]

# Rename columns: replace 'Adj Close' with 'Close'
new_columns = ['Date']
for col_tuple in data.columns[1:]:  # Skip 'Date' column
    if isinstance(col_tuple, tuple) and len(col_tuple) == 2:
        price_type, ticker = col_tuple
    else:
        price_type, ticker = col_tuple if isinstance(col_tuple, str) else (col_tuple, "UNKNOWN")

    if price_type == 'Adj Close':
        price_type = 'Close'

    new_columns.append(f"{price_type}_{ticker}")

data.columns = new_columns
print("Columns after reset_index():", data.columns)

# --- Data Reshaping Using `melt()` ---
data = data.melt(id_vars=['Date'], var_name='column', value_name='value')

# Ensure column names are valid before splitting
data = data.dropna(subset=['column'])  # Remove NaN values

# Handle missing underscores safely, filling missing values properly
split_columns = data['column'].apply(lambda x: x.split('_', 1) if '_' in x else [x, "UNKNOWN"])
split_df = pd.DataFrame(split_columns.tolist(), index=data.index)

# Ensure the split results match expected dimensions
if split_df.shape[1] == 2:
    data[['price_type', 'ticker']] = split_df
else:
    print("⚠ Warning: Column splitting produced unexpected results!")
    data['price_type'] = "UNKNOWN"
    data['ticker'] = "UNKNOWN"

# Drop the original 'column' since we split it
data = data.drop(columns=['column'])

# **Ensure only 'Close' and 'Volume' are pivoted**
if 'price_type' in data.columns:
    data = data[data['price_type'].isin(['Close', 'Volume'])]  # Keep only relevant data
else:
    raise KeyError("Column 'price_type' not found in DataFrame.")

# Pivot to structure correctly
if 'price_type' in data.columns and 'ticker' in data.columns:
    data = data.pivot_table(index=['Date', 'ticker'], columns='price_type', values='value').reset_index()
else:
    raise ValueError("DataFrame is missing required columns for pivoting.")

# Print column count before renaming (debugging)
print("Column count before renaming:", len(data.columns))

# Rename columns to match PostgreSQL schema
expected_columns = ['Date', 'ticker', 'Close', 'Volume']
if len(data.columns) == len(expected_columns):
    data.columns = ['date', 'ticker', 'close', 'volume']
else:
    print("⚠ Warning: Unexpected column count. Filling missing columns with NaN.")
    for col in expected_columns:
        if col not in data.columns:
            data[col] = np.nan
    data = data[expected_columns]

# --- Data Cleaning ---
data['date'] = pd.to_datetime(data['date'], errors='coerce')  # Ensure date format
data['ticker'] = data['ticker'].astype(str)  # Ensure ticker is string
data['close'] = pd.to_numeric(data['close'], errors='coerce')  # Ensure price is float
data['volume'] = pd.to_numeric(data['volume'], errors='coerce').fillna(0).astype(int)  # Ensure volume is integer

# --- Store Data in PostgreSQL ---
data.to_sql('financial_data', engine, if_exists='replace', index=False)

print("✅ Data successfully stored in PostgreSQL.")

