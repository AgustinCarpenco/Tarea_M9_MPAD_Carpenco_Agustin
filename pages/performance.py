import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from dash.exceptions import PreventUpdate
import os

# Registrar esta página
dash.register_page(
    __name__,
    path='/performance',
    title='Dashboard de Performance',
    name='Performance'
)
def cargar_datos():
    """Carga y preprocesa los datos de GPS"""
    # Directorio de datos
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    try:
        df = pd.read_csv(os.path.join(data_dir, 'gps_full.csv'))
        
        # Convertir columnas de fecha
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        
        # Crear categoría de velocidad 
        bins = [0, 20, 25, 27, 30, 100]
        labels = ['<20 km/h', '20-25 km/h', '25-27 km/h', '27-30 km/h', '>30 km/h']
        df['vel_category'] = pd.cut(df['max_vel'], bins=bins, labels=labels, right=False)
        
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

def filtrar_dataframe(df, division=None, team=None, position=None, player=None, date_range=None):
    """Filtra el DataFrame según los criterios seleccionados"""
    filtered_df = df.copy()
    
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    if position and position != "Todas":
        filtered_df = filtered_df[filtered_df['position_name'] == position]
    
    if player and player != "Todos":
        filtered_df = filtered_df[filtered_df['athlete_name'] == player]
    
    if date_range:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & 
                                  (filtered_df['date'] <= end_date)]
    
    return filtered_df

def generar_grafico_radar(df, jugador=None):
    """Genera un gráfico de radar para un jugador o promedio del equipo"""
    if jugador and jugador != "Todos" and jugador in df['athlete_name'].unique():
        datos = df[df['athlete_name'] == jugador]
        titulo = f"Perfil de Rendimiento: {jugador}"
    else:
        datos = df
        titulo = "Perfil de Rendimiento: Promedio Equipo"
    
    if datos.empty:
        return go.Figure()
    
    # Métricas para el radar chart
    metricas = [
        'z_max_vel', 'z_sprint_+25.2_km/h', 'z_mts_19.8-25_km/h', 
        'z_mts_14.4-19.8_km/h', 'z_acc_max', 'z_acc+3_m/ss', 'z_PL'
    ]
    
    nombres_metricas = [
        'Velocidad Máxima', 'Distancia Sprint', 'Distancia Alta Vel.', 
        'Distancia Media Vel.', 'Aceleración Máx.', 'Aceleraciones Fuertes', 'Player Load'
    ]
    
    # Calcular valores promedio
    valores = []
    for metrica in metricas:
        prom = datos[metrica].replace([np.inf, -np.inf], np.nan).mean()
        if np.isnan(prom):
            prom = 0
        valores.append(prom)
    
    # Crear el gráfico radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=nombres_metricas,
        fill='toself',
        name=titulo,
        line_color='rgba(31, 119, 180, 0.8)',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-3, 3])),
        title=dict(text=titulo, x=0.5, font=dict(size=16)),
        showlegend=False,
        height=500
    )
    
    return fig

def generar_grafico_distancia_velocidad(df):
    """Gráfico de dispersión de distancia vs velocidad máxima"""
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df, 
        x='total_distance', 
        y='max_vel',
        color='position_name',
        size='total_player_load',
        hover_name='athlete_name',
        labels={
            'total_distance': 'Distancia Total (m)',
            'max_vel': 'Velocidad Máxima (km/h)',
            'total_player_load': 'Player Load',
            'position_name': 'Posición'
        },
        title='Relación entre Distancia Total y Velocidad Máxima',
        height=500
    )
    
    return fig

def generar_grafico_comparativa_posiciones(df):
    """Gráfico de barras comparando métricas por posición"""
    if df.empty:
        return go.Figure()
    
    # Agrupar por posición
    df_posiciones = df.groupby('position_name').agg({
        'total_distance': 'mean',
        'max_vel': 'mean',
        'velocity_band5_total_distance': 'mean',
        'total_player_load': 'mean'
    }).reset_index()
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_posiciones['position_name'],
        y=df_posiciones['total_distance'],
        name='Distancia Total (m)',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        x=df_posiciones['position_name'],
        y=df_posiciones['max_vel'],
        name='Velocidad Máxima (km/h)',
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title='Comparativa de Métricas por Posición',
        xaxis=dict(title='Posición'),
        yaxis=dict(title='Valor Promedio'),
        barmode='group',
        height=500
    )
    
    return fig

# Layout principal del dashboard - Reordenado para solucionar el problema de superposición
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Dashboard de Performance", className="mb-4 text-primary")
        ])
    ]),
    
    # Panel de filtros con z-index ajustado
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtros"),
                dbc.CardBody([
                    dbc.Row([
                        # Filtro de divisiones
                        dbc.Col([
                            html.Label("División:"),
                            dcc.Dropdown(
                                id="division-filter", 
                                placeholder="Seleccionar División",
                                style={"position": "relative", "zIndex": "999"}
                            )
                        ], md=3),
                        
                        # Filtro de equipos
                        dbc.Col([
                            html.Label("Equipo:"),
                            dcc.Dropdown(
                                id="team-filter", 
                                placeholder="Seleccionar Equipo",
                                style={"position": "relative", "zIndex": "998"}
                            )
                        ], md=3),
                        
                        # Filtro de posiciones
                        dbc.Col([
                            html.Label("Posición:"),
                            dcc.Dropdown(
                                id="position-filter", 
                                placeholder="Seleccionar Posición",
                                style={"position": "relative", "zIndex": "997"}
                            )
                        ], md=3),
                        
                        # Filtro de jugadores
                        dbc.Col([
                            html.Label("Jugador:"),
                            dcc.Dropdown(
                                id="player-filter", 
                                placeholder="Seleccionar Jugador",
                                style={"position": "relative", "zIndex": "996"}
                            )
                        ], md=3)
                    ])
                ])
            ], className="mb-4", style={"position": "relative", "zIndex": "1000"})
        ])
    ]),
    
    # Almacenamiento de datos filtrados
    dcc.Store(id='filtered-data'),
    
    # KPIs - Ahora con un z-index menor que los filtros
    dbc.Row(
        id="kpi-cards-row", 
        className="mb-4", 
        style={"position": "relative", "zIndex": "1"}
    ),
    
    # Gráficos principales - También con z-index menor
    dbc.Row([
        # Gráfico de radar
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Perfil de Rendimiento"),
                dbc.CardBody([
                    dcc.Graph(id="radar-chart")
                ])
            ], style={"position": "relative", "zIndex": "1"})
        ], md=6, className="mb-4"),
        
        # Gráfico de dispersión
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Relación Distancia vs Velocidad"),
                dbc.CardBody([
                    dcc.Graph(id="scatter-plot")
                ])
            ], style={"position": "relative", "zIndex": "1"})
        ], md=6, className="mb-4")
    ]),
    
    # Segunda fila de gráficos
    dbc.Row([
        # Gráfico de barras comparativo
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Comparativa por Posición"),
                dbc.CardBody([
                    dcc.Graph(id="bar-chart")
                ])
            ], style={"position": "relative", "zIndex": "1"})
        ], md=12, className="mb-4")
    ]),
    
], fluid=True)

# Cargar opciones de filtros iniciales solo para la división
@callback(
    [Output("division-filter", "options"),
     Output("division-filter", "value")],
    [Input("_", "children")]
)
def inicializar_filtros(_):
    df = cargar_datos()
    
    # Opciones para divisiones
    divisiones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": div, "value": div} for div in sorted(df['division'].unique())
    ]
    
    return divisiones, "Todas"

# Actualizar opciones de equipos cuando cambia la división
@callback(
    Output("team-filter", "options"),
    Output("team-filter", "value"),
    [Input("division-filter", "value")],
    prevent_initial_call=True
)
def actualizar_opciones_equipos(division):
    df = cargar_datos()
    
    # Si se selecciona "Todas" o no hay selección, mostrar todos los equipos
    if not division or division == "Todas":
        equipos = [{"label": "Todos", "value": "Todos"}] + [
            {"label": equipo, "value": equipo} for equipo in sorted(df['team_name'].unique())
        ]
        return equipos, "Todos"
    
    # Filtrar los equipos según la división seleccionada
    filtered_df = df[df['division'] == division]
    equipos = [{"label": "Todos", "value": "Todos"}] + [
        {"label": equipo, "value": equipo} for equipo in sorted(filtered_df['team_name'].unique())
    ]
    
    return equipos, "Todos"

# Actualizar opciones de posiciones cuando cambian división y equipo
@callback(
    Output("position-filter", "options"),
    Output("position-filter", "value"),
    [Input("division-filter", "value"),
     Input("team-filter", "value")],
    prevent_initial_call=True
)
def actualizar_opciones_posiciones(division, team):
    df = cargar_datos()
    filtered_df = df.copy()
    
    # Aplicar filtros secuenciales
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    # Crear opciones para el dropdown de posiciones
    posiciones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": pos, "value": pos} for pos in sorted(filtered_df['position_name'].unique())
    ]
    
    return posiciones, "Todas"

# Actualizar opciones de jugadores cuando cambian los otros filtros
@callback(
    Output("player-filter", "options"),
    Output("player-filter", "value"),
    [Input("division-filter", "value"),
     Input("team-filter", "value"),
     Input("position-filter", "value")],
    prevent_initial_call=True
)
def actualizar_opciones_jugadores(division, team, position):
    df = cargar_datos()
    filtered_df = df.copy()
    
    # Aplicar filtros secuenciales
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    if position and position != "Todas":
        filtered_df = filtered_df[filtered_df['position_name'] == position]
    
    # Crear opciones para el dropdown de jugadores
    jugadores = [{"label": "Todos", "value": "Todos"}] + [
        {"label": jug, "value": jug} for jug in sorted(filtered_df['athlete_name'].unique())
    ]
    
    return jugadores, "Todos"

# Actualizar datos filtrados y gráficos automáticamente al cambiar filtros
@callback(
    [Output("filtered-data", "data"),
     Output("radar-chart", "figure"),
     Output("scatter-plot", "figure"),
     Output("bar-chart", "figure")],
    [Input("division-filter", "value"),
     Input("team-filter", "value"),
     Input("position-filter", "value"),
     Input("player-filter", "value")]
)
def actualizar_datos_y_graficos(division, team, position, player):
    # Cargar y filtrar datos
    df = cargar_datos()
    filtered_df = filtrar_dataframe(df, division, team, position, player)
    
    # Generar gráficos
    radar_fig = generar_grafico_radar(filtered_df, player)
    scatter_fig = generar_grafico_distancia_velocidad(filtered_df)
    bar_fig = generar_grafico_comparativa_posiciones(filtered_df)
    
    # Devolver datos filtrados y gráficos
    return filtered_df.to_json(date_format='iso', orient='split'), radar_fig, scatter_fig, bar_fig

# Actualizar los KPIs
@callback(
    Output("kpi-cards-row", "children"),
    [Input("filtered-data", "data")]
)
def actualizar_kpis(json_data):
    if not json_data:
        raise PreventUpdate
    
    df = pd.read_json(json_data, orient='split')
    
    # Calcular métricas clave
    n_jugadores = df['athlete_name'].nunique()
    dist_promedio = df['total_distance'].mean()
    vel_max = df['max_vel'].max()
    
    # Crear tarjetas KPI
    kpi_cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Jugadores", className="card-subtitle"),
                    html.H3(f"{n_jugadores}", className="card-title text-primary")
                ])
            ], className="text-center")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Distancia Promedio", className="card-subtitle"),
                    html.H3(f"{dist_promedio:.1f} m", className="card-title text-success")
                ])
            ], className="text-center")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Velocidad Máxima", className="card-subtitle"),
                    html.H3(f"{vel_max:.1f} km/h", className="card-title text-danger")
                ])
            ], className="text-center")
        ], md=4)
    ]
    
    return kpi_cards

# Componente invisible para inicializar la página
layout.children.append(html.Div(id="_", style={"display": "none"}))