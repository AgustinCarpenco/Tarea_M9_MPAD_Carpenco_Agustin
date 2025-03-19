# utils/ollama_integration.py
import httpx
import json
import pandas as pd

class OllamaAnalysis:
    def __init__(self, model="deepseek-r1:8b", host="http://localhost:11434"):
        """Inicializa la integración con Ollama."""
        self.model = model
        self.host = host
        self.api_endpoint = f"{host}/api/generate"
    
    async def analyze_data(self, data, analysis_type="general"):
        """
        Solicita análisis de datos a Ollama.
        
        Args:
            data: DataFrame o datos a analizar
            analysis_type: Tipo de análisis (general, velocidad, distancia, etc.)
            
        Returns:
            El análisis generado por el modelo
        """
        if isinstance(data, pd.DataFrame):
            # Preparar un resumen del DataFrame para el prompt
            data_summary = self._prepare_data_summary(data)
        else:
            data_summary = str(data)
        
        # Crear el prompt según el tipo de análisis
        prompt = self._create_prompt(data_summary, analysis_type)
        
        try:
            # Hacer la llamada a la API de Ollama
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_endpoint,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No se pudo obtener un análisis.")
                else:
                    return f"Error al comunicarse con Ollama: {response.status_code}"
        
        except Exception as e:
            return f"Error en la comunicación con Ollama: {str(e)}"
    
    def _prepare_data_summary(self, df):
        """Prepara un resumen del DataFrame para usar en el prompt."""
        summary = {}
        
        # Información básica
        summary["shape"] = df.shape
        
        # Estadísticas básicas para columnas numéricas
        if not df.empty:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                summary["numeric_stats"] = {}
                for col in numeric_cols[:5]:  # Limitar a 5 columnas para no hacer el prompt muy largo
                    if col in df.columns:
                        col_stats = {
                            "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else "N/A",
                            "min": float(df[col].min()) if not pd.isna(df[col].min()) else "N/A",
                            "max": float(df[col].max()) if not pd.isna(df[col].max()) else "N/A"
                        }
                        summary["numeric_stats"][col] = col_stats
            
            # Información categórica
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if cat_cols:
                summary["categorical_info"] = {}
                for col in cat_cols[:3]:  # Limitar a 3 columnas
                    if col in df.columns:
                        val_counts = df[col].value_counts().head(3).to_dict()
                        summary["categorical_info"][col] = val_counts
        
        return json.dumps(summary, default=str)
    
    def _create_prompt(self, data_summary, analysis_type):
        """Crea el prompt específico para el tipo de análisis."""
        base_prompt = f"""Eres un analista deportivo experto en datos GPS de jugadores. 
Analiza los siguientes datos y proporciona observaciones relevantes.

DATOS:
{data_summary}

"""
        
        if analysis_type == "general":
            prompt = base_prompt + """
Proporciona un análisis general de estos datos GPS, incluyendo:
1. Principales observaciones sobre velocidad y distancia
2. Tendencias o patrones destacables
3. Recomendaciones basadas en los datos

Tu análisis debe ser conciso, profesional y orientado a entrenadores deportivos.
"""
        elif analysis_type == "velocidad":
            prompt = base_prompt + """
Enfócate específicamente en el análisis de velocidad:
1. Rangos de velocidad máxima y su importancia
2. Comparación entre diferentes posiciones (si es posible)
3. Recomendaciones para mejorar el rendimiento de velocidad

Tu análisis debe ser conciso, profesional y orientado a entrenadores deportivos.
"""
        elif analysis_type == "distancia":
            prompt = base_prompt + """
Enfócate específicamente en el análisis de distancia recorrida:
1. Patrones de distancia por posición o jugador
2. Implicaciones para la condición física y táctica
3. Recomendaciones para optimizar la carga de trabajo

Tu análisis debe ser conciso, profesional y orientado a entrenadores deportivos.
"""
        else:
            prompt = base_prompt + """
Proporciona un análisis breve y profesional de estos datos para entrenadores deportivos.
"""
            
        return prompt