import streamlit as st

# IMPORTS SIEMPRE ARRIBA (NO dentro de if)
import materia_prima
import precios_vigentes
import costo_produccion
import compras_necesarias

# CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="Recetario y Costos 2026",
    layout="wide",
    page_icon="🚀"
)

# =========================
# SESSION STATE (CRÍTICO)
# =========================
if "insumos_globales" not in st.session_state:
    st.session_state.insumos_globales = {}

if "receta_actual" not in st.session_state:
    st.session_state.receta_actual = {}

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🚀 Recetario y Costos")
st.sidebar.write("Sistema de Gestión Gastronómica")
st.sidebar.divider()

opcion = st.sidebar.radio(
    "Seleccioná un Módulo:",
    (
        "Configurar Recetas",
        "Actualizar Precios",
        "Costo Final",
        "Planificador de Compras"
    )
)

# =========================
# CONTENIDO PRINCIPAL
# =========================
st.title("Recetario y Costos 2026")

if opcion == "Configurar Recetas":
    materia_prima.pantalla_materia_prima()

elif opcion == "Actualizar Precios":
    precios_vigentes.pantalla_precios()

elif opcion == "Costo Final":
    costo_produccion.pantalla_costos()

elif opcion == "Planificador de Compras":
    compras_necesarias.pantalla_compras()


