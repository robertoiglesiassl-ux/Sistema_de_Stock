import streamlit as st
import json
import os

def mostrar_pantalla():
    st.title("📊 Reporte de Costo de Producción")
    
    PRECIOS_FILE = "precios_vigentes.json"
    insumos = st.session_state.get('insumos_globales', {})
    
    if not insumos:
        st.warning("⚠️ No hay datos de recetas configurados.")
        return

    # Cargar precios guardados en Módulo 2
    precios_db = {}
    if os.path.exists(PRECIOS_FILE):
        with open(PRECIOS_FILE, "r", encoding='utf-8') as f:
            precios_db = json.load(f)

    # 1. Resumen de Tabla (Solo lectura)
    st.subheader("Detalle de Costos por Insumo")
    
    total_costo_tanda = 0.0
    total_kilos_tanda = 0.0
    
    datos_tabla = []
    
    for nombre, info in insumos.items():
        costo_unitario = precios_db.get(nombre, {}).get("costo_neto_unidad", 0.0)
        costo_total_insumo = costo_unitario * info['cantidad_receta']
        
        total_costo_tanda += costo_total_insumo
        total_kilos_tanda += info['cantidad_receta']
        
        datos_tabla.append({
            "Insumo": nombre,
            "Cantidad": f"{info['cantidad_receta']} {info.get('unidad', 'Kg')}",
            "Costo x Unidad Neta": f"$ {costo_unitario:,.2f}",
            "Subtotal Receta": f"$ {costo_total_insumo:,.2f}"
        })

    st.table(datos_tabla)

    # 2. Análisis Final de Tanda
    st.divider()
    st.subheader("Análisis de Producto Terminado")
    
    costo_kilo_final = total_costo_tanda / total_kilos_tanda if total_kilos_tanda > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Kilos Totales", f"{total_kilos_tanda:,.2f} Kg")
    c2.metric("Costo Total Tanda", f"$ {total_costo_tanda:,.2f}")
    c3.metric("COSTO POR KILO", f"$ {costo_kilo_final:,.2f}", help="Costo de producción de 1kg de producto final")

    # 3. Comparativo de Venta Directo
    st.write("##")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Escenario Mayorista**")
        p_v_mayo = st.number_input("Precio Venta Mayorista ($)", min_value=0.0, key="v_m_3")
        margen_m = p_v_mayo - costo_kilo_final
        if p_v_mayo > 0:
            porcentaje = (margen_m / costo_kilo_final * 100) if costo_kilo_final > 0 else 0
            st.write(f"Ganancia por Kg: **$ {margen_m:,.2f}** ({porcentaje:.1f}%)")

    with col2:
        st.info("**Escenario Minorista**")
        p_v_mino = st.number_input("Precio Venta Minorista ($)", min_value=0.0, key="v_mi_3")
        margen_mi = p_v_mino - costo_kilo_final
        if p_v_mino > 0:
            porcentaje_mi = (margen_mi / costo_kilo_final * 100) if costo_kilo_final > 0 else 0
            st.write(f"Ganancia por Kg: **$ {margen_mi:,.2f}** ({porcentaje_mi:.1f}%)")

    if st.button("🖨️ Simular Impresión / Guardar PDF"):
        st.toast("Función de exportación lista para configurar")