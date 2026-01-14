import streamlit as st
import json
import os

def mostrar_pantalla():
    PRECIOS_FILE = "precios_vigentes.json"
    st.markdown("### 💰 Actualizar Precios de Compra")

    # Recuperar insumos del estado global (Módulo 1)
    insumos = st.session_state.get('insumos_globales', {})

    if not insumos:
        st.warning("⚠️ No hay insumos en memoria. Por favor, configúralos en el Módulo 1.")
        return

    # Cargar base de datos de precios si existe
    precios_db = {}
    if os.path.exists(PRECIOS_FILE):
        with open(PRECIOS_FILE, "r", encoding='utf-8') as f:
            precios_db = json.load(f)

    # Cabecera de la tabla
    h1, h2, h3, h4, h5 = st.columns([2.5, 1.5, 2, 2, 1])
    h1.caption("INSUMO")
    h2.caption("CANT. RECETA")
    h3.caption("PRECIO BULTO")
    h4.caption("COSTO EN RECETA")
    h5.caption("ACCIONES")
    st.divider()

    # Variables para acumular totales
    total_costo_receta = 0.0
    total_kilos_receta = 0.0

    for nombre, info in insumos.items():
        edit_mode = st.session_state.get(f"edit_local_{nombre}", False)
        c1, c2, c3, c4, c5 = st.columns([2.5, 1.5, 2, 2, 1])
        
        c1.markdown(f"**{nombre}**")
        c2.write(f"{info['cantidad_receta']} {info.get('unidad', 'Kg')}")

        # Acumular kilos de la receta para el costo unitario
        total_kilos_receta += info['cantidad_receta']

        # Input de precio pagado por el bulto
        p_previo = precios_db.get(nombre, {}).get("precio_total_pagado", 0.0)
        precio_bulto = c3.number_input("Precio", min_value=0.0, value=float(p_previo), key=f"p_{nombre}", label_visibility="collapsed")

        # --- LÓGICA DE CÁLCULO SOLICITADA ---
        rendimiento_decimal = info['rendimiento'] / 100
        kilos_netos_bulto = info['peso_bulto'] * rendimiento_decimal
        
        if kilos_netos_bulto > 0:
            costo_kg_neto = precio_bulto / kilos_netos_bulto
            costo_final_receta = costo_kg_neto * info['cantidad_receta']
            
            c4.markdown(f"#### $ {costo_final_receta:,.2f}")
            
            # Sumamos al total de la receta
            total_costo_receta += costo_final_receta
            
            precios_db[nombre] = {
                "costo_neto_unidad": costo_kg_neto, 
                "precio_total_pagado": precio_bulto
            }
        else:
            c4.error("Datos invalidos")

        # Botones de Acción
        b1, b2 = c5.columns(2)
        if b1.button("💾", key=f"save_{nombre}"):
            with open(PRECIOS_FILE, "w", encoding='utf-8') as f:
                json.dump(precios_db, f, indent=4)
            st.toast(f"Guardado: {nombre}")

        if b2.button("📝", key=f"edit_{nombre}"):
            st.session_state[f"edit_local_{nombre}"] = not edit_mode
            st.rerun()

        if edit_mode:
            with st.expander(f"Ajustar Datos Técnicos de {nombre}", expanded=True):
                e1, e2, e3 = st.columns(3)
                n_p = e1.number_input("Peso Bulto (Kg)", value=float(info['peso_bulto']), key=f"e_p_{nombre}")
                n_r = e2.number_input("Rendimiento %", value=float(info['rendimiento']), key=f"e_r_{nombre}")
                if e3.button("✅ Aplicar", key=f"ok_{nombre}"):
                    st.session_state.insumos_globales[nombre]['peso_bulto'] = n_p
                    st.session_state.insumos_globales[nombre]['rendimiento'] = n_r
                    st.session_state[f"edit_local_{nombre}"] = False
                    st.rerun()

        st.markdown("<hr style='margin:2px 0px'>", unsafe_allow_html=True)

    # --- ANÁLISIS DE RENTABILIDAD Y COSTO UNITARIO ---
    st.write("##")
    st.markdown("### 📊 Análisis de Rentabilidad")
    
    # Cálculo de costo por kilo de producto terminado
    costo_unitario_kilo = total_costo_receta / total_kilos_receta if total_kilos_receta > 0 else 0
    
    st.info(f"**Costo Unitario:** Un kilo de esta preparación te cuesta **$ {costo_unitario_kilo:,.2f}**")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        v_mayorista = st.number_input("Precio Venta Mayorista (por kilo)", min_value=0.0, step=100.0)
    with col_v2:
        v_minorista = st.number_input("Precio Venta Minorista (por kilo)", min_value=0.0, step=100.0)
    
    st.divider()
    
    # Análisis de Ganancia o Pérdida
    def mostrar_resultado(precio_v, costo_u, etiqueta):
        diferencia = precio_v - costo_u
        if precio_v == 0:
            st.write(f"{etiqueta}: Pendiente de precio")
        elif diferencia > 0:
            st.success(f"**{etiqueta}: GANANCIA de $ {diferencia:,.2f}** per/kg")
        else:
            st.error(f"**{etiqueta}: PÉRDIDA de $ {abs(diferencia):,.2f}** per/kg")

    res1, res2 = st.columns(2)
    with res1:
        mostrar_resultado(v_mayorista, costo_unitario_kilo, "MAYORISTA")
    with res2:
        mostrar_resultado(v_minorista, costo_unitario_kilo, "MINORISTA")