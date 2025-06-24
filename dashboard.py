import streamlit as st
import pandas as pd
import altair as alt

# Definición de secciones con las columnas asociadas
GROUPS = {
    "CONCENTRADO ROUGHER": [
        "NivelCajonHP003_Percent",
        "VelocidadMotorPU003_Percent",
        "VelocidadPU003_rpm",
        "PotenciaPU003_kW",
    ],
    "ALIMENTACIÓN REMOLIENDA": [
        "NivelCajonHP010_Percent",
        "FlujoDescargaEspumadoPU010_m3xhr",
        "FlujoDescargaPU010_m3xhr2",
        "VelocidadMotorPU010_Percent",
        "VelocidadPU010_rpm",
        "PotenciaPU010_kW",
    ],
    "CONCENTRADO A CLEANER 2": [
        "NivelCajonHP011_Percent",
        "VelocidadMotorPU011_Percent",
        "VelocidadPU011_rpm",
        "PotenciaPU011_kW",
    ],
    "CLEANER SCAVENGER": [
        "NivelCajonHP015_Percent",
        "VelocidadMotorPU015_Percent",
        "VelocidadPU015_rpm",
        "PotenciaPU015_kW",
    ],
    "COLAS CLEANER 2 A CLEANER 1": [
        "NivelCajonHP022_Percent",
        "VelocidadMotorPU022_Percent",
        "VelocidadPU022_rpm",
        "PotenciaPU022_kW",
    ],
    "SISTEMA SPARGING FC-21": [
        "VelocidadPU023_Percent",
        "PotenciaPU023_kW",
    ],
    "SISTEMA SPARGING FC-22": [
        "VelocidadPU024_Percent",
        "PotenciaPU024_kW",
    ],
    "CONCENTRADO SCAVENGER A CLEANER 3": [
        "NivelCajonHP031_Percent",
        "VelocidadMotorPU031_Percent",
        "VelocidadPU031_rpm",
        "PotenciaPU031_kW",
    ],
    "SISTEMA SPARGING FC-31": [
        "VelocidadPU217_Percent",
        "PotenciaPU217_kW",
    ],
    "CONCENTRADO A FILTRO": [
        "NivelTK061_Percent",
        "VelocidadPU061_Percent",
        "VelocidadPU061_rpm",
        "PotenciaPU061_kW",
    ],
    "TK DE FILTRADO": [
        "NivelTK062_Percent",
        "VelocidadPU062_Percent",
        "PotenciaPU062_kW",
    ],
    "DISTRIBUCIÓN DE CAL": [
        "NivelTK242_Percent",
        "VelocidadPU243_Percent",
        "PotenciaPU243_kW",
        "VelocidadPU244_Percent",
        "PotenciaPU244_kW",
    ],
    "ALIMENTACIÓN CICLONES PLANTA DE ARENA": [
        "NivelCajonHP101_Percent",
        "VelocidadMotorPU101_Percent",
        "VelocidadPU101_rpm",
        "FlujoDescargaPU101_m3xhr",
        "Densisdad6415_Kgxm3",
        "PotenciaPU101_kW",
    ],
    "BOMBA 1 U/F ESPESADOR": [
        "NivelTH101_Percent",
        "Densisdad6712_Kgxm3",
        "VelocidadPU200_Percent",
        "PotenciaPU200_kW",
    ],
    "BOMBA 2 U/F ESPESADOR": [
        "NivelTH101_Percent2",
        "VelocidadPU205_Percent",
        "PotenciaPU205_kW",
    ],
    "DISTRIBUCIÓN DE ARENA": [
        "NivelHP102_Percent",
        "Densidad6625_Kgxm3",
        "Densidad6601_Kgxm3",
        "VelocidadMotorPU111_Percent",
        "VelocidadPU111_rpm",
        "PotenciaPU111_kW",
        "VelocidadPU112_Percent",
        "PotenciaPU112_kW",
        "VelocidadPU113_Percent",
        "PotenciaPU113_kW",
    ],
    "DISTRIBUCIÓN DE LAMAS T1": [
        "NivelHP103_Percent",
        "DensidadPU131_Kgxm3",
        "VelocidadPU131_rpm",
        "PotenciaPU131_kW",
    ],
    "U/F ESPESADOR DE RELAVES": [
        "NivelTH002_Percent",
        "FlujoDescargaPU071_m3xhr",
        "DensisdadPU071_Kgxm3",
        "VelocidadMotorPU071_Percent",
        "VelocidadPU071_rpm",
        "PotenciaPU071_kW",
    ],
}

# Configuración de página
st.set_page_config(page_title='Pump Dashboard', layout='wide')
st.title('📊 Pump Performance Dashboard')

@st.cache_data
# Carga de datos desde CSV limpio
def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path, parse_dates=['Fecha'])

# Clasificación de métrica para esquema de color
def classify_metric(m: str) -> str:
    if m.startswith('Nivel'): return 'Nivel'
    if m.startswith('VelocidadMotor'): return 'VelocidadMotor'
    if m.endswith('_rpm') or m.startswith('Velocidad'): return 'Velocidad'
    if m.startswith('Potencia'): return 'Potencia'
    if m.startswith('FlujoDescargaEspumado'): return 'FlujoEspumado'
    if m.startswith('FlujoDescarga'): return 'Flujo'
    if 'Densidad' in m: return 'Densidad'
    return 'Otros'

# Mapa de colores base
tipo_map = {
    'Nivel': '#1f77b4',
    'VelocidadMotor': '#ff7f0e',
    'Velocidad': '#2ca02c',
    'Potencia': '#d62728',
    'FlujoEspumado': '#9467bd',
    'Flujo': '#8c564b',
    'Densidad': '#e377c2',
    'Otros': '#7f7f7f'
}

# Sidebar: ruta CSV y selección de sección
data_path = st.sidebar.text_input('Ruta al CSV limpio', 'data/clean_pumps.csv')
section = st.sidebar.selectbox('Selecciona sección', list(GROUPS.keys()))

# Carga y filtrado de datos
df = load_data(data_path)
cols = GROUPS[section]
df_section = df[['Fecha'] + cols]

# Transformación a largo e inclusión de tipo
df_long = (
    df_section
    .melt(id_vars='Fecha', var_name='metric', value_name='valor')
    .assign(tipo=lambda d: d['metric'].apply(classify_metric))
)

# Definir paleta dinámica según tipos presentes
present_types = df_long['tipo'].unique().tolist()
palette = [tipo_map[t] for t in present_types]

# Gráfico de líneas
title = f'Sección: {section} - Series de Tiempo'
line = alt.Chart(df_long).mark_line().encode(
    x='Fecha:T',
    y='valor:Q',
    color=alt.Color('tipo:N', scale=alt.Scale(domain=present_types, range=palette), legend=alt.Legend(title='Tipo')),
    tooltip=['Fecha:T','metric:N','valor:Q']
).interactive().properties(width='container', height=350, title=title)
st.altair_chart(line, use_container_width=True)

# Estadísticas descriptivas
st.header('Estadísticas descriptivas')
st.dataframe(
    df_long
    .groupby(['tipo','metric'])['valor']
    .agg(['count','mean','min','max','std'])
    .reset_index()
)

# Relaciones de flujo vs potencia y nivel
st.header('Relaciones de flujo')
flows = [c for c in cols if 'Flujo' in c]
pows = [c for c in cols if 'Potencia' in c]
levels = [c for c in cols if 'Nivel' in c]
# Scatter Flujo vs Potencia
if flows and pows:
    for f in flows:
        for p in pows:
            st.subheader(f'{f} vs {p}')
            chart = alt.Chart(df_section).mark_circle(size=60).encode(
                x=alt.X(f+':Q', title=f),
                y=alt.Y(p+':Q', title=p),
                color=alt.value(tipo_map['Potencia']),
                tooltip=['Fecha:T', f+':Q', p+':Q']
            ).interactive().properties(width='container', height=300)
            st.altair_chart(chart, use_container_width=True)
# Scatter Flujo vs Nivel
if flows and levels:
    for f in flows:
        for l in levels:
            st.subheader(f'{f} vs {l}')
            chart = alt.Chart(df_section).mark_circle(size=60).encode(
                x=alt.X(f+':Q', title=f),
                y=alt.Y(l+':Q', title=l),
                color=alt.value(tipo_map['Velocidad']),
                tooltip=['Fecha:T', f+':Q', l+':Q']
            ).interactive().properties(width='container', height=300)
            st.altair_chart(chart, use_container_width=True)

# Box-and-Whisker plots separados por métrica con escala independiente
st.header('Distribución de métricas')
base = df_long
box = alt.Chart(base).mark_boxplot(size=40, extent='min-max').encode(
    x=alt.X('metric:N', axis=None),
    y=alt.Y('valor:Q', title='Valor'),
    color=alt.Color('tipo:N', scale=alt.Scale(domain=present_types, range=palette), legend=None)
)
mean = alt.Chart(base).mark_point(shape='diamond', size=80, color='black').transform_aggregate(
    mean_val='mean(valor)', groupby=['metric']
).encode(
    x=alt.X('metric:N', axis=None),
    y=alt.Y('mean_val:Q')
)
box_mean = alt.layer(box, mean).facet(
    column=alt.Column('metric:N', title='Métrica')
).resolve_scale(
    y='independent'
).properties(
    width=100,
    height=300
)
st.altair_chart(box_mean.configure_facet(spacing=20), use_container_width=True)

st.markdown('---')
st.write('✌️ Fin del análisis')

