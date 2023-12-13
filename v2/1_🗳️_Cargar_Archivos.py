import streamlit as st
from scripts.clean_production_files import LiquidoCleaner

def render_page():
    catalogo = 'data/catalogo_productos.xlsx'
    clean_data = 'data/datos_produccion.parquet'

    liquido_cleaner = LiquidoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)
    

if __name__ == '__main__':
    render_page()