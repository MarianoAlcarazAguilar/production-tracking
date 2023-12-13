import streamlit as st
from scripts.file_cleaner import FileCleaner
import pandas as pd
from scripts.excel_functions import ExcelFunctions

def open_styles(location='data/static/style.css'):
    '''
    Función genérica que se utiliza para tener el mismo formato en todas las páginas
    '''
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Dragón',
        page_icon='🐉'
    )

    with open(location) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def download_button(data, file_name):
    '''
    Función genérica que se utiliza para poder permitirle al usuario descargar un archivo
    '''
    if data is not None:
        st.download_button(
            label='📥 Descargar Datos',
            data=data,
            file_name=file_name
        )

def download_df(df:pd.DataFrame, selected_sku:str):
    '''
    TODO: Función que reciba un dataframe y permita descargarlo como un excel.
    Nota: ya hay una función en excel_functions que hace exactamente eso, solo es necesario modificar
    aquí para que el archivo, una vez descargado, sea eliminado. También debe mostrarse el botón de descargar datos
    que ya existe arriba.
    Input:
        df -> DataFrame a descargar
    '''
    ef = ExcelFunctions()
    bytes_data, filename = ef.save_and_download_excel_file(
        df=df,
        dir_location='data/reportes',
        file_name=f'reporte_sku_{selected_sku}',
        sheet_name='datos-intervalo',
        n_cols_to_bold=4
    )
    download_button(bytes_data, filename)

def show_aggregated_insights(df_aux:pd.DataFrame):
    '''
    Función que pone datos agregados de la producción de un producto
    '''
    col_fechas, col_kilos, col_agregados = st.columns(3)
    # Rango de fechas
    df = df_aux.copy()
    df['inicio_semana_real'] = pd.to_datetime(df.inicio_semana_real, dayfirst=True)
    min_date = df.inicio_semana_real.min()
    max_date = df.inicio_semana_real.max()
    with col_fechas:
        st.metric(label='Datos desde', value=min_date.strftime('%d/%m/%Y'))
        st.metric(label='Hasta', value=max_date.strftime('%d/%m/%Y'))

    # Total Planeado
    total_planeado = df.planeado.sum()
    # Total producido
    total_producido = df.producido.sum()
    with col_kilos:
        st.metric('Total KG/LT planeados', value=total_planeado)
        st.metric(label='Total Producido', value=total_producido)
    # Número de datos registrados
    n_datos = df.shape[0]
    # Overall Percentage
    overall_production = round(total_producido/total_planeado*100, 2)
    with col_agregados:
        st.metric(label='Número de registros', value=n_datos)
        st.metric(label='Overall production', value=f'{overall_production}%')



def render_page():
    open_styles()
    st.sidebar.write('''
        <p class="paragraph">
            En esta página puedes generar los reportes necesarios de los <b>productos</b> que sean necesarios.
        </p>
    ''',unsafe_allow_html=True) 

    fc = FileCleaner()

    filtrar_por = st.sidebar.radio('Elige tipo de filtro', options=['Familia', 'Marca', 'Producto'], horizontal=False)

    if filtrar_por == 'Familia':
        familias = fc.get_column(column='familia', unique=True)
        selected_family = st.sidebar.selectbox('Elige la familia', options=familias, label_visibility="collapsed")
        unique_skus = fc.get_filtered_values(columna='familia', valor=selected_family, return_column='sku', unique=True)
        selected_sku = st.sidebar.selectbox('elige el producto', options=unique_skus, label_visibility="collapsed")
   
    elif filtrar_por == 'Marca':
        marcas = fc.get_column(column='marca', unique=True)
        selected_marca = st.sidebar.selectbox('Elige la marca', options=marcas, label_visibility="collapsed")
        unique_marcas = fc.get_filtered_values(columna='marca', valor=selected_marca, return_column='sku', unique=True)
        selected_sku = st.sidebar.selectbox('elige el producto', options=unique_marcas, label_visibility="collapsed")
    else:
        productos = fc.get_column(column='descripcion', unique=True)
        selected_product = st.sidebar.selectbox('Elige el producto', options=productos, label_visibility="collapsed")
        unique_descriptions = fc.get_filtered_values(columna='descripcion', valor=selected_product, return_column='sku', unique=True)
        selected_sku = st.sidebar.selectbox('elige el producto', options=unique_descriptions, label_visibility='collapsed')


    # TODO: Función que filtre los datos d un producto y que genere un reporte
    datos_producto = fc.get_values_for_sku(sku=selected_sku)
    
    show_aggregated_insights(datos_producto)
    st.dataframe(datos_producto, hide_index=True, use_container_width=True)
    download_df(df=datos_producto, selected_sku=selected_sku)

        
        



if __name__ == '__main__':
    render_page()