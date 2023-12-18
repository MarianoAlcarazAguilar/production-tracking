import streamlit as st
from scripts.clean_production_files import LiquidoCleaner, PolvoCleaner, LermaCleaner
from scripts.my_scripts.excel_functions import ExcelFunctions
import pandas as pd

def download_button(data, file_name):
    if data is not None:
        st.download_button(
            label='📥 Descargar Datos',
            data=data,
            file_name=file_name
        )

def open_styles(location='data/style.css'):
    
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Dragón',
        page_icon='🐉'
    )

    with open(location) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def update_polvos(polvo_cleaner:PolvoCleaner):
    col_uploading, col_errors = st.columns(2, gap="large")
    
    with col_uploading:
        files = st.file_uploader(label='sube el archivo de líquidos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
            bad_data = pd.DataFrame()
            for file in files:
                try:
                    polvo_cleaner.extract_and_save_data(file=file)
                    st.success(f'{file.name} ha sido cargado de manera exitosa')
                    # Ahora vemos si hubo datos inválidos
                    aux_bad_data = polvo_cleaner.bad_data.assign(file=file.name)
                    bad_data = pd.concat((bad_data, aux_bad_data), ignore_index=True).drop_duplicates()
                except Exception as e:
                    st.error(f'Error en el archivo {file.name}: {e}')

    with col_errors:
        if bad_data is not None and bad_data.size > 0:
            st.dataframe(bad_data, hide_index=True, use_container_width=True)
            data, filename = ExcelFunctions().save_and_download_excel_file(bad_data, 'data/', 'errores_al_cargar', 'errores')
            download_button(data, filename)



def update_liquidos(liquido_cleaner:LiquidoCleaner):
    col_uploading, col_errors = st.columns(2, gap="large")
    
    with col_uploading:
        files = st.file_uploader(label='sube el archivo de líquidos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
            bad_data = pd.DataFrame()
            for file in files:
                try:
                    liquido_cleaner.extract_and_save_data(file=file)
                    st.success(f'{file.name} ha sido cargado de manera exitosa')
                    # Ahora vemos si hubo datos inválidos
                    aux_bad_data = liquido_cleaner.bad_data.assign(file=file.name)
                    bad_data = pd.concat((bad_data, aux_bad_data), ignore_index=True).drop_duplicates()
                except Exception as e:
                    st.error(f'Error en el archivo {file.name}: {e}')

    with col_errors:
        if bad_data is not None and bad_data.size > 0:
            st.dataframe(bad_data, hide_index=True, use_container_width=True)
            data, filename = ExcelFunctions().save_and_download_excel_file(bad_data, 'data/', 'errores_al_cargar', 'errores')
            download_button(data, filename)

        


def update_lerma(lerma_cleaner:LiquidoCleaner):
    col_uploading, col_errors = st.columns(2, gap="large")
    
    with col_uploading:
        files = st.file_uploader(label='sube el archivo de líquidos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
            bad_data = pd.DataFrame()
            for file in files:
                try:
                    lerma_cleaner.extract_and_save_data(file=file)
                    st.success(f'{file.name} ha sido cargado de manera exitosa')
                    # Ahora vemos si hubo datos inválidos
                    aux_bad_data = lerma_cleaner.bad_data.assign(file=file.name)
                    bad_data = pd.concat((bad_data, aux_bad_data), ignore_index=True).drop_duplicates()
                except Exception as e:
                    st.error(f'Error en el archivo {file.name}: {e}')

    with col_errors:
        if bad_data is not None and bad_data.size > 0:
            st.dataframe(bad_data, hide_index=True, use_container_width=True)
            data, filename = ExcelFunctions().save_and_download_excel_file(bad_data, 'data/', 'errores_al_cargar', 'errores')
            download_button(data, filename)


def render_page():
    open_styles()
    catalogo = 'data/catalogo_productos.xlsx'
    clean_data = 'data/datos_produccion.parquet'

    liquido_cleaner = LiquidoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)
    polvo_cleaner = PolvoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)
    lerma_cleaner = LermaCleaner(catalogo_file=catalogo, clean_data_file=clean_data)

    st.sidebar.write('''
        <p class="paragraph">
            En esta página puedes cargar los archivos operacionales de planeación de producción para que se actualicen de forma automática
        </p>''',
    unsafe_allow_html=True)

    type_of_file = st.sidebar.radio('Elige el tipo de archivo a subir', ['Polvos', 'Líquidos', 'Lerma'])

    if type_of_file == 'Polvos':
        update_polvos(polvo_cleaner=polvo_cleaner)

    elif type_of_file == 'Líquidos':
        update_liquidos(liquido_cleaner=liquido_cleaner)

    elif type_of_file == "Lerma":
        update_lerma(lerma_cleaner=lerma_cleaner)

if __name__ == '__main__':
    render_page()