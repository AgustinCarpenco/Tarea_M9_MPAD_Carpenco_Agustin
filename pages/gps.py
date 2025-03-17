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
                                placeholder="Seleccionar División"
                            )
                        ], md=3),
                        
                        # Filtro de equipos
                        dbc.Col([
                            html.Label("Equipo:"),
                            dcc.Dropdown(
                                id="team-filter-gps", 
                                placeholder="Seleccionar Equipo"
                            )
                        ], md=3),
                        
                        # Filtro de posiciones
                        dbc.Col([
                            html.Label("Posición:"),
                            dcc.Dropdown(
                                id="position-filter-gps", 
                                placeholder="Seleccionar Posición"
                            )
                        ], md=3),
                        
                        # Filtro de jugadores
                        dbc.Col([
                            html.Label("Jugador:"),
                            dcc.Dropdown(
                                id="player-filter-gps", 
                                placeholder="Seleccionar Jugador"
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
    ]),
    
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
    
    # Tabla de jugadores
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
        
        return None, empty_fig, empty_fig, empty_kpis, [], []
    
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
    
    # Devolver todos los outputs
    return filtered_df.to_json(date_format='iso', orient='split'), velocidad_fig, player_load_fig, kpi_cards, table_data, table_columns

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
    if not n_clicks or not json_data:
        raise PreventUpdate
    
    try:
        # Convertir JSON a DataFrame
        df = pd.read_json(json_data, orient='split')
        
        # Importar bibliotecas para PDF
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        # Crear buffer para PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Título
        elements.append(Paragraph("Informe de Análisis GPS", title_style))
        elements.append(Spacer(1, 12))
        
        # Fecha
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Generado el: {fecha}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Filtros aplicados
        elements.append(Paragraph("Filtros aplicados:", subtitle_style))
        filtros = [
            f"División: {division if division else 'Todas'}",
            f"Equipo: {team if team else 'Todos'}",
            f"Posición: {position if position else 'Todas'}",
            f"Jugador: {player if player else 'Todos'}"
        ]
        
        for filtro in filtros:
            elements.append(Paragraph(filtro, normal_style))
        
        elements.append(Spacer(1, 20))
        
        # Resumen estadístico
        elements.append(Paragraph("Resumen Estadístico:", subtitle_style))
        
        if not df.empty:
            # Calcular estadísticas
            n_jugadores = df['athlete_name'].nunique()
            max_vel_prom = df['max_vel'].mean()
            player_load_prom = df['total_player_load'].mean()
            distance_prom = df['total_distance'].mean()
            
            data = [
                ["Métrica", "Valor"],
                ["Jugadores", f"{n_jugadores}"],
                ["Velocidad Máxima Promedio", f"{max_vel_prom:.2f} km/h"],
                ["Player Load Promedio", f"{player_load_prom:.2f}"],
                ["Distancia Promedio", f"{distance_prom:.2f} m"]
            ]
            
            tabla = Table(data, colWidths=[250, 200])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(tabla)
            elements.append(Spacer(1, 20))
            
            # Top jugadores
            elements.append(Paragraph("Top 10 Jugadores por Velocidad Máxima:", subtitle_style))
            
            top_jugadores = df.sort_values('max_vel', ascending=False).head(10)
            top_data = [["Jugador", "Posición", "Vel. Máx (km/h)", "Distancia (m)"]]
            
            for _, row in top_jugadores.iterrows():
                top_data.append([
                    row['athlete_name'],
                    row['position_name'],
                    f"{row['max_vel']:.2f}",
                    f"{row['total_distance']:.2f}"
                ])
            
            top_tabla = Table(top_data, colWidths=[150, 120, 120, 120])
            top_tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(top_tabla)
        else:
            elements.append(Paragraph("No hay datos disponibles con los filtros seleccionados.", normal_style))
        
        # Construir el PDF
        doc.build(elements)
        
        # Obtener el contenido del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"informe_gps_{timestamp}.pdf"
        
        return dict(
            content=pdf,
            filename=filename,
            type="application/pdf"
        )
        
    except Exception as e:
        print(f"Error al generar PDF: {e}")
        # En caso de error, crear un PDF simple con mensaje de error
        buffer = io.BytesIO()
        buffer.write(f"Error al generar PDF: {str(e)}".encode())
        buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_gps_{timestamp}.txt"
        
        return dict(
            content=buffer.getvalue(),
            filename=filename,
            type="text/plain"
        )