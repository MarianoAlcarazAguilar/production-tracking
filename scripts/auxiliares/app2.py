import streamlit as st
import datetime
from scripts.plots import Plotter
from scripts import auxiliar_functions
from st_pages import Page, show_pages

def main():
    plotter = Plotter()
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Dragón',
        page_icon='🐉'
    )

    with open('others/style.css') as f:
        # Cargamos el estilo de css (estoy utilizando uno de internet)
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    


    # --- Sidebar ----
    st.sidebar.header('') 
    semanas_a_retroceder = st.sidebar.number_input(
        'Número de semanas a retroceder',
        min_value=1,
        max_value=100
    )
    fecha_min, fecha_max = plotter.get_date_ranges()
    fecha_inicio, fecha_fin = (auxiliar_functions.retroceder_semanas(fecha_max, semanas_a_retroceder), fecha_max)
    fecha_fin  = fecha_fin + datetime.timedelta(days=6)
    unique_skus_dragon, unique_skus_externos = plotter.get_unique_skus_in_time(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

    max_selections = 4
    col_dragon, col_externos = st.sidebar.columns(2)
    with col_dragon:
        print(unique_skus_dragon)
        chosen_products_dragon = st.multiselect(
            'Productos Dragón',
            options=unique_skus_dragon,
            #default='L094',
            max_selections=max_selections
        )
    already_chosen = len(chosen_products_dragon)
    with col_externos:
        chosen_productos_externo = st.multiselect(
            'Productos Externos',
            options=unique_skus_externos,
            max_selections=already_chosen-len(chosen_products_dragon)
        )
    chosen_skus = chosen_products_dragon + chosen_productos_externo
    chosen_skus = chosen_skus if len(chosen_skus) > 0 else ['L094']

    st.sidebar.markdown(f'''
        <b>Fecha Inicio:</b> {fecha_inicio.strftime('%d/%m/%Y')}<br>
        <b>Fecha Fin:</b> {fecha_fin.strftime('%d/%m/%Y')}
    ''', unsafe_allow_html=True)


    dimensions_expander = st.sidebar.expander('Dimensiones')
    pixel_size = dimensions_expander.slider(
        label='Tamaño en pixeles',
        min_value=1000,
        max_value=2000,
        value=1500,
        step=100
    )

    height = dimensions_expander.slider(
        label='Alto en pixeles',
        min_value=100,
        max_value=1000,
        value=350,
        step=50
    )


    # --- Body ---
    st.write('''
        <div class="title">
            Todas las plantas
        </div>
    ''', unsafe_allow_html=True)

    fig1 = plotter.plot_first_grid(
        num_semanas=semanas_a_retroceder, 
        total_prods_dragon=len(unique_skus_dragon), 
        total_prods_externo=len(unique_skus_externos), 
        pixel_size=pixel_size, 
        height=height
    )
    fig2 = plotter.plot_second_grid(
        chosen_skus=chosen_skus, 
        num_semanas=semanas_a_retroceder, 
        pixel_size=pixel_size,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


    st.plotly_chart(fig1, config={'displayModeBar': False})
    st.plotly_chart(fig2, config={'displayModeBar': False})
    

if __name__ == '__main__':
    main()