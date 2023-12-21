import pandas as pd
import datetime

class DataProcessor:
    def __init__(self, file_location:str) -> None:
        """
        file_location: dónde están los datos de producción
        tipo_de_filtro: el tipo de filtro que se va a usar -> [familia, producto, marca]
        """
        self.datos = pd.read_parquet(file_location)
        self.filtro = None
        self.filter_value = None
        self.date_range = (None, None)
        self.filtered_data = None
        self.fully_instanciated_processor = False

    def set_type_of_filter(self, type_of_filter:str):
        assert type_of_filter in ['familia', 'sku', 'marca'], "Tipo de filtro inválido"
        self.filtro = type_of_filter

    def set_filter_value(self, filter_value):
        self.filter_value = filter_value

    def set_date_range(self, min_date:datetime.date, max_date:datetime.date):
        assert self.filter_value is not None, "Aún no has especificado el valor del filtro"
        min_date = pd.Timestamp(min_date)
        max_date = pd.Timestamp(max_date)
        self.date_range = (min_date, max_date)
        self.filtered_data = self.__get_filtered_data()
        # Nos aseguramos que verdaderamente existan datos en el rango dado
        if self.filtered_data.size <= 0: return
        self.fully_instanciated_processor = True


    def get_available_values(self) -> list:
        """
        Esta función se utiliza para tener las familias para las cuales se tienen datos disponibles
        """
        if self.filtro is None: return []
        if self.filtro == 'sku': return sorted(list(self.datos.apply(lambda x: str(x.sku)+' - '+str(x.descripcion), axis=1).unique()))
        return sorted(list(self.datos[self.filtro].unique()))
    
    def get_available_dates(self):
        """
        Esta función necesita que ya se haya especifcado filtro y filter_value
        """
        assert self.filtro is not None and self.filter_value is not None, "Se necesitan más datos aún"
        filtered_data_so_far =(
            self
            .datos
            .query(f"{self.filtro} == '{self.filter_value}'")            
        )
        min_date = filtered_data_so_far.fecha.min()
        max_date = filtered_data_so_far.fecha.max()
        return min_date, max_date
    
    def get_my_kpis(self):
        return self.__get_kpis_by_familia_and_marca()

    def __get_kpis_by_familia_and_marca(self) -> dict:
        """
        Esta función regresa todos los kpis que se tienen para las familias, que son los siguientes:
            - Cuántos skus distintos hay
            - Total de kilos/litros fabricados
            - Total de kilos/litros programados
            - Porcentaje de cumplimento (por kilos/litros)
            - Porcentaje de cumplimento (por número de productos terminados)
            - El mejor producto
            - El peor producto
        """
        assert self.fully_instanciated_processor, "Aún no has terminado de instanciar el procesador"
        unique_skus = self.filtered_data.sku.unique().size
        total_fabricado = self.filtered_data.fabricado.sum()
        total_programado = self.filtered_data.programado.sum()
        porcentaje_cumplimento_kilos_litros = round(total_fabricado / total_programado * 100, 2)
        cumpliento_por_producto = (
            self.filtered_data
            .groupby('sku')
            .agg(
                fabricado=pd.NamedAgg('fabricado', 'sum'),
                programado=pd.NamedAgg('programado', 'sum')
            )
            .assign(
                cumplimiento=lambda x: round(x.fabricado / x.programado*100, 2),
                terminado = lambda x: (x.fabricado >= x.programado).astype(int)
            )
            .dropna()
        )
        skus_terminados = cumpliento_por_producto.terminado.sum()
        porcentaje_cumplimento_productos_terminados = round(cumpliento_por_producto.terminado.mean()*100, 2)
        best_product = cumpliento_por_producto.head(1).T.to_dict()
        worst_product = cumpliento_por_producto.tail(1).T.to_dict()
        return {
            'unique_skus':unique_skus,
            'skus_terminados':skus_terminados,
            'kglt_programados':total_programado,
            'kglt_fabricados':total_fabricado,
            'cumplimiento_kglt':porcentaje_cumplimento_kilos_litros,
            'cumplimiento_productos':porcentaje_cumplimento_productos_terminados,
            'best_product':best_product,
            'worst_product':worst_product
        }
    
    def __get_filtered_data(self):
        """
        Esta función privada se utiliza para generar los filtros que el usuario desee.
        """
        # Aplicamos los filtros que ya tengamos
        # Se supone que cuando se ejecute esta función ya debemos saber el valor del filtro
        # y el rango de fechas
        min_date, max_date = self.date_range
        filtered_data = (
            self.datos
            .query(f"{self.filtro} == '{self.filter_value}'")
            .query(f'@min_date <= fecha <= @max_date')
            .reset_index(drop=True)
        )
        return filtered_data
