import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Registra esta página en el sistema de páginas de Dash
dash.register_page(
    __name__,
    path='/',  # Ruta raíz
    title='Home',
    name='Home'
)

# Define el layout de la página
layout = dbc.Container([
    # Header con el mismo estilo que el login
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Dashboard Deportivo", className="text-white mb-3 display-4 text-center fw-bold"),
                    html.P(
                        "Plataforma de análisis GPS y métricas de rendimiento futbolístico",
                        className="text-white lead text-center"
                    ),
                ], width={"size": 10, "offset": 1})
            ], className="py-5")
        ], fluid=True)
    ], style={
        "background": "linear-gradient(135deg, #1e3c72, #2a5298)",
        "margin-bottom": "2rem",
        "border-radius": "0 0 15px 15px"
    }),
    
    # Espacio para mejor separación visual
    html.Div(className="mt-4 mb-4"),
    
    # Tarjetas de navegación principales
    dbc.Row([
        # Performance
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-3x text-primary")
                        ], className="rounded-circle bg-light p-4 d-inline-flex mb-3 shadow-sm")
                    ], className="text-center"),
                    html.H4("Dashboard de Performance", className="text-center mb-3"),
                    html.P([
                        "Análisis completo de rendimiento deportivo con métricas individuales y grupales."
                    ], className="text-center mb-4"),
                    html.Div([
                        html.P([
                            "• Comparativas entre jugadores",
                            html.Br(),
                            "• Análisis de métricas físicas",
                            html.Br(),
                            "• Evolución de rendimiento"
                        ], className="small text-muted mb-4 text-center"),
                    ]),
                    dbc.Button([
                        "Ir a Performance ",
                        html.I(className="fas fa-arrow-right ms-1")
                    ], href="/performance", color="primary", className="w-100")
                ])
            ], className="h-100 shadow")
        ], width=12, md=6, lg=4, className="mb-4"),
        
        # GPS
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-map-marker-alt fa-3x text-success")
                        ], className="rounded-circle bg-light p-4 d-inline-flex mb-3 shadow-sm")
                    ], className="text-center"),
                    html.H4("Análisis GPS", className="text-center mb-3"),
                    html.P([
                        "Visualización de datos de ubicación, velocidad y distancias recorridas en el campo."
                    ], className="text-center mb-4"),
                    html.Div([
                        html.P([
                            "• Mapas de calor por posición",
                            html.Br(),
                            "• Métricas de velocidad y sprint",
                            html.Br(),
                            "• Análisis por división y posición"
                        ], className="small text-muted mb-4 text-center"),
                    ]),
                    dbc.Button([
                        "Ir a GPS ",
                        html.I(className="fas fa-arrow-right ms-1")
                    ], href="/gps", color="success", className="w-100")
                ])
            ], className="h-100 shadow")
        ], width=12, md=6, lg=4, className="mb-4"),
        
        # Reportes
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-file-pdf fa-3x text-danger")
                        ], className="rounded-circle bg-light p-4 d-inline-flex mb-3 shadow-sm")
                    ], className="text-center"),
                    html.H4("Informes y Reportes", className="text-center mb-3"),
                    html.P([
                        "Generación de informes personalizados para entrenadores y equipo técnico."
                    ], className="text-center mb-4"),
                    html.Div([
                        html.P([
                            "• Exportación a PDF",
                            html.Br(),
                            "• Reportes por jugador y equipo",
                            html.Br(),
                            "• Resúmenes de partidos"
                        ], className="small text-muted mb-4 text-center"),
                    ]),
                    dbc.Button([
                        "Ver Reportes ",
                        html.I(className="fas fa-arrow-right ms-1")
                    ], href="#", color="danger", className="w-100")
                ])
            ], className="h-100 shadow")
        ], width=12, md=6, lg=4, className="mb-4"),
    ]),
    
    # Sección de acceso rápido
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Accesos Rápidos", className="mb-0")
                ], className="bg-light"),
                dbc.CardBody([
                    dbc.Row([
                        # Último partido
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-futbol me-2"),
                                "Último Partido"
                            ], color="primary", outline=True, className="w-100 mb-2")
                        ], width=12, sm=6, md=4, className="mb-3"),
                        
                        # Comparar divisiones
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-users me-2"),
                                "Comparar Divisiones"
                            ], color="success", outline=True, className="w-100 mb-2")
                        ], width=12, sm=6, md=4, className="mb-3"),
                        
                        # Exportar datos
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-download me-2"),
                                "Exportar Datos"
                            ], color="info", outline=True, className="w-100 mb-2")
                        ], width=12, sm=6, md=4, className="mb-3"),
                    ])
                ])
            ], className="shadow-sm mb-4")
        ], width={"size": 10, "offset": 1})
    ]),
    
    # Footer con información adicional
    html.Footer([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P([
                        "Dashboard Deportivo © 2025 - Desarrollado para el ",
                        html.Span("Máster en Python Avanzado Aplicado al Deporte", className="fw-bold")
                    ], className="text-center text-muted small mb-0 py-3")
                ])
            ])
        ], fluid=True)
    ], className="mt-5 bg-light")
    
], fluid=True, className="pt-0")