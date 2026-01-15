import streamlit as st

st.set_page_config(
    page_title="Recetario y Costos 2026",
    page_icon="📦",
    layout="wide"
)

import materia_prima
import precios_vigentes
import costo_produccion
import compras_necesarias  # Nuevo módulo

# Inicialización de la memoria global
if 'insumos_globales' not in st.session_state:
    st.session_state.insumos_globales = {}

# Barra Lateral
st.sidebar.title("🚀 Recetario y Costos")
st.sidebar.write("Sistema de Gestión Gastronómica")
st.sidebar.divider()

opcion = st.sidebar.radio(
    "Seleccioná un Módulo:",
    [
        "Configurar Recetas",
        "Actualizar Precios",
        "Costo Final",
        "Planificador de Compras"
    ]
)

