import pandas as pd
import numpy as np
import os

# Definir rutas relativas para catálogos
RUTA_CATALOGO = os.path.join("data", "tablaSKU.xlsx")
RUTA_TIENDAS = os.path.join("data", "listado_tiendas.xlsx")

def cargar_datos(ventas_path, inventario_path):
    # Cargar datos de ventas e inventario
    ventas = pd.read_excel(ventas_path)
    inventario = pd.read_excel(inventario_path)
    catalogo = pd.read_excel(RUTA_CATALOGO)
    tiendas = pd.read_excel(RUTA_TIENDAS)
    
    # Convertir fecha y extraer mes
    ventas["ORD DATE"] = pd.to_datetime(ventas["ORD DATE"], format="%Y%m%d", errors="coerce")
    ventas["Mes"] = ventas["ORD DATE"].dt.to_period("M").astype(str)
    
    # Cruce con catálogo y tiendas
    ventas = ventas.merge(catalogo, on="SKU", how="left")
    inventario = inventario.merge(catalogo, on="SKU", how="left")
    ventas = ventas.merge(tiendas[["STORE", "Tienda"]], on="STORE", how="left")
    
    # Cruce con inventario
    datos_finales = ventas.merge(
        inventario[["STORE", "SKU", "AVAILABLE"],].drop_duplicates(),
        on=["STORE", "SKU"],
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
