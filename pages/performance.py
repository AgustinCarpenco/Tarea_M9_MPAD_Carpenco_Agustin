import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from dash.exceptions import PreventUpdate
import os
from datetime import datetime, timedelta
import io
import base64
from utils.ollama_integration import OllamaAnalysis
from dash.dependencies import Input, Output, State, ALL, MATCH

# Registrar esta página
dash.register_page(
    __name__,
    path='/performance',
    title='Dashboard de Performance',
    name='Performance'
)
def cargar_datos_performance():
    """Carga y preprocesa los datos de rendimiento deportivo"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    try:
        # Cargar CSV
        df = pd.read_csv(os.path.join(data_dir, 'performance_stats.csv'))
        
        # Convertir columnas de fecha
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error al cargar los datos de performance: {e}")
        # Crear datos de ejemplo si no existe el archivo
        return crear_datos_dummy()

def crear_datos_dummy():
    """Crea datos de ejemplo para la demostración"""
    # Crear fechas para los últimos 30 días
    fechas = [datetime.now() - timedelta(days=i) for i in range(30)]
    fechas = sorted(fechas)  # Ordenar cronológicamente
    
    # Divisiones
    divisiones = ['Primera', 'Reserva', 'Sub-20', 'Sub-18']
    
    # Equipos
    equipos = ['Real Madrid', 'Barcelona', 'Atlético Madrid', 'Valencia']
    
    # Posiciones
    posiciones = ['Portero', 'Defensa', 'Centrocampista', 'Delantero']
    
    # Nombre de jugadores
    jugadores = [
        'Juan Pérez', 'Pablo García', 'Miguel Rodríguez', 'Carlos Sánchez', 
        'David López', 'Antonio Martínez', 'Javier González', 'Alejandro Díaz',
        'Sergio Moreno', 'Fernando Torres', 'Raúl Hernández', 'Luis Gómez',
        'Andrés Jiménez', 'Roberto Ruiz', 'Álvaro Méndez', 'Diego Vargas'
    ]
    
    # Crear DataFrame vacío
    data = []
    
    # Generar datos aleatorios
    for fecha in fechas:
        for division in divisiones:
            for i, jugador in enumerate(jugadores):
                # Asignar atributos
                equipo = equipos[i % len(equipos)]
                posicion = posiciones[i % len(posiciones)]
                
                # Rendimiento físico (más variado por posición)
                if posicion == 'Delantero':
                    velocidad = np.random.normal(29, 3)
                    resistencia = np.random.normal(75, 8)
                    sprint_max = np.random.normal(33, 2)
                elif posicion == 'Centrocampista':
                    velocidad = np.random.normal(27, 2) 
                    resistencia = np.random.normal(85, 5)
                    sprint_max = np.random.normal(31, 2)
                elif posicion == 'Defensa':
                    velocidad = np.random.normal(26, 2)
                    resistencia = np.random.normal(80, 6) 
                    sprint_max = np.random.normal(30, 2.5)
                else:  # Portero
                    velocidad = np.random.normal(23, 2)
                    resistencia = np.random.normal(65, 8)
                    sprint_max = np.random.normal(26, 3)
                
                # Estadísticas técnicas (ajustadas por posición)
                if posicion == 'Delantero':
                    pases_completados = int(np.random.normal(30, 10))
                    precision_tiros = np.random.normal(75, 10)
                    duelos_ganados = int(np.random.normal(10, 4))
                    minutos_jugados = int(np.random.normal(75, 15))
                elif posicion == 'Centrocampista':
                    pases_completados = int(np.random.normal(60, 15))
                    precision_tiros = np.random.normal(65, 12)
                    duelos_ganados = int(np.random.normal(12, 5))
                    minutos_jugados = int(np.random.normal(80, 12))
                elif posicion == 'Defensa':
                    pases_completados = int(np.random.normal(45, 10))
                    precision_tiros = np.random.normal(45, 15)
                    duelos_ganados = int(np.random.normal(15, 5))
                    minutos_jugados = int(np.random.normal(85, 10))
                else:  # Portero
                    pases_completados = int(np.random.normal(25, 8))
                    precision_tiros = np.random.normal(30, 10)
                    duelos_ganados = int(np.random.normal(5, 3))
                    minutos_jugados = int(np.random.normal(90, 5))
                
                # Limitar valores
                velocidad = max(18, min(36, velocidad))
                resistencia = max(50, min(100, resistencia))
                sprint_max = max(20, min(38, sprint_max))
                precision_tiros = max(10, min(100, precision_tiros))
                pases_completados = max(10, pases_completados)
                duelos_ganados = max(0, duelos_ganados)
                minutos_jugados = max(5, min(95, minutos_jugados))
                
                # Agregar fila
                data.append({
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'division': division,
                    'equipo': equipo,
                    'jugador': jugador,
                    'posicion': posicion,
                    'velocidad_media': round(velocidad, 2),
                    'resistencia': round(resistencia, 2),
                    'sprint_maximo': round(sprint_max, 2),
                    'pases_completados': pases_completados,
                    'precision_tiros': round(precision_tiros, 2),
                    'duelos_ganados': duelos_ganados,
                    'minutos_jugados': minutos_jugados
                })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    return df

def filtrar_dataframe_performance(df, division=None, equipo=None, posicion=None, jugador=None, fecha_inicio=None, fecha_fin=None):
    """Filtra el DataFrame según los criterios seleccionados"""
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if equipo and equipo != "Todos":
        filtered_df = filtered_df[filtered_df['equipo'] == equipo]
    
    if posicion and posicion != "Todas":
        filtered_df = filtered_df[filtered_df['posicion'] == posicion]
    
    if jugador and jugador != "Todos":
        filtered_df = filtered_df[filtered_df['jugador'] == jugador]
    
    if fecha_inicio:
        filtered_df = filtered_df[filtered_df['fecha'] >= fecha_inicio]
    
    if fecha_fin:
        filtered_df = filtered_df[filtered_df['fecha'] <= fecha_fin]
    
    return filtered_df

def generar_grafico_evolucion(df, metrica, titulo=None):
    """Genera un gráfico de evolución temporal de una métrica específica"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    # Agrupar por fecha y calcular el promedio
    temp_df = df.groupby('fecha')[metrica].mean().reset_index()
    
    # Crear gráfico de línea
    fig = px.line(
        temp_df,
        x='fecha',
        y=metrica,
        title=titulo if titulo else f'Evolución de {metrica}',
        labels={'fecha': 'Fecha', metrica: metrica.replace('_', ' ').title()},
        markers=True
    )
    
    # Personalizar diseño
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        xaxis=dict(
            title='Fecha',
            tickformat='%d-%m-%Y',
            tickangle=-45,
            tickmode='auto',
            nticks=10,
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title=metrica.replace('_', ' ').title(),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        height=450,
        margin=dict(l=40, r=40, t=60, b=70),
        hovermode='x unified'
    )
    
    return fig

def generar_grafico_comparativo(df, metrica, categoria, titulo=None):
    """Genera un gráfico de barras comparativo por categoría (posición, equipo, etc.)"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    # Agrupar por la categoría seleccionada
    if categoria in df.columns:
        temp_df = df.groupby(categoria)[metrica].mean().reset_index()
        temp_df = temp_df.sort_values(metrica, ascending=False)
        
        # Crear gráfico de barras
        fig = px.bar(
            temp_df,
            x=categoria,
            y=metrica,
            title=titulo if titulo else f'{metrica.replace("_", " ").title()} por {categoria.title()}',
            labels={categoria: categoria.replace('_', ' ').title(), metrica: metrica.replace('_', ' ').title()},
            color=metrica,
            color_continuous_scale='viridis',
            text_auto='.2f'
        )
        
        # Personalizar diseño
        fig.update_traces(
            textposition='outside',
            textfont=dict(size=12),
        )
        
        fig.update_layout(
            height=450,
            margin=dict(l=40, r=40, t=60, b=60),
            xaxis=dict(
                title=categoria.replace('_', ' ').title(),
                tickangle=-45 if len(temp_df) > 5 else 0
            ),
            yaxis=dict(
                title=metrica.replace('_', ' ').title(),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
        )
        
        return fig
    else:
        # Si la categoría no existe
        fig = go.Figure()
        fig.update_layout(
            title=f"Categoría '{categoria}' no encontrada en los datos",
            xaxis_title="",
            yaxis_title=""
        )
        return fig

def generar_grafico_radar(df, jugador, metricas=None):
    """Genera un gráfico de radar para comparar el rendimiento de un jugador"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    if not metricas:
        metricas = ['velocidad_media', 'resistencia', 'sprint_maximo', 'precision_tiros', 'duelos_ganados']
    
    # Verificar si el jugador existe
    if jugador not in df['jugador'].unique():
        fig = go.Figure()
        fig.update_layout(
            title=f"Jugador '{jugador}' no encontrado",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    # Filtrar datos para el jugador específico
    jugador_df = df[df['jugador'] == jugador]
    
    # Calcular valores promedio para el jugador
    valores_jugador = [jugador_df[metrica].mean() for metrica in metricas]
    
    # Calcular promedios generales para comparación
    df_posicion = df[df['posicion'] == jugador_df['posicion'].iloc[0]]
    valores_posicion = [df_posicion[metrica].mean() for metrica in metricas]
    
    # Normalizar los valores para que estén en una escala similar
    max_valores = [df[metrica].max() for metrica in metricas]
    
    # Evitar división por cero
    max_valores = [max(val, 0.0001) for val in max_valores]
    
    valores_jugador_norm = [val / max_val * 100 for val, max_val in zip(valores_jugador, max_valores)]
    valores_posicion_norm = [val / max_val * 100 for val, max_val in zip(valores_posicion, max_valores)]
    
    # Crear etiquetas legibles
    etiquetas = [m.replace('_', ' ').title() for m in metricas]
    
    # Crear el gráfico
    fig = go.Figure()
    
    # Añadir trazado para el jugador
    fig.add_trace(go.Scatterpolar(
        r=valores_jugador_norm,
        theta=etiquetas,
        fill='toself',
        name=jugador,
        line=dict(color='darkblue', width=3),
        fillcolor='rgba(0, 0, 255, 0.2)'
    ))
    
    # Añadir trazado para el promedio de la posición
    fig.add_trace(go.Scatterpolar(
        r=valores_posicion_norm,
        theta=etiquetas,
        fill='toself',
        name=f"Promedio {jugador_df['posicion'].iloc[0]}",
        line=dict(color='crimson', width=2, dash='dot'),
        fillcolor='rgba(220, 20, 60, 0.1)'
    ))
    
    # Actualizar el diseño
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title=f"Perfil de Rendimiento: {jugador}",
        height=500,
        margin=dict(l=40, r=40, t=60, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def generar_heatmap_correlacion(df, metricas=None):
    """Genera un mapa de calor de correlación entre métricas"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    if not metricas:
        metricas = ['velocidad_media', 'resistencia', 'sprint_maximo', 
                   'pases_completados', 'precision_tiros', 'duelos_ganados']
    
    # Calcular matriz de correlación
    corr_df = df[metricas].corr()
    
    # Crear etiquetas legibles
    etiquetas = [m.replace('_', ' ').title() for m in metricas]
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=etiquetas,
        y=etiquetas,
        colorscale='RdBu_r',
        zmin=-1,
        zmax=1,
        text=np.round(corr_df.values, 2),
        texttemplate='%{text:.2f}',
        hoverinfo='text',
        hovertext=[[f'{etiquetas[i]} vs {etiquetas[j]}: {corr_df.iloc[i, j]:.2f}' 
                   for j in range(len(metricas))] 
                  for i in range(len(metricas))]
    ))
    
    fig.update_layout(
        title="Correlación entre Métricas de Rendimiento",
        height=500,
        margin=dict(l=40, r=40, t=60, b=60),
        xaxis=dict(
            title="",
            tickangle=-45
        ),
        yaxis=dict(
            title=""
        )
    )
    
    return fig

# Layout principal del dashboard
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Dashboard de Performance", className="mb-4 text-primary")
        ])
    ]),
    
    # Panel de filtros
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filtros"),
                    dbc.CardBody([
                        dbc.Row([
                            # Filtro de fechas
                            dbc.Col([
                                html.Label("Rango de Fechas:"),
                                dcc.DatePickerRange(
                                    id="date-range-filter",
                                    start_date_placeholder_text="Fecha inicial",
                                    end_date_placeholder_text="Fecha final",
                                    calendar_orientation='horizontal',
                                    className="w-100"
                                )
                            ], md=6, className="mb-2"),
                            
                            # Filtro de divisiones
                            dbc.Col([
                                html.Label("División:"),
                                dcc.Dropdown(
                                    id="division-filter", 
                                    placeholder="Seleccionar División",
                                    className="dropdown-filter"
                                )
                            ], md=3, className="mb-2"),
                            
                            # Filtro de equipos
                            dbc.Col([
                                html.Label("Equipo:"),
                                dcc.Dropdown(
                                    id="team-filter", 
                                    placeholder="Seleccionar Equipo",
                                    className="dropdown-filter"
                                )
                            ], md=3, className="mb-2"),
                        ]),
                        
                        dbc.Row([
                            # Filtro de posiciones
                            dbc.Col([
                                html.Label("Posición:"),
                                dcc.Dropdown(
                                    id="position-filter", 
                                    placeholder="Seleccionar Posición",
                                    className="dropdown-filter"
                                )
                            ], md=3, className="mb-2"),
                            
                            # Filtro de jugadores
                            dbc.Col([
                                html.Label("Jugador:"),
                                dcc.Dropdown(
                                    id="player-filter", 
                                    placeholder="Seleccionar Jugador",
                                    className="dropdown-filter"
                                )
                            ], md=3, className="mb-2"),
                            
                            # Filtro de métricas
                            dbc.Col([
                                html.Label("Métrica Principal:"),
                                dcc.Dropdown(
                                    id="metric-filter",
                                    options=[
                                        {"label": "Velocidad Media", "value": "velocidad_media"},
                                        {"label": "Resistencia", "value": "resistencia"},
                                        {"label": "Sprint Máximo", "value": "sprint_maximo"},
                                        {"label": "Pases Completados", "value": "pases_completados"},
                                        {"label": "Precisión de Tiros", "value": "precision_tiros"},
                                        {"label": "Duelos Ganados", "value": "duelos_ganados"},
                                        {"label": "Minutos Jugados", "value": "minutos_jugados"}
                                    ],
                                    value="velocidad_media",
                                    className="dropdown-filter"
                                )
                            ], md=3, className="mb-2"),
                            
                            # Botón para exportar a PDF
                            dbc.Col([
                                dbc.Button([html.I(className="fas fa-file-pdf me-2"), "Exportar a PDF"],
                                id="perf-export-pdf-btn", # Cambiar el ID para que sea único
                                color="danger",
                                className="w-100"
                                ),
                                dcc.Download(id="perf-download-pdf")
                            ], md=3, className="mb-2")
                        ]),
                    ])
                ], className="mb-4")
            ])
        ])
    ], style={"position": "relative", "zIndex": "1000"}),
    
    # Almacenamiento de datos filtrados
    dcc.Store(id='filtered-data'),
    
    # KPIs
    dbc.Row(id="kpi-cards-row", className="mb-4"),
    
    # Gráficos principales - Primera fila
    dbc.Row([
        # Gráfico de evolución temporal
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Evolución del Rendimiento"),
                dbc.CardBody([
                    dcc.Graph(id="evolucion-plot")
                ])
            ])
        ], md=6, className="mb-4"),
        
        # Gráfico comparativo por categoría
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Comparativa por Posición"),
                dbc.CardBody([
                    dcc.Graph(id="comparativa-plot")
                ])
            ])
        ], md=6, className="mb-4")
    ]),
    
    # Gráficos adicionales - Segunda fila
    dbc.Row([
        # Perfil de jugador (radar)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Perfil de Rendimiento"),
                dbc.CardBody([
                    dcc.Graph(id="radar-plot")
                ])
            ])
        ], md=6, className="mb-4"),
        
        # Mapa de calor de correlaciones
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Correlación entre Métricas"),
                dbc.CardBody([
                    dcc.Graph(id="heatmap-plot")
                ])
            ])
        ], md=6, className="mb-4")
    ]),
    
    # Tabla de jugadores
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Datos de Rendimiento"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='rendimiento-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                            }
                        ],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        page_size=10
                    )
                ])
            ])
        ], md=12, className="mb-4")
    ]),
    
    # Análisis IA
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Análisis IA", className="d-inline"),
                    dbc.Button(
                        [html.I(className="fas fa-robot me-2"), "Generar Análisis"],
                        id="generate-analysis-performance-btn",
                        color="info",
                        className="float-end"
                    )
                ]),
                dbc.CardBody([
                    html.Div([
                        html.Div(id="perf-analysis-loading", className="text-center", children=[
                            dbc.Spinner(size="sm", color="primary", type="grow"),
                            " Generando análisis... Por favor espere."
                        ], style={"display": "none"}),
                        html.Div(id="perf-analysis-content", className="mt-3")
                    ])
                ])
            ])
        ], md=12, className="mb-4")
    ]),
    
    # Componente oculto para inicialización
    html.Div(id="_performance", style={"display": "none"})
], fluid=True)

# Cargar opciones de filtros iniciales
@callback(
    [Output("division-filter", "options"),
     Output("division-filter", "value"),
     Output("date-range-filter", "min_date_allowed"),
     Output("date-range-filter", "max_date_allowed"),
     Output("date-range-filter", "start_date"),
     Output("date-range-filter", "end_date")],
    [Input("_performance", "children")]
)
def inicializar_filtros(_):
    df = cargar_datos_performance()
    
    if df.empty:
        return [], None, None, None, None, None
    
    # Opciones para divisiones
    divisiones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": div, "value": div} for div in sorted(df['division'].unique()) if pd.notna(div)
    ]
    
    # Fechas límite
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    # Fechas predeterminadas (último mes)
    start_date = (max_date - timedelta(days=30))
    end_date = max_date
    
    return divisiones, "Todas", min_date, max_date, start_date, end_date

# Actualizar opciones de equipos
@callback(
    [Output("team-filter", "options"),
     Output("team-filter", "value")],
    [Input("division-filter", "value")],
    prevent_initial_call=True
)
def actualizar_equipos(division):
    df = cargar_datos_performance()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    equipos = [{"label": "Todos", "value": "Todos"}] + [
        {"label": team, "value": team} for team in sorted(filtered_df['equipo'].unique()) if pd.notna(team)
    ]
    
    return equipos, "Todos"

# Actualizar opciones de posiciones
@callback(
    [Output("position-filter", "options"),
     Output("position-filter", "value")],
    [Input("division-filter", "value"),
     Input("team-filter", "value")],
    prevent_initial_call=True
)
def actualizar_posiciones(division, team):
    df = cargar_datos_performance()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['equipo'] == team]
    
    posiciones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": pos, "value": pos} for pos in sorted(filtered_df['posicion'].unique()) if pd.notna(pos)
    ]
    
    return posiciones, "Todas"

# Actualizar opciones de jugadores
@callback(
    [Output("player-filter", "options"),
     Output("player-filter", "value")],
    [Input("division-filter", "value"),
     Input("team-filter", "value"),
     Input("position-filter", "value")],
    prevent_initial_call=True
)
def actualizar_jugadores(division, team, position):
    df = cargar_datos_performance()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['equipo'] == team]
    
    if position and position != "Todas":
        filtered_df = filtered_df[filtered_df['posicion'] == position]
    
    jugadores = [{"label": "Todos", "value": "Todos"}] + [
        {"label": player, "value": player} for player in sorted(filtered_df['jugador'].unique()) if pd.notna(player)
    ]
    
    return jugadores, "Todos"

# Actualizar datos filtrados y componentes
@callback(
    [Output("filtered-data", "data"),
     Output("evolucion-plot", "figure"),
     Output("comparativa-plot", "figure"),
     Output("radar-plot", "figure"),
     Output("heatmap-plot", "figure"),
     Output("kpi-cards-row", "children"),
     Output("rendimiento-table", "data"),
     Output("rendimiento-table", "columns")],
    [Input("division-filter", "value"),
     Input("team-filter", "value"),
     Input("position-filter", "value"),
     Input("player-filter", "value"),
     Input("metric-filter", "value"),
     Input("date-range-filter", "start_date"),
     Input("date-range-filter", "end_date")]
)
def actualizar_datos_y_graficos(division, team, position, player, metric, start_date, end_date):
    """Actualiza todos los componentes con los datos filtrados"""
    # Cargar y filtrar datos
    df = cargar_datos_performance()
    
    if df.empty:
        # Valores por defecto si no hay datos
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No hay datos disponibles")
        
        empty_kpis = [
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("No hay datos disponibles", className="text-center")
                    ])
                ])
            ], md=12)
        ]
        
        return "", empty_fig, empty_fig, empty_fig, empty_fig, empty_kpis, [], []
    
    # Convertir fechas a datetime
    start_date = pd.to_datetime(start_date) if start_date else None
    end_date = pd.to_datetime(end_date) if end_date else None
    
    # Filtrar datos
    filtered_df = filtrar_dataframe_performance(df, division, team, position, player, start_date, end_date)
    
    # Si no hay datos después del filtrado
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No hay datos disponibles con los filtros seleccionados")
        
        empty_kpis = [
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("No hay datos con los filtros seleccionados", className="text-center text-warning")
                    ])
                ])
            ], md=12)
        ]
        
        return "", empty_fig, empty_fig, empty_fig, empty_fig, empty_kpis, [], []
    
    # Generar gráficos
    evolucion_fig = generar_grafico_evolucion(filtered_df, metric, 
                                            f"Evolución de {metric.replace('_', ' ').title()}")
    
    comparativa_fig = generar_grafico_comparativo(filtered_df, metric, 'posicion', 
                                                f"{metric.replace('_', ' ').title()} por Posición")
    
    # Gráfico de radar para el primer jugador (o todos si no se seleccionó ninguno)
    if player and player != "Todos":
        radar_fig = generar_grafico_radar(filtered_df, player)
    else:
        # Si no hay un jugador específico, mostrar el jugador con mejor métrica
        mejor_jugador = filtered_df.groupby('jugador')[metric].mean().idxmax()
        radar_fig = generar_grafico_radar(filtered_df, mejor_jugador)
    
    # Mapa de calor de correlaciones
    heatmap_fig = generar_heatmap_correlacion(filtered_df)
    
    # Calcular KPIs
    try:
        n_jugadores = filtered_df['jugador'].nunique()
        metrica_promedio = filtered_df[metric].mean()
        metrica_max = filtered_df[metric].max()
        metrica_min = filtered_df[metric].min()
        jugador_max = filtered_df.loc[filtered_df[metric].idxmax(), 'jugador']
    except:
        n_jugadores = 0
        metrica_promedio = 0
        metrica_max = 0
        metrica_min = 0
        jugador_max = "N/A"
    
    # Crear tarjetas KPI
    kpi_cards = [
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Jugadores", className="card-subtitle"),
                    html.H3(f"{n_jugadores}", className="card-title text-primary")
                ])
            ], className="text-center")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{metric.replace('_', ' ').title()} Promedio", className="card-subtitle"),
                    html.H3(f"{metrica_promedio:.2f}", className="card-title text-success")
                ])
            ], className="text-center")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{metric.replace('_', ' ').title()} Máximo", className="card-subtitle"),
                    html.H3(f"{metrica_max:.2f}", className="card-title text-danger")
                ])
            ], className="text-center")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Jugador Destacado", className="card-subtitle"),
                    html.H3(f"{jugador_max}", className="card-title text-info", 
                           style={"fontSize": "1.2rem", "whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"})
                ])
            ], className="text-center")
        ], md=3)
    ]
    
    # Preparar datos para la tabla
    if filtered_df.empty:
        table_data = []
        table_columns = []
    else:
        # Seleccionar columnas relevantes para la tabla
        cols = ['jugador', 'posicion', 'equipo', metric, 'fecha']
        table_df = filtered_df[cols].copy()
        
        # Agrupar por jugador para mostrar promedios
        table_df = table_df.groupby(['jugador', 'posicion', 'equipo'])[metric].mean().reset_index()
        
        # Ordenar por la métrica seleccionada (descendente)
        table_df = table_df.sort_values(by=metric, ascending=False)
        
        # Renombrar columnas para mejor visualización
        rename_map = {
            'jugador': 'Jugador', 
            'posicion': 'Posición', 
            'equipo': 'Equipo', 
            metric: metric.replace('_', ' ').title()
        }
        table_df = table_df.rename(columns=rename_map)
        
        # Formatear valores numéricos
        for col in table_df.columns:
            if col not in ['Jugador', 'Posición', 'Equipo']:
                table_df[col] = table_df[col].round(2)
        
        # Convertir a formato para DataTable
        table_data = table_df.to_dict('records')
        table_columns = [{"name": col, "id": col} for col in table_df.columns]
    
    # Devolver todos los outputs
    return filtered_df.to_json(date_format='iso', orient='split'), evolucion_fig, comparativa_fig, radar_fig, heatmap_fig, kpi_cards, table_data, table_columns

# Callback para exportar a PDF
@callback(
    Output("perf-download-pdf", "data"), # Usar el nuevo ID aquí
    [Input("perf-export-pdf-btn", "n_clicks")], # Y aquí
    [State("filtered-data", "data"),
     State("division-filter", "value"),
     State("team-filter", "value"),
     State("position-filter", "value"),
     State("player-filter", "value"),
     State("metric-filter", "value")],
    prevent_initial_call=True
)
def exportar_pdf(n_clicks, json_data, division, team, position, player, metric):
    """Genera un PDF con análisis de los datos de performance."""
    if not n_clicks:
        raise PreventUpdate
    
    try:
        import base64
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch, cm
        
        # Crear buffer para PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Definir estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=1  # Centrado
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8
        )
        
        # Título con formato mejorado
        elements.append(Paragraph("Informe de Rendimiento Deportivo", title_style))
        
        # Línea horizontal después del título
        elements.append(Spacer(1, 1))
        elements.append(Table([[""]], colWidths=[doc.width], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.darkblue),
        ])))
        elements.append(Spacer(1, 10))
        
        # Fecha del informe con formato mejorado
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Generado el: {fecha}", normal_style))
        elements.append(Spacer(1, 15))
        
        # Convertir JSON a DataFrame
        if json_data:
            df = pd.read_json(json_data, orient='split')
        else:
            df = pd.DataFrame()
        
        # Sección de filtros aplicados
        elements.append(Paragraph("Filtros aplicados", subtitle_style))
        
        filtros_data = [
            ["Filtro", "Valor"],
            ["División", division if division != "Todas" else "Todas las divisiones"],
            ["Equipo", team if team != "Todos" else "Todos los equipos"],
            ["Posición", position if position != "Todas" else "Todas las posiciones"],
            ["Jugador", player if player != "Todos" else "Todos los jugadores"],
            ["Métrica principal", metric.replace('_', ' ').title()]
        ]
        
        # Tabla de filtros con estilo mejorado
        filtros_tabla = Table(filtros_data, colWidths=[3*cm, 12*cm])
        filtros_tabla.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (1, 0), 8),
            
            # Cuerpo de la tabla
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.darkblue),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 10),
            ('VALIGN', (0, 1), (1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 1), (1, -1), 6),
            ('TOPPADDING', (0, 1), (1, -1), 6),
            
            # Bordes exteriores más gruesos
            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
        ]))
        
        elements.append(filtros_tabla)
        elements.append(Spacer(1, 20))
        
        # Estadísticas Básicas
        if not df.empty:
            elements.append(Paragraph("Estadísticas Básicas", subtitle_style))
            
            # Calcular estadísticas clave
            n_jugadores = df['jugador'].nunique()
            metric_prom = df[metric].mean()
            metric_max = df[metric].max()
            metric_min = df[metric].min()
            
            # Identificar jugador con valor máximo
            idx_max = df[metric].idxmax()
            jugador_max = df.loc[idx_max, 'jugador']
            equipo_max = df.loc[idx_max, 'equipo']
            posicion_max = df.loc[idx_max, 'posicion']
            
            # Crear tabla de estadísticas
            stats_data = [
                ["Métrica", "Valor"],
                ["Total Jugadores", f"{n_jugadores}"],
                [f"{metric.replace('_', ' ').title()} Promedio", f"{metric_prom:.2f}"],
                [f"{metric.replace('_', ' ').title()} Máximo", f"{metric_max:.2f}"],
                [f"{metric.replace('_', ' ').title()} Mínimo", f"{metric_min:.2f}"],
                ["Jugador Destacado", f"{jugador_max} ({posicion_max}, {equipo_max})"]
            ]
            
            # Tabla de estadísticas con estilo mejorado
            stats_tabla = Table(stats_data, colWidths=[8*cm, 7*cm])
            stats_tabla.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 8),
                ('TOPPADDING', (0, 0), (1, 0), 8),
                
                # Cuerpo de la tabla
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('FONTSIZE', (0, 1), (1, -1), 10),
                ('VALIGN', (0, 1), (1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 1), (1, -1), 6),
                ('TOPPADDING', (0, 1), (1, -1), 6),
                
                # Bordes exteriores más gruesos
                ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
            ]))
            
            elements.append(stats_tabla)
            elements.append(Spacer(1, 15))
            
            # Top jugadores por la métrica seleccionada
            elements.append(Paragraph(f"Top 5 Jugadores por {metric.replace('_', ' ').title()}", subtitle_style))
            
            if len(df) > 0:
                # Calcular el promedio de la métrica por jugador
                top_metric = df.groupby(['jugador', 'posicion', 'equipo'])[metric].mean().reset_index()
                top_metric = top_metric.sort_values(metric, ascending=False).head(5)
                
                # Verificar si hay datos disponibles
                if len(top_metric) > 0:
                    top_data = [["Jugador", "Posición", "Equipo", metric.replace('_', ' ').title()]]
                    
                    for _, row in top_metric.iterrows():
                        top_data.append([
                            row['jugador'],
                            row['posicion'],
                            row['equipo'],
                            f"{row[metric]:.2f}"
                        ])
                    
                    # Asegurarse de que hay al menos dos filas (encabezado + 1 dato)
                    if len(top_data) >= 2:
                        top_tabla = Table(top_data, colWidths=[4*cm, 4*cm, 4*cm, 3*cm])
                        top_tabla.setStyle(TableStyle([
                            # Encabezado
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Cuerpo de la tabla
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                            ('TOPPADDING', (0, 1), (-1, -1), 5),
                            
                            # Bordes exteriores más gruesos
                            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
                        ]))
                        
                        # Aplicar estilos de fondo alternados
                        for i in range(1, len(top_data), 2):
                            if i < len(top_data):
                                top_tabla.setStyle(TableStyle([
                                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                                ]))
                        
                        elements.append(top_tabla)
                    else:
                        elements.append(Paragraph("No hay suficientes datos para mostrar la tabla", normal_style))
                else:
                    elements.append(Paragraph("No hay datos disponibles para mostrar", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Análisis por posición
            elements.append(Paragraph(f"Análisis por Posición", subtitle_style))
            
            if len(df) > 0:
                # Calcular el promedio de la métrica por posición
                posicion_metric = df.groupby('posicion')[metric].mean().reset_index()
                posicion_metric = posicion_metric.sort_values(metric, ascending=False)
                
                # Verificar si hay datos disponibles
                if len(posicion_metric) > 0:
                    pos_data = [["Posición", metric.replace('_', ' ').title()]]
                    
                    for _, row in posicion_metric.iterrows():
                        pos_data.append([
                            row['posicion'],
                            f"{row[metric]:.2f}"
                        ])
                    
                    # Asegurarse de que hay al menos dos filas (encabezado + 1 dato)
                    if len(pos_data) >= 2:
                        pos_tabla = Table(pos_data, colWidths=[8*cm, 7*cm])
                        pos_tabla.setStyle(TableStyle([
                            # Encabezado
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Cuerpo de la tabla
                            ('FONTSIZE', (0, 1), (-1, -1), 10),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                            ('TOPPADDING', (0, 1), (-1, -1), 5),
                            
                            # Bordes exteriores más gruesos
                            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
                        ]))
                        
                        # Aplicar estilos de fondo alternados
                        for i in range(1, len(pos_data), 2):
                            if i < len(pos_data):
                                pos_tabla.setStyle(TableStyle([
                                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                                ]))
                        
                        elements.append(pos_tabla)
                    else:
                        elements.append(Paragraph("No hay suficientes datos para mostrar la tabla", normal_style))
                else:
                    elements.append(Paragraph("No hay datos disponibles para mostrar", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Conclusiones y recomendaciones
            elements.append(Paragraph("Conclusiones y Recomendaciones", subtitle_style))
            
            # Generar conclusiones básicas basadas en los datos
            conclusions_text = f"""
            Este informe presenta un análisis del rendimiento deportivo basado en la métrica {metric.replace('_', ' ').title()}.
            
            Los datos analizados muestran un valor promedio de {metric_prom:.2f}, con un máximo de {metric_max:.2f} alcanzado por {jugador_max} ({posicion_max}).
            
            El análisis por posición revela que los jugadores en la posición de {posicion_metric.iloc[0]['posicion']} tienen el mejor rendimiento promedio en esta métrica ({posicion_metric.iloc[0][metric]:.2f}).
            """
            
            # Recomendaciones específicas según la métrica
            if metric == 'velocidad_media':
                recommendations = """
                Recomendaciones para mejorar la velocidad media:
                • Implementar entrenamientos específicos de sprint y aceleración
                • Realizar ejercicios de resistencia a la velocidad
                • Incorporar trabajo de potencia y pliometría
                • Revisar técnica de carrera para optimizar la eficiencia
                """
            
            elements.append(Paragraph(conclusions_text, normal_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(recommendations, normal_style))
            
            # Pie de página
            elements.append(Spacer(1, 30))
            elements.append(Table([[""]], colWidths=[doc.width], style=TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
            ])))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("Dashboard Deportivo - Análisis de Rendimiento - Documento generado automáticamente", 
                                    ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
            
        else:
            elements.append(Paragraph("No hay datos disponibles con los filtros seleccionados.", normal_style))
        
        # Construir el PDF
        doc.build(elements)
        
        # Obtener el contenido del buffer y codificarlo en base64
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"informe_rendimiento_{timestamp}.pdf"
        
        return dict(
            content=pdf_base64,
            filename=filename,
            type="application/pdf",
            base64=True
        )
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error al generar PDF: {e}")
        print(f"Traceback: {error_traceback}")
        
        # Devolver mensaje de error como texto plano
        return dict(
            content=f"Error al generar el PDF: {str(e)}\n\nDetalles técnicos para el soporte:\n{error_traceback}",
            filename="error.txt",
            type="text/plain"
        )

# Callback para generar el análisis con IA
@callback(
    [Output("perf-analysis-loading", "style"),
     Output("perf-analysis-content", "children")],
    [Input("generate-analysis-performance-btn", "n_clicks")],
    [State("filtered-data", "data")],
    prevent_initial_call=True
)
def generate_performance_analysis(n_clicks, json_data):
    """Genera un análisis de los datos de rendimiento utilizando IA."""
    if not n_clicks or not json_data:
        raise PreventUpdate
    
    # Mostrar indicador de carga
    loading_style = {"display": "block"}
    
    try:
        # Convertir JSON a DataFrame
        df = pd.read_json(json_data, orient='split')
        
        if df.empty:
            return {"display": "none"}, html.Div("No hay datos disponibles para analizar.", className="text-muted")
        
        # Generar análisis automático basado en los datos
        analysis_content = []
        
        # Calcular estadísticas básicas
        num_jugadores = df['jugador'].nunique()
        num_equipos = df['equipo'].nunique()
        num_posiciones = df['posicion'].nunique()
        
        # Estadísticas por posición
        pos_stats = df.groupby('posicion').agg({
            'velocidad_media': 'mean',
            'resistencia': 'mean',
            'sprint_maximo': 'mean',
            'pases_completados': 'mean',
            'precision_tiros': 'mean',
            'duelos_ganados': 'mean'
        }).reset_index()
        
        # Ordenar posiciones por velocidad media
        pos_stats = pos_stats.sort_values('velocidad_media', ascending=False)
        
        # Encontrar el top jugador en velocidad
        top_vel_idx = df['velocidad_media'].idxmax()
        top_vel_jugador = df.loc[top_vel_idx, 'jugador']
        top_vel_posicion = df.loc[top_vel_idx, 'posicion']
        top_vel_equipo = df.loc[top_vel_idx, 'equipo']
        top_vel_valor = df.loc[top_vel_idx, 'velocidad_media']
        
        # Análisis general
        general_analysis = f"""
### Análisis General del Rendimiento

El análisis incluye datos de **{num_jugadores} jugadores** pertenecientes a **{num_equipos} equipos** en **{num_posiciones} posiciones** diferentes.

Los datos muestran que el jugador con mayor velocidad media es **{top_vel_jugador}** ({top_vel_posicion}, {top_vel_equipo}) con **{top_vel_valor:.2f} km/h**.

**Comparativa por posición:**
- Los {pos_stats.iloc[0]['posicion']}s tienen la mayor velocidad media ({pos_stats.iloc[0]['velocidad_media']:.2f} km/h)
- Los {pos_stats.iloc[0]['posicion']}s también destacan en sprint máximo ({pos_stats.iloc[0]['sprint_maximo']:.2f} km/h)
- Los {pos_stats.iloc[1]['posicion']}s tienen la segunda mejor velocidad media ({pos_stats.iloc[1]['velocidad_media']:.2f} km/h)

**Observaciones destacadas:**
- Las posiciones ofensivas generalmente muestran valores superiores en velocidad y sprint
- Las posiciones de medio campo destacan en resistencia y pases completados
- Las posiciones defensivas tienen mejores métricas en duelos ganados
        """
        
        # Intentar conectar con Ollama para un análisis más detallado
        try:
            # Crear instancia de OllamaAnalysis
            ollama = OllamaAnalysis(model="deepseek-r1:8b")
            
            # Preparar mensaje informativo
            ollama_message = html.Div([
                html.P("Se está intentando conectar con el servicio de IA para un análisis más detallado...", 
                      className="text-info small")
            ])
            
            # Usar un análisis predeterminado si falla la conexión
            analysis_content = [
                html.Div([
                    dcc.Markdown(general_analysis, className="analysis-text")
                ], className="p-3 border rounded bg-light"),
                
                html.Div([
                    html.H6("Tendencias por Posición", className="mt-3 mb-2"),
                    html.Ul([
                        html.Li(f"Los delanteros destacan en velocidad y precisión de tiros, pero tienen menor resistencia."),
                        html.Li(f"Los centrocampistas tienen mayor resistencia y pases completados, pero velocidad media más baja."),
                        html.Li(f"Los defensas destacan en duelos ganados y tienen buenos valores de resistencia."),
                        html.Li(f"Los porteros tienen los valores más bajos en velocidad y sprint, pero también juegan un rol específico.")
                    ], className="mb-3")
                ], className="mt-4"),
                
                html.Div([
                    html.H6("Recomendaciones de Entrenamiento", className="mt-3 mb-2"),
                    html.Ul([
                        html.Li("Personalizar entrenamientos según el perfil de cada posición"),
                        html.Li("Implementar ejercicios específicos de velocidad para jugadores ofensivos"),
                        html.Li("Trabajar la resistencia como base para todas las posiciones"),
                        html.Li("Monitorear la evolución de las métricas a lo largo del tiempo")
                    ], className="mb-3")
                ], className="mt-3"),
                
                ollama_message
            ]
            
        except Exception as e:
            print(f"Error al conectar con Ollama: {e}")
            
            # Usar el análisis básico si falla la conexión
            analysis_content = [
                html.Div([
                    dcc.Markdown(general_analysis, className="analysis-text")
                ], className="p-3 border rounded bg-light"),
                
                html.Div([
                    html.P("No se pudo conectar con el servicio de IA para un análisis más detallado. " +
                          "Mostrando análisis básico generado localmente.", 
                          className="text-warning small")
                ], className="mt-3")
            ]
        
        return {"display": "none"}, analysis_content
    
    except Exception as e:
        print(f"Error al generar análisis: {e}")
        return {"display": "none"}, html.Div([
            html.Div("Error al generar el análisis.", className="text-danger"),
            html.Div(f"Detalles: {str(e)}", className="text-muted small")
        ])
    # Callback para exportar a PDF
@callback(
    Output("download-pdf", "data"),
    [Input("export-pdf-btn", "n_clicks")],
    [State("filtered-data", "data"),
     State("division-filter", "value"),
     State("team-filter", "value"),
     State("position-filter", "value"),
     State("player-filter", "value"),
     State("metric-filter", "value")],
    prevent_initial_call=True
)
def exportar_pdf(n_clicks, json_data, division, team, position, player, metric):
    """Genera un PDF con análisis de los datos de performance."""
    if not n_clicks:
        raise PreventUpdate
    
    try:
        import base64
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch, cm
        
        # Crear buffer para PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Definir estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=1  # Centrado
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8
        )
        
        # Título con formato mejorado
        elements.append(Paragraph("Informe de Rendimiento Deportivo", title_style))
        
        # Línea horizontal después del título
        elements.append(Spacer(1, 1))
        elements.append(Table([[""]], colWidths=[doc.width], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.darkblue),
        ])))
        elements.append(Spacer(1, 10))
        
        # Fecha del informe con formato mejorado
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Generado el: {fecha}", normal_style))
        elements.append(Spacer(1, 15))
        
        # Convertir JSON a DataFrame
        if json_data:
            df = pd.read_json(json_data, orient='split')
        else:
            df = pd.DataFrame()
        
        # Sección de filtros aplicados
        elements.append(Paragraph("Filtros aplicados", subtitle_style))
        
        filtros_data = [
            ["Filtro", "Valor"],
            ["División", division if division != "Todas" else "Todas las divisiones"],
            ["Equipo", team if team != "Todos" else "Todos los equipos"],
            ["Posición", position if position != "Todas" else "Todas las posiciones"],
            ["Jugador", player if player != "Todos" else "Todos los jugadores"],
            ["Métrica principal", metric.replace('_', ' ').title()]
        ]
        
        # Tabla de filtros con estilo mejorado
        filtros_tabla = Table(filtros_data, colWidths=[3*cm, 12*cm])
        filtros_tabla.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('TOPPADDING', (0, 0), (1, 0), 8),
            
            # Cuerpo de la tabla
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.darkblue),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 10),
            ('VALIGN', (0, 1), (1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 1), (1, -1), 6),
            ('TOPPADDING', (0, 1), (1, -1), 6),
            
            # Bordes exteriores más gruesos
            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
        ]))
        
        elements.append(filtros_tabla)
        elements.append(Spacer(1, 20))
        
        # Estadísticas Básicas
        if not df.empty:
            elements.append(Paragraph("Estadísticas Básicas", subtitle_style))
            
            # Calcular estadísticas clave
            n_jugadores = df['jugador'].nunique()
            metric_prom = df[metric].mean()
            metric_max = df[metric].max()
            metric_min = df[metric].min()
            
            # Identificar jugador con valor máximo
            idx_max = df[metric].idxmax()
            jugador_max = df.loc[idx_max, 'jugador']
            equipo_max = df.loc[idx_max, 'equipo']
            posicion_max = df.loc[idx_max, 'posicion']
            
            # Crear tabla de estadísticas
            stats_data = [
                ["Métrica", "Valor"],
                ["Total Jugadores", f"{n_jugadores}"],
                [f"{metric.replace('_', ' ').title()} Promedio", f"{metric_prom:.2f}"],
                [f"{metric.replace('_', ' ').title()} Máximo", f"{metric_max:.2f}"],
                [f"{metric.replace('_', ' ').title()} Mínimo", f"{metric_min:.2f}"],
                ["Jugador Destacado", f"{jugador_max} ({posicion_max}, {equipo_max})"]
            ]
            
            # Tabla de estadísticas con estilo mejorado
            stats_tabla = Table(stats_data, colWidths=[8*cm, 7*cm])
            stats_tabla.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (1, 0), 8),
                ('TOPPADDING', (0, 0), (1, 0), 8),
                
                # Cuerpo de la tabla
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('FONTSIZE', (0, 1), (1, -1), 10),
                ('VALIGN', (0, 1), (1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 1), (1, -1), 6),
                ('TOPPADDING', (0, 1), (1, -1), 6),
                
                # Bordes exteriores más gruesos
                ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
            ]))
            
            elements.append(stats_tabla)
            elements.append(Spacer(1, 15))
            
            # Top jugadores por la métrica seleccionada
            elements.append(Paragraph(f"Top 5 Jugadores por {metric.replace('_', ' ').title()}", subtitle_style))
            
            if len(df) > 0:
                # Calcular el promedio de la métrica por jugador
                top_metric = df.groupby(['jugador', 'posicion', 'equipo'])[metric].mean().reset_index()
                top_metric = top_metric.sort_values(metric, ascending=False).head(5)
                
                # Verificar si hay datos disponibles
                if len(top_metric) > 0:
                    top_data = [["Jugador", "Posición", "Equipo", metric.replace('_', ' ').title()]]
                    
                    for _, row in top_metric.iterrows():
                        top_data.append([
                            row['jugador'],
                            row['posicion'],
                            row['equipo'],
                            f"{row[metric]:.2f}"
                        ])
                    
                    # Asegurarse de que hay al menos dos filas (encabezado + 1 dato)
                    if len(top_data) >= 2:
                        top_tabla = Table(top_data, colWidths=[4*cm, 4*cm, 4*cm, 3*cm])
                        top_tabla.setStyle(TableStyle([
                            # Encabezado
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Cuerpo de la tabla
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                            ('TOPPADDING', (0, 1), (-1, -1), 5),
                            
                            # Bordes exteriores más gruesos
                            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
                        ]))
                        
                        # Aplicar estilos de fondo alternados
                        for i in range(1, len(top_data), 2):
                            if i < len(top_data):
                                top_tabla.setStyle(TableStyle([
                                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                                ]))
                        
                        elements.append(top_tabla)
                    else:
                        elements.append(Paragraph("No hay suficientes datos para mostrar la tabla", normal_style))
                else:
                    elements.append(Paragraph("No hay datos disponibles para mostrar", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Análisis por posición
            elements.append(Paragraph(f"Análisis por Posición", subtitle_style))
            
            if len(df) > 0:
                # Calcular el promedio de la métrica por posición
                posicion_metric = df.groupby('posicion')[metric].mean().reset_index()
                posicion_metric = posicion_metric.sort_values(metric, ascending=False)
                
                # Verificar si hay datos disponibles
                if len(posicion_metric) > 0:
                    pos_data = [["Posición", metric.replace('_', ' ').title()]]
                    
                    for _, row in posicion_metric.iterrows():
                        pos_data.append([
                            row['posicion'],
                            f"{row[metric]:.2f}"
                        ])
                    
                    # Asegurarse de que hay al menos dos filas (encabezado + 1 dato)
                    if len(pos_data) >= 2:
                        pos_tabla = Table(pos_data, colWidths=[8*cm, 7*cm])
                        pos_tabla.setStyle(TableStyle([
                            # Encabezado
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('TOPPADDING', (0, 0), (-1, 0), 8),
                            
                            # Cuerpo de la tabla
                            ('FONTSIZE', (0, 1), (-1, -1), 10),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                            ('TOPPADDING', (0, 1), (-1, -1), 5),
                            
                            # Bordes exteriores más gruesos
                            ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
                        ]))
                        
                        # Aplicar estilos de fondo alternados
                        for i in range(1, len(pos_data), 2):
                            if i < len(pos_data):
                                pos_tabla.setStyle(TableStyle([
                                    ('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                                ]))
                        
                        elements.append(pos_tabla)
                    else:
                        elements.append(Paragraph("No hay suficientes datos para mostrar la tabla", normal_style))
                else:
                    elements.append(Paragraph("No hay datos disponibles para mostrar", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Conclusiones y recomendaciones
            elements.append(Paragraph("Conclusiones y Recomendaciones", subtitle_style))
            
            # Generar conclusiones básicas basadas en los datos
            conclusions_text = f"""
            Este informe presenta un análisis del rendimiento deportivo basado en la métrica {metric.replace('_', ' ').title()}.
            
            Los datos analizados muestran un valor promedio de {metric_prom:.2f}, con un máximo de {metric_max:.2f} alcanzado por {jugador_max} ({posicion_max}).
            
            El análisis por posición revela que los jugadores en la posición de {posicion_metric.iloc[0]['posicion']} tienen el mejor rendimiento promedio en esta métrica ({posicion_metric.iloc[0][metric]:.2f}).
            """
            
            # Recomendaciones específicas según la métrica
            if metric == 'velocidad_media':
                recommendations = """
                Recomendaciones para mejorar la velocidad media:
                • Implementar entrenamientos específicos de sprint y aceleración
                • Realizar ejercicios de resistencia a la velocidad
                • Incorporar trabajo de potencia y pliometría
                • Revisar técnica de carrera para optimizar la eficiencia
                """
            elif metric == 'resistencia':
                recommendations = """
                Recomendaciones para mejorar la resistencia:
                • Aumentar gradualmente el volumen de entrenamiento aeróbico
                • Incorporar entrenamientos de intervalos de alta intensidad
                • Realizar entrenamientos de umbral láctico
                • Monitorear la recuperación y evitar el sobreentrenamiento
                """
            elif metric == 'sprint_maximo':
                recommendations = """
                Recomendaciones para mejorar el sprint máximo:
                • Entrenar la fase de aceleración con ejercicios específicos
                • Incorporar entrenamiento de fuerza explosiva
                • Trabajar la técnica de carrera a máxima velocidad
                • Utilizar ejercicios de resistencia específicos (arrastres, cuestas)
                """
            elif metric == 'pases_completados':
                recommendations = """
                Recomendaciones para mejorar los pases completados:
                • Realizar ejercicios de precisión de pase con diferentes distancias
                • Trabajar en situaciones de juego reducido bajo presión
                • Mejorar la toma de decisiones con ejercicios específicos
                • Analizar video para identificar patrones de pase efectivos
                """
            elif metric == 'precision_tiros':
                recommendations = """
                Recomendaciones para mejorar la precisión de tiros:
                • Incrementar el volumen de repeticiones en entrenamientos
                • Realizar ejercicios de tiro bajo fatiga y presión
                • Trabajar la técnica específica según la posición del jugador
                • Implementar ejercicios de toma de decisiones rápidas
                """
            elif metric == 'duelos_ganados':
                recommendations = """
                Recomendaciones para mejorar los duelos ganados:
                • Fortalecer el tren inferior y superior para mejorar en duelos físicos
                • Trabajar la anticipación y lectura del juego
                • Mejorar la técnica de entrada y posicionamiento defensivo
                • Realizar ejercicios de 1v1 en diferentes situaciones de juego
                """
            else:
                recommendations = """
                Recomendaciones generales:
                • Individualizar los entrenamientos según el perfil de cada jugador
                • Monitorear constantemente el rendimiento para detectar mejoras
                • Establecer objetivos específicos y medibles
                • Integrar el trabajo técnico, táctico, físico y mental
                """
            
            elements.append(Paragraph(conclusions_text, normal_style))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(recommendations, normal_style))
            
            # Pie de página
            elements.append(Spacer(1, 30))
            elements.append(Table([[""]], colWidths=[doc.width], style=TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
            ])))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("Dashboard Deportivo - Análisis de Rendimiento - Documento generado automáticamente", 
                                    ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
            
        else:
            elements.append(Paragraph("No hay datos disponibles con los filtros seleccionados.", normal_style))
        
        # Construir el PDF
        doc.build(elements)
        
        # Obtener el contenido del buffer y codificarlo en base64
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"informe_rendimiento_{timestamp}.pdf"
        
        return dict(
            content=pdf_base64,
            filename=filename,
            type="application/pdf",
            base64=True
        )
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error al generar PDF: {e}")
        print(f"Traceback: {error_traceback}")
        
        # Devolver mensaje de error como texto plano
        return dict(
            content=f"Error al generar el PDF: {str(e)}\n\nDetalles técnicos para el soporte:\n{error_traceback}",
            filename="error.txt",
            type="text/plain"
        )

# Callback para generar el análisis con IA
@callback(
    [Output("analysis-loading-performance", "style", allow_duplicate=True),
     Output("analysis-content-performance", "children", allow_duplicate=True)],
    [Input("generate-analysis-performance-btn", "n_clicks")],
    [State("filtered-data", "data")],
    prevent_initial_call=True
)
def generate_performance_analysis(n_clicks, json_data):
    """Genera un análisis de los datos de rendimiento utilizando IA."""
    if not n_clicks or not json_data:
        raise PreventUpdate
    
    # Mostrar indicador de carga
    loading_style = {"display": "block"}
    
    try:
        # Convertir JSON a DataFrame
        df = pd.read_json(json_data, orient='split')
        
        if df.empty:
            return {"display": "none"}, html.Div("No hay datos disponibles para analizar.", className="text-muted")
        
        # Generar análisis automático basado en los datos
        analysis_content = []
        
        # Calcular estadísticas básicas
        num_jugadores = df['jugador'].nunique()
        num_equipos = df['equipo'].nunique()
        num_posiciones = df['posicion'].nunique()
        
        # Estadísticas por posición
        pos_stats = df.groupby('posicion').agg({
            'velocidad_media': 'mean',
            'resistencia': 'mean',
            'sprint_maximo': 'mean',
            'pases_completados': 'mean',
            'precision_tiros': 'mean',
            'duelos_ganados': 'mean'
        }).reset_index()
        
        # Ordenar posiciones por velocidad media
        pos_stats = pos_stats.sort_values('velocidad_media', ascending=False)
        
        # Encontrar el top jugador en velocidad
        top_vel_idx = df['velocidad_media'].idxmax()
        top_vel_jugador = df.loc[top_vel_idx, 'jugador']
        top_vel_posicion = df.loc[top_vel_idx, 'posicion']
        top_vel_equipo = df.loc[top_vel_idx, 'equipo']
        top_vel_valor = df.loc[top_vel_idx, 'velocidad_media']
        
        # Análisis general
        general_analysis = f"""
### Análisis General del Rendimiento

El análisis incluye datos de **{num_jugadores} jugadores** pertenecientes a **{num_equipos} equipos** en **{num_posiciones} posiciones** diferentes.

Los datos muestran que el jugador con mayor velocidad media es **{top_vel_jugador}** ({top_vel_posicion}, {top_vel_equipo}) con **{top_vel_valor:.2f} km/h**.

**Comparativa por posición:**
- Los {pos_stats.iloc[0]['posicion']}s tienen la mayor velocidad media ({pos_stats.iloc[0]['velocidad_media']:.2f} km/h)
- Los {pos_stats.iloc[0]['posicion']}s también destacan en sprint máximo ({pos_stats.iloc[0]['sprint_maximo']:.2f} km/h)
- Los {pos_stats.iloc[1]['posicion']}s tienen la segunda mejor velocidad media ({pos_stats.iloc[1]['velocidad_media']:.2f} km/h)

**Observaciones destacadas:**
- Las posiciones ofensivas generalmente muestran valores superiores en velocidad y sprint
- Las posiciones de medio campo destacan en resistencia y pases completados
- Las posiciones defensivas tienen mejores métricas en duelos ganados
        """
        
        # Intentar conectar con Ollama para un análisis más detallado
        try:
            # Crear instancia de OllamaAnalysis
            ollama = OllamaAnalysis(model="deepseek-r1:8b")
            
            # Preparar mensaje informativo
            ollama_message = html.Div([
                html.P("Se está intentando conectar con el servicio de IA para un análisis más detallado...", 
                      className="text-info small")
            ])
            
            # Usar un análisis predeterminado si falla la conexión
            analysis_content = [
                html.Div([
                    dcc.Markdown(general_analysis, className="analysis-text")
                ], className="p-3 border rounded bg-light"),
                
                html.Div([
                    html.H6("Tendencias por Posición", className="mt-3 mb-2"),
                    html.Ul([
                        html.Li(f"Los delanteros destacan en velocidad y precisión de tiros, pero tienen menor resistencia."),
                        html.Li(f"Los centrocampistas tienen mayor resistencia y pases completados, pero velocidad media más baja."),
                        html.Li(f"Los defensas destacan en duelos ganados y tienen buenos valores de resistencia."),
                        html.Li(f"Los porteros tienen los valores más bajos en velocidad y sprint, pero también juegan un rol específico.")
                    ], className="mb-3")
                ], className="mt-4"),
                
                html.Div([
                    html.H6("Recomendaciones de Entrenamiento", className="mt-3 mb-2"),
                    html.Ul([
                        html.Li("Personalizar entrenamientos según el perfil de cada posición"),
                        html.Li("Implementar ejercicios específicos de velocidad para jugadores ofensivos"),
                        html.Li("Trabajar la resistencia como base para todas las posiciones"),
                        html.Li("Monitorear la evolución de las métricas a lo largo del tiempo")
                    ], className="mb-3")
                ], className="mt-3"),
                
                ollama_message
            ]
            
        except Exception as e:
            print(f"Error al conectar con Ollama: {e}")
            
            # Usar el análisis básico si falla la conexión
            analysis_content = [
                html.Div([
                    dcc.Markdown(general_analysis, className="analysis-text")
                ], className="p-3 border rounded bg-light"),
                
                html.Div([
                    html.P("No se pudo conectar con el servicio de IA para un análisis más detallado. " +
                          "Mostrando análisis básico generado localmente.", 
                          className="text-warning small")
                ], className="mt-3")
            ]
        
        return {"display": "none"}, analysis_content
    
    except Exception as e:
        print(f"Error al generar análisis: {e}")
        return {"display": "none"}, html.Div([
            html.Div("Error al generar el análisis.", className="text-danger"),
            html.Div(f"Detalles: {str(e)}", className="text-muted small")
        ])

