### Machine learning model to supplement the Monte Carlo Simulation

The model building will be split into 3 sections mainly becasue the integrations of these model serves the following : 


1. Volatility Prediction using LSTM (TensorFlow)
2. Market Regime Detection using K-Means Clustering (Scikit-learn)
3. Trend Analysis using Linear Regression (Statsmodels)

----------------------------------------
1. Volatility Prediction (LSTM – TensorFlow)
Purpose:
 - Forecast the future volatility of assets based on historical price returns using time series modeling.
Implementation Steps:
 - Normalize and reshape the historical return data for LSTM input.
 - Create time windows (e.g. 30 days of returns → 1 day volatility prediction).
 - Build and train an LSTM model using TensorFlow/Keras.
 - Evaluate using RMSE and visualize predicted vs actual volatility.

2. Market Regime Classification (K-Means – Scikit-learn)
Purpose:
 - Detect and label distinct market conditions like high-volatility, low-volatility, or bullish/bearish regimes.
Input Features:
 - Daily returns
 - Volatility (from part 1 or rolling std dev)
 - Trading volume (if available)
Implementation Steps:
 - Use StandardScaler to normalize features.
 - Run KMeans(n_clusters=3) to classify into market regimes.
 - Plot regime clusters using PCA or t-SNE for interpretation.
 - Label your dataset with regime identifiers for simulation enhancement.

3. Trend Analysis (Linear Regression – Statsmodels)
Purpose:
 - Use macro indicators or aggregate signals to detect long-term trends.
Implementation Steps:
 - Build regression models using selected indicators (e.g. moving averages, momentum, fundamental indicators if collected).
 - Evaluate coefficient significance (p-values) and model summary from Statsmodels.
 - Interpret linear trends and use insights to adjust portfolio strategies.

----------------------------------------

### Integration with Monte Carlo Simulation

Once these models are ready:
 - Use predicted volatility to update asset return distributions before simulation.
 - Modify simulation logic to condition on regime clusters.
 - Use trend indicators to weight scenarios (e.g. bullish regime → higher expected returns).