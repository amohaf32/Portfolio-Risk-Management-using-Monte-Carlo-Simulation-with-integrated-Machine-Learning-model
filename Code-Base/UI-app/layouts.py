# from dash import html, dcc
# import dash_bootstrap_components as dbc

# def get_layout():
#     return dbc.Container([

#         # --- Title ---
#         html.H2("📊 Portfolio Risk Management Dashboard", className="my-4"),

#         # --- Inputs Row ---
#         dbc.Row([
#             dbc.Col([
#                 html.Label("Select Tickers:"),
#                 dcc.Dropdown(id="ticker-dropdown", multi=True, placeholder="Choose assets"),
#             ], width=6),

#             dbc.Col([
#                 html.Label("Portfolio Weights (comma-separated or auto):"),
#                 dcc.Input(id="weight-input", type="text", placeholder="e.g. 0.3, 0.3, 0.4", className="mb-2", style={"width": "100%"}),
#                 dbc.Button("Equal Weight", id="equal-weight-btn", color="secondary", size="sm", className="me-2"),
#                 dbc.Button("Run Simulation", id="run-sim-btn", color="primary", size="sm"),
#                 html.Div(id="error-message", className="text-danger mt-2")
#             ], width=6),
#         ], className="mb-4"),

#         # --- Simulation Output Plot ---
#         dbc.Card([
#             dbc.CardBody([
#                 html.H4("Simulated Portfolio Value Paths"),
#                 dcc.Graph(id="portfolio-plot")
#             ])
#         ], className="mb-4"),

#         # --- Metrics and Allocation Row ---
#         dbc.Row([
#             dbc.Col([
#                 dbc.Card([
#                     dbc.CardBody([
#                         html.H5("Risk Metrics"),
#                         html.Div(id="risk-metrics-output")
#                     ])
#                 ])
#             ], width=6),
#             dbc.Col([
#                 dbc.Card([
#                     dbc.CardBody([
#                         html.H5("Portfolio Allocation"),
#                         dcc.Graph(id="allocation-plot")
#                     ])
#                 ])
#             ], width=6)
#         ]),

#         # --- Tooltips (top-level placement so they attach properly) ---
#         dbc.Tooltip("Select one or more tickers to include in your portfolio simulation.",
#                     target="ticker-dropdown", placement="right"),

#         dbc.Tooltip("Enter weights like 0.3, 0.3, 0.4 — must sum to 1.",
#                     target="weight-input", placement="right"),

#         dbc.Tooltip("Auto-assign equal weights to each selected asset.",
#                     target="equal-weight-btn", placement="bottom"),

#         dbc.Tooltip("Run Monte Carlo simulation with selected inputs.",
#                     target="run-sim-btn", placement="bottom")
#     ], fluid=True)


from dash import html, dcc
import dash_bootstrap_components as dbc
from theme_config import THEMES

def get_layout():
    return dbc.Container([

        # --- Title ---
        html.H2("📊 Portfolio Risk Management Dashboard", className="my-4"),

        # --- Help Toggle (collapsible) ---
        dbc.Button("ℹ️ Help & Terminology", id="help-toggle", color="info", className="mb-3", n_clicks=0),
        dbc.Collapse(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Definitions", className="card-title"),
                    html.Ul([
                        html.Li("Monte Carlo Simulation: Repeated random sampling to project future outcomes."),
                        html.Li("Value at Risk (VaR): Maximum expected loss with a given confidence level."),
                        html.Li("Conditional VaR (CVaR): Expected loss if the VaR threshold is breached."),
                        html.Li("Drawdown: Peak-to-trough decline in portfolio value."),
                    ])
                ])
            ]),
            id="help-section",
            is_open=False
        ),
        
        # # --- Theme Toggle ---
        # dbc.Row([
        # dbc.Col([
        #     dbc.Label("Theme"),
        #         dcc.Dropdown(
        #             id="theme-switcher",
        #             value="Flatly (Light)",
        #             options=[{"label": name, "value": name} for name in THEMES.keys()],
        #             clearable=False,
        #         style={"width": "200px"}
        #         )
        #     ])
        # ], className="mb-3"),

        # --- Input Panel ---
        dbc.Row([
            dbc.Col([
                html.Label("Select Tickers:"),
                dcc.Dropdown(id="ticker-dropdown", multi=True, placeholder="Choose assets")
            ], width=6),

            dbc.Col([
                html.Label("Portfolio Weights (comma-separated or auto):"),
                dcc.Input(id="weight-input", type="text", placeholder="e.g. 0.3, 0.3, 0.4", style={"width": "100%"}),
                dbc.Button("Equal Weight", id="equal-weight-btn", color="secondary", size="sm", className="me-2 mt-2"),
                dbc.Button("Run Simulation", id="run-sim-btn", color="primary", size="sm", className="mt-2"),
                html.Div(id="error-message", className="text-danger mt-2")
            ], width=6),
        ], className="mb-4"),

        # --- Portfolio Value Plot ---
        dbc.Card([
            dbc.CardBody([
                html.H4("Simulated Portfolio Value Paths", className="card-title"),
                dcc.Graph(id="portfolio-plot")
            ])
        ], className="mb-4"),

        # --- Risk Metrics and Allocation ---
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Risk Metrics"),
                        html.Div(id="risk-metrics-output")
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Portfolio Allocation"),
                        dcc.Graph(id="allocation-plot")
                    ])
                ])
            ], width=6)
        ]),

        # --- Tooltips ---
        dbc.Tooltip("Choose the stocks to include in your portfolio simulation.",
                    target="ticker-dropdown", placement="right"),

        dbc.Tooltip("Enter weights (e.g. 0.3, 0.3, 0.4) matching the number of selected tickers. They must sum to 1.",
                    target="weight-input", placement="right"),

        dbc.Tooltip("Click to automatically assign equal weights to selected assets.",
                    target="equal-weight-btn", placement="bottom"),

        dbc.Tooltip("Run the Monte Carlo simulation with selected settings.",
                    target="run-sim-btn", placement="bottom")
    ], fluid=True)
