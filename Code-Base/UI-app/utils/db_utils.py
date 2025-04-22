import pandas as pd
from sqlalchemy import create_engine

# --- PostgreSQL connection ---
engine = create_engine("postgresql://akilfiros:@127.0.0.1:5432/postgres")

# --- Get unique tickers for dropdown ---
def get_all_tickers():
    query = "SELECT DISTINCT ticker FROM financial_data ORDER BY ticker"
    df = pd.read_sql(query, engine)
    return sorted(df['ticker'].tolist())

# --- Get historical price data ---
def get_price_data():
    query = "SELECT date, ticker, close FROM financial_data"
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

# --- Get optimal weights (if saved) ---
def get_optimal_weights():
    try:
        query = "SELECT * FROM optimal_portfolio_weights"
        df = pd.read_sql(query, engine)
        return df.set_index('ticker')['weight'].to_dict()
    except:
        return {}
