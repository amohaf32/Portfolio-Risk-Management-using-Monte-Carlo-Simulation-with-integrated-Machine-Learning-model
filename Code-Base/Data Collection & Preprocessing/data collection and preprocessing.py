import yfinance as yf
import pandas as pd 
from sqlalchemy import create_engine

# --- PostgreSQL connection ---

engine = create_engine('postgresql://akilfiros:@127.0.0.1:5432/postgres')

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
end_date = "2024-12-31"

# Download stock data
data = yf.download(tickers, start=start_date, end=end_date, interval="1d")

# Print columns to verify structure
# Print columns before processing
print("Columns before processing:", data.columns)

# --- Fix MultiIndex Problem ---
data.reset_index(inplace=True)  # Ensure 'Date' is a column

# Rename `Date` column properly (flatten MultiIndex)
data.columns = ['Date'] + [f"{col[0]}_{col[1]}" for col in data.columns[1:]]
print("Columns after reset_index():", data.columns)  # Debugging step

# --- Data Reshaping Using `melt()` ---
# Convert wide MultiIndex DataFrame into long format
data = data.melt(id_vars=['Date'], var_name='column', value_name='value')

# Extract 'Close' and 'Volume' columns
data[['price_type', 'ticker']] = data['column'].str.split('_', expand=True)
data = data.drop(columns=['column'])

# **Ensure only 'Close' and 'Volume' are pivoted**
data = data[data['price_type'].isin(['Close', 'Volume'])]  # Keep only relevant data

# Pivot to structure correctly
data = data.pivot_table(index=['Date', 'ticker'], columns='price_type', values='value').reset_index()

# Print column count before renaming (debugging)
print("Column count before renaming:", len(data.columns))

# Rename columns to match PostgreSQL schema
expected_columns = ['Date', 'ticker', 'Close', 'Volume']
if len(data.columns) == len(expected_columns):
    data.columns = ['date', 'ticker', 'close', 'volume']
else:
    raise ValueError(f"Unexpected column count: {len(data.columns)}. Expected: {len(expected_columns)}")

# --- Data Cleaning ---
data['date'] = pd.to_datetime(data['date'])  # Ensure date format
data['ticker'] = data['ticker'].astype(str)  # Ensure ticker is string
data['close'] = data['close'].astype(float)  # Ensure price is float
data['volume'] = data['volume'].fillna(0).astype(int)  # Ensure volume is integer

# --- Store Data in PostgreSQL ---
data.to_sql('financial_data', engine, if_exists='replace', index=False)

print("✅ Data successfully stored in PostgreSQL.")
