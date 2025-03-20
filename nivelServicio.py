import pandas as pd
import numpy as np

def procesar_datos(ventas_df, inventario_df, catalogo_df, tiendas_df):
    """
    Procesa los datos de ventas e inventario para generar reportes de ventas, inventario y nivel de servicio.
    :param ventas_df: DataFrame con los datos de ventas.
    :param inventario_df: DataFrame con los datos de inventario.
    :param catalogo_df: DataFrame con el catálogo de SKUs.
    :param tiendas_df: DataFrame con la información de tiendas.
    :return: DataFrame con el reporte final.
    """
    # Convertir fechas en ventas
    ventas_df["ORD DATE"] = pd.to_datetime(ventas_df["ORD DATE"].astype(str), format="%Y%m%d", errors="coerce")
    ventas_df["Mes"] = ventas_df["ORD DATE"].dt.to_period("M").astype(str)
    
    # Unir ventas con el catálogo para obtener estilo, color y talla
    ventas_df = ventas_df.merge(catalogo_df, on="SKU", how="left")
    inventario_df = inventario_df.merge(catalogo_df, on="SKU", how="left")
    
    # Unir con tiendas para obtener el nombre de la tienda
    ventas_df = ventas_df.merge(tiendas_df, on="STORE", how="left")
    inventario_df = inventario_df.merge(tiendas_df, on="STORE", how="left")
    
    # Crear columna Estilo-Color
    ventas_df["Estilo-Color"] = ventas_df["STYLE"].fillna("Desconocido") + " - " + ventas_df["Color Name"].fillna("Desconocido")
    inventario_df["Estilo-Color"] = inventario_df["STYLE"].fillna("Desconocido") + " - " + inventario_df["Color Name"].fillna("Desconocido")
    
    # Manejo de valores nulos en inventario
    inventario_df["AVAILABLE"].fillna(0, inplace=True)
    
    # Calcular métricas
    ventas_agrupadas = ventas_df.groupby(["Estilo-Color", "Size", "Mes"]).agg({"M3 QTY": "sum"}).reset_index()
    inventario_agrupado = inventario_df.groupby(["Estilo-Color", "Size"]).agg({"AVAILABLE": "sum"}).reset_index()
    
    # Unir ventas e inventario
    reporte = ventas_agrupadas.merge(inventario_agrupado, on=["Estilo-Color", "Size"], how="left")
    reporte["AVAILABLE"].fillna(0, inplace=True)
    
    # Calcular Sell-Through y Nivel de Servicio
    reporte["SellThrough"] = np.where(reporte["AVAILABLE"] > 0, reporte["M3 QTY"] / reporte["AVAILABLE"], np.nan)
    reporte["NivelServicio"] = np.where(
        (reporte["M3 QTY"] + reporte["AVAILABLE"]) != 0,
        reporte["M3 QTY"] / (reporte["M3 QTY"] + reporte["AVAILABLE"]),
        np.nan
    )
    
    return reporte
