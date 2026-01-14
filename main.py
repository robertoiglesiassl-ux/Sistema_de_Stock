import streamlit as st

# ⚠️ SIEMPRE PRIMERO
st.set_page_config(
    page_title="Recetario y Costos 2026",
    page_icon="📦",   # o "icon.png" si lo agregás
    layout="wide"
)

# Recién después los imports
import materia_prima
import precios_vigentes
import costo_produccion
import compras_necesarias  # Nuevo módulo

# Configuración de la página
st.set_page_config(page_title="Recetario y Costos 2026", layout="wide")

# Inicialización de la memoria global (Sesión de Streamlit)
if 'insumos_globales' not in st.session_state:
    st.session_state.insumos_globales = {}

# Barra Lateral - Navegación
st.sidebar.title("🚀 Recetario y Costos")
st.sidebar.write("Sistema de Gestión Gastronómica")
st.sidebar.divider()

opcion = st.sidebar.radio(
    "Seleccioná un Módulo:", 
    [
        "Configurar Recetas", 
        "Actualizar Precios", 
        "Costo Final",
        "Planificador de Compras"  # Nueva opción
    ]
)

st.sidebar.divider()
st.sidebar.info("Aries 1984 - Año de Consolidación")

# Lógica de navegación entre archivos
if opcion == "Configurar Recetas":
    materia_prima.mostrar_pantalla()

elif opcion == "Actualizar Precios":
    precios_vigentes.mostrar_pantalla()

elif opcion == "Costo Final":
    costo_produccion.mostrar_pantalla()

elif opcion == "Planificador de Compras":

    compras_necesarias.mostrar_pantalla()
