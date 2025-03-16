import dash
from dash import html


dash.register_page(__name__, path='/performance')

def layout():
    return dbc.Container([
        html.H1('Performance Dashboard'),
        html.P('Contenido del dashboard Performance')
    ])

