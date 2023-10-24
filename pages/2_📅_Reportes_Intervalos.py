import streamlit as st
import scripts.auxiliar_functions as af
from scripts.file_cleaner import FileCleaner
from scripts.excel_functions import ExcelFunctions
import pandas as pd
import datetime

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

def get_corresponding_sundays(fecha_inicio:pd.Timestamp, fecha_fin:pd.Timestamp) -> (pd.Timestamp, pd.Timestamp):
    '''
    Función que recibe dos fechas y las convierte a sus domingos correspondientes.
    Es necesaria porque en muchos casos se supone que las fechas utilizadas son domingos, entonces así ya no
    es necesario estar calculandolos desde cero cada vez.
    Inputs:
        fecha_inicio -> inicio de la semana (es lunes)
        fecha_fin -> fin de la semana (es viernes)
    Return:
        (pd.Timestamp, pd.Timestamp) -> (lunes menos un día, viernes más dos días)
    '''
    domingo_inicio = fecha_inicio - pd.Timedelta(days=1)
    domingo_final = fecha_fin + pd.Timedelta(days=2)
    return domingo_inicio, domingo_final

def get_intervalo_ultima_semana(file_cleaner:FileCleaner) -> (pd.Timestamp, pd.Timestamp):
    '''
    Función que muestre el número de semana de inicio que se consideran en los datos
    además de la semana de fin. Junto con sus respectivos inicios y fines de semana en fechas.
    Input:
        fc -> FileCleaner que tiene acceso a todos los datos
    Return: 
        (pd.Timestamp, pd.Timestamp) -> (fecha de inicio, fecha de fin), ambas fechas deben de corresponder a la misma semana
    '''
    # Encontramos las fechas
    fechas = file_cleaner.get_last_update_date() # Regresa diccionario con fechas de última actualización
    fecha_inicio = af.encontrar_fecha_mas_grande(fechas) # Fecha inicio me regresa segundos desde 1970 de la fecha más reciente del diccionario
    inicio_semana = pd.Timestamp(fecha_inicio, unit='s') + pd.Timedelta(days=1) # Convertimos a timestamp de pandas. Nota: la fecha es del domingo que inicia la semana, entonces le sumamos un día para que sea lunes
    fin_semana = pd.Timestamp(fecha_inicio, unit='s') + pd.Timedelta(days=5) # Convertimos a timestamp de pandas. Le sumamos 5 días para que sea el viernes

    return inicio_semana, fin_semana

def get_porcentaje_cumplimiento(file_cleaner:FileCleaner, fecha_inicio:pd.Timestamp, fecha_fin:pd.Timestamp) -> float:
    '''
    Función que calcule el porcentaje de cumplimiento overall en un intervalo determinado.
    Input: 
        fecha_inicio -> un timestamp de inicio (el lunes de la semana)
        fecha_fin -> un timestamp de final (el viernes de la semana)
    Return: 
        float -> porcentaje de cumplimento en el tiempo dado. Se consideran todos los tipos de productos
    '''
    # Tenemos que asegurarnos de enviar dos domingos

    domingo_inicio, domingo_final = get_corresponding_sundays(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    cumplimiento = file_cleaner.get_cumplimiento_en_intervalo(inicio=domingo_inicio, fin=domingo_final)
    
    return cumplimiento

def get_num_productos_terminados(file_cleaner:FileCleaner, fecha_inicio:pd.Timestamp, fecha_fin:pd.Timestamp) -> (int, int, int):
    '''
    Función que encuentre el total de productos terminados en un intervalo de tiempo dado
    Input:
        fecha_inicio -> un timestamp de inicio
        fecha_fin -> un timestamp de final
    Return:
        (int, int, int) -> (total de productos, total de productos de dragón, total de productos externos)
    ''' 
    # Para este ya es bien fácil, porque nada más tengo que usar las funciones que hice en el file_cleaner
    domingo_inicio, domingo_fin = get_corresponding_sundays(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    total_prods, total_dragon, total_externos = file_cleaner.get_total_products_on_interval(inicio=domingo_inicio, fin=domingo_fin)

    return total_prods, total_dragon, total_externos

def get_tabla_con_productos(file_cleaner: FileCleaner, fecha_inicio:pd.Timestamp, fecha_fin:pd.Timestamp) -> pd.DataFrame:
    '''
    TODO: Función que genere un dataframe con los productos que se hicieron en el intervalo seleccionado, 
    incluyendo columnas para la descripción, el tipo, total de planeación, total producido, porcentaje y la planta donde se hizo.
    Se debe asegurar de que solo exista un registro por sku, y si hay más de uno los debe agrupar en uno solo.
    Input:
        fecha_inicio -> un timestamp de inicio
        fecha_fin -> un timestamp de final
    Return:
        pd.DataFrame -> Dataframe con los datos extraídos.
    '''
    
    domingo_inicio, domingo_fin = get_corresponding_sundays(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    productos = file_cleaner.get_products_on_interval(domingo_inicio, domingo_fin)
    return productos

def download_df(df:pd.DataFrame):
    '''
    TODO: Función que reciba un dataframe y permita descargarlo como un excel.
    Nota: ya hay una función en excel_functions que hace exactamente eso, solo es necesario modificar
    aquí para que el archivo, una vez descargado, sea eliminado. También debe mostrarse el botón de descargar datos
    que ya existe arriba.
    Input:
        df -> DataFrame a descargar
    '''
    ef = ExcelFunctions()
    if 'lista_datos' in df.columns:
        df = df.drop('lista_datos', axis=1)
    bytes_data, filename = ef.save_and_download_excel_file(
        df=df,
        dir_location='data/reportes',
        file_name='reporte_generado',
        sheet_name='datos-intervalo',
        n_cols_to_bold=3
    )
    download_button(bytes_data, filename)

def show_cumplimiento_historico(n_semanas:int):
    '''
    TODO: función que muestre una gráfica para ver el históricio de cumplimiento.
    La verdad no sé si esto sea necesario.
    '''
    pass

def lunes_anterior_cercano(fecha:datetime.date):
    # Calcula el día de la semana de la fecha dada (0 = lunes, 1 = martes, ..., 6 = domingo)
    dia_semana = fecha.weekday()
    
    # Calcula la diferencia en días para retroceder al lunes anterior
    diferencia_dias = (dia_semana - 0) % 7
    
    # Calcula la fecha del lunes anterior más cercano
    lunes_anterior = fecha - datetime.timedelta(days=diferencia_dias)
    
    return lunes_anterior

def viernes_siguiente_cercano(fecha:datetime.date):
    # Calcula el día de la semana de la fecha dada (0 = lunes, 1 = martes, ..., 6 = domingo)
    dia_semana = fecha.weekday()
    
    # Calcula la diferencia en días para avanzar al viernes siguiente
    diferencia_dias = (4 - dia_semana) % 7
    
    # Calcula la fecha del viernes siguiente más cercano
    viernes_siguiente = fecha + datetime.timedelta(days=diferencia_dias)
    
    return viernes_siguiente

def render_page():
    open_styles()
    fc = FileCleaner()

    fecha_inicio_ultima_semana, fecha_fin_ultima_semana = get_intervalo_ultima_semana(file_cleaner=fc)

    col_fecha_inicio, col_fecha_fin = st.sidebar.columns(2)

    fecha_inicio = col_fecha_inicio.date_input('Fecha de inicio', value=fecha_inicio_ultima_semana, max_value=fecha_fin_ultima_semana)
    fecha_fin = col_fecha_fin.date_input('Fecha de fin', value=fecha_fin_ultima_semana, min_value=fecha_inicio)
    fecha_inicio = lunes_anterior_cercano(fecha_inicio)
    fecha_fin = viernes_siguiente_cercano(fecha_fin)
    st.sidebar.write('''
        <p class="paragraph">
            Dada una fecha de inicio, se considerará el <b>lunes anterior más cercano</b>
        </p>
        <p class="paragraph">
            Dada una fecha de fin, se considerará el <b>viernes próximo más cercano</b>
        </p>
    ''',unsafe_allow_html=True) 



    if st.sidebar.button('Ver datos última semana'):
        fecha_inicio = fecha_inicio_ultima_semana
        fecha_fin = fecha_fin_ultima_semana



    cumplimiento = get_porcentaje_cumplimiento(file_cleaner=fc, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    total_productos, total_dragon, total_externos = get_num_productos_terminados(file_cleaner=fc, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    # Estas son las columnas que vamos a usar para los datos que van hasta arriba
    intervalo_estudio, porcentaje_cumplimiento, num_productos = st.columns(3, gap='large')

    with intervalo_estudio:
        st.markdown('##### Intervalo Estudiado')
        col11, col12 = st.columns((.2,.8), gap='small')
        col11.metric('Semana', fecha_inicio.isocalendar().week)
        with col12:
            st.write(f'<b>Inicio</b> {fecha_inicio.strftime("%d/%m/%Y")}', unsafe_allow_html=True)
            st.write(f'<b>Fin</b> {fecha_fin.strftime("%d/%m/%Y")}', unsafe_allow_html=True)

    with porcentaje_cumplimiento:
        st.markdown('##### Porcentaje Cumplimiento')
        st.metric('Cumplimiento', f'{round(cumplimiento*100)}%', label_visibility='visible')
        st.write('''
            <p class="paragraph">
                Cumplimiento considera el porcentaje de productos cuya producción fue mayor o igual al total de la planeación.
            </p>
        ''',unsafe_allow_html=True)
        
    with num_productos:
        st.markdown('##### Número de Productos')
        col31, col32 = st.columns(2)
        with col31:
            st.metric('Total Productos', f'{total_productos}')
        with col32:
            st.write(f'<b>Dragón</b> {total_dragon}', unsafe_allow_html=True)
            st.write(f'<b>Externos</b> {total_externos}', unsafe_allow_html=True)
    

    df_productos = get_tabla_con_productos(file_cleaner=fc, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)#.drop(['lista_datos'], axis=1)
    st.dataframe(df_productos, hide_index=True, use_container_width=True)
    download_df(df=df_productos)

    show_cumplimiento_historico(n_semanas=10)
    


if __name__ == '__main__':
    render_page()