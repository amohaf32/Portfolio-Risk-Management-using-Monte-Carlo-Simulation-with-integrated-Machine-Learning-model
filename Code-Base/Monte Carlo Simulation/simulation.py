import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from sqlalchemy import create_engine

# --- PostgreSQL Connection ---
engine = create_engine('postgresql://akilfiros:@127.0.0.1:5432/postgres')

# --- Load Processed Data ---
query = "SELECT date, ticker, close FROM financial_data"
data = pd.read_sql(query, engine)
data['date'] = pd.to_datetime(data['date'])

# --- Prepare Data for Monte Carlo Simulation ---
# Pivot data so that each column is a ticker and rows are dates
returns = data.pivot(index='date', columns='ticker', values='close').pct_change().dropna()

# Define simulation parameters
num_simulations = 1000  # Number of Monte Carlo Simulations
num_days = 252  # Number of trading/working days in a year
initial_investment = 1000  # Starting capital

# Calculate mean and covariance of returns
mean_returns = returns.mean()
cov_matrix = returns.cov()

# --- Monte Carlo Simulation Function ---
def monte_carlo_simulation(portfolio_weights, num_simulations, num_days):
    portfolio_returns = []
    for _ in range(num_simulations):
        daily_returns = np.random.multivariate_normal(mean_returns, cov_matrix, num_days)
        portfolio_daily_returns = daily_returns @ portfolio_weights
        portfolio_cumulative_returns = np.cumprod(1 + portfolio_daily_returns) * initial_investment
        portfolio_returns.append(portfolio_cumulative_returns[-1])  # Store final portfolio value
    return np.array(portfolio_returns)

# Example: Equal-weighted portfolio
num_assets = len(mean_returns)
portfolio_weights = np.ones(num_assets) / num_assets  # Equal weight for all assets

# Run Simulation
simulated_portfolio_values = monte_carlo_simulation(portfolio_weights, num_simulations, num_days)

# --- Calculate Risk Metrics (VaR & CVaR) ---
var_95 = np.percentile(simulated_portfolio_values, 5)  # 5% worst-case loss
cvar_95 = simulated_portfolio_values[simulated_portfolio_values <= var_95].mean()

print(f"95% Value at Risk (VaR): ${initial_investment - var_95:.2f}")
print(f"95% Conditional Value at Risk (CVaR): ${initial_investment - cvar_95:.2f}")

# --- Visualization ---
plt.figure(figsize=(10, 5))
sns.histplot(simulated_portfolio_values, bins=50, kde=True, color='blue')
plt.axvline(var_95, color='red', linestyle='dashed', label=f'VaR 95%: ${var_95:.2f}')
plt.axvline(cvar_95, color='orange', linestyle='dashed', label=f'CVaR 95%: ${cvar_95:.2f}')
plt.title("Monte Carlo Simulation Portfolio Distribution")
plt.xlabel("Portfolio Value")
plt.ylabel("Frequency")
plt.legend()
plt.show()
