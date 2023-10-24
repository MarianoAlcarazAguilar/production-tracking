import streamlit as st
from scripts.file_cleaner import FileCleaner

def update_polvos(fc: FileCleaner):
    st.title('Limpieza de polvos')
    uploaded_files = st.file_uploader('Actualización de polvos', type=['xls', 'xlsx', 'xlsm'], accept_multiple_files=True)

    if len(uploaded_files) > 0:
        for file in uploaded_files:
            try:
                fc.clean_polvos(file)
                st.success(f'{file.name} ha sido cargado de manera exitosa')
            except:
                # Si no se pudo, a lo mejor se equivocaron de archivo
                # Verficamos que esté en la primera línea y los arreglamos
                primera_palara_nombre = file.name.split()[0].lower()
                if primera_palara_nombre in ["liquidos", 'líquido', 'liquido', 'líquidos']:
                    try:
                        fc.clean_liquidos(file)
                        st.success(f'{file.name} ha sido cargado de manera exitosa')
                    except:
                        st.error(f'Error al cargar {file.name}')
                else:
                    st.error(f'Error al cargar {file.name}')

    show_last_update_date(fc, 'POLVOS')

def update_liquidos(fc: FileCleaner):
    st.title('Limpieza de líquidos')
    uploaded_files = st.file_uploader('Actualización de líquidos', type=['xls', 'xlsx', 'xlsm'], accept_multiple_files=True)

    if len(uploaded_files) > 0:
        for file in uploaded_files:
            try:
                success = fc.clean_liquidos(file)
                if success:
                    st.success(f'{file.name} ha sido cargado de manera exitosa')
                else:
                    st.error(f'No se entendió la fecha en el archivo {file.name}')
            except:
                # Si no se pudo, a lo mejor se equivocaron de archivo
                # Verficamos que esté en la primera línea y los arreglamos
                primera_palara_nombre = file.name.split()[0].lower()
                if primera_palara_nombre in ["polvos", 'polvo']:
                    try:
                        fc.clean_polvos(file)
                        st.success(f'{file.name} ha sido cargado de manera exitosa')
                    except:
                        st.error(f'Error al cargar {file.name}')
                else:
                    st.error(f'Error al cargar {file.name}')

    show_last_update_date(fc, 'LIQUIDOS')

def update_lerma(fc: FileCleaner):
    st.title('Limpieza de archivos de Lerma')
    file = st.file_uploader('Actualización de líquidos', type=['xls', 'xlsx', 'xlsm'], accept_multiple_files=False)

    if file:
        try:
            processed_weeks = fc.clean_lerma(file)
            if len(processed_weeks) == 0:
                st.success(f'{file.name} ha sido cargado de manera exitosa, pero no se encontraron datos nuevos para actualizar')
            else:
                st.success(f'{file.name} ha sido cargado de manera exitosa. Semanas actualizadas: {processed_weeks}')
        except:
            st.error(f'Error al cargar {file.name}')
    
    show_last_update_date(fc, 'TBD')
            
def show_last_update_date(fc:FileCleaner, tipo:str):
    ultima_fecha_actualizada = fc.get_last_update_date()
    if tipo not in ultima_fecha_actualizada:
        st.write('''<p class="last-date">No hay datos para este tipo de archivos</p>''', unsafe_allow_html=True)
        return False
    st.write(f'''
        <p class="last-date">La última fecha actualizada es <b>{ultima_fecha_actualizada[tipo]}</b></p>
    ''', unsafe_allow_html=True)

def open_styles(location='data/static/style.css'):
    
    st.set_page_config(
        layout='wide', 
        initial_sidebar_state='expanded',
        page_title='Dragón',
        page_icon='🐉'
    )

    with open(location) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_page():
    open_styles()
    fc = FileCleaner()

    st.sidebar.write('''
        <p class="paragraph">
            En esta página puedes cargar los archivos operacionales de planeación de producción para que se actualicen de forma automática
        </p>''',
    unsafe_allow_html=True)

    type_of_file = st.sidebar.radio('Elige el tipo de archivo a subir', ['Polvos', 'Líquidos', 'Lerma'])

    if type_of_file == 'Polvos':
        update_polvos(fc)

    elif type_of_file == 'Líquidos':
        update_liquidos(fc)

    elif type_of_file == "Lerma":
        update_lerma(fc)



if __name__ == "__main__":
    render_page()