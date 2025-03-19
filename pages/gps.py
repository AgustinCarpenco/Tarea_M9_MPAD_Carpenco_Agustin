import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
from dash.exceptions import PreventUpdate
import os
from datetime import datetime
import io
from utils.ollama_integration import OllamaAnalysis
from dash.dependencies import Input, Output, State, ALL, MATCH
import asyncio

# Registrar esta página
dash.register_page(
    __name__,
    path='/gps',
    title='Dashboard de GPS',
    name='GPS'
)

def cargar_datos_gps():
    """Carga y preprocesa los datos de GPS"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    
    try:
        # Cargar CSV
        df = pd.read_csv(os.path.join(data_dir, 'gps_full.csv'))
        
        # Convertir columnas de fecha
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error al cargar los datos GPS: {e}")
        return pd.DataFrame()

def filtrar_dataframe_gps(df, division=None, team=None, position=None, player=None):
    """Filtra el DataFrame según los criterios seleccionados"""
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    if position and position != "Todas":
        filtered_df = filtered_df[filtered_df['position_name'] == position]
    
    if player and player != "Todos":
        filtered_df = filtered_df[filtered_df['athlete_name'] == player]
    
    return filtered_df

def generar_grafico_velocidad_posicion(df):
    """Genera un gráfico de velocidad máxima por posición"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    # Agrupar por posición
    pos_data = df.groupby('position_name').agg({
        'max_vel': 'mean'
    }).reset_index()
    
    # Crear gráfico de barras
    fig = px.bar(
        pos_data,
        x='position_name',
        y='max_vel',
        title='Velocidad Máxima Promedio por Posición',
        labels={'position_name': 'Posición', 'max_vel': 'Velocidad Máxima (km/h)'},
        color='max_vel',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    
    fig.update_layout(height=500)
    return fig

def generar_grafico_player_load(df):
    """Genera un gráfico de player load por posición"""
    if df.empty:
        # Devolver un gráfico vacío
        fig = go.Figure()
        fig.update_layout(
            title="No hay datos disponibles",
            xaxis_title="",
            yaxis_title=""
        )
        return fig
    
    # Agrupar por posición
    pos_data = df.groupby('position_name').agg({
        'total_player_load': 'mean'
    }).reset_index()
    
    # Crear gráfico de barras
    fig = px.bar(
        pos_data,
        x='position_name',
        y='total_player_load',
        title='Player Load Promedio por Posición',
        labels={'position_name': 'Posición', 'total_player_load': 'Player Load'},
        color='total_player_load',
        color_continuous_scale=px.colors.sequential.Bluered
    )
    
    fig.update_layout(height=500)
    return fig

# Layout principal del dashboard
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Dashboard de GPS", className="mb-4 text-success")
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
                            # Filtro de divisiones
                            dbc.Col([
                                html.Label("División:"),
                                dcc.Dropdown(
                                    id="division-filter-gps", 
                                    placeholder="Seleccionar División",
                                    className="dropdown-filter"
                                )
                            ], md=3),
                            
                            # Filtro de equipos
                            dbc.Col([
                                html.Label("Equipo:"),
                                dcc.Dropdown(
                                    id="team-filter-gps", 
                                    placeholder="Seleccionar Equipo",
                                    className="dropdown-filter"
                                )
                            ], md=3),
                            
                            # Filtro de posiciones
                            dbc.Col([
                                html.Label("Posición:"),
                                dcc.Dropdown(
                                    id="position-filter-gps", 
                                    placeholder="Seleccionar Posición",
                                    className="dropdown-filter"
                                )
                            ], md=3),
                            
                            # Filtro de jugadores
                            dbc.Col([
                                html.Label("Jugador:"),
                                dcc.Dropdown(
                                    id="player-filter-gps", 
                                    placeholder="Seleccionar Jugador",
                                    className="dropdown-filter"
                                )
                            ], md=3)
                        ]),
                        dbc.Row([
                            # Botón para exportar a PDF
                            dbc.Col([
                                dbc.Button(
                                    [html.I(className="fas fa-file-pdf me-2"), "Exportar a PDF"],
                                    id="export-pdf-gps-btn",
                                    color="danger",
                                    className="w-100 mt-3"
                                ),
                                dcc.Download(id="download-pdf-gps")
                            ], width={"size": 3, "offset": 9})
                        ], className="mt-3")
                    ])
                ], className="mb-4")
            ])
        ])
    ], style={"position": "relative", "zIndex": "1000"}),
    
    # Almacenamiento de datos filtrados
    dcc.Store(id='filtered-data-gps'),
    
    # KPIs
    dbc.Row(id="kpi-cards-row-gps", className="mb-4"),
    
    # Gráficos principales
    dbc.Row([
        # Gráfico de velocidad por posición
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Velocidad Máxima por Posición"),
                dbc.CardBody([
                    dcc.Graph(id="velocidad-plot")
                ])
            ])
        ], md=6, className="mb-4"),
        
        # Gráfico de player load
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Player Load por Posición"),
                dbc.CardBody([
                    dcc.Graph(id="player-load-plot")
                ])
            ])
        ], md=6, className="mb-4")
    ]),
    
    # Tabla de jugadores - AÑADIR ESTE BLOQUE QUE FALTABA
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Datos de Jugadores"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='jugadores-table',
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px'
                        },
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
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
                        id="generate-analysis-btn",
                        color="info",
                        className="float-end"
                    )
                ]),
                dbc.CardBody([
                    html.Div([
                        html.Div(id="analysis-loading", className="text-center", children=[
                            dbc.Spinner(size="sm", color="primary", type="grow"),
                            " Generando análisis... Por favor espere."
                        ], style={"display": "none"})
                    ]),
                    html.Div(id="analysis-content", className="mt-3")
                ])
            ])
        ], md=12, className="mb-4")
    ]),
    
    # Componente oculto para inicialización
    html.Div(id="_gps", style={"display": "none"})
], fluid=True)

# Cargar opciones de filtros iniciales
@callback(
    [Output("division-filter-gps", "options"),
     Output("division-filter-gps", "value")],
    [Input("_gps", "children")]
)
def inicializar_filtros_gps(_):
    df = cargar_datos_gps()
    
    if df.empty:
        return [], None
    
    # Opciones para divisiones
    divisiones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": div, "value": div} for div in sorted(df['division'].unique()) if pd.notna(div)
    ]
    
    return divisiones, "Todas"

# Actualizar opciones de equipos
@callback(
    Output("team-filter-gps", "options"),
    Output("team-filter-gps", "value"),
    [Input("division-filter-gps", "value")],
    prevent_initial_call=True
)
def actualizar_equipos_gps(division):
    df = cargar_datos_gps()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    equipos = [{"label": "Todos", "value": "Todos"}] + [
        {"label": team, "value": team} for team in sorted(filtered_df['team_name'].unique()) if pd.notna(team)
    ]
    
    return equipos, "Todos"

# Actualizar opciones de posiciones
@callback(
    Output("position-filter-gps", "options"),
    Output("position-filter-gps", "value"),
    [Input("division-filter-gps", "value"),
     Input("team-filter-gps", "value")],
    prevent_initial_call=True
)
def actualizar_posiciones_gps(division, team):
    df = cargar_datos_gps()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    posiciones = [{"label": "Todas", "value": "Todas"}] + [
        {"label": pos, "value": pos} for pos in sorted(filtered_df['position_name'].unique()) if pd.notna(pos)
    ]
    
    return posiciones, "Todas"

# Actualizar opciones de jugadores
@callback(
    Output("player-filter-gps", "options"),
    Output("player-filter-gps", "value"),
    [Input("division-filter-gps", "value"),
     Input("team-filter-gps", "value"),
     Input("position-filter-gps", "value")],
    prevent_initial_call=True
)
def actualizar_jugadores_gps(division, team, position):
    df = cargar_datos_gps()
    
    if df.empty:
        return [], None
    
    filtered_df = df.copy()
    if division and division != "Todas":
        filtered_df = filtered_df[filtered_df['division'] == division]
    
    if team and team != "Todos":
        filtered_df = filtered_df[filtered_df['team_name'] == team]
    
    if position and position != "Todas":
        filtered_df = filtered_df[filtered_df['position_name'] == position]
    
    jugadores = [{"label": "Todos", "value": "Todos"}] + [
        {"label": player, "value": player} for player in sorted(filtered_df['athlete_name'].unique()) if pd.notna(player)
    ]
    
    return jugadores, "Todos"

# Actualizar datos filtrados y componentes
@callback(
    [Output("filtered-data-gps", "data"),
     Output("velocidad-plot", "figure"),
     Output("player-load-plot", "figure"),
     Output("kpi-cards-row-gps", "children"),
     Output("jugadores-table", "data"),
     Output("jugadores-table", "columns")],
    [Input("division-filter-gps", "value"),
     Input("team-filter-gps", "value"),
     Input("position-filter-gps", "value"),
     Input("player-filter-gps", "value")]
)
def actualizar_datos_gps(division, team, position, player):
    # Cargar y filtrar datos
    df = cargar_datos_gps()
    
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
        
        # Importante: Asegurarse de que todos los outputs son del tipo correcto
        return "", empty_fig, empty_fig, empty_kpis, [], []  # Cadena vacía en lugar de None para data
    
    # Filtrar datos
    filtered_df = filtrar_dataframe_gps(df, division, team, position, player)
    
    # Generar gráficos
    velocidad_fig = generar_grafico_velocidad_posicion(filtered_df)
    player_load_fig = generar_grafico_player_load(filtered_df)
    
    # Calcular KPIs
    try:
        n_jugadores = filtered_df['athlete_name'].nunique()
        max_vel_prom = filtered_df['max_vel'].mean()
        player_load_prom = filtered_df['total_player_load'].mean()
        distance_prom = filtered_df['total_distance'].mean()
    except Exception as e:
        print(f"Error al calcular KPIs: {e}")
        n_jugadores = 0
        max_vel_prom = 0
        player_load_prom = 0
        distance_prom = 0
    
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
                    html.H6("Vel. Máx. Promedio", className="card-subtitle"),
                    html.H3(f"{max_vel_prom:.1f} km/h", className="card-title text-success")
                ])
            ], className="text-center")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Player Load Promedio", className="card-subtitle"),
                    html.H3(f"{player_load_prom:.1f}", className="card-title text-danger")
                ])
            ], className="text-center")
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Distancia Promedio", className="card-subtitle"),
                    html.H3(f"{distance_prom:.0f} m", className="card-title text-info")
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
        cols = ['athlete_name', 'position_name', 'team_name', 'max_vel', 'total_distance', 'total_player_load']
        table_df = filtered_df[cols].copy()
        
        # Renombrar columnas para mejor visualización
        table_df.columns = ['Jugador', 'Posición', 'Equipo', 'Vel. Máx. (km/h)', 'Distancia (m)', 'Player Load']
        
        # Formatear valores numéricos
        for col in ['Vel. Máx. (km/h)', 'Distancia (m)', 'Player Load']:
            if col in table_df.columns:
                table_df[col] = table_df[col].round(1)
        
        # Convertir a formato para DataTable
        table_data = table_df.to_dict('records')
        table_columns = [{"name": col, "id": col} for col in table_df.columns]
    
    # Devolver todos los outputs asegurando que ninguno es None o un objeto no serializable
    return filtered_df.to_json(date_format='iso', orient='split'), velocidad_fig, player_load_fig, kpi_cards, table_data if table_data else [], table_columns if table_columns else []

# Callback para exportar a PDF
@callback(
    Output("download-pdf-gps", "data"),
    [Input("export-pdf-gps-btn", "n_clicks")],
    [State("filtered-data-gps", "data"),
     State("division-filter-gps", "value"),
     State("team-filter-gps", "value"),
     State("position-filter-gps", "value"),
     State("player-filter-gps", "value")],
    prevent_initial_call=True
)
def exportar_pdf_gps(n_clicks, json_data, division, team, position, player):
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
        
        # Crear documento - usar A4 para mejor presentación
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Definir estilos mejorados
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
        
        # Estilo para pies de página e información adicional
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Italic'],
            fontSize=8,
            textColor=colors.darkgrey
        )
        
        # Logo o encabezado del informe (opcional)
        # Si tienes un logo, podrías incluirlo así:
        # logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'logo.png')
        # if os.path.exists(logo_path):
        #     img = Image(logo_path, width=1.5*inch, height=0.5*inch)
        #     elements.append(img)
        
        # Título con formato mejorado
        elements.append(Paragraph("Informe de Análisis GPS", title_style))
        
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
        df = pd.read_json(json_data, orient='split')
        
        # Sección de filtros aplicados
        elements.append(Paragraph("Filtros aplicados", subtitle_style))
        
        filtros_data = [
            ["Filtro", "Valor"],
            ["División", division if division != "Todas" else "Todas las divisiones"],
            ["Equipo", team if team != "Todos" else "Todos los equipos"],
            ["Posición", position if position != "Todas" else "Todas las posiciones"],
            ["Jugador", player if player != "Todos" else "Todos los jugadores"]
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
            n_jugadores = df['athlete_name'].nunique()
            max_vel_prom = df['max_vel'].mean()
            max_vel_max = df['max_vel'].max()
            player_load_prom = df['total_player_load'].mean()
            distance_prom = df['total_distance'].mean()
            
            # Crear tabla de estadísticas
            stats_data = [
                ["Métrica", "Valor"],
                ["Total Jugadores", f"{n_jugadores}"],
                ["Velocidad Máxima Promedio", f"{max_vel_prom:.2f} km/h"],
                ["Velocidad Máxima", f"{max_vel_max:.2f} km/h"],
                ["Player Load Promedio", f"{player_load_prom:.2f}"],
                ["Distancia Promedio", f"{distance_prom:.2f} m"]
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
            elements.append(Spacer(1, 20))
            
            # Top jugadores por velocidad
            elements.append(Paragraph("Top 5 Jugadores por Velocidad Máxima", subtitle_style))
            
            if len(df) > 0:
                top_velocidad = df.sort_values('max_vel', ascending=False).head(5)
                
                vel_data = [["Jugador", "Posición", "Equipo", "Vel. Máx. (km/h)"]]
                
                for _, row in top_velocidad.iterrows():
                    vel_data.append([
                        row['athlete_name'],
                        row['position_name'],
                        row['team_name'],
                        f"{row['max_vel']:.2f}"
                    ])
                
                vel_tabla = Table(vel_data, colWidths=[4*cm, 4*cm, 4*cm, 3*cm])
                vel_tabla.setStyle(TableStyle([
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
                    
                    # Resaltar filas alternadas
                    ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
                    ('BACKGROUND', (0, 3), (-1, 3), colors.lightgrey),
                    ('BACKGROUND', (0, 5), (-1, 5), colors.lightgrey),
                    
                    # Bordes exteriores más gruesos
                    ('BOX', (0, 0), (-1, -1), 1, colors.darkblue)
                ]))
                
                elements.append(vel_tabla)
                elements.append(Spacer(1, 30))
                
            # Conclusiones y notas (opcional)
            elements.append(Paragraph("Observaciones", subtitle_style))
            observaciones = [
                "• Los datos presentados en este informe corresponden a las métricas GPS recopiladas durante el período analizado.",
                "• Las velocidades máximas y distancias pueden variar según la posición y rol de cada jugador.",
                "• Se recomienda revisar estos datos en conjunto con los análisis técnicos y tácticos del equipo."
            ]
            
            for observacion in observaciones:
                elements.append(Paragraph(observacion, normal_style))
                
            # Pie de página
            elements.append(Spacer(1, 30))
            elements.append(Table([[""]], colWidths=[doc.width], style=TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
            ])))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("Dashboard Deportivo - Análisis GPS - Documento generado automáticamente", info_style))
            
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
        filename = f"informe_gps_{timestamp}.pdf"
        
        return dict(
            content=pdf_base64,
            filename=filename,
            type="application/pdf",
            base64=True
        )
        
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        # En caso de error, devolver un mensaje de texto
        return dict(
            content="Error al generar el PDF. Por favor, intente nuevamente.",
            filename="error.txt",
            type="text/plain"
        )

# Callback para generar el análisis con Ollama
@callback(
    [Output("analysis-loading", "style"),
     Output("analysis-content", "children")],
    [Input("generate-analysis-btn", "n_clicks")],
    [State("filtered-data-gps", "data")],
    prevent_initial_call=True
)
async def generate_analysis(n_clicks, json_data):
    """Genera un análisis de los datos utilizando Ollama."""
    if not n_clicks or not json_data:
        raise PreventUpdate
    
    # Mostrar indicador de carga
    loading_style = {"display": "block"}
    
    try:
        # Convertir JSON a DataFrame
        df = pd.read_json(json_data, orient='split')
        
        if df.empty:
            return {"display": "none"}, html.Div("No hay datos disponibles para analizar.", className="text-muted")
        
        # Crear instancia de OllamaAnalysis
        ollama = OllamaAnalysis(model="deepseek-r1:8b")
        
        # Obtener análisis general
        general_analysis = await ollama.analyze_data(df, analysis_type="general")
        
        # Formatear análisis como componentes de Dash
        analysis_content = [
            html.H6("Análisis General", className="text-info mt-3"),
            html.Div([
                dcc.Markdown(general_analysis, className="analysis-text")
            ], className="p-3 border rounded bg-light"),
            
            # Botones para análisis específicos
            html.Div([
                dbc.Button(
                    "Análisis de Velocidad",
                    id={"type": "specific-analysis-btn", "index": "velocidad"},
                    color="outline-primary",
                    size="sm",
                    className="me-2 mt-3"
                ),
                dbc.Button(
                    "Análisis de Distancia",
                    id={"type": "specific-analysis-btn", "index": "distancia"},
                    color="outline-primary",
                    size="sm",
                    className="me-2 mt-3"
                )
            ]),
            
            # Contenedor para análisis específicos
            html.Div(id="specific-analysis-container", className="mt-3")
        ]
        
        return {"display": "none"}, analysis_content
    
    except Exception as e:
        print(f"Error al generar análisis: {e}")
        return {"display": "none"}, html.Div([
            html.Div("Error al generar el análisis.", className="text-danger"),
            html.Div(f"Detalles: {str(e)}", className="text-muted small")
        ])

# Callback para análisis específicos
@callback(
    Output("specific-analysis-container", "children"),
    [Input({"type": "specific-analysis-btn", "index": ALL}, "n_clicks")],
    [State({"type": "specific-analysis-btn", "index": ALL}, "id"),
     State("filtered-data-gps", "data")],
    prevent_initial_call=True
)
async def generate_specific_analysis(n_clicks_list, btn_ids, json_data):
    """Genera análisis específicos basados en el botón clickeado."""
    ctx_triggered = ctx.triggered_id
    if not ctx_triggered or not any(n_clicks_list) or not json_data:
        raise PreventUpdate
    
    # Determinar qué botón fue clickeado
    triggered_index = ctx_triggered.get("index", "")
    
    try:
        # Convertir JSON a DataFrame
        df = pd.read_json(json_data, orient='split')
        
        if df.empty:
            return html.Div("No hay datos disponibles para analizar.", className="text-muted")
        
        # Crear instancia de OllamaAnalysis
        ollama = OllamaAnalysis(model="deepseek-r1:8b")
        
        # Generar análisis específico
        specific_analysis = await ollama.analyze_data(df, analysis_type=triggered_index)
        
        # Formatear el resultado
        return html.Div([
            html.H6(f"Análisis de {triggered_index.capitalize()}", className="text-info mt-3"),
            html.Div([
                dcc.Markdown(specific_analysis, className="analysis-text")
            ], className="p-3 border rounded bg-light")
        ])
    
    except Exception as e:
        print(f"Error al generar análisis específico: {e}")
        return html.Div([
            html.Div(f"Error al generar el análisis de {triggered_index}.", className="text-danger"),
            html.Div(f"Detalles: {str(e)}", className="text-muted small")
        ])
        
# Al final de app.py
if __name__ == '__main__':
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Intentar puertos 8060, 8061, 8062 o cualquier disponible
    port = 8060
    while is_port_in_use(port) and port < 8070:
        print(f"Puerto {port} ocupado, intentando {port + 1}")
        port += 1
    
    print(f"Iniciando aplicación en puerto {port}")
    app.run_server(debug=True, port=port)