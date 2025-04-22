import dash
from dash import html
import dash_bootstrap_components as dbc

from layouts import get_layout
from callbacks import register_callbacks

# --- Initialize Dash with Bootstrap Theme ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],  # or MINTY, SOLAR, etc.
    suppress_callback_exceptions=True
)

app.title = "Portfolio Risk Management Dashboard"
server = app.server

# --- Set Layout & Callbacks ---
app.layout = get_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)

# import dash
# from dash import html
# import dash_bootstrap_components as dbc
# from dash_bootstrap_templates import load_figure_template

# from layouts import get_layout
# from callbacks import register_callbacks
# # from theme_config import THEMES

# # Load figure styling for both themes
# load_figure_template(["flatly", "darkly"])

# app = dash.Dash(
#     __name__,
#     external_stylesheets=[THEMES["Flatly (Light)"]],
#     suppress_callback_exceptions=True
# )

# app.title = "Portfolio Risk Management Dashboard"
# server = app.server

# # Global layout
# app.layout = get_layout()

# # Attach callbacks
# register_callbacks(app)
