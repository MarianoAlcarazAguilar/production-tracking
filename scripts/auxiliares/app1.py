import streamlit as st
import datetime
from scripts.plots import Plotter
from scripts import auxiliar_functions

def main():
    plotter = Plotter()
    st.set_page_config(layout='wide', initial_sidebar_state='expanded')

    with open('style.css') as f:
        # Cargamos el estilo de css (estoy utilizando uno de internet)
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # ---------------- SIDEBAR --------------------------------
    st.sidebar.header('')
    categorias = st.sidebar.multiselect("Categorías", ['Todos', 'Líquidos', 'Polvos'])
    fecha_min, fecha_max = plotter.get_date_ranges()
    selected_dates = st.sidebar.date_input(
        label='Selecciona un rango de fechas',
        value=(auxiliar_functions.retroceder_semanas(fecha_max, 20), fecha_max),
        min_value=fecha_min,
        max_value=fecha_max
    )
    semanas_a_retroceder = st.sidebar.number_input(
        'Número de semanas a retroceder',
        min_value=0,
        max_value=100
    )
    selected_dates = (auxiliar_functions.retroceder_semanas(fecha_max, semanas_a_retroceder), fecha_max)
    st.sidebar.markdown(f'<b>Fecha Inicio:</b> {selected_dates[0]}<br><b>Fecha Fin:</b> {selected_dates[1]}', unsafe_allow_html=True)
    if len(selected_dates) > 1:
        plotter.update_range_data(*selected_dates) # Actualizamos las fechas al rango especificado
    if len(selected_dates) == 1:
        selected_dates = (selected_dates, fecha_max)
    if len(categorias) == 0:
        categorias = ['Todos']

    # ---------------- BODY --------------------------------
    dict_categorias = auxiliar_functions.cast_to_booleans(categorias)
    data_completados = plotter.get_completed()

    st.markdown('## Manejo de Cumplimiento de Producción')
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Productos", *plotter.get_total_products_and_change(
        todos=dict_categorias['todos'], 
        liquidos=dict_categorias['liquidos'], 
        polvos=dict_categorias['polvos']
    ))
    col2.metric("Cumplimiento Última Semana", *plotter.get_cumplimiento_ultima_semana(
        todos=dict_categorias['todos'], 
        liquidos=dict_categorias['liquidos'], 
        polvos=dict_categorias['polvos']
    ))
    col3.metric("Cumplimiento Intervalo Seleccionado", "86%", "4%")

    fig_bar_categories = plotter.plot_bar_chart_categories()

    fig_bar_families = plotter.plot_bar_chart_families()

    fig_historic_line = plotter.plot_historical_line_chart(
        focus_dates=selected_dates,
        todos=dict_categorias['todos'], 
        liquidos=dict_categorias['liquidos'], 
        polvos=dict_categorias['polvos']
    )

    fig_productos_termiandos = plotter.plot_circular_kpi(
        auxiliar_functions.get_corresponding_mean(
            data_completados, 
            categorias
        ), 
        size=500, 
        r=.4, 
        padding=.1,
        colors=auxiliar_functions.get_colors_for_ciruclar_kpi(categorias)
    )

    col1, _, col2 = st.columns((0.45, 0.15, 0.45))
    with col1:
        st.plotly_chart(fig_bar_categories, config={'displayModeBar':False})
    with col2:
        st.plotly_chart(fig_bar_families, config={'displayModeBar':False})

    col1, _, col2 = st.columns((.7,.1,.2))
    with col1:
        st.plotly_chart(fig_historic_line, config={'displayModeBar': False})
    with col2:
        st.plotly_chart(fig_productos_termiandos, config={'displayModeBar':False})

if __name__ == '__main__':
    main()