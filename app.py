import dash
import dash_bootstrap_components as dbc
import dash_auth
from dash import html

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin'
}

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY]
)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = dbc.Container([
    dbc.NavbarSimple([
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Performance", href="/performance")),
        dbc.NavItem(dbc.NavLink("GPS", href="/gps")),
    ], brand="Dashboard Deportivo", color="primary", dark=True),
    dash.page_container
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
