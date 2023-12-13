from my_scripts.new_excel_functions import DataExtraction
from errores import FechaNoEsLunes, FechaNoEncontrada, ArchivoNoPermitido, ColumnasNoCoinciden
import pandas as pd
import numpy as np
import datetime
import os

class AuxiliarFunctions:
    '''
    Esta clase son las funciones genéricas que se usan para limpiar todos los archivos.
    '''
    def encuentra_fecha(self, extractor:DataExtraction, allowed_values:list) -> datetime.datetime:
        '''
        Esta función encuentra la fecha en el documento.
        Se hacen las verificaciones correspondientes.
        La fecha debe de ser el lunes del inicio de la semana que se está considerando.
        '''
        # Primero tenemos que asegurarnos de que venga una celda con la palabra buscada
        # Vamos a intentar con dos opciones de tíutlo de fecha: 'fecha' y 'Fecha'
        celda_fecha = (-1,-1)
        
        for nombre_fecha in allowed_values:
            lista_celda_fecha = extractor.find_value(nombre_fecha)
            if len(lista_celda_fecha) > 0:
                celda_fecha = lista_celda_fecha[0]
                break
        
        if celda_fecha == (-1,-1):
            raise FechaNoEncontrada(allowed_values)
        
        # La fecha puede estar a la derecha o debajo de donde diga fecha
        # Buscamos en ambas opciones
        row_fecha, col_fecha = celda_fecha
        opciones_fecha = [(row_fecha+1, col_fecha), (row_fecha, col_fecha+1)]
        fecha = None
        
        for opcion_fecha in opciones_fecha:
            aux_fecha = extractor.get_value_on_cell(opcion_fecha)
            if isinstance(aux_fecha, datetime.datetime):
                fecha = aux_fecha
                break
                
        if fecha is None:
            raise FechaNoEncontrada(nombre_fecha)
        if fecha.weekday() != 0:
            raise FechaNoEsLunes(fecha)
        return fecha
    
    def homologar_df(self, df:pd.DataFrame, rename_columns_dict:dict, cols_to_add:dict=None) -> pd.DataFrame:
        '''
        Esta función cambia los nombres de las columnas y agrega las deseadas.
        '''
        my_df = df.copy()
        my_df.rename(rename_columns_dict, axis=1, inplace=True)
        for col_to_add in cols_to_add:
            my_df[col_to_add] = cols_to_add[col_to_add]
        return my_df  
    
    def save_data(self, df:pd.DataFrame, location:str, type_of_file:str, drop_duplicates:bool):
        '''
        Esta función guarda los datos en un archivo que se especifique.
        Verifica la existencia del archivo. Si este existe, lo abre y agrega los datos
        y si drop_duplicates es True, tira los duplicados que se encuentren.
        '''
        # Si existe el archivo
        if os.path.exists(location):
            if type_of_file == 'csv':
                existing_file = pd.read_csv(location)
            elif type_of_file == 'xlsx':
                existing_file = pd.read_excel(location)
            elif type_of_file == 'parquet':
                existing_file = pd.read_parquet(location)
            else:
                raise ArchivoNoPermitido(['csv', 'xlsx', 'parquet'])
            
            # Aquí se supone que ya tenemos un archivo cargado
            # Hay que ver que las columnas sean iguales
            if not existing_file.columns.equals(df.columns):
                raise ColumnasNoCoinciden(existing_file.columns, df.columns)

        else:
            existing_file = pd.DataFrame()

        # Aquí ya tenemos dos df con los datos que necesitamos
        together_data = pd.concat((existing_file, df), ignore_index=True)
        if drop_duplicates:
            together_data.drop_duplicates(inplace=True)
        # Guardamos los datos
        if type_of_file == 'csv':
            existing_file = together_data.to_csv(location, index=False)
        elif type_of_file == 'xlsx':
            existing_file = together_data.to_excel(location, index=False)
        else:
            existing_file = together_data.to_parquet(location, index=False)
        
class LiquidoCleaner:
    def __init__(self, catalogo_file:str, clean_data_file:str, type_of_file:str='parquet') -> None:
        '''
        catalogo_file: ubicación del archivo que se usa como catálogo de los productos. Tiene las columnas sku, descripcion, familia, marca
        '''
        self.catalogo = pd.read_excel(catalogo_file)
        self.clean_data_file = clean_data_file
        self.type_of_file = type_of_file
        self.funciones_auxiliares = AuxiliarFunctions()
        self.INDEX_VALUE = 'CLAVE'
        self.COLS_TO_EXTRACT = ['Fabricado', 'Programa']
        self.OUTPUT_COLUMN_NAMES = ['sku', 'fabricado', 'programado']
        self.TIPO_ARCHIVO = 'liquido'
        self.SHIFT_BETWEEN_VALUES = 0
        self.SHEET_NAME = 0
        self.ALLOWED_VALUES_FOR_DATE = ['DEL:', 'Del:', 'DEL', 'del']
        self.extracted_data = None
        self.good_data, self.bad_data = None, None
    
    def extract_data(
            self,
            file
        ):
        '''
        Esta función limpia el archivo de polvos si el template es el adecuado
        ''' 
        # Cargamos el archivo en un extractor
        extractor = DataExtraction(file, sheet_name=self.SHEET_NAME)
        
        # Buscamos la fecha en el archivo
        fecha = self.funciones_auxiliares.encuentra_fecha(extractor=extractor, allowed_values=self.ALLOWED_VALUES_FOR_DATE)
        
        # Ahora sí sacamos los datos
        df = extractor.extract_data_from_file(
            index_value=self.INDEX_VALUE,
            cols_to_extract=self.COLS_TO_EXTRACT,
            shift_between_values=self.SHIFT_BETWEEN_VALUES
        )
        # Tiramos los skus que sean 0
        df = df.query(f'{self.INDEX_VALUE} != 0')
        
        # Homologamos los datos
        rename_dict = {llave:valor for llave, valor in zip([self.INDEX_VALUE] + self.COLS_TO_EXTRACT, self.OUTPUT_COLUMN_NAMES)}
        cols_to_add = {'fecha':fecha, 'tipo':self.TIPO_ARCHIVO}
        df = self.funciones_auxiliares.homologar_df(df, rename_columns_dict=rename_dict, cols_to_add=cols_to_add)
        self.extract_data = df
    
    def valida_datos(self) -> pd.DataFrame:
        '''
        Ahora hacemos las validaciones necesarias.
        1. Convertir a números lo fabricado y programado
        2. Hacer el match de los sku con los del catálogo
        '''
        assert self.extract_data is not None, "Aún no se han limpiado los datos"
        cols = ['fabricado', 'programado']
        catalogo = self.catalogo
        
        my_df = self.extract_data
        for col in cols:
            my_df[col] = pd.to_numeric(my_df[col], errors='coerce')
        
        df_sin_nan = my_df.dropna(subset=cols, how='any')
        bad_production_data = my_df[my_df[cols].isna().any(axis=1)].sku
        
        # Ahora, para los productos que sí tienen números en lo producido y fabricado
        # nos aseguramos de que los skus estén en el catálogo existente. Si no están,
        # no los queremos.
        df_skus_bien = df_sin_nan.merge(catalogo, on='sku', how='left').dropna(subset=['familia']).reset_index(drop=True)
        bad_sku_codes = df_sin_nan.merge(catalogo, on='sku', how='left').pipe(lambda df: df[df.familia.isna()]).sku
        
        df_reporte_errores = (
            pd.concat((pd.DataFrame(bad_production_data).assign(error='cantidades'),
                    pd.DataFrame(bad_sku_codes).assign(error='sku invalido')), 
                    ignore_index=True)
        )
        
        self.good_data, self.bad_data =  (df_skus_bien, df_reporte_errores)

    def save_data(self):
        '''
        Esta función guarda los datos limpios en donde se especifique
        '''
        assert self.good_data is not None, "Aún no se han limpiado los datos"
        self.funciones_auxiliares.save_data(self.good_data, location=self.clean_data_file, type_of_file=self.type_of_file, drop_duplicates=True)

    def extract_and_save_data(self, file):
        '''
        Esta función extrae los datos, los valida y los guarda.
        '''
        self.extract_data(file)
        self.valida_datos()
        self.save_data()

class PolvoCleaner:
    def __init__(self, catalogo_file:str, clean_data_file:str, type_of_file:str='parquet') -> None:
        '''
        catalogo_file: ubicación del archivo que se usa como catálogo de los productos. Tiene las columnas sku, descripcion, familia, marca
        '''
        self.catalogo = pd.read_excel(catalogo_file)
        self.funciones_auxiliares = AuxiliarFunctions()
        self.clean_data_file = clean_data_file
        self.type_of_file = type_of_file
        self.extracted_data = None
        self.good_data, self.bad_data = None, None

        self.INDEX_VALUE = 'CLAVE'
        self.COLS_TO_EXTRACT = ['KG FABRICADOS', 'KG PROGRAMADOS']
        self.OUTPUT_COLUMN_NAMES = ['sku', 'fabricado', 'programado']
        self.TIPO_ARCHIVO = 'polvo'
        self.SHIFT_BETWEEN_VALUES = 0
        self.SHEET_NAME = 0
        self.ALLOWED_VALUES_FOR_DATE = ['Fecha', 'fecha', 'Fecha Inicio']



    def extract_data(
            self,
            file
        ):
        '''
        Esta función limpia el archivo de polvos si el template es el adecuado
        ''' 
        # Cargamos el archivo en un extractor
        extractor = DataExtraction(file, sheet_name=self.SHEET_NAME)
        
        # Buscamos la fecha en el archivo
        fecha = self.funciones_auxiliares.encuentra_fecha(extractor=extractor, allowed_values=self.ALLOWED_VALUES_FOR_DATE)
        
        # Ahora sí sacamos los datos
        df = extractor.extract_data_from_file(
            index_value=self.INDEX_VALUE,
            cols_to_extract=self.COLS_TO_EXTRACT,
            shift_between_values=self.SHIFT_BETWEEN_VALUES
        )
        # Tiramos los skus que sean 0
        df = df.query(f'{self.INDEX_VALUE} != 0')
        
        # Homologamos los datos
        rename_dict = {llave:valor for llave, valor in zip([self.INDEX_VALUE] + self.COLS_TO_EXTRACT, self.OUTPUT_COLUMN_NAMES)}
        cols_to_add = {'fecha':fecha, 'tipo':self.TIPO_ARCHIVO}
        df = self.funciones_auxiliares.homologar_df(df, rename_columns_dict=rename_dict, cols_to_add=cols_to_add)
        self.extract_data = df

    def valida_datos(self) -> pd.DataFrame:
        '''
        Ahora hacemos las validaciones necesarias.
        1. Convertir a números lo fabricado y programado
        2. Hacer el match de los sku con los del catálogo
        '''
        assert self.extract_data is not None, "Aún no se han limpiado los datos"
        cols = ['fabricado', 'programado']
        catalogo = self.catalogo
        
        my_df = self.extract_data
        for col in cols:
            my_df[col] = pd.to_numeric(my_df[col], errors='coerce')
        
        df_sin_nan = my_df.dropna(subset=cols, how='any')
        bad_production_data = my_df[my_df[cols].isna().any(axis=1)].sku
        
        # Ahora, para los productos que sí tienen números en lo producido y fabricado
        # nos aseguramos de que los skus estén en el catálogo existente. Si no están,
        # no los queremos.
        df_skus_bien = df_sin_nan.merge(catalogo, on='sku', how='left').dropna(subset=['familia']).reset_index(drop=True)
        bad_sku_codes = df_sin_nan.merge(catalogo, on='sku', how='left').pipe(lambda df: df[df.familia.isna()]).sku
        
        df_reporte_errores = (
            pd.concat((pd.DataFrame(bad_production_data).assign(error='cantidades'),
                    pd.DataFrame(bad_sku_codes).assign(error='sku invalido')), 
                    ignore_index=True)
        )
        
        self.good_data, self.bad_data =  (df_skus_bien, df_reporte_errores)

    def save_data(self):
        '''
        Esta función guarda los datos limpios en donde se especifique
        '''
        assert self.good_data is not None, "Aún no se han limpiado los datos"
        self.funciones_auxiliares.save_data(self.good_data, location=self.clean_data_file, type_of_file=self.type_of_file, drop_duplicates=True)

    def extract_and_save_data(self, file):
        '''
        Esta función extrae los datos, los valida y los guarda.
        '''
        self.extract_data(file)
        self.valida_datos()
        self.save_data()

class LermaCleaner:
    '''
    Esta funciona para limpiar todo lo de lerma
    '''
    def __init__(self, catalogo_file:str, clean_data_file:str, type_of_file:str='parquet') -> None:
        '''
        catalogo_file: ubicación del archivo que se usa como catálogo de los productos. Tiene las columnas sku, descripcion, familia, marca
        '''
        self.catalogo = pd.read_excel(catalogo_file)
        self.funciones_auxiliares = AuxiliarFunctions()
        self.clean_data_file = clean_data_file
        self.type_of_file = type_of_file

        self.INDEX_VALUE = 'Clave'
        self.COLS_TO_EXTRACT = ['Programado por \nsemana', 'Producido']
        self.OUTPUT_COLUMN_NAMES = ['sku', 'fabricado', 'programado']
        self.TIPO_ARCHIVO = 'lerma'
        self.SHIFT_BETWEEN_VALUES = 0
        self.SHEET_NAME = 0
        self.ALLOWED_VALUES_FOR_DATE = ['Fecha', 'fecha', 'fecha:', 'Fecha:']

    def extract_data(
            self,
            file
        ):
        '''
        Esta función limpia el archivo de polvos si el template es el adecuado
        ''' 
        # Cargamos el archivo en un extractor
        extractor = DataExtraction(file, sheet_name=self.SHEET_NAME)
        
        # Buscamos la fecha en el archivo
        fecha = self.funciones_auxiliares.encuentra_fecha(extractor=extractor, allowed_values=self.ALLOWED_VALUES_FOR_DATE)
        
        # Ahora sí sacamos los datos
        df = extractor.extract_data_from_file(
            index_value=self.INDEX_VALUE,
            cols_to_extract=self.COLS_TO_EXTRACT,
            shift_between_values=self.SHIFT_BETWEEN_VALUES
        )
        # Tiramos los skus que sean 0
        df = df.query(f'{self.INDEX_VALUE} != 0')
        
        # Homologamos los datos
        rename_dict = {llave:valor for llave, valor in zip([self.INDEX_VALUE] + self.COLS_TO_EXTRACT, self.OUTPUT_COLUMN_NAMES)}
        cols_to_add = {'fecha':fecha, 'tipo':self.TIPO_ARCHIVO}
        df = self.funciones_auxiliares.homologar_df(df, rename_columns_dict=rename_dict, cols_to_add=cols_to_add)
        self.extract_data = df

    def valida_datos(self) -> pd.DataFrame:
        '''
        Ahora hacemos las validaciones necesarias.
        1. Convertir a números lo fabricado y programado
        2. Hacer el match de los sku con los del catálogo
        '''
        assert self.extract_data is not None, "Aún no se han limpiado los datos"
        cols = ['fabricado', 'programado']
        catalogo = self.catalogo
        
        my_df = self.extract_data
        for col in cols:
            my_df[col] = pd.to_numeric(my_df[col], errors='coerce')
        
        df_sin_nan = my_df.dropna(subset=cols, how='any')
        bad_production_data = my_df[my_df[cols].isna().any(axis=1)].sku
        
        # Ahora, para los productos que sí tienen números en lo producido y fabricado
        # nos aseguramos de que los skus estén en el catálogo existente. Si no están,
        # no los queremos.
        df_skus_bien = df_sin_nan.merge(catalogo, on='sku', how='left').dropna(subset=['familia']).reset_index(drop=True)
        bad_sku_codes = df_sin_nan.merge(catalogo, on='sku', how='left').pipe(lambda df: df[df.familia.isna()]).sku
        
        df_reporte_errores = (
            pd.concat((pd.DataFrame(bad_production_data).assign(error='cantidades'),
                    pd.DataFrame(bad_sku_codes).assign(error='sku invalido')), 
                    ignore_index=True)
        )
        
        self.good_data, self.bad_data =  (df_skus_bien, df_reporte_errores)

    def save_data(self):
        '''
        Esta función guarda los datos limpios en donde se especifique
        '''
        assert self.good_data is not None, "Aún no se han limpiado los datos"
        self.funciones_auxiliares.save_data(self.good_data, location=self.clean_data_file, type_of_file=self.type_of_file, drop_duplicates=True)

    def extract_and_save_data(self, file):
        '''
        Esta función extrae los datos, los valida y los guarda.
        '''
        self.extract_data(file)
        self.valida_datos()
        self.save_data()


if __name__ == '__main__':
    print('Running clean_production_files.py as main. This is not adviced.')