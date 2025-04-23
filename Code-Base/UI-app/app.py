# import dash
# from dash import html
# import dash_bootstrap_components as dbc

# from layouts import get_layout
# from callbacks import register_callbacks

# # --- Initialize Dash with Bootstrap Theme ---
# app = dash.Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.FLATLY],  # or MINTY, SOLAR, etc.
#     suppress_callback_exceptions=True
# )

# app.title = "Portfolio Risk Management Dashboard"
# server = app.server

# # --- Set Layout & Callbacks ---
# app.layout = get_layout()
# register_callbacks(app)

# if __name__ == "__main__":
#     app.run(debug=True)

# import dash
# from dash import html
# import dash_bootstrap_components as dbc

# from layouts import get_layout
# from callbacks import register_callbacks

# # Initialize Dash app
# app = dash.Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.FLATLY],
#     suppress_callback_exceptions=True,
#     meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
# )

# app.title = "Portfolio Risk Management Dashboard"
# server = app.server

# # Set layout and callbacks
# app.layout = get_layout()
# register_callbacks(app)

# if __name__ == "__main__":
#     app.run(debug=True, dev_tools_hot_reload=False)

import dash
from dash import html
import dash_bootstrap_components as dbc

from layouts import get_layout
from callbacks import register_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)

app.title = "Portfolio Risk Management Dashboard"
server = app.server

app.layout = get_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, dev_tools_hot_reload=False)