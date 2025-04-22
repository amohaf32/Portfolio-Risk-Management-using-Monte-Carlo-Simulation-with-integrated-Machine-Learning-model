from dash import Input, Output, State, html
import plotly.graph_objs as go
import numpy as np
from utils.simulation_runner import run_portfolio_simulation

def register_callbacks(app):

    # --- Populate ticker dropdown from PostgreSQL on app load ---
    @app.callback(
        Output("ticker-dropdown", "options"),
        Input("ticker-dropdown", "id")
    )
    def populate_ticker_dropdown(_):
        from utils.db_utils import get_all_tickers
        tickers = get_all_tickers()
        return [{"label": t, "value": t} for t in tickers]

    # --- Equal Weight Button: Auto-fill weights field ---
    @app.callback(
        Output("weight-input", "value"),
        Input("equal-weight-btn", "n_clicks"),
        State("ticker-dropdown", "value")
    )
    def assign_equal_weights(n_clicks, selected_tickers):
        if not selected_tickers:
            return ""
        equal_weight = round(1 / len(selected_tickers), 4)
        weight_list = [equal_weight] * len(selected_tickers)
        return ", ".join(map(str, weight_list))

    # --- Run Simulation Button: Triggers MC simulation and updates output ---
    @app.callback(
        Output("portfolio-plot", "figure"),            # Fan chart
        Output("risk-metrics-output", "children"),     # Text metrics (VaR, CVaR)
        Output("allocation-plot", "figure"),           # Bar chart of weights
        Output("error-message", "children"),           # Error banner

        Input("run-sim-btn", "n_clicks"),              # Trigger on click
        State("ticker-dropdown", "value"),             # Get tickers
        State("weight-input", "value")                 # Get weights from input
    )
    def run_simulation(n_clicks, tickers, weight_str):
        if not n_clicks or not tickers or not weight_str:
            return go.Figure(), "", go.Figure(), "⚠️ Please select tickers and weights before running."

        # --- Parse and validate weights ---
        try:
            weights = list(map(float, weight_str.split(",")))
            weights = [w for w in weights if w >= 0]
            if len(weights) != len(tickers) or not np.isclose(sum(weights), 1.0, atol=0.01):
                return go.Figure(), "", go.Figure(), "⚠️ Number of weights must match tickers and sum to 1."
        except:
            return go.Figure(), "", go.Figure(), "⚠️ Invalid weight format."

        # --- Run backend simulation ---
        try:
            sims = run_portfolio_simulation(tickers, weights)
        except Exception as e:
            return go.Figure(), "", go.Figure(), f"❌ Simulation error: {str(e)}"

        # --- Create portfolio path fan chart ---
        fig = go.Figure()
        for i in range(min(sims.shape[1], 100)):  # limit to 100 paths for visibility
            fig.add_trace(go.Scatter(
                y=sims[:, i],
                mode='lines',
                line=dict(width=1),
                opacity=0.2,
                showlegend=False
            ))
        fig.update_layout(
            title="Simulated Portfolio Value Paths",
            xaxis_title="Days",
            yaxis_title="Portfolio Value"
        )

        # --- Compute VaR and CVaR from final values ---
        final_vals = sims[-1]
        VaR_95 = np.percentile(final_vals, 5)
        CVaR_95 = final_vals[final_vals <= VaR_95].mean()
        risk_text = [
            f"Value at Risk (95%): ${final_vals.mean() - VaR_95:,.2f}",
            f"Conditional VaR (95%): ${final_vals.mean() - CVaR_95:,.2f}"
        ]

        # --- Allocation bar chart ---
        alloc_fig = go.Figure(go.Bar(
            x=tickers,
            y=weights,
            marker_color='teal'
        ))
        alloc_fig.update_layout(
            title="Portfolio Allocation",
            xaxis_title="Ticker",
            yaxis_title="Weight"
        )

        # --- Return results to UI ---
        return fig, html.Ul([html.Li(x) for x in risk_text]), alloc_fig, ""

    # --- Help Section Toggle ---
    @app.callback(
        Output("help-section", "is_open"),
        Input("help-toggle", "n_clicks"),
        State("help-section", "is_open")
    )
    def toggle_help(n, is_open):
        if n:
            return not is_open
        return is_open