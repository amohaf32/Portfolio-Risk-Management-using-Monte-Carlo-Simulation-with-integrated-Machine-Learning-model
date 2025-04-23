from dash import html, dcc
import dash_bootstrap_components as dbc

COLOR_PALETTE = {
    "primary": "#3498db",
    "secondary": "#2ecc71",
    "accent": "#e74c3c",
    "background": "#f8f9fa",
    "card": "#ffffff",
    "text": "#333333"
}

def get_layout():
    return dbc.Container([
        # Header Section
        html.Div([
            html.H2("📊 Portfolio Risk Management Dashboard", 
                   className="mb-2",
                   style={"color": COLOR_PALETTE["primary"]}),
            html.Hr(style={"borderTop": f"2px solid {COLOR_PALETTE['primary']}"})
        ], className="my-4"),

        # Help Section
        dbc.Button("ℹ️ Help & Terminology", id="help-toggle", 
                 color="info", className="mb-3", outline=True),
        dbc.Collapse(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Quick Start Guide", className="card-title"),
                    html.Ol([
                        html.Li("Select assets from the dropdown"),
                        html.Li([
                            "Enter either:",
                            html.Ul([
                                html.Li("Specific weights (must sum to 1.0)"),
                                html.Li("Investment amounts to auto-calculate weights")
                            ])
                        ]),
                        html.Li("Click 'Run Simulation'")
                    ], className="mb-3"),
                    
                    html.H5("Interpreting Results", className="card-title mt-4"),
                    html.Ul([
                        html.Li("The shaded area shows likely outcome ranges"),
                        html.Li("Darker central line indicates average expected path"),
                        html.Li("Risk metrics show potential downsides")
                    ]),
                    
                    html.H5("Tips", className="card-title mt-4"),
                    html.Ul([
                        html.Li("Start with 2-3 assets for clearer patterns"),
                        html.Li("Compare different time horizons"),
                        html.Li("Use equal weights as a baseline")
                    ])
                ])
            ], style={"borderLeft": "4px solid #3498db"}),
            id="help-section",
            is_open=True
        ),
        
        # Key Metrics Cards
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Total Investment"),
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-coins mr-2"),
                            html.H4(id="total-investment", children="Not specified", 
                                className="text-success d-inline")
                        ]),
                        dbc.Tooltip("Sum of all investment amounts", 
                                target="total-investment")
                    ])
                ], className="shadow-sm"), 
                width=3, className="mb-3"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Expected Return"),
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-chart-line mr-2"),
                            html.H4(id="expected-return", children="0.00%", 
                                className="text-primary d-inline")
                        ]),
                        dbc.Tooltip("Projected annualized return", 
                                target="expected-return")
                    ])
                ], className="shadow-sm"), 
                width=3, className="mb-3"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Portfolio Volatility"),
                    dbc.CardBody([
                        html.Div([
                            html.I(className="fas fa-chart-bar mr-2"),
                            html.H4(id="portfolio-volatility", children="0.00%", 
                                className="text-warning d-inline")
                        ]),
                        dbc.Tooltip("Standard deviation of returns", 
                                target="portfolio-volatility")
                    ])
                ], className="shadow-sm"), 
                width=3, className="mb-3"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Performance Summary"),
                    dbc.CardBody([
                        html.Div([
                            html.Span("Annualized:", className="metric-label"),
                            html.Span(id="annual-return", className="metric-value")
                        ], className="metric-row"),
                        html.Div([
                            html.Span("Best Case:", className="metric-label"),
                            html.Span(id="best-case", className="metric-value")
                        ], className="metric-row"),
                        html.Div([
                            html.Span("Worst Case:", className="metric-label"),
                            html.Span(id="worst-case", className="metric-value")
                        ], className="metric-row")
                    ])
                ], className="shadow-sm"), 
                width=3, className="mb-3"
            )
        ], className="mb-4"),

        # Input Panel
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Assets:", className="font-weight-bold"),
                        dcc.Dropdown(
                            id="ticker-dropdown", 
                            multi=True,
                            placeholder="Select 2-5 assets",
                            className="mb-3"
                        ),
                        
                        html.Label("Simulation Period:", className="font-weight-bold"),
                        dcc.Dropdown(
                            id="time-horizon",
                            options=[
                                {"label": "1 Month (21 days)", "value": 21},
                                {"label": "3 Months (63 days)", "value": 63},
                                {"label": "1 Year (252 days)", "value": 252}
                            ],
                            value=252,
                            clearable=False,
                            className="mb-3"
                        ),
                    ], width=6),

                    dbc.Col([
                        html.Label("Portfolio Weights:", className="font-weight-bold"),
                        dbc.InputGroup([
                            dcc.Input(
                                id="weight-input",
                                type="text",
                                placeholder="e.g. 0.5, 0.3, 0.2",
                                className="form-control"
                            ),
                            dbc.Button(
                                "Validate",
                                id="validate-weights",
                                color="secondary",
                                size="sm"
                            )
                        ], className="mb-3"),
                        
                        dbc.Progress(
                            id="weight-validation",
                            striped=True,
                            animated=True,
                            className="my-2"
                        ),
                        
                        dbc.Row([
                            dbc.Col(
                                dbc.Button("Equal Weight", id="equal-weight-btn",
                                          color="secondary", size="sm", className="mt-2"),
                                width=6
                            ),
                            dbc.Col(
                                dbc.Button("Run Simulation", id="run-sim-btn",
                                          color="primary", size="sm", className="mt-2"),
                                width=6
                            )
                        ]),
                        
                        html.Div(id="error-message", className="text-danger mt-2"),
                        dbc.Alert(
                            id="simulation-status",
                            color="light",
                            className="mt-3",
                            style={"display": "none"},
                            dismissable=True
                        ),
                        
                        # Weight Calculator Section
                        html.Hr(),
                        html.H5("💡 Investment Calculator", className="mt-3"),
                        html.Small(
                            "Enter amounts to auto-calculate weights (e.g., 123.45)",
                            className="form-text text-muted mb-2"
                        ),
                        html.Div(id="investment-inputs", className="mb-3"),
                        dbc.Button("Calculate Weights", id="calc-weight-btn",
                                  color="success", className="mt-2 mb-2"),
                        html.Div(id="total-investment-display", className="font-weight-bold text-right"),
                        
                        # Weight Visualization
                        html.Div([
                            html.H5("Current Allocation", className="mt-4 mb-3"),
                            html.Div(id="weight-visualization", 
                                    style={"borderLeft": f"4px solid {COLOR_PALETTE['secondary']}", 
                                           "padding": "10px",
                                           "backgroundColor": "#f8f9fa"})
                        ])
                    ], width=6)
                ])
            ])
        ], className="mb-4 shadow"),

        # Results Section
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Simulation Results", className="font-weight-bold"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button("📊 Export Chart", id="export-chart", outline=True, color="primary", className="mr-2"),
                            dbc.Button("📁 Export Data", id="export-data", outline=True, color="secondary")
                        ], className="mb-3"),
                        dcc.Loading(
                            id="loading-simulation",
                            type="circle",
                            children=dcc.Graph(id="portfolio-plot")
                        )
                    ])
                ], className="shadow-sm h-100"),
                width=12, className="mb-4"
            )
        ]),
        
        # Risk Metrics Section
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Risk Analysis", className="font-weight-bold"),
                    dbc.CardBody([
                        dbc.Tabs([
                            dbc.Tab(
                                html.Div(id="var-metrics"),
                                label="Value at Risk",
                                tabClassName="text-danger"
                            ),
                            dbc.Tab(
                                html.Div(id="cvar-metrics"),
                                label="Conditional VaR",
                                tabClassName="text-warning"
                            ),
                            dbc.Tab(
                                html.Div(id="drawdown-metrics"),
                                label="Drawdown",
                                tabClassName="text-info"
                            )
                        ])
                    ])
                ], className="shadow-sm h-100"),
                width=6, className="mb-4"
            ),
            
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Portfolio Allocation", className="font-weight-bold"),
                    dbc.CardBody([
                        dcc.Graph(id="allocation-plot")
                    ])
                ], className="shadow-sm h-100"),
                width=6, className="mb-4"
            )
        ]),

        # Hidden storage
        dcc.Store(id="simulation-results"),
        dcc.Store(id="portfolio-stats"),
        dcc.Download(id="download-weights")
    ], fluid=True, style={"backgroundColor": COLOR_PALETTE["background"]})