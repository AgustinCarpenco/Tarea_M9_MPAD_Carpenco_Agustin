# Dashboard Deportivo con Dash y Plotly

## Descripción

Una aplicación web interactiva desarrollada con Dash y Plotly para visualizar y analizar datos de rendimiento deportivo. Esta herramienta permite a entrenadores, analistas y staff técnico acceder a métricas de rendimiento de los atletas a través de una interfaz intuitiva, interactiva y segura.

El proyecto forma parte de la evaluación del Módulo 9: "Dash con Plotly, para crear aplicaciones de centralización de datos deportivos" del Máster en Python Avanzado Aplicado al Deporte.

## Características Principales

- **Sistema de autenticación**: Login seguro con Flask-Login (usuario: admin, contraseña: admin)
- **Navegación intuitiva**: Sistema de páginas con menú de navegación consistente
- **Dashboard de Performance**:
  - Gráficos interactivos de evolución temporal
  - Comparativas por posición
  - Perfil de rendimiento en formato radar
  - Mapa de calor de correlaciones
  - Exportación a PDF personalizado
- **Dashboard de GPS**:
  - Visualización de velocidad máxima por posición
  - Análisis de Player Load
  - Tablas interactivas con datos detallados
  - Integración con sistema de análisis IA
- **Diseño responsive**: Interfaz adaptable a diferentes dispositivos

## Tecnologías utilizadas

- Python 3.13
- Dash & Plotly
- Flask & Flask-Login
- Dash Bootstrap Components
- Pandas & NumPy
- ReportLab (para exportación a PDF)
- Integración con Ollama (para análisis IA)

## Estructura del proyecto

```
proyecto/
├── app.py                # Aplicación principal
├── assets/               # Archivos estáticos (CSS, imágenes)
│   └── logo.png
├── data/                 # Datos de ejemplo
│   ├── performance_stats.csv
│   └── gps_full.csv
├── pages/                # Páginas del dashboard
│   ├── home.py
│   ├── performance.py
│   └── gps.py
├── utils/                # Funciones auxiliares
│   └── ollama_integration.py
├── requirements.txt      # Dependencias
└── README.md             # Este archivo
```

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
```

2. Activar el entorno virtual:
   - En Windows:
   ```bash
   venv\Scripts\activate
   ```
   - En macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
python app.py
```

5. Abrir en el navegador: http://localhost:8060

## Credenciales de acceso

- **Usuario**: admin
- **Contraseña**: admin

## Funcionalidades implementadas

### Sistema de Autenticación (20 puntos)
- Login con usuario y contraseña
- Gestión de sesiones con Flask-Login
- Botón de logout en la barra de navegación
- Protección de rutas

### Navegación y Layout (20 puntos)
- Menú de navegación responsivo
- Tres páginas principales: Home, Performance y GPS
- Diseño con Dash Bootstrap Components
- CSS personalizado para mejorar la estética

### Dashboards y Visualizaciones (25 puntos)
- Dashboard de Performance:
  - Gráficos de evolución temporal y comparativa por posición
  - Perfil de jugador en formato radar
  - Mapa de calor de correlaciones
  - Exportación a PDF con template personalizado
- Dashboard de GPS:
  - Gráficos de velocidad máxima por posición
  - Visualización de Player Load
  - Tabla de datos detallados

### Interactividad y Datos (25 puntos)
- Callbacks para actualización de gráficos
- Filtros dependientes e interconectados
- Manejo de errores y estados de carga
- Generación de datos de ejemplo

### Publicación y Documentación (10 puntos)
- Estructura de proyecto organizada
- Archivo requirements.txt
- README.md con instrucciones
- Código comentado

## Funcionalidades adicionales

- **Integración con IA**: Análisis automático de datos mediante Ollama
- **Exportación a PDF**: Informes detallados personalizados 
- **Sistema de KPIs**: Visualización rápida de métricas clave
- **Componentes reutilizables**: Estructura modular para facilitar extensiones

## Autor

Agustín Carpenco - Máster en Python Avanzado Aplicado al Deporte