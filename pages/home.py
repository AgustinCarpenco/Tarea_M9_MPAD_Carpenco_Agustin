import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path='/')

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H1("🏟️ Dashboard Deportivo", className="display-3"),
                        html.P("Bienvenido al Dashboard principal de análisis deportivo.", className="lead"),
                        dbc.Button("Ir a Performance", href="/performance", color="primary", className="me-2"),
                        dbc.Button("Ver GPS", href="/gps", color="info"),
                    ])
                ], className="p-5 bg-light rounded-3 shadow-sm text-center")
            ], width=12)
        ], justify='center', align='center', className='mt-5')
    ], fluid=True)
