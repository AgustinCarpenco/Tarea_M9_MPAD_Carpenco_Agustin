import dash
from dash import html


dash.register_page(__name__, path='/gps')


def layout():
    return html.Div([
        html.H1('Dashboard Deportivo - Home'),
        html.P('Página protegida por dash-auth')
    ])

