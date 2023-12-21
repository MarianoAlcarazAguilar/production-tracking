import os
import shutil
import datetime
import streamlit as st
from scripts.clean_production_files import LiquidoCleaner, PolvoCleaner, LermaCleaner
from scripts.my_scripts.excel_functions import ExcelFunctions
import pandas as pd

def download_button(data, file_name, label:str='📥 Descargar Datos'):
    if data is not None:
        st.download_button(
            label=label,
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
    bad_data = pd.DataFrame()

    with col_uploading:
        files = st.file_uploader(label='Sube el archivo de polvos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
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
    bad_data = pd.DataFrame()
    
    with col_uploading:
        files = st.file_uploader(label='Sube el archivo de líquidos', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
            
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
    bad_data = pd.DataFrame()
    with col_uploading:
        files = st.file_uploader(label='Sube el archivo de Lerma', accept_multiple_files=True, type=['xlsx', 'xlsm'])

        if len(files) > 0:
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

def catalogo_expander(catalogo_actual:str, directorio_historicos:str='data/historico-catalogos'):
    """
    Esta función se utiliza para permitirle al usuario cambiar el catálogo que se está usando actualmente.
    Manda al histórico el catálogo que se está usando ahora para que no haya problemas si se quiere volver a uno previo.

    catalogo_actual: la ubicación del archivo de catálogo actual
    """
    os.makedirs(directorio_historicos, exist_ok=True)
    with st.sidebar.expander("Catálogo de productos"):
        historico, actualizar = st.tabs(["Histórico", "Actualizar"])
        with historico:
            # Hay que permitirle al usuario descargar el archivo actual
            data = ExcelFunctions().download_excel_file(catalogo_actual)
            download_button(data, 'catalogo_actual.xlsx', "Descargar catálogo actual")
            # Permitimos descargar catálogos históricos
            show_files_in_directory(directory=directorio_historicos)
            
        with actualizar:
            nuevo_catalogo = st.file_uploader(label='Sube el nuevo catálogo', accept_multiple_files=False, type=['xlsx'])
            if nuevo_catalogo:
                update_catalogo(catalogo_actual=catalogo_actual, nuevo_catalogo=nuevo_catalogo, directorio_historicos=directorio_historicos)


        
def update_catalogo(catalogo_actual:str, nuevo_catalogo, directorio_historicos:str):
    """
    Esta función recibe la ubicación del catálogo actual y los datos del nuevo catálogo.
    Se asegura de que tengan las mismas columnas en los dos.
    Mueve el catálogo actual al histórico de catálogos.
    Pone el nuevo catálogo en la ubicación y nombre donde esté el actual.
    """
    # Nos aseguramos de que el directorio de históricos exista
    os.makedirs(directorio_historicos, exist_ok=True)

    # Nos aseguramos de que las columnas de los dos archivos sean iguales
    actual = pd.read_excel(catalogo_actual)
    nuevo = pd.read_excel(nuevo_catalogo)
    if not nuevo.columns.equals(actual.columns):
        st.error('Las columnas de los archivos no coinciden')
        return False
    
    # Movemos el archivo actual al histórico con el nombre de la fecha del día que se haya hecho el movimiento
    fecha_hoy = datetime.datetime.now().strftime("%d-%m-%Y")
    shutil.copy(catalogo_actual, f"{directorio_historicos}/{fecha_hoy}.xlsx")
    
    # Guardamos el nuevo catálogo en el lugar del viejo
    nuevo.to_excel(catalogo_actual, index=False)
    st.success("Catálogo actualizado")

def show_files_in_directory(directory:str):
    """
    Esta función permite descargar los archivos de excel que haya en el directorio especificado
    """
    files = [file for file in os.listdir(directory) if file.split('.')[-1] == 'xlsx']
    if len(files) == 0: return
    chosen_file = st.selectbox(label='Catálogos históricos', options=files)
    download_button(
        data=ExcelFunctions().download_excel_file(f"{directory}/{chosen_file}"),
        file_name=chosen_file
    )

def open_cleaners(catalogo:str, clean_data:str):
    liquido_cleaner = LiquidoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)
    polvo_cleaner = PolvoCleaner(catalogo_file=catalogo, clean_data_file=clean_data)
    lerma_cleaner = LermaCleaner(catalogo_file=catalogo, clean_data_file=clean_data)

    return liquido_cleaner, polvo_cleaner, lerma_cleaner

def add_description_to_page():
    st.sidebar.write('''
        <p class="paragraph" align="justify">
            En esta página puedes cargar los archivos operacionales de planeación de producción para que se actualicen de forma automática
        </p>''',
    unsafe_allow_html=True)

def render_page():
    open_styles()
    add_description_to_page()
    
    catalogo = 'data/catalogo_productos.xlsx'
    clean_data = 'data/datos_produccion.parquet'

    liquido_cleaner, polvo_cleaner, lerma_cleaner = open_cleaners(catalogo=catalogo, clean_data=clean_data)

    # ------ SIDEBAR ------
    type_of_file = st.sidebar.radio('Elige el tipo de archivo a subir', ['Polvos', 'Líquidos', 'Lerma'])
    catalogo_expander(catalogo_actual=catalogo)

    # ------- BODY --------
    if type_of_file == 'Polvos':
        update_polvos(polvo_cleaner=polvo_cleaner)
    elif type_of_file == 'Líquidos':
        update_liquidos(liquido_cleaner=liquido_cleaner)
    elif type_of_file == "Lerma":
        update_lerma(lerma_cleaner=lerma_cleaner)

    

if __name__ == '__main__':
    render_page()