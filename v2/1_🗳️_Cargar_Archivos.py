import streamlit as st
from scripts.clean_production_files import LiquidoCleaner

def render_page():
    catalogo = 'data/catalogo_productos.xlsx'
    clean_data = 'data/datos_produccion.parquet'

    liquido_cleaner = LiquidoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)

    files = st.file_uploader(label='sube el archivo de líquidos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

    if len(files) > 0:
        for file in files:
            try:
                liquido_cleaner.extract_and_save_data(file=file)
                st.success(f'{file.name} ha sido cargado de manera exitosa')
                # Ahora vemos si hubo datos inválidos
                st.dataframe(liquido_cleaner.bad_data)
            except Exception as e:
                st.error(f'Error en el archivo {file.name}: {e}')
    

if __name__ == '__main__':
    render_page()