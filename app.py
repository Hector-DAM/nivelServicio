from flask import Flask, request, render_template
import pandas as pd
import os
from nivelServicio import procesar_datos

app = Flask(__name__)

# Ruta relativa del catálogo en GitHub
catalogo_path = "./tablaSKU.xlsx"
tiendas_path = "./TiendasM3.xlsx"
catalogo = pd.read_excel(catalogo_path)
tiendas = pd.read_excel(tiendas_path)

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
    
    resultado = procesar_datos(ventas_df, inventario_df, catalogo, tiendas)
    
    return render_template('resultado.html', ventas=ventas_df.to_html(), inventario=inventario_df.to_html(), nivel_servicio=resultado.to_html())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
