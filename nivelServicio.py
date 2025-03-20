import pandas as pd

def procesar_nivel_servicio(ventas_df, inventario_df, catalogo_df, tiendas_df):
    """
    Procesa los datos de ventas e inventario para generar un reporte de nivel de servicio.
    :param ventas_df: DataFrame con los datos de ventas.
    :param inventario_df: DataFrame con los datos de inventario.
    :param catalogo_df: DataFrame con el catálogo de SKUs.
    :param tiendas_df: DataFrame con la información de tiendas.
    :return: DataFrame con el reporte de nivel de servicio.
    """
    # Convertir fechas en ventas
    ventas_df["ORD DATE"] = pd.to_datetime(ventas_df["ORD DATE"].astype(str), format="%Y%m%d")
    ventas_df["MES"] = ventas_df["ORD DATE"].dt.to_period("M")
    
    # Intentar unir ventas con el catálogo para obtener estilo, color y talla
    try:
        ventas_df = ventas_df.merge(catalogo_df, on="SKU", how="left")
    except KeyError:
        ventas_df["STYLE"] = "N/A"
        ventas_df["Color Name"] = "N/A"
        ventas_df["Size"] = "N/A"
    
    # Intentar unir inventario con el catálogo para agregar tallas
    try:
        inventario_df = inventario_df.merge(catalogo_df, on="SKU", how="left")
    except KeyError:
        inventario_df["STYLE_y"] = "N/A"
        inventario_df["Color Name"] = "N/A"
        inventario_df["Size"] = "N/A"
    
    # Reemplazar NaN en STYLE y Color Name antes de concatenar
    ventas_df["STYLE"].fillna("Desconocido", inplace=True)
    ventas_df["Color Name"].fillna("Desconocido", inplace=True)
    
    inventario_df["STYLE_y"].fillna("Desconocido", inplace=True)
    inventario_df["Color Name"].fillna("Desconocido", inplace=True)
    
    # Crear columna Estilo-Color
    ventas_df["Estilo-Color"] = ventas_df["STYLE"] + " - " + ventas_df["Color Name"]
    inventario_df["Estilo-Color"] = inventario_df["STYLE_y"] + " - " + inventario_df["Color Name"]
    
    # Agrupar ventas por Estilo-Color y talla
    ventas_agrupadas = ventas_df.groupby(["Estilo-Color", "Size", "MES"]).agg({"M3 QTY": "sum"}).reset_index()
    
    # Agrupar inventario por Estilo-Color y talla
    inventario_agrupado = inventario_df.groupby(["Estilo-Color", "Size"]).agg({"AVAILABLE": "sum"}).reset_index()
    
    # Unir ventas e inventario
    reporte = ventas_agrupadas.merge(inventario_agrupado, on=["Estilo-Color", "Size"], how="left")
    reporte["AVAILABLE"].fillna(0, inplace=True)
    
    # Calcular Sell-Through
    reporte["Sell-Through"] = reporte["M3 QTY"] / (reporte["M3 QTY"] + reporte["AVAILABLE"])
    
    return reporte
