import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import dcc, html
import dash.dependencies as dd

# Cargar catálogos previamente cargados
catalogo_path = "./tablaSKU.xlsx"
tiendas_path = "./TiendasM3.xlsx"
catalogo = pd.read_excel(catalogo_path)
tiendas = pd.read_excel(tiendas_path)

def procesar_datos(ventas_df, inventario_df):
    # Convertir fecha y extraer mes
    ventas_df["ORD DATE"] = pd.to_datetime(ventas_df["ORD DATE"], format="%Y%m%d", errors="coerce")
    ventas_df["Mes"] = ventas_df["ORD DATE"].dt.to_period("M").astype(str)
    
    # Cruce con catálogo
    ventas_catalogo = ventas_df.merge(catalogo, on="SKU", how="left")
    inventario_catalogo = inventario_df.merge(catalogo, on="SKU", how="left")
    
    # Cruce con inventario
    datos_finales = ventas_catalogo.merge(
        inventario_catalogo[["STORE", "SKU", "AVAILABLE"]].drop_duplicates(),
        on=["STORE", "SKU"],
        how="left"
    )
    
    # Merge con el listado de tiendas para obtener el nombre de la tienda
    datos_finales = datos_finales.merge(
        tiendas[["Tienda", "STORE"]], 
        on="STORE", 
        how="left"
    )
    
    # Crear columna combinada Estilo-Color
    datos_finales["Estilo-Color"] = datos_finales["STYLE"].astype(str) + " - " + datos_finales["Color Name"].astype(str)
    
    # Manejo de divisiones por cero
    datos_finales["AVAILABLE"] = datos_finales["AVAILABLE"].replace(0, np.nan)
    
    # Cálculo seguro de indicadores
    datos_finales["SellThrough"] = np.where(
        datos_finales["AVAILABLE"].notna(),
        datos_finales["M3 QTY"] / datos_finales["AVAILABLE"],
        np.nan
    )
    
    datos_finales["NivelServicio"] = np.where(
        (datos_finales["M3 QTY"] + datos_finales["AVAILABLE"]) != 0,
        datos_finales["M3 QTY"] / (datos_finales["M3 QTY"] + datos_finales["AVAILABLE"]),
        np.nan
    )
    
    return datos_finales

# Crear aplicación Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Cargar Archivos para Análisis"),
    dcc.Upload(id='upload-ventas', children=html.Button('Cargar Ventas')),
    dcc.Upload(id='upload-inventario', children=html.Button('Cargar Inventario')),
    dcc.Graph(id="graf_ventas", style={'height': '70vh'}),
    dcc.Graph(id="graf_inventario", style={'height': '70vh'}),
    dcc.Graph(id="graf_nivel_servicio", style={'height': '70vh'})
], style={'padding': '20px'})

@app.callback(
    [dd.Output("graf_ventas", "figure"),
     dd.Output("graf_inventario", "figure"),
     dd.Output("graf_nivel_servicio", "figure")],
    [dd.Input("upload-ventas", "contents"),
     dd.Input("upload-inventario", "contents")]
)
def actualizar_graficos(ventas_content, inventario_content):
    if not ventas_content or not inventario_content:
        return (px.scatter(title="Esperando archivos..."),
                px.scatter(title="Esperando archivos..."),
                px.scatter(title="Esperando archivos..."))
    
    ventas_df = pd.read_excel(ventas_content)
    inventario_df = pd.read_excel(inventario_content)
    df = procesar_datos(ventas_df, inventario_df)
    
    pivot_ventas = df.pivot_table(index=["Estilo-Color"], columns="Size", values="M3 QTY", aggfunc="sum").reset_index()
    pivot_inventario = df.pivot_table(index=["Estilo-Color"], columns="Size", values="AVAILABLE", aggfunc="sum").reset_index()
    pivot_nivel_servicio = df.pivot_table(index=["Estilo-Color"], columns="Size", values="NivelServicio", aggfunc="mean").reset_index()
    
    fig_ventas = px.imshow(pivot_ventas.set_index("Estilo-Color"), color_continuous_scale="Blues", title="Ventas")
    fig_inventario = px.imshow(pivot_inventario.set_index("Estilo-Color"), color_continuous_scale="Oranges", title="Inventario")
    fig_nivel_servicio = px.imshow(pivot_nivel_servicio.set_index("Estilo-Color"), color_continuous_scale="Viridis", title="Nivel de Servicio")
    
    return fig_ventas, fig_inventario, fig_nivel_servicio

