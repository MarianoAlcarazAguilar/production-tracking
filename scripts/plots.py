import warnings
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
from numpy import sin, cos, pi
import plotly.subplots as sp
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.tools import mpl_to_plotly

# Quito unas warnings muy molestas
warnings.filterwarnings('ignore', category=UserWarning)

def generate_color_list(color1, color2, n, semanas):
    color_list = [color1] * n
    color_list[-semanas:] = [color2] * semanas
    return color_list

def hex_to_RGB(hex_str):
    """ #FFFFFF -> [255,255,255]"""
    #Pass 16 to the integer function for change of base
    return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]

def degree_to_radian(degrees):
    return degrees*pi/180

def convertir_a_grados(numero):
    if numero < 0 or numero > 100:
        raise ValueError("El número debe estar entre 0 y 100")
    
    grados = ((100 - numero) / 100) * 360 - 180
    
    return grados

def obtener_posicion(lista, porcentaje):
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100")
    
    cantidad_posiciones = len(lista)
    if porcentaje == 100:
        indice = -1
    elif porcentaje == 0:
        indice = 0
    else:
        indice = int(porcentaje / 100 * cantidad_posiciones)
    
    return lista[indice]

def get_color_gradient(c1, c2, n):
    """
    Given two hex colors, returns a color gradient
    with n colors.
    """
    assert n > 1
    c1_rgb = np.array(hex_to_RGB(c1))/255
    c2_rgb = np.array(hex_to_RGB(c2))/255
    mix_pcts = [x/(n-1) for x in range(n)]
    rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
    return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]

def verificar_booleans(a, b, c):
    booleans = [a, b, c]
    true_count = booleans.count(True)
    return true_count >= 2


class Plotter:
    def __init__(self):
        self.data = self.load_data()
        self.completed = None
        self.range_data = None # esta es la data que se utiliza para trabajar cuando se necestien rangos de fechas específicos
        self.completed_range_data = None
        self.catalogo_dragon = self.load_catalogo()

        self.process_completed_products()
        self.update_range_data()

    def get_data(self):
        return self.data
    
    def get_completed(self):
        if self.completed is None:
            self.process_completed_products()
        return self.completed

    def load_data(self):
        data = (pd
        .read_csv('data/data_for_qlik.csv')
        .assign(
            inicio_semana=lambda x: pd.to_datetime(x.inicio_semana, dayfirst=True),
            inicio_semana_real=lambda x: pd.to_datetime(x.inicio_semana_real, dayfirst=True),
            int_skus_cleaned=lambda df: np.nan_to_num(pd.to_numeric(df.sku, errors='coerce'), nan=0).astype('int'),
            int_skus=lambda df: df.int_skus_cleaned.replace(0, None),
            sku=lambda df: df.int_skus.fillna(df.sku)
        )
        .drop(columns=['int_skus_cleaned'])
        )
        return data

    def load_catalogo(self):
        catalogo = pd.read_excel('data/catalogo_productos.xlsx')
        return catalogo

    def get_unique_skus_in_time(self, fecha_inicio, fecha_fin):
        data = self.data
        catalogo_productos = self.catalogo_dragon
        fecha_inicio, fecha_fin = pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin)

        datos_filtrados_tiempo = data[(data.inicio_semana_real >= fecha_inicio) & (data.inicio_semana_real <= fecha_fin)]
        skus_dragon = catalogo_productos.Sku.unique()

        unique_skus_dragon = (datos_filtrados_tiempo
         [datos_filtrados_tiempo.sku.isin(skus_dragon)]
         .sku
         .unique()
        )
        unique_skus_externos = (datos_filtrados_tiempo
         [~datos_filtrados_tiempo.sku.isin(skus_dragon)]
         .sku
         .unique()
        )
        return unique_skus_dragon, unique_skus_externos

    def update_range_data(self, fecha_inicio=None, fecha_fin=None):
        data = self.data
        min_date, max_date = self.get_date_ranges()
        if fecha_inicio is None:
            fecha_inicio = min_date
        if fecha_fin is None:
            fecha_fin = max_date
        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin)
        self.range_data = data[(data.inicio_semana_real >= fecha_inicio) & (data.inicio_semana_real <= fecha_fin)]
        self.process_completed_products(data=self.range_data, all_data=False)

    def get_date_ranges(self):
        data = self.data
        fecha_min = data.inicio_semana_real.min().date()
        fecha_max = data.inicio_semana_real.max().date()
        return (fecha_min, fecha_max)

    def process_completed_products(self, data=None, all_data=True):
        '''
        Esta función carga los datos necesarios para los datos completados
        Antes era None, pero aquí se actualizan
        '''
        if data is None:
            data = self.data
        # Encontramos los porcentajes por tipo de datos (LÍQUIDOS o POLVOS)
        completados_por_tipo = (data
         .groupby(['tipo', 'inicio_semana_real'])
         .agg(porcentaje=pd.NamedAgg('terminado', np.mean))
         .reset_index()
         .pivot(index=['inicio_semana_real'], columns='tipo', values='porcentaje')
         .rename(columns={'LIQUIDOS':'liquidos', 'POLVOS':'polvos'})
        )
        # La primera gráfica de la que me acuerdo es la siguiente:
        # Se tiene una línea que me va diciendo la semana correspondiente y el porcentaje de completados de esa fecha
        completados = (data
         # Encontramos cuántos productos están terminados en cada semana
         .assign(completado=lambda df: df.groupby(['semana', 'anio']).terminado.transform(np.mean))
         # Agregamos tick para las gráficas
         .assign(tick=lambda x: x.semana.astype(str) + '-' + x.anio.astype(str))
         .drop_duplicates(subset=['semana', 'anio'], keep='first')
         .set_index('inicio_semana_real')
         .sort_index()
         [['completado', 'tick']]
         .merge(completados_por_tipo, left_index=True, right_index=True)
        )
        if all_data:
            self.completed = completados
        else:
            self.completed_range_data = completados

    def get_total_products_and_change(self, todos=True, liquidos=False, polvos=False):
        #data = self.data
        data = self.range_data
        ultima_semana = data.inicio_semana_real.max()
        # Filtramos solo los datos que se nos han solicitado
        if liquidos and not polvos and not todos: # si solamente me piden liquidos
            data = data.query('tipo == "LIQUIDOS"')
        elif polvos and not liquidos and not todos: # si solamente me piden polvos
            data = data.query('tipo == "POLVOS"')
        total_productos = data.shape[0]
        productos_ultima_semana = data[data.inicio_semana_real == ultima_semana].shape[0]
        return (f'{total_productos}', f'{productos_ultima_semana}')
    
    def get_cumplimiento_ultima_semana(self, todos=True, liquidos=False, polvos=False):
        data = self.data
        ultima_semana = data.inicio_semana_real.max()
        # Filtramos solo los datos que se nos han solicitado
        if liquidos and not polvos and not todos: # si solamente me piden liquidos
            data = data.query('tipo == "LIQUIDOS"')
        elif polvos and not liquidos and not todos: # si solamente me piden polvos
            data = data.query('tipo == "POLVOS"')
        
        cumplimiento_ultima_semana = data[data.inicio_semana_real == ultima_semana].terminado.mean()
        if cumplimiento_ultima_semana is not np.nan:
            cumplimiento_medio = data.terminado.mean() # este es el cumplimiento medio del tipo de producto pedido
            cambio = np.round(cumplimiento_ultima_semana - cumplimiento_medio, 3)*100
            cumplimiento_ultima_semana = np.round(cumplimiento_ultima_semana, 3)*100
        else:
            cumplimiento_ultima_semana = ''
            cambio = ''
        return (f'{cumplimiento_ultima_semana}%', f'{cambio}%')

    def plot_historical_line_chart(self, focus_dates, todos=True, liquidos=False, polvos=False):
        '''
        Esta función regresa una fig de plotly.
        Dependiendo de lo especificado, se grafican las líneas necesarias
        '''
        if self.completed is None:
            self.process_completed_products()
        data_plotly = self.completed
        show_legend = verificar_booleans(todos, liquidos, polvos)

        marker_size_tipos = 5
        color_linea = '#0077b6'
        color_linea_liquidos = '#fb8500'
        color_linea_polvos = '#70e000'
        colores_puntos = ['#ade8f4', '#0077b6']
        colores_puntos_liquidos = ['#ffdd00', '#fb8500']
        colores_puntos_polvos = ['#70e000', '#70e000']
        spines_color = '#415a77'

        fig = go.Figure()
            
        if liquidos:
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.liquidos,
                    mode='lines',
                    name='',
                    opacity=.6,
                    line=dict(
                        color=color_linea_liquidos,
                        width=2,
                        dash='solid'
                    )
                )
            )

            # Agregamos los marcadores
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.liquidos,
                    mode='markers',
                    name='Líquidos',
                    hovertemplate='%{x|%d/%m/%Y}<br>%{y:.0%}<extra></extra>',
                    marker=dict(
                        color=get_color_gradient(
                            colores_puntos_liquidos[0], 
                            colores_puntos_liquidos[1], 
                            data_plotly.index.size
                        ),
                        size=marker_size_tipos,
                        symbol='circle',
                        line=dict(
                            color=color_linea_liquidos,
                            width=0
                        )
                    )
                )
            )
            
        if polvos:
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.polvos,
                    mode='lines',
                    name='',
                    opacity=.6,
                    line=dict(
                        color=color_linea_polvos,
                        width=2,
                        dash='solid'
                    )
                )
            )

            # Agregamos los marcadores
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.polvos,
                    mode='markers',
                    name='Polvos',
                    hovertemplate='%{x|%d/%m/%Y}<br>%{y:.0%}<extra></extra>',
                    marker=dict(
                        color=get_color_gradient(
                            colores_puntos_polvos[0], 
                            colores_puntos_polvos[1], 
                            data_plotly.index.size
                        ),
                        size=marker_size_tipos,
                        symbol='circle',
                        line=dict(
                            color=color_linea_polvos,
                            width=1.5
                        )
                    )
                )
            )
            
        if todos:
            # Agregamos la línea principal
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.completado,
                    mode='lines',
                    name='',
                    opacity=.6,
                    line=dict(
                        color=color_linea,
                        width=2,
                        dash='solid'
                    )
                )
            )

            # Agregamos los marcadores
            fig.add_trace(
                go.Scatter(
                    x=data_plotly.index,
                    y=data_plotly.completado,
                    mode='markers',
                    name='Todos',
                    hovertemplate='%{x|%d/%m/%Y}<br>%{y:.0%}<extra></extra>',
                    marker=dict(
                        color=get_color_gradient(colores_puntos[0], colores_puntos[1], data_plotly.index.size),
                        size=marker_size_tipos*1.3,
                        symbol='circle',
                        line=dict(
                            color=color_linea,
                            width=0
                        )
                    )
                )
            )
            
        # Personalizamos diseño de la gráfica
        fig.update_layout(
            title='Histórico de Productos Terminados',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=show_legend,
            dragmode='pan',
            font=dict(
                color='#454955'
            ),
            legend=dict(
                title='Leyenda',
                bgcolor='rgba(0,0,0,0)'
            ),
            xaxis=dict(
                title='Semana-Año',
                tickmode='array',
                tickvals=data_plotly.index,
                ticktext=data_plotly.tick,
                tickangle=270,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color=spines_color
                ),
                showgrid=False,
                linecolor=spines_color,
                linewidth=2,
                #range=[focus_dates[0], focus_dates[1]],
                #type='date'
            ),
            yaxis=dict(
                fixedrange=True,
                title='Porcentaje (%)',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color=spines_color
                ),
                gridcolor='rgba(94,84,142,.1)'
            ),
            width=870,
            height=450
        )
        return fig
    
    def plot_circular_kpi(self, porcentaje, degree_start=180, r=1.0, padding=0.2, tick_length=0.02, colors = ['#ade8f4', '#023e8a'], size=300):
        if porcentaje < 1:
            porcentaje = porcentaje*100
        degree_end = convertir_a_grados(porcentaje)
        annotation_text = f'{np.round(porcentaje, 1)}%'
        radian_start, radian_end =  degree_to_radian(degree_start), degree_to_radian(degree_end)
        theta = np.linspace(radian_start,radian_end,5000)
        x = r * cos(theta)
        y = r * sin(theta)

        # Generamos los colores y tomamos el primero y el último correspondiente al porcentaje
        full_palette = get_color_gradient(colors[0], colors[1], x.size)
        final_color = obtener_posicion(full_palette, porcentaje)
        
        
        fig = go.Figure()

        # draw the bar
        fig.add_trace(go.Scatter(
            x=x, 
            y=y, 
            mode='markers', 
            marker_symbol='circle', 
            marker_size=30, 
            hoverinfo='skip', 
            marker_color=get_color_gradient(
                colors[0], 
                final_color, 
                x.size
            )
        ))
        
        # draw the outer border
        for r_outer in [r-padding,r+padding]:
            fig.add_shape(
                type="circle",
                xref="x", 
                yref="y",
                x0=-r_outer, 
                y0=-r_outer, 
                x1=r_outer, 
                y1=r_outer,
                line_color="rgba(0,0,0,0)",
            )

        n_ticks = 5
        tick_theta = np.linspace(pi,-pi,n_ticks+1)
        tick_labels = np.linspace(0,80,n_ticks)
        tick_start_x, tick_end_x = (r+padding)*cos(tick_theta), (r+padding+tick_length)*cos(tick_theta)
        tick_start_y, tick_end_y = (r+padding)*sin(tick_theta), (r+padding+tick_length)*sin(tick_theta)
        tick_label_x, tick_label_y = (r+padding+0.04+tick_length)*cos(tick_theta), (r+padding+0.04+tick_length)*sin(tick_theta)

        # add ticks
        for i in range(len(tick_theta)):
            fig.add_trace(go.Scatter(
                x=[tick_start_x[i], tick_end_x[i]],
                y=[tick_start_y[i], tick_end_y[i]],
                mode='text+lines',
                marker=dict(color="rgb(147, 151, 153)"),
                hoverinfo='skip'
            ))
        
        # add ticklabels
        fig.add_trace(go.Scatter(
            x=tick_label_x,
            y=tick_label_y,
            text=tick_labels,
            mode='text',
            hoverinfo='skip'
        ))

        ## add text in the center of the plot
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode="text",
            text=[annotation_text],
            textfont=dict(size=30),
            textposition="middle center",
            hoverinfo='skip'
        ))

        ## get rid of axes, ticks, background
        fig.update_layout(
            title='Productos Terminados',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis_range=[-.7,.7], 
            yaxis_range=[-.7,.7], 
            xaxis_visible=False,
            yaxis_visible=False, 
            xaxis_showticklabels=False, 
            yaxis_showticklabels=False,
            width=size*.65, 
            height=size,
            dragmode=False
        )
        return fig  
    
    def plot_bar_chart_categories(self):
        data = self.completed_range_data
        datos_barras = data.drop(columns=['tick']).rename(columns={'completado':'todos'}).mean()

        categorias = np.char.capitalize(datos_barras.index.values.astype(str))
        valores = np.round(datos_barras.values*100, 1)
        colores = ['#4e8ab9', '#ffac00', '#7dd181']
        colores = get_color_gradient('#014f86', '#a9d6e5', 3)

        fig = go.Figure()

        for categoria, valor, color in zip(categorias, valores, colores):
            fig.add_trace(go.Bar(
                x=[valor],
                y=[categoria],
                name='',
                orientation='h',
                marker=dict(
                    color=color,
                    line=dict(
                        color='rgba(0, 0, 0, 0)', 
                        width=0
                    ),  # Oculta los bordes por defecto
                    line_width=2,  # Ancho de los bordes redondeados
                    line_color=color  # Color de los bordes redondeados
                ),
                hovertemplate='%{x}%',
                textposition='auto',
                textfont=dict(color='white'),
                text=[f'{valor}%'],
                showlegend=False
            ))
            
        # Configuración del diseño
        fig.update_layout(
            title='Cumplimiento por Tipo de Producto',
            xaxis=dict(
                title='Porcentaje (%)'
            ),
            yaxis=dict(
                title=''
            ),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=.05,
            font=dict(color='#454955'),
            annotations=[
                dict(
                    text='Porcentaje de productos terminados en el tiempo especificado por tipo de producto',
                    xref='paper',
                    yref='paper',
                    x=.95,
                    y=1.1,
                    showarrow=False,
                    font=dict(size=11, color='gray'),
                )
            ],
            height=400,
            margin=dict(l=50, r=50, t=95, b=50),
            dragmode=False
        )
        return fig
    
    def plot_bar_chart_families(self):
        data = self.range_data
        data_familias = (data
        .groupby(['familia'])
        .agg(
            porcentaje=pd.NamedAgg('terminado', np.mean),
            n_prods=pd.NamedAgg('terminado', 'count')
        )
        .sort_values('porcentaje', ascending=True)
        .reset_index()
        )


        color_hex = ['#bee3db', '#555b6e']
        categorias = np.char.capitalize(data_familias.familia.values.astype(str))
        n_prods = data_familias.n_prods.values
        valores = np.round(data_familias.porcentaje.values*100, 1)
        colores = get_color_gradient(*color_hex, valores.size)
        posiciones = np.arange(valores.size)

        fig = go.Figure()

        for posicion, categoria, valor, color, n_prod in zip(posiciones, categorias, valores, colores, n_prods):
            fig.add_trace(go.Bar(
                y=[posicion],
                x=[valor],
                name=categoria,
                orientation='h',
                marker=dict(
                    color=color
                ),
                hovertemplate='Porcentaje: %{x}%<br>Total Prouctos: '+f'{n_prod}',
                showlegend=False
            ))
            
        fig.update_layout(
            title='Cumplimento por Familia',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=.05,
            font_color='#454955',
            annotations=[
                dict(
                    text='Porcentaje de productos terminados por <b>tipo de familia</b>',
                    xref='paper',
                    yref='paper',
                    x=.95,
                    y=1.1,
                    showarrow=False,
                    font=dict(
                        size=11,
                        color='gray'
                    ),
                )
            ],
            yaxis=dict(
                tickmode='array',
                tickvals=posiciones,
                ticktext=categorias,
                range=[posiciones[0]-.5,posiciones[-1]+.5]
            ),
            xaxis=dict(
                title='Porcentaje (%)',
                fixedrange=True
            ),
            dragmode=False,
            height=400,
            width=500,
            margin=dict(l=50, r=50, t=95, b=50),
        )
            
        return fig
    
    def plot_first_grid(self, num_semanas, total_prods_dragon, total_prods_externo, pixel_size=1000, height=350):
        '''
        Esta función recibe los datos necesarios, el número de semanas y los totales de sku's.
        Genera una figura de plotly y la regresa.
        '''
        # NO OLVIDAR CAMBIAR df por datos completados en el plotter
        df = self.completed
        # Revisamos que los datos sean adecuados
        if num_semanas <= 1:
            num_semanas = 1
        
        # Definimos las variables internas de la función
        color_hex = ['#8ac926', '#008000']
        color_barra_100 = '#e9ecef'
        text_color = '#6c757d'
        spines_color = 'rgba(1,1,1,0)'
        width_overall = .7
        
        # Extraemos los datos a partir de las variables que nos dieron
        fecha_x = df.index
        valor_y = df.completado
        colores = generate_color_list( # Generamos los colores, tomando el número de semanas dado
            color_hex[0], 
            color_hex[1], 
            fecha_x.size, 
            num_semanas
        )
        media_tiempo_seleccionado = (df # Tomamos la media de productos terminados en el número de semanas dado
        .tail(num_semanas)
        .completado
        .mean()
        ) 
        
        # Definimos la forma del grid para las gráficas
        specs = [
            [{'rowspan':3, 'colspan':2}, None, {'rowspan':2, 'type':'indicator'}, {'rowspan':2, 'type':'indicator'}],
            [None, None, None, None],
            [None, None, {'colspan':2}, None]
        ]
        
        fig = make_subplots(
            rows=3,
            cols=4,
            specs=specs,
            column_widths=[0.35, 0.35, 0.15, 0.15],
            horizontal_spacing=0.05,
            vertical_spacing=0.2,
            subplot_titles=[None, None, None, '<b>Overall</b>']
        )

        # Subplot de la gráfica de barras. Posición (1,1)
        for fecha, valor, color in zip(fecha_x, valor_y, colores):
            fig.add_trace(row=1, col=1, trace=go.Bar(
                x=[fecha],
                y=[valor],
                name='',
                hovertemplate=f'Fecha: {fecha.strftime("%d/%m/%Y")}<br>Porcentaje: {np.round(valor*100, 1)}%',
                marker=dict(
                    color=color,
                    line_width=0,
                    line_color=color
                )
            ))
            
        # Subplot de la barra de cumplimiento en el tiempo seleccionado. Posición (3,3)
        fig.add_trace(row=3, col=3, trace=go.Bar(
            y=['A'],
            x=[media_tiempo_seleccionado],
            orientation='h',
            width=width_overall,
            name='',
            marker=dict(color=colores[-1],line_width=0),
            hovertemplate=f'{np.round(media_tiempo_seleccionado*100, 2)}%',
            text=[f'{int(media_tiempo_seleccionado*100)}%'],
            textangle=0,
            textfont={'size':17}
        ))
        fig.add_trace(row=3, col=3, trace=go.Bar(
            y=['A'],
            x=[1-media_tiempo_seleccionado],
            width=width_overall,
            orientation='h',
            name='',
            marker=dict(color=color_barra_100,line_width=0),
            hovertemplate=f'100%'
        ))

        # Subplot de número de productos Dragón. Posición (1,3)
        fig.add_trace(row=1, col=3, trace=go.Indicator(
            title='Dragón',
            number={'font': {'color': '#55a630'}},
            mode='number',
            value=total_prods_dragon,
            domain=dict(
                x=[0,1],
                y=[0,1]
            )
        ))
        
        # Subplot de número de productos de externos. Posición (1,4)
        fig.add_trace(row=1, col=4, trace=go.Indicator(
            title='Externos',
            mode='number',
            number={'font': {'color':'#168aad'}},
            value=total_prods_externo,
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(
            title=dict(
                text='Histórico de Cumplimiento',
                font_size=20
            ),
            paper_bgcolor='rgba(152, 193, 217, 0)',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            font_color='#454955',
            barmode='stack',
            dragmode='pan',
            showlegend=False,
            bargap=0.1,
            width=pixel_size,
            height=height,
            margin=dict(l=50, r=50, t=30, b=50),
            font=dict(family='Trebuchet MS', color=text_color),
            yaxis=dict(title='Porcentaje (%)', fixedrange=True, linecolor=spines_color, linewidth=2),
            xaxis=dict(title=None, linecolor=spines_color, linewidth=2, tickfont=dict(family='Trebuchet MS', size=12, color=colores[-1])),
            yaxis2=dict(tickmode='array', tickvals=['A'], ticktext=[''], fixedrange=True),
            xaxis2=dict(tickmode='array', tickvals=[.5], ticktext=[''], fixedrange=True)
        )
        
        return fig

    def plot_second_grid(self, chosen_skus, num_semanas, pixel_size=1000, height=130, fecha_inicio=None, fecha_fin=None):
        if len(chosen_skus) == 1:
            height = 150
        df = self.data # Estos son los datos sin procesar. Todo lo necesario se hace en la función
        min_date, max_date = self.get_date_ranges()
        light_colors = ["#a8dadc","#c9e4ca","#cfe1b9","#d5d0cd"]
        dark_colors = ['#457b9d', '#55828b', '#97a97c', '#9a998c']
        rows = [i+1 for i in range(len(chosen_skus))]

        y_axis_dicts = {f'yaxis{i*2+1}':{'title':chosen_skus[i], 
                                        'fixedrange':True,
                                        'gridcolor':'rgba(94,84,142,.2)'} 
                        for i in range(len(chosen_skus))}
        x_axis_dicts = {f'xaxis{i*2+1}':{'fixedrange':True,
                                        'range':[min_date-datetime.timedelta(days=4), max_date+datetime.timedelta(days=4)],
                                        'type':'date',
                                        'gridcolor':'rgba(94,84,142,.2)'} 
                        for i in range(len(chosen_skus))}
        y_axis_dicts_overall = {f'yaxis{i*2+2}':{'fixedrange':True} for i in range(len(chosen_skus))}
        

        width_overall = .5
        color_barra_gris = '#e9ecef'
        text_color = '#6c757d'

        data_lineas_prods = (df
        [df.sku.isin(chosen_skus)]
        .pivot_table(index='inicio_semana_real', columns='sku', values='porcentaje', aggfunc=np.mean)
        .sort_index()
        )

        fecha_inicio, fecha_fin = pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin)
        data_lineas_prods_semanas_seleccionadas = (data_lineas_prods
            [(data_lineas_prods.index >= fecha_inicio) & (data_lineas_prods.index <= fecha_fin)]
        )
        max_mean = data_lineas_prods_semanas_seleccionadas.mean().max() if data_lineas_prods_semanas_seleccionadas.mean().max() >= 1 else 1
        x_axis_dicts_overall = {f'xaxis{i*2+2}':{'fixedrange':True, 'showticklabels':False, 'range':[0,max_mean]} for i in range(len(chosen_skus))}

        fig = sp.make_subplots(
            cols=2,
            rows=len(chosen_skus),
            column_widths=[.7, .3],
            shared_xaxes=True,
            shared_yaxes=True,
            vertical_spacing=0.05,
            horizontal_spacing=0.07
        )

        for row, sku, light_color, dark_color in zip(rows, chosen_skus, light_colors, dark_colors):
            total_dark_bars = data_lineas_prods_semanas_seleccionadas[sku].dropna().size
            mean_sku = data_lineas_prods_semanas_seleccionadas[sku].mean()
            if mean_sku is np.nan:
                mean_sku = 0
            # Generamos los colores para cada una
            colores_barras = generate_color_list(light_color, dark_color, data_lineas_prods.index.size, total_dark_bars)

            fig.add_trace(row=row, col=1, trace=go.Bar(
                x=data_lineas_prods.index,
                y=data_lineas_prods[sku],
                name=sku,
                hovertemplate='%{x|%d/%m/%Y}<br>%{y:.0%}<extra></extra>',
                marker=dict(
                    color=colores_barras,
                    line_width=0
                )
            ))
            fig.add_trace(row=row, col=2, trace=go.Bar(
                y=[sku],
                x=[mean_sku],
                orientation='h',
                width=width_overall,
                name='',
                marker=dict(color=dark_color,line_width=0),
                hovertemplate=f'{np.round(mean_sku*100, 2)}%',
                text=[f'{int(mean_sku*100)}%'],
                textangle=0,
                textfont={'size':14, 'color':'white'}
            ))
            fig.add_trace(row=row, col=2, trace=go.Bar(
                y=[sku],
                x=[max_mean-mean_sku],
                width=width_overall,
                orientation='h',
                name='',
                marker=dict(color=color_barra_gris,line_width=0),
                hovertemplate=f'{np.round(max_mean*100, 0)}%'
            ))

        fig.update_layout(
            title='Cumplimiento Por Producto',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            barmode='stack',
            font_color='#454955',
            dragmode='pan',
            bargap=0.1,
            width=pixel_size,
            height=height*len(chosen_skus),
            margin=dict(l=50, r=50, t=30, b=30),
            font=dict(family='Trebuchet MS', color=text_color),
            **x_axis_dicts,
            **y_axis_dicts,
            **y_axis_dicts_overall,
            **x_axis_dicts_overall
        )
        return fig


if __name__ == '__main__':
    plotter = Plotter()
    line_chart_historical_data = plotter.plot_historical_line_chart(todos=True, liquidos=True, polvos=True)
    