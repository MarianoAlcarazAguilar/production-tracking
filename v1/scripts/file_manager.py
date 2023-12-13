import os
import numpy as np
from scripts.file_cleaner import FileCleaner

class FileManager:
    def get_files_on_directory(self, dir_location: str, type_of_files=[]) -> list:
        if dir_location is None:
            print('No se ha especificado ningún directorio')
            return None
        
        if len(type_of_files) == 0: # Si no dan una lista, se toman por defecto los archivos de excel y csv
            type_of_files = [".xlsx", ".xlsm", ".xlsb", ".xltx", ".xltm", ".xls", ".xlt", ".xlam", ".xlw", ".csv"]

        lista_archivos = [archivo for archivo in os.listdir(dir_location) if any(archivo.endswith(terminacion) for terminacion in type_of_files)]
        lista_archivos = [elemento for elemento in lista_archivos if not elemento.startswith("~$")]

        lista_archivos = np.sort(np.array(lista_archivos))
        return lista_archivos
    
    def download_file(self, file_location: str):
        '''
        file_location debe incluir el nombre del archivo junto con la extensión
        '''
        try:
            file_name = file_location.split('/')[-1]
        except:
            print('No se pudo extraer el nombre del archivo')
            return None, None
        try:
            with open(file_location, 'rb') as f:
                bytes_data = f.read()
            return bytes_data, file_name
        except:
            print(f'The file does not exist: {file_location}')
            return None, None
        
    def save_file(self, file, directory: str):
        existing_files = os.listdir(f'{directory}')
        
        filename = FileCleaner().eliminar_parentesis_duplicados(file.name)
        

        # Nos aseguramos de que el archivo no exista ya
        if filename in existing_files:
            return False
        
        with open(f'{directory}/{filename}', 'wb') as f:
            f.write(file.getbuffer())

        return True
    