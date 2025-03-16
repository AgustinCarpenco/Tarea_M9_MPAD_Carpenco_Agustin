import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Intentar cargar datos reales de GPS si existe el archivo
try:
    if os.path.exists('data/gps_full.csv'):
        df_gps = pd.read_csv('data/gps_full.csv')
        print("Datos GPS cargados correctamente.")
    else:
        raise FileNotFoundError("Archivo GPS no encontrado, creando datos de ejemplo.")
except Exception as e:
    print(f"Error al cargar datos GPS: {e}")
    # Crear datos de muestra si no se puede cargar el archivo
    def generar_datos_gps_muestra():
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
                # Solo incluir fechas de "entrenamientos" (lunes a viernes)
                if date.dayofweek < 5:  # Lunes a Viernes
                    # Generar estadísticas GPS aleatorias
                    distance = np.random.uniform(6, 12)  # Distancia en km
                    sprint_count = np.random.randint(10, 50)  # Número de sprints
                    max_speed = np.random.uniform(25, 35)  # Velocidad máxima en km/h
                    avg_speed = np.random.uniform(8, 15)  # Velocidad promedio en km/h
                    high_intensity_distance = np.random.uniform(1, 4)  # Distancia a alta intensidad en km
                    acceleration_count = np.random.randint(20, 100)  # Número de aceleraciones
                    deceleration_count = np.random.randint(20, 100)  # Número de desaceleraciones
                    
                    data.append({
                        'fecha': date,
                        'jugador': player,
                        'distancia_total_km': distance,
                        'num_sprints': sprint_count,
                        'velocidad_max_kmh': max_speed,
                        'velocidad_promedio_kmh': avg_speed,
                        'distancia_alta_intensidad_km': high_intensity_distance,
                        'num_aceleraciones': acceleration_count,
                        'num_desaceleraciones': deceleration_count
                    })
        
        return pd.DataFrame(data)
    
    df_gps = generar_datos_gps_muestra()

def layout():
    """Layout de la página de GPS."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard de GPS", className="mb-4"),
                
                # Filtros específicos de GPS
                dbc.Card([
                    dbc.CardHeader("Filtros"),
                    dbc.CardBody([
                        dbc.Row([
                            # Selector de fechas
                            dbc.Col([
                                html.Label("Rango de Fechas"),
                                dcc.DatePickerRange(
                                    id='gps-date-range',
                                    start_date=datetime.now() - timedelta(days=30),
                                    end_date=datetime.now(),
                                    calendar_orientation='horizontal',
                                    clearable=True,
                                    with_portal=True,
                                    first_day_of_week=1
                                )
                            ], md=4),
                            
                            # Selector de jugadores
                            dbc.Col([
                                html.Label("Seleccionar Jugadores"),
                                dcc.Dropdown(
                                    id='gps-player-dropdown',
                                    options=[
                                        {'label': player, 'value': player} for player in df_gps['jugador'].unique()
                                    ],
                                    multi=True,
                                    placeholder="Seleccione jugadores",
                                    value=df_gps['jugador'].unique().tolist()[:2]  # Seleccionar primeros 2 jugadores por defecto
                                )
                            ], md=4),
                            
                            # Selector de métricas
                            dbc.Col([
                                html.Label("Métricas a Mostrar"),
                                dcc.Dropdown(
                                    id='gps-metric-dropdown',
                                    options=[
                                        {'label': 'Distancia Total (km)', 'value': 'distancia_total_km'},
                                        {'label': 'Número de Sprints', 'value': 'num_sprints'},
                                        {'label': 'Velocidad Máxima (km/h)', 'value': 'velocidad_max_kmh'},
                                        {'label': 'Distancia a Alta Intensidad (km)', 'value': 'distancia_alta_intensidad_km'},
                                        {'label': 'Aceleraciones', 'value': 'num_aceleraciones'},
                                        {'label': 'Desaceleraciones', 'value': 'num_desaceleraciones'}
                                    ],
                                    value='distancia_total_km',
                                    clearable=False
                                )
                            ], md=4)
                        ]),
                        
                        # Botón para aplicar filtros
                        dbc.Button("Aplicar Filtros", id="apply-gps-filters-btn", color="primary", className="mt-3")
                    ])
                ], className="mb-4 shadow"),
                
                # Tabla interactiva de datos GPS
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Datos GPS"),
                            dbc.CardBody([
                                html.Div(id="gps-table-container")
                            ])
                        ], className="shadow")
                    ], className="mb-4")
                ]),
                
                # Gráficos de GPS
                dbc.Row([
                    # Gráfico 1: Mapa de Calor por Jugador
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Mapa de Calor de Métricas por Jugador"),
                            dbc.CardBody([
                                dcc.Graph(id='gps-heatmap')
                            ])
                        ], className="shadow h-100")
                    ], md=6, className="mb-4"),
                    
                    # Gráfico 2: Comparación de Métricas
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Comparación de Métricas por Jugador"),
                            dbc.CardBody([
                                dcc.Graph(id='gps-comparison')
                            ])
                        ], className="shadow h-100")
                    ], md=6, className="mb-4")
                ]),
                
                # Gráfico 3: Evolución temporal
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Evolución Temporal de Métricas"),
                            dbc.CardBody([
                                dcc.Graph(id='gps-timeline')
                            ])
                        ], className="shadow")
                    ], className="mb-4")
                ])
            ])
        ])
    ], fluid=True)

# Callback para actualizar la tabla y los gráficos GPS
@callback(
    [Output('gps-table-container', 'children'),
     Output('gps-heatmap', 'figure'),
     Output('gps-comparison', 'figure'),
     Output('gps-timeline', 'figure')],
    [Input('apply-gps-filters-btn', 'n_clicks')],
    [State('gps-date-range', 'start_date'),
     State('gps-date-range', 'end_date'),
     State('gps-player-dropdown', 'value'),
     State('gps-metric-dropdown', 'value')]
)
def update_gps_visualizations(n_clicks, start_date, end_date, selected_players, selected_metric):
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
        selected_players = df_gps['jugador'].unique().tolist()
    
    # Asegurarse de que fecha sea datetime si es string
    if 'fecha' in df_gps.columns and df_gps['fecha'].dtype == 'object':
        df_gps['fecha'] = pd.to_datetime(df_gps['fecha'])
    
    # Filtrar datos
    filtered_df = df_gps[
        (df_gps['fecha'] >= start_date) & 
        (df_gps['fecha'] <= end_date) & 
        (df_gps['jugador'].isin(selected_players))
    ].copy()
    
    # Crear tabla interactiva
    table = dash_table.DataTable(
        id='gps-data-table',
        columns=[
            {"name": "Fecha", "id": "fecha"},
            {"name": "Jugador", "id": "jugador"},
            {"name": "Distancia (km)", "id": "distancia_total_km"},
            {"name": "Sprints", "id": "num_sprints"},
            {"name": "Vel. Máx. (km/h)", "id": "velocidad_max_kmh"},
            {"name": "Dist. Alta Int. (km)", "id": "distancia_alta_intensidad_km"},
            {"name": "Aceleraciones", "id": "num_aceleraciones"},
            {"name": "Desaceleraciones", "id": "num_desaceleraciones"}
        ],
        data=filtered_df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '8px'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        filter_action="native",
        sort_action="native"
    )
    
    # Variables para título del gráfico de evolución
    metric_labels = {
        'distancia_total_km': 'Distancia Total (km)',
        'num_sprints': 'Número de Sprints',
        'velocidad_max_kmh': 'Velocidad Máxima (km/h)',
        'distancia_alta_intensidad_km': 'Distancia a Alta Intensidad (km)',
        'num_aceleraciones': 'Aceleraciones',
        'num_desaceleraciones': 'Desaceleraciones'
    }
    
    # Obtener nombre bonito de la métrica seleccionada
    metric_name = metric_labels.get(selected_metric, selected_metric)
    
    # Agrupar por jugador para el primer gráfico y generar matriz para el heatmap
    # Primero, obtener todas las métricas relevantes
    metrics = ['distancia_total_km', 'num_sprints', 'velocidad_max_kmh', 
              'distancia_alta_intensidad_km', 'num_aceleraciones', 'num_desaceleraciones']
    
    # Crear un DataFrame normalizado para el heatmap
    heatmap_data = []
    
    for player in selected_players:
        player_data = filtered_df[filtered_df['jugador'] == player]
        if len(player_data) > 0:
            player_means = player_data[metrics].mean()
            
            # Normalizar valores para cada métrica (0-1 range)
            max_values = filtered_df[metrics].max()
            normalized_values = player_means / max_values
            
            for metric in metrics:
                heatmap_data.append({
                    'jugador': player,
                    'metrica': metric_labels[metric],
                    'valor': player_means[metric],
                    'valor_normalizado': normalized_values[metric]
                })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Gráfico 1: Heatmap de métricas por jugador
    if len(heatmap_df) > 0:
        fig1 = px.density_heatmap(
            heatmap_df, 
            x='metrica', 
            y='jugador', 
            z='valor_normalizado',
            color_continuous_scale='Viridis',
            title='Mapa de Calor de Métricas por Jugador (Normalizado)',
            labels={'jugador': 'Jugador', 'metrica': 'Métrica', 'valor_normalizado': 'Valor Normalizado'}
        )
        
        # Añadir anotaciones con los valores originales
        for i, row in heatmap_df.iterrows():
            fig1.add_annotation(
                x=row['metrica'],
                y=row['jugador'],
                text=f"{row['valor']:.1f}",
                showarrow=False,
                font=dict(color="white" if row['valor_normalizado'] > 0.5 else "black")
            )
    else:
        # Heatmap vacío si no hay datos
        fig1 = go.Figure()
        fig1.update_layout(title="No hay datos suficientes para mostrar el heatmap")
    
    # Gráfico 2: Comparación de la métrica seleccionada entre jugadores
    # Agrupar por jugador para la métrica seleccionada
    player_comparison = filtered_df.groupby('jugador')[selected_metric].mean().reset_index()
    
    fig2 = px.bar(
        player_comparison, 
        x='jugador', 
        y=selected_metric,
        color='jugador',
        title=f'Comparación de {metric_name} por Jugador',
        labels={'jugador': 'Jugador', selected_metric: metric_name}
    )
    
    # Gráfico 3: Evolución temporal de la métrica seleccionada
    # Agrupar por fecha y jugador para ver la evolución temporal
    time_series = filtered_df.groupby(['fecha', 'jugador']).agg({
        selected_metric: 'mean'
    }).reset_index()
    
    fig3 = px.line(
        time_series, 
        x='fecha', 
        y=selected_metric, 
        color='jugador',
        title=f'Evolución de {metric_name} a lo Largo del Tiempo',
        labels={'fecha': 'Fecha', selected_metric: metric_name, 'jugador': 'Jugador'}
    )
    
    fig3.update_xaxes(title='Fecha')
    fig3.update_yaxes(title=metric_name)
    
    return table, fig1, fig2, fig3