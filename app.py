from flask import Flask, request, render_template
import pandas as pd
import os
from nivelServicio import procesar_nivel_servicio

app = Flask(__name__)

# Ruta relativa del catálogo en GitHub
catalogo_path = "./tablaSKU.xlsx"
tiendas_path = "./TiendasM3.xlsx"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'ventas' not in request.files or 'inventario' not in request.files:
        return "Error: Se deben subir ambos archivos (ventas e inventario)", 400
    
    ventas_file = request.files['ventas']
    inventario_file = request.files['inventario']
    
    ventas_df = pd.read_excel(ventas_file)
    inventario_df = pd.read_excel(inventario_file)
    
    if os.path.exists(catalogo_path) and os.path.exists(tiendas_path):
        catalogo_df = pd.read_excel(catalogo_path)
        tiendas_df = pd.read_excel(tiendas_path)
        
        resultado = procesar_nivel_servicio(ventas_df, inventario_df, catalogo_df, tiendas_df)
        
        return resultado.to_html()
    else:
        return "Error: No se encontraron los archivos de catálogo o tiendas en la ruta especificada.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
