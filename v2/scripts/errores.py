class FechaNoEsLunes(Exception):
    def __init__(self, fecha):
        super().__init__(f"La fecha {fecha} no es un lunes")

class FechaNoEncontrada(Exception):
    def __init__(self, opciones_de_fecha):
        super().__init__(f"No se encontró la fecha. Debe estar arriba o abajo de '{opciones_de_fecha}'")

class ArchivoNoPermitido(Exception):
    def __init__(self, tipo_de_archivo):
        super().__init__(f'Tipo de archivo no soportado: {tipo_de_archivo}')

class ColumnasNoCoinciden(Exception):
    def __init__(self, columnas_1, columnas_2) -> None:
        super().__init__(f'Las columnas no coinciden: {columnas_1} y {columnas_2}')