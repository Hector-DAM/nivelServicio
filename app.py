# app.py
import streamlit as st
import pandas as pd
import os
from nivelServicio import procesar_nivel_servicio

# Configurar la interfaz
st.title("Análisis de Nivel de Servicio en Retail")

# Cargar archivos de ventas e inventario
ventas_file = st.file_uploader("Subir archivo de ventas (Excel)", type=["xlsx"])
inventario_file = st.file_uploader("Subir archivo de inventario (Excel)", type=["xlsx"])

# Ruta relativa del catálogo en GitHub
catalogo_path = "./tablaSKU.xlsx"
tiendas_path = "./TiendasM3.xlsx"

# Verificar si se cargaron los archivos
if ventas_file and inventario_file:
    ventas_df = pd.read_excel(ventas_file)
    inventario_df = pd.read_excel(inventario_file)
    
    # Cargar catálogos desde rutas relativas
    if os.path.exists(catalogo_path) and os.path.exists(tiendas_path):
        catalogo_df = pd.read_excel(catalogo_path)
        tiendas_df = pd.read_excel(tiendas_path)
        
        # Procesar los datos
        resultado = procesar_nivel_servicio(ventas_df, inventario_df, catalogo_df, tiendas_df)
        
        # Mostrar resultados
        st.write("### Reporte de Nivel de Servicio")
        st.dataframe(resultado)
    else:
        st.error("No se encontraron los archivos de catálogo o tiendas en la ruta especificada.")
