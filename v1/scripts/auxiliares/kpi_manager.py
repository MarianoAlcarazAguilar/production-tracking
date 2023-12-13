import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go


class KpiManager:
    '''
    Lo que tengo que poder hacer con este objeto es básicamente ver la siguiente información:
    - Cómo está el porcentaje de cumplimiento en una semana dada
    - Cómo se ha comportado a lo largo del tiempo el cumplimiento
    - Cuántos productos se produjeron en un lapso de tiempo dado
    - Total de productos en un lapso
        - De esos productos, cuántos fueron termianados, cuántos no, y qué porcentajes representan cada uno. Puedo colorear cada barra por productos de dragón o externos


    Lo que necesito que me den para poder procesar:
    - Número de semana de inicio
    - Número de semana de final

    '''


    def __init__(self, main=False):
        self.current_dir = '..' if main else '.'
        self.qlik_file_name = 'data_for_qlik.parquet'
        self.datos = pd.read_parquet(f'{self.current_dir}/data/{self.qlik_file_name}')
        self.unidades = pd.read_csv(f'{self.current_dir}/data/static/conversion_unidades.csv')
        self.catalogo = pd.read_excel(f'{self.current_dir}/data/static/catalogo_productos.xlsx', usecols=['Sku', 'Familia', 'Marca', 'Descripción']).rename(columns={'Sku':'sku', 'Familia':'familia', 'Marca':'marca', 'Descripción':'descripcion'})

    def __obtener_primer_dia_semana(self, numero_semana, anio):
        numero_semana, anio = int(numero_semana), int(anio)
        # Crear un objeto de fecha y tiempo para el primer día del año dado
        primer_dia_anio = datetime.datetime(anio, 1, 1)

        # Calcular la diferencia en días entre el primer día del año y el primer día de la semana dada
        dias_diferencia = (numero_semana - 1) * 7

        # Obtener el primer día de la semana sumando la diferencia de días al primer día del año
        primer_dia_semana = primer_dia_anio + datetime.timedelta(days=dias_diferencia)

        return primer_dia_semana


    def get_available_weeks(self):
        '''
        Esta función regresa las semanas disponibles con su respectivo inicio de semana
        '''
        weeks = (self.datos
        [['semana', 'anio']]
        .drop_duplicates()
        .assign(
            inicio_semana=lambda df: df.apply(lambda row: self.__obtener_primer_dia_semana(row.semana, row.anio), axis=1),
            display=lambda x: x.semana.astype(str) +'-'+ x.anio.astype(str) +' | '+ x.inicio_semana.dt.strftime('%d-%m-%Y')
        )
        .sort_values('inicio_semana', ascending=False)
        .drop(['inicio_semana'], axis=1)
        )
        return weeks

    
if __name__ == "__main__":
    print('kpi_manager.py running as main')

    manager = KpiManager(main=True)


    