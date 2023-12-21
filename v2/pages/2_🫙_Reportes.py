import streamlit as st
import pandas as pd
import os
from scripts.data_processor import DataProcessor
from scripts.my_scripts.excel_functions import ExcelFunctions

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

def add_description_to_page():
    st.sidebar.write('''
        <p class="paragraph" align="justify">
            En esta página puedes generar reportes de la producción utilizando cualquiera de los siguientes filtros.
        </p>''',
    unsafe_allow_html=True)

def display_filtering_controls(data_processor:DataProcessor):
    # Permitimos al usuario elegir lo que usará de filtro
    valores = data_processor.get_available_values()
    chosen_value = st.sidebar.selectbox("Elige la familia", options=valores)

    # Ahora filtramos los datos de esa familia
    if not chosen_value: return
    data_processor.set_filter_value(filter_value=chosen_value)

    # Ahora le permitimos elegir el rango de fechas que quiere filtrar
    available_dates = data_processor.get_available_dates()
    chosen_dates = st.sidebar.date_input('Elige el rango de fechas', value=available_dates, min_value=available_dates[0], max_value=available_dates[1])
    if len(chosen_dates) != 2: return
    data_processor.set_date_range(*chosen_dates)
    if not data_processor.fully_instanciated_processor: 
        st.warning("El rango de fechas no es suficientemente amplio para mostrar información")

    return chosen_value, chosen_dates


def display_kpis(kpis:dict, col_kpis, sku:bool=False):
    with col_kpis:
        if not sku:
            st.subheader('Productos')
            kpi_1, kpi_2 = st.columns(2)
            kpi_1.metric(label='Skus únicos', value=kpis['unique_skus'])
            kpi_2.metric(label='Skus completados', value=kpis['skus_terminados'])
            st.metric(label='Porcentaje productos completados', value=f"{kpis['cumplimiento_productos']}%")
            st.divider()

        st.subheader('Kilos/Litros')
        kpi_3, kpi_4 = st.columns(2)
        kpi_3.metric(label='Kilos Programados', value=kpis['kglt_programados'])
        kpi_4.metric(label='Kilos Fabricados', value=kpis['kglt_fabricados'])
        st.metric(label='Porcentaje kilos litros fabricados', value=f"{kpis['cumplimiento_kglt']}%")
        st.divider()

        if not sku:
            st.subheader('Mejor producto')
            best_product = next(iter(kpis['best_product']))
            kpi_5, kpi_6, kpi_7 = st.columns(3)
            kpi_5.metric(label='Producto', value=best_product)
            kpi_6.metric(label='Programado', value=kpis['best_product'][best_product]['programado'])
            kpi_7.metric(label='Fabricado', value=kpis['best_product'][best_product]['fabricado'])
            st.divider()

            st.subheader('Peor producto')
            worst_product = next(iter(kpis['worst_product']))
            kpi_8, kpi_9, kpi_10 = st.columns(3)
            kpi_8.metric(label='Producto', value=worst_product)
            kpi_9.metric(label='Programado', value=kpis['worst_product'][worst_product]['programado'])
            kpi_10.metric(label='Fabricado', value=kpis['worst_product'][worst_product]['fabricado'])

def display_data_col(df:pd.DataFrame, col_datos, file_name:str, sheet_name:str):
    with col_datos:
        downloadable = ExcelFunctions().save_and_download_excel_file(df.assign(fecha=lambda x: x.fecha.dt.strftime('%Y-%m-%d')), 'data/', file_name, sheet_name)
        os.remove(f'data/{file_name}.xlsx')
        download_button(*downloadable)
        st.dataframe(df.assign(fecha=lambda x: x.fecha.dt.strftime('%Y-%m-%d')), use_container_width=True, hide_index=True)
    

def filtro_familia(data_processor:DataProcessor):
    """
    Esta función pone la información que se necesita cuando el usuario desea filtrar por familia
    """
    chosen_family, _ = display_filtering_controls(data_processor=data_processor)
    kpis = data_processor.get_my_kpis()

    st.title('KPIS FAMILIAS')
    col_kpis, col_datos = st.columns((.4, .6))
    display_kpis(kpis, col_kpis)
    display_data_col(data_processor.filtered_data, col_datos, f'reporte_familia_{chosen_family.lower()}', 'reporte de familia')

 
def filtro_marca(data_processor:DataProcessor):
    """
    Esta función pone la información que se necesita cuando el usuario desea filtrar por marca
    """
    chosen_brand, _ = display_filtering_controls(data_processor=data_processor)
    kpis = data_processor.get_my_kpis()
    st.title('KPIS MARCAS')
    col_kpis, col_datos = st.columns((.4, .6))
    display_kpis(kpis, col_kpis)
    display_data_col(data_processor.filtered_data, col_datos, f'reporte_familia_{chosen_brand.lower()}', 'reporte de marca')

def filtro_producto(data_processor:DataProcessor):
    chosen_sku, _ = display_filtering_controls(data_processor=data_processor)
    kpis = data_processor.get_my_kpis()
    st.title('KPIS PRODUCTO')
    col_kpis, col_datos = st.columns((.4, .6))
    display_kpis(kpis, col_kpis, sku=True)
    display_data_col(data_processor.filtered_data, col_datos, f'reporte_familia_{chosen_sku.lower()}', 'reporte de producto')


def render_page():
    """
    Lo que quiero mostrar en esta página es lo siguiente:
        - Dar la opción de filtrar por producto (ya sea por sku o por descripción)
        - Dar la opción de filtrar por familia
        - Dar la opción de filtrar por marca
        - Generar un excel con los datos que se tengan
        - El overall production de cada filtro
    """
    open_styles()
    add_description_to_page()
    produccion_file = "data/datos_produccion.parquet"
    data_processor = DataProcessor(produccion_file)

    # ------ SIDEBAR ---------
    type_of_filter = st.sidebar.radio('Elige el tipo de filtro', ['Familia', 'Marca', 'Producto'])
    
    # ------- BODY --------
    if type_of_filter == 'Familia':
        data_processor.set_type_of_filter(type_of_filter='familia')
        filtro_familia(data_processor=data_processor)
    elif type_of_filter == 'Marca':
        data_processor.set_type_of_filter(type_of_filter='marca')
        filtro_marca(data_processor=data_processor)
    elif type_of_filter == "Producto":
        data_processor.set_type_of_filter(type_of_filter='sku')
        filtro_producto(data_processor=data_processor)


if __name__ == "__main__":
    render_page()