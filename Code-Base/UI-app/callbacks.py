from dash import Input, Output, State, html, dcc, ALL, callback_context, no_update
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import logging
from utils.simulation_runner import run_portfolio_simulation
import dash_bootstrap_components as dbc
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_callbacks(app):
    # Populate ticker dropdown
    @app.callback(
        Output("ticker-dropdown", "options"),
        Input("ticker-dropdown", "id")
    )
    def populate_tickers(_):
        from utils.db_utils import get_all_tickers
        return [{"label": t, "value": t} for t in get_all_tickers()]

    # Create investment inputs
    @app.callback(
        Output("investment-inputs", "children"),
        Input("ticker-dropdown", "value")
    )
    def create_investment_inputs(tickers):
        if not tickers:
            return html.Div("Select assets to calculate weights", className="text-muted")
        
        inputs = []
        for ticker in tickers:
            inputs.append(
                dbc.Row([
                    dbc.Col(
                        dbc.Label(f"{ticker} Amount ($):", width="auto"), 
                        width=4
                    ),
                    dbc.Col(
                        dcc.Input(
                            id={"type": "inv-input", "index": ticker},
                            type="number",
                            min=0,
                            max=1000000,
                            step="any",
                            value=0,
                            className="form-control",
                            style={"width": "100%"},
                            inputMode="numeric",
                            pattern="[0-9]*\.?[0-9]*"
                        ),
                        width=4
                    )
                ], className="mb-2")
            )
        return inputs

    # Weight calculation
    @app.callback(
        Output("weight-input", "value"),
        Output("total-investment-display", "children"),
        Input("calc-weight-btn", "n_clicks"),
        Input("equal-weight-btn", "n_clicks"),
        State("ticker-dropdown", "value"),
        State({"type": "inv-input", "index": ALL}, "value"),
        prevent_initial_call=True
    )
    def calculate_weights(calc_clicks, equal_clicks, tickers, amounts):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
            
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Equal weights
        if trigger == "equal-weight-btn":
            if not tickers:
                return no_update, no_update
            weight = round(1 / len(tickers), 4)
            return ", ".join([str(weight)] * len(tickers)), ""
        
        # Investment-based weights
        if trigger == "calc-weight-btn":
            if not tickers or not amounts:
                return "Select assets and amounts", ""
            
            try:
                amounts = [float(amt) if amt not in [None, ""] else 0.0 for amt in amounts]
                if any(a < 0 for a in amounts):
                    return "Negative amounts not allowed", ""
                    
                total = sum(amounts)
                
                if total <= 0:
                    return "Amounts must be positive", ""
                
                weights = [round(a/total, 4) for a in amounts]
                return ", ".join([f"{w:.4f}" for w in weights]), f"Total Investment: ${total:,.2f}"
            except ValueError:
                return "Invalid number format", ""
            except Exception as e:
                logger.error(f"Calculation error: {str(e)}")
                return f"Error: {str(e)}", ""

        return no_update, no_update

    # Weight validation
    @app.callback(
        Output("weight-validation", "value"),
        Output("weight-validation", "color"),
        Input("weight-input", "value"),
        prevent_initial_call=True
    )
    def validate_weights(weight_str):
        if not weight_str:
            return 0, "secondary"
        
        try:
            weights = [float(w.strip()) for w in weight_str.split(",")]
            total = sum(weights)
            
            if abs(total - 1.0) < 0.01:  # Allow small rounding
                return 100, "success"
            elif total > 0:
                return min(abs(total)*100, 100), "warning"
            return 0, "secondary"
        except:
            return 0, "secondary"

    # Weight visualization
    @app.callback(
        Output("weight-visualization", "children"),
        Input("weight-input", "value"),
        State("ticker-dropdown", "value"),
        prevent_initial_call=True
    )
    def visualize_weights(weights, tickers):
        if not weights or not tickers:
            return "Weights will appear here"
        
        try:
            weights = [float(w.strip()) for w in weights.split(",")]
            return html.Div([
                dbc.Row([
                    dbc.Col(tickers[i], width=3),
                    dbc.Col(
                        dbc.Progress(
                            value=w*100,
                            label=f"{w*100:.1f}%",
                            style={"height": "20px"},
                            color="primary" if w > 0.2 else "warning",
                            className="mb-2"
                        ), width=9
                    )
                ]) for i, w in enumerate(weights)
            ])
        except:
            return "Invalid weight format"

    # Simulation status
    @app.callback(
        Output("simulation-status", "children"),
        Output("simulation-status", "style"),
        Output("simulation-status", "color"),
        Input("run-sim-btn", "n_clicks"),
        State("ticker-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_status(n_clicks, tickers):
        if not n_clicks:
            return "", {"display": "none"}, "light"
        
        if not tickers:
            return "⚠️ Please select assets first", {"display": "block"}, "warning"
        
        return "🔄 Simulation running...", {"display": "block"}, "info"

    # Function to create a simulation plot
    def create_allocation_plot(tickers, weights):
    #Create a pie chart showing portfolio allocation
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=tickers,
            values=weights,
            hole=0.4,
            marker_colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],  # Color palette
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Portfolio Allocation",
            showlegend=False,
            margin=dict(t=40, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig 
    
    # Main simulation callback (UPDATED)
    @app.callback(
        Output("portfolio-plot", "figure"),
        Output("var-metrics", "children"),
        Output("cvar-metrics", "children"),
        Output("drawdown-metrics", "children"),
        Output("allocation-plot", "figure"),
        Output("error-message", "children"),
        Output("simulation-results", "data"),
        Output("portfolio-stats", "data"),
        Output("annual-return", "children"),
        Output("best-case", "children"),
        Output("worst-case", "children"),
        Output("total-investment", "children"),
        Output("expected-return", "children"),
        Output("portfolio-volatility", "children"),
        Input("run-sim-btn", "n_clicks"),
        State("ticker-dropdown", "value"),
        State("weight-input", "value"),
        State("time-horizon", "value"),
        State({"type": "inv-input", "index": ALL}, "value"),
        prevent_initial_call=True
    )
    def run_simulation(n_clicks, tickers, weights_str, days, investment_amounts):
        if not n_clicks:
            return [no_update] * 14
        
        if not tickers or not weights_str:
            return [no_update] * 6 + [None, None, "-", "-", "-", "Not specified", "0.00%", "0.00%"]
        
        try:
            weights = [float(w.strip()) for w in weights_str.split(",")]
            if len(weights) != len(tickers):
                return [no_update] * 5 + ["Weights/tickers mismatch"] + [None, None, "-", "-", "-", "Not specified", "0.00%", "0.00%"]
                
            if not np.isclose(sum(weights), 1.0, atol=0.01):
                return [no_update] * 5 + ["Weights must sum to 1"] + [None, None, "-", "-", "-", "Not specified", "0.00%", "0.00%"]
            
            # Calculate total investment from input amounts
            try:
                total_investment = sum(float(amt) if amt not in [None, ""] else 0.0 
                                    for amt in investment_amounts)
            except:
                total_investment = 0
            
            # Run simulation
            sim_results = run_portfolio_simulation(tickers, weights, days)
            
            # Calculate statistics
            final_vals = sim_results[-1]
            initial_value = np.mean(sim_results[0])
            mean_final = np.mean(final_vals)
            return_pct = (mean_final - initial_value) / initial_value
            volatility = np.std(final_vals) / initial_value
            
            # Risk metrics
            VaR_95 = np.percentile(final_vals, 5)
            CVaR_95 = final_vals[final_vals <= VaR_95].mean()
            max_drawdown = (initial_value - np.min(sim_results)) / initial_value
            
            stats = {
                "initial_value": initial_value,
                "mean_final": mean_final,
                "return_pct": return_pct,
                "volatility": volatility,
                "sharpe": return_pct / volatility if volatility > 0 else 0,
                "var": VaR_95,
                "cvar": CVaR_95,
                "drawdown": max_drawdown
            }
            
            # Create plots
            fig = create_simulation_plot(sim_results)
            alloc_fig = create_allocation_plot(tickers, weights)
            
            # Calculate relative metrics
            var_relative = (initial_value - VaR_95) / initial_value
            cvar_relative = (initial_value - CVaR_95) / initial_value
            drawdown_absolute = initial_value * max_drawdown

            # Enhanced metric displays
            var_content = dbc.Card([
                dbc.CardHeader("Value at Risk (95%)", className="bg-danger text-white"),
                dbc.CardBody([
                    html.H4(f"${initial_value - VaR_95:,.2f}", className="mb-2"),
                    html.P([
                        html.Span(f"{var_relative:.2%} of portfolio", className="text-muted"),
                        html.Br(),
                        html.Small("Worst loss under normal conditions", 
                                className="text-muted")
                    ])
                ])
            ], className="shadow-sm mb-3")

            cvar_content = dbc.Card([
                dbc.CardHeader("Conditional VaR (95%)", className="bg-warning text-dark"),
                dbc.CardBody([
                    html.H4(f"${initial_value - CVaR_95:,.2f}", className="mb-2"),
                    html.P([
                        html.Span(f"{cvar_relative:.2%} of portfolio", className="text-muted"),
                        html.Br(),
                        html.Small("Average loss when VaR is breached", 
                                className="text-muted")
                    ])
                ])
            ], className="shadow-sm mb-3")

            drawdown_content = dbc.Card([
                dbc.CardHeader("Max Drawdown", className="bg-info text-white"),
                dbc.CardBody([
                    html.H4(f"{max_drawdown:.2%}", className="mb-2"),
                    html.P([
                        html.Span(f"${drawdown_absolute:,.2f} absolute", className="text-muted"),
                        html.Br(),
                        html.Small("Largest peak-to-trough decline", 
                                className="text-muted")
                    ])
                ])
            ], className="shadow-sm mb-3")
            
            # Performance metrics
            annual_return = f"{return_pct:.2%}"
            best_case = f"${np.percentile(final_vals, 95):,.2f}"
            worst_case = f"${VaR_95:,.2f}"
            
            # Format the new outputs
            total_investment_display = f"${total_investment:,.2f}" if total_investment > 0 else "Not specified"
            expected_return_display = f"{return_pct:.2%}"
            volatility_display = f"{volatility:.2%}"
            
            return [
                fig,
                var_content,
                cvar_content,
                drawdown_content,
                alloc_fig,
                "",
                sim_results.tolist(),
                stats,
                annual_return,
                best_case,
                worst_case,
                total_investment_display,
                expected_return_display,
                volatility_display
            ]
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            return [no_update] * 5 + [f"Error: {str(e)}"] + [None, None, "-", "-", "-", "Not specified", "0.00%", "0.00%"]

    # Helper functions
    def create_simulation_plot(sim_results):
        fig = go.Figure()
        
        # Add individual paths (limit to 50 for better performance)
        for i in range(min(sim_results.shape[1], 50)):
            fig.add_trace(go.Scatter(
                y=sim_results[:, i],
                mode='lines',
                line=dict(width=1, color="#3498db"),
                opacity=0.15,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add mean path with confidence interval
        mean_path = np.mean(sim_results, axis=1)
        std_dev = np.std(sim_results, axis=1)
        
        fig.add_trace(go.Scatter(
            y=mean_path + std_dev,
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            y=mean_path - std_dev,
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='±1 Std Dev',
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            y=mean_path,
            mode='lines',
            line=dict(width=3, color="#2c3e50"),
            name='Mean Path',
            hovertemplate='Day %{x}<br>Value: $%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Simulated Portfolio Paths with Confidence Band",
            xaxis_title="Trading Days",
            yaxis_title="Portfolio Value ($)",
            plot_bgcolor='white',
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    # Export functionality
    @app.callback(
        Output("download-weights", "data"),
        Input("export-data", "n_clicks"),
        State("ticker-dropdown", "value"),
        State("weight-input", "value"),
        prevent_initial_call=True
    )
    def export_weights(n_clicks, tickers, weights):
        if not n_clicks or not tickers or not weights:
            return no_update
        
        try:
            weights = [float(w.strip()) for w in weights.split(",")]
            df = pd.DataFrame({
                "Ticker": tickers,
                "Weight": weights,
                "Allocation": [f"{w*100:.1f}%" for w in weights]
            })
            return dcc.send_data_frame(df.to_csv, "portfolio_weights.csv")
        except:
            return no_update

    # Help toggle
    @app.callback(
        Output("help-section", "is_open"),
        Input("help-toggle", "n_clicks"),
        State("help-section", "is_open")
    )
    def toggle_help(n, is_open):
        if n:
            return not is_open
        return is_open