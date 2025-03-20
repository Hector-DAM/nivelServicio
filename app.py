import dash
from dash import dcc, html
import dash.dependencies as dd
import pandas as pd
import plotly.express as px
from nivelServicio import cargar_datos

# Inicializar aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Reporte de Nivel de Servicio", style={'textAlign': 'center'}),
    
    dcc.Upload(
        id='upload-ventas',
        children=html.Button('Cargar Archivo de Ventas')
    ),
    dcc.Upload(
        id='upload-inventario',
        children=html.Button('Cargar Archivo de Inventario')
    ),
    
    html.Div(id='output-data-upload'),
    
    dcc.Graph(id="graf_tallas", style={'height': '70vh'})
])

@app.callback(
    dd.Output("graf_tallas", "figure"),
    [dd.Input("upload-ventas", "contents"),
     dd.Input("upload-inventario", "contents")]
)
def actualizar_graf_tallas(ventas_path, inventario_path):
    if not ventas_path or not inventario_path:
        return px.scatter(title="Cargue archivos para visualizar los datos")
    
    df = cargar_datos(ventas_path, inventario_path)
    
    # Validación de datos
    if df.empty:
        return px.scatter(title="No hay datos disponibles")
    
    # Crear tabla pivote
    pivot = df.pivot_table(index=["Estilo-Color"], columns="Size", values="NivelServicio", aggfunc="mean").reset_index()
    
    # Generar heatmap
    fig = px.imshow(
        pivot.set_index("Estilo-Color"),
        color_continuous_scale="Viridis",
        labels={"x": "Talla", "y": "Estilo-Color", "color": "Nivel de Servicio"},
        title="Nivel de Servicio"
    )
    fig.update_layout(xaxis_nticks=len(pivot.columns), yaxis_nticks=len(pivot.index))
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
