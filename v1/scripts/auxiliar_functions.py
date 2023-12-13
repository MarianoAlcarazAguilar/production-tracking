import datetime

def cast_to_booleans(lista):
    todos = 'Todos' in lista
    liquidos = 'Líquidos' in lista
    polvos = 'Polvos' in lista
    resp = {'todos':todos, 'liquidos':liquidos, 'polvos':polvos}
    return resp

def get_colors_for_ciruclar_kpi(lista):
    if 'Todos' in lista:
        return ['#ade8f4', '#023e8a']
    if 'Líquidos' in lista:
        return ['#ffea00', '#ff7b00']
    else:
        return ['#92e6a7', '#155d27']
    
def get_corresponding_mean(df, lista):
    if 'Todos' in lista:
        return df.completado.mean()
    if 'Líquidos' in lista and 'Polvos' in lista:
        return df.completado.mean()
    if 'Líquidos' in lista:
        return df.liquidos.mean()
    return df.polvos.mean() 
    
def retroceder_semanas(fecha, semanas):
    # Calcular el número total de días a retroceder
    dias_retroceso = semanas * 7

    # Restar los días al objeto date
    fecha_retrocedida = fecha - datetime.timedelta(days=dias_retroceso) + datetime.timedelta(days=7)

    return fecha_retrocedida

def encontrar_fecha_mas_grande(diccionario:dict):
    # Inicializamos una variable para almacenar la fecha más grande
    fecha_mas_grande = None

    for fecha_str in diccionario.values():
        # Convertir la fecha del formato 'dd-mm-yyyy' a un objeto datetime
        fecha_obj = datetime.datetime.strptime(fecha_str, '%d-%m-%Y')

        # Comprobar si esta fecha es la más grande hasta ahora
        if fecha_mas_grande is None or fecha_obj > fecha_mas_grande:
            fecha_mas_grande = fecha_obj

    # Convertir la fecha más grande a un timestamp
    timestamp_fecha_mas_grande = fecha_mas_grande.timestamp()

    return timestamp_fecha_mas_grande

if __name__ == '__main__':
    print('Executing auxiliar_functions.py')