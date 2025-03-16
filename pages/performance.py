import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Datos de muestra para desarrollo
def generar_datos_muestra():
    # Generar fechas para los últimos 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Lista de jugadores
    players = ['Jugador 1', 'Jugador 2', 'Jugador 3', 'Jugador 4', 'Jugador 5']
    
    # Generar datos
    data = []
    for date in date_range:
        for player in players:
            # Generar estadísticas aleatorias
            goals = np.random.randint(0, 3)
            assists = np.random.randint(0, 2)
            minutes = np.random.randint(0, 90)
            passes = np.random.randint(10, 100)
            distance = np.random.uniform(4, 12)
            
            # Calcular puntuación de rendimiento
            performance = goals*3 + assists*2 + minutes/10 + passes/20 + distance/2
            
            data.append({
                'fecha': date,
                'jugador': player,
                'goles': goals,
                'asistencias': assists,
                'minutos': minutes,
                'pases': passes,
                'distancia_km': distance,
                'rendimiento': performance
            })
    
    return pd.DataFrame(data)

# Generar datos de muestra
df_performance = generar_datos_muestra()

def layout():
    """Layout de la página de Performance."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard de Performance", className="mb-4"),
                
                # Filtros
                dbc.Card([
                    dbc.CardHeader("Filtros"),
                    dbc.CardBody([
                        dbc.Row([
                            # Selector de fechas
                            dbc.Col([
                                html.Label("Rango de Fechas"),
                                dcc.DatePickerRange(
                                    id='date-picker-range',
                                    start_date=datetime.now() - timedelta(days=30),
                                    end_date=datetime.now(),
                                    calendar_orientation='horizontal',
                                    clearable=True,
                                    with_portal=True,
                                    first_day_of_week=1
                                )
                            ], md=6),
                            
                            # Selector de jugadores
                            dbc.Col([
                                html.Label("Seleccionar Jugadores"),
                                dcc.Dropdown(
                                    id='player-dropdown',
                                    options=[
                                        {'label': player, 'value': player} for player in df_performance['jugador'].unique()
                                    ],
                                    multi=True,
                                    placeholder="Seleccione jugadores",
                                    value=df_performance['jugador'].unique().tolist()[:2]  # Seleccionar primeros 2 jugadores por defecto
                                )
                            ], md=6)
                        ]),
                        
                        # Botón para aplicar filtros
                        dbc.Button("Aplicar Filtros", id="apply-filters-btn", color="primary", className="mt-3")
                    ])
                ], className="mb-4 shadow"),
                
                # Gráficos de Performance
                dbc.Row([
                    # Gráfico 1: Rendimiento por jugador
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Rendimiento por Jugador"),
                            dbc.CardBody([
                                dcc.Graph(id='performance-graph-1')
                            ])
                        ], className="shadow h-100")
                    ], md=6, className="mb-4"),
                    
                    # Gráfico 2: Estadísticas clave
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Estadísticas Clave"),
                            dbc.CardBody([
                                dcc.Graph(id='performance-graph-2')
                            ])
                        ], className="shadow h-100")
                    ], md=6, className="mb-4")
                ]),
                
                # Gráfico 3: Evolución temporal
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Evolución Temporal"),
                            dbc.CardBody([
                                dcc.Graph(id='performance-graph-3')
                            ])
                        ], className="shadow")
                    ], className="mb-4")
                ]),
                
                # Botón para exportar a PDF
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="fas fa-file-pdf me-2"),
                            "Exportar a PDF"
                        ], id="export-pdf-btn", color="danger", className="float-end")
                    ])
                ])
            ])
        ])
    ], fluid=True)

# Callback para actualizar gráficos de performance
@callback(
    [Output('performance-graph-1', 'figure'),
     Output('performance-graph-2', 'figure'),
     Output('performance-graph-3', 'figure')],
    [Input('apply-filters-btn', 'n_clicks')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('player-dropdown', 'value')]
)
def update_performance_graphs(n_clicks, start_date, end_date, selected_players):
    # Convertir fechas
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
    else:
        start_date = datetime.now() - timedelta(days=30)
        
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
    else:
        end_date = datetime.now()
        
    # Si no hay jugadores seleccionados, usar todos
    if not selected_players:
        selected_players = df_performance['jugador'].unique().tolist()
    
    # Filtrar datos
    filtered_df = df_performance[
        (df_performance['fecha'] >= start_date) & 
        (df_performance['fecha'] <= end_date) & 
        (df_performance['jugador'].isin(selected_players))
    ]
    
    # Agrupar por jugador para el primer gráfico
    player_summary = filtered_df.groupby('jugador').agg({
        'rendimiento': 'mean',
        'goles': 'sum',
        'asistencias': 'sum',
        'minutos': 'sum',
        'distancia_km': 'mean'
    }).reset_index()
    
    # Gráfico 1: Rendimiento promedio por jugador (gráfico de barras)
    fig1 = px.bar(
        player_summary, 
        x='jugador', 
        y='rendimiento',
        color='jugador',
        title='Rendimiento Promedio por Jugador',
        labels={'jugador': 'Jugador', 'rendimiento': 'Rendimiento Promedio'},
        height=400
    )
    
    # Gráfico 2: Estadísticas clave por jugador (gráfico de radar)
    fig2 = go.Figure()
    
    for player in player_summary['jugador']:
        player_data = player_summary[player_summary['jugador'] == player]
        
        # Normalizar valores para el radar
        max_goals = player_summary['goles'].max()
        max_assists = player_summary['asistencias'].max()
        max_minutes = player_summary['minutos'].max()
        max_distance = player_summary['distancia_km'].max()
        
        normalized_goals = (player_data['goles'].values[0] / max_goals) * 100 if max_goals > 0 else 0
        normalized_assists = (player_data['asistencias'].values[0] / max_assists) * 100 if max_assists > 0 else 0
        normalized_minutes = (player_data['minutos'].values[0] / max_minutes) * 100 if max_minutes > 0 else 0
        normalized_distance = (player_data['distancia_km'].values[0] / max_distance) * 100 if max_distance > 0 else 0
        
        fig2.add_trace(go.Scatterpolar(
            r=[normalized_goals, normalized_assists, normalized_minutes, normalized_distance, normalized_goals],
            theta=['Goles', 'Asistencias', 'Minutos', 'Distancia', 'Goles'],
            fill='toself',
            name=player
        ))
    
    fig2.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title='Estadísticas Clave por Jugador (Normalizado)',
        height=400
    )
    
    # Gráfico 3: Evolución temporal del rendimiento (gráfico de líneas)
    # Agrupar por fecha y jugador para ver la evolución
    time_series = filtered_df.groupby(['fecha', 'jugador']).agg({
        'rendimiento': 'mean'
    }).reset_index()
    
    fig3 = px.line(
        time_series, 
        x='fecha', 
        y='rendimiento', 
        color='jugador',
        title='Evolución del Rendimiento a lo Largo del Tiempo',
        labels={'fecha': 'Fecha', 'rendimiento': 'Rendimiento', 'jugador': 'Jugador'},
        height=400
    )
    
    fig3.update_xaxes(title='Fecha')
    fig3.update_yaxes(title='Rendimiento')
    
    return fig1, fig2, fig3