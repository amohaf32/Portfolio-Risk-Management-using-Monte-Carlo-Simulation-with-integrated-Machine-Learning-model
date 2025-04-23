import pandas as pd
import numpy as np
from utils.db_utils import get_price_data

def run_portfolio_simulation(tickers, weights, days=252, paths=1000):
    # --- Get clean price data ---
    df = get_price_data()
    df = df[df['ticker'].isin(tickers)]
    
    # Pivot to date x ticker
    price_df = df.pivot(index='date', columns='ticker', values='close').dropna()

    # --- Compute log returns ---
    log_returns = np.log(price_df / price_df.shift(1)).dropna()

    # --- Initialize simulation matrix ---
    simulations = np.zeros((days, paths))

    for i, ticker in enumerate(tickers):
        mu = log_returns[ticker].mean() * 252
        sigma = log_returns[ticker].std() * np.sqrt(252)
        start_price = price_df[ticker].iloc[-1]

        # Simulate asset paths
        dt = 1 / 252
        random_walks = np.random.normal(loc=(mu - 0.5 * sigma**2) * dt,
                                        scale=sigma * np.sqrt(dt),
                                        size=(days, paths))
        price_paths = start_price * np.exp(np.cumsum(random_walks, axis=0))

        # Add to portfolio matrix
        simulations += price_paths * weights[i]

    return simulations
