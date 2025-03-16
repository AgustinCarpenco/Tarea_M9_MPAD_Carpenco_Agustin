import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def layout():
    """Layout de la página de inicio."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Bienvenido al Dashboard Deportivo", className="text-center mb-4"),
                html.P("Seleccione una de las opciones de navegación para acceder a los diferentes dashboards:", className="lead text-center"),
                
                # Tarjetas para acceder a las diferentes secciones
                dbc.Row([
                    # Tarjeta para Performance
                    dbc.Col([
                        dbc.Card([
                            dbc.CardImg(src="/assets/performance.jpg", top=True, style={"height": "180px", "object-fit": "cover"}),
                            dbc.CardBody([
                                html.H4("Dashboard de Performance", className="card-title"),
                                html.P("Análisis de rendimiento deportivo y métricas de jugadores.", className="card-text"),
                                dbc.Button("Ir a Performance", href="/performance", color="primary")
                            ])
                        ], className="h-100 shadow")
                    ], width=12, md=6, lg=4, className="mb-4"),
                    
                    # Tarjeta para GPS
                    dbc.Col([
                        dbc.Card([
                            dbc.CardImg(src="/assets/gps.jpg", top=True, style={"height": "180px", "object-fit": "cover"}),
                            dbc.CardBody([
                                html.H4("Dashboard de GPS", className="card-title"),
                                html.P("Datos de seguimiento GPS y análisis de movimiento en campo.", className="card-text"),
                                dbc.Button("Ir a GPS", href="/gps", color="primary")
                            ])
                        ], className="h-100 shadow")
                    ], width=12, md=6, lg=4, className="mb-4"),
                    
                    # Tarjeta para Documentación
                    dbc.Col([
                        dbc.Card([
                            dbc.CardImg(src="/assets/docs.jpg", top=True, style={"height": "180px", "object-fit": "cover"}),
                            dbc.CardBody([
                                html.H4("Documentación", className="card-title"),
                                html.P("Manuales, guías y recursos para el uso del dashboard.", className="card-text"),
                                dbc.Button("Ver Documentación", href="#", color="primary")
                            ])
                        ], className="h-100 shadow")
                    ], width=12, md=6, lg=4, className="mb-4"),
                ], className="mt-4")
            ])
        ])
    ], fluid=True)