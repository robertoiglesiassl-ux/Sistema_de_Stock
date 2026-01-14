import streamlit as st
import json
import os
import math

def mostrar_pantalla():
    # --- CONFIGURACIÓN DE ARCHIVOS ---
    FOLDER = "recetas_maestras"
    PRECIOS_FILE = "precios_vigentes.json"
    PLAN_FILE = "plan_produccion_semanal.json"
    STOCK_FILE = "stock_actual.json"
    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    # --- BOTONES DE CONTROL SUPERIOR ---
    st.title("📅 Planificador de Producción Semanal")
    
    col_inicio1, col_inicio2 = st.columns(2)
    with col_inicio1:
        if st.button("🆕 INICIAR PRÓXIMA PLANIFICACIÓN", use_container_width=True, help="Borra la producción semanal pero MANTIENE el stock"):
            st.session_state.plan_multireceta = {dia: [] for dia in DIAS}
            if os.path.exists(PLAN_FILE):
                os.remove(PLAN_FILE)
            st.session_state.resultados_memoria = None
            st.rerun()
            
    with col_inicio2:
        if st.button("⚠️ REINICIAR TODO EL STOCK A 0", use_container_width=True):
            if os.path.exists(STOCK_FILE):
                os.remove(STOCK_FILE)
            st.rerun()

    st.divider()

    if not os.path.exists(FOLDER):
        st.warning("No se encontró la carpeta 'recetas_maestras'.")
        return

    # --- PERSISTENCIA ---
    if 'plan_multireceta' not in st.session_state:
        st.session_state.plan_multireceta = json.load(open(PLAN_FILE, "r", encoding='utf-8')) if os.path.exists(PLAN_FILE) else {dia: [] for dia in DIAS}
    if 'resultados_memoria' not in st.session_state:
        st.session_state.resultados_memoria = None

    precios_db = json.load(open(PRECIOS_FILE, "r", encoding='utf-8')) if os.path.exists(PRECIOS_FILE) else {}
    stock_db = json.load(open(STOCK_FILE, "r", encoding='utf-8')) if os.path.exists(STOCK_FILE) else {}

    # --- 1. CARGA DE PRODUCCIÓN ---
    st.subheader("1. Cargar Producción Diaria")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.5, 3, 1.5, 1])
        dia_sel = c1.selectbox("Día", DIAS)
        rec_sel = c2.selectbox("Seleccionar Receta", [f.replace(".json", "") for f in os.listdir(FOLDER) if f.endswith(".json")])
        cant_pedida = c3.number_input("Cantidad", min_value=0.1, value=1.0, step=0.5)
        if c4.button("➕ Añadir"):
            st.session_state.plan_multireceta[dia_sel].append({"receta": rec_sel, "cantidad": cant_pedida})
            with open(PLAN_FILE, "w", encoding='utf-8') as f: json.dump(st.session_state.plan_multireceta, f, indent=4)
            st.session_state.resultados_memoria = None
            st.rerun()

    # CRONOGRAMA VISUAL
    st.write("---")
    cols_dias = st.columns(5)
    for i, dia in enumerate(DIAS):
        with cols_dias[i]:
            st.markdown(f"**{dia}**")
            for idx, item in enumerate(st.session_state.plan_multireceta[dia]):
                with st.expander(f"{item['receta']} ({item['cantidad']})", expanded=True):
                    if st.button("🗑️", key=f"del_{dia}_{idx}"):
                        st.session_state.plan_multireceta[dia].pop(idx)
                        with open(PLAN_FILE, "w", encoding='utf-8') as f: json.dump(st.session_state.plan_multireceta, f, indent=4)
                        st.session_state.resultados_memoria = None
                        st.rerun()

    # --- 2. RESUMEN DE PRODUCCIÓN SEMANAL ---
    produccion_consolidada = {}
    for dia in DIAS:
        for item in st.session_state.plan_multireceta[dia]:
            nombre_r = item['receta']
            produccion_consolidada[nombre_r] = produccion_consolidada.get(nombre_r, 0.0) + item['cantidad']

    if produccion_consolidada:
        st.subheader("2. Total de Producción Semanal")
        st.table([{"Receta": k, "Total a Producir": f"{v:.2f} kg/un."} for k, v in produccion_consolidada.items()])

    # --- 3. CÁLCULO DE COMPRAS Y EFICIENCIA ---
    if st.button("📊 GENERAR LISTA DE COMPRAS Y COSTOS", type="primary", use_container_width=True):
        consolidado_insumos = {}
        reporte_txt = "=== REPORTE DE COMPRAS Y PRODUCCIÓN ===\n\n"
        reporte_txt += "RESUMEN DE PRODUCCIÓN SEMANAL:\n"
        for rec, tot in produccion_consolidada.items():
            reporte_txt += f"- {rec}: {tot:.2f} kg/un.\n"
        
        reporte_txt += "\nRESUMEN DE COMPRA Y EFICIENCIA:\n"
        reporte_txt += f"{'INSUMO':<21} | {'NECESIDAD':<13} | {'STOCK USADO':<13} | {'COMPRA':<20} | {'SOBRANTE REAL'}\n"
        reporte_txt += "-" * 95 + "\n"

        for rec, total_cant in produccion_consolidada.items():
            data = json.load(open(os.path.join(FOLDER, f"{rec}.json"), "r", encoding='utf-8'))
            factor = total_cant / data.get("cantidad_base", 1.0)
            for ins in data.get("insumos", []):
                nom = ins['insumo']
                if nom not in consolidado_insumos:
                    consolidado_insumos[nom] = {"neta": 0.0, "bulto": ins['bulto'], "rend": ins['rendimiento'], "uni": ins['unidad']}
                consolidado_insumos[nom]["neta"] += (ins['cantidad'] * factor)

        tabla_resultados = []
        total_compra_caja = 0.0
        nuevo_stock_proyectado = {}

        for nom, info in consolidado_insumos.items():
            stk_actual = float(stock_db.get(nom, 0.0))
            faltante = max(0, info['neta'] - stk_actual)
            
            u_netas_bulto = info['bulto'] * (info['rend'] / 100)
            bultos = math.ceil(faltante / u_netas_bulto) if u_netas_bulto > 0 else 0
            p_bulto = precios_db.get(nom, {}).get("precio_total_pagado", 0.0)
            costo_compra = bultos * p_bulto
            total_compra_caja += costo_compra
            
            sobrante = (stk_actual + (bultos * u_netas_bulto)) - info['neta']
            nuevo_stock_proyectado[nom] = round(sobrante, 2)

            tabla_resultados.append({
                "Insumo": nom,
                "Necesidad": f"{info['neta']:.2f} {info['uni']}",
                "Stock": f"{stk_actual:.2f}",
                "Compra": f"{bultos} un. (${costo_compra:,.2f})",
                "Sobrante": f"{sobrante:.2f} {info['uni']}"
            })

            reporte_txt += f"{nom:<21} | {info['neta']:>8.2f} {info['uni']:<3} | {stk_actual:>11.2f} | {bultos:>2} un. (${costo_compra:>10,.2f}) | {sobrante:>8.2f} {info['uni']}\n"

        reporte_txt += "-" * 95 + "\n"
        reporte_txt += f"TOTAL INVERSIÓN EN CAJA: $ {total_compra_caja:,.2f}\n"

        st.session_state.resultados_memoria = {"tabla": tabla_resultados, "total": total_compra_caja, "txt": reporte_txt, "proyeccion": nuevo_stock_proyectado}

    # --- 4. RESULTADOS FINALES Y BOTONES DE STOCK ---
    if st.session_state.resultados_memoria:
        st.divider()
        st.subheader("🛒 3. Resumen de Compra y Eficiencia")
        st.table(st.session_state.resultados_memoria["tabla"])
        st.metric("INVERSIÓN EN CAJA", f"$ {st.session_state.resultados_memoria['total']:,.2f}")

        c1, c2 = st.columns(2)
        if c1.button("✅ GUARDAR STOCK PARA LA PRÓXIMA SEMANA", use_container_width=True):
            with open(STOCK_FILE, "w", encoding='utf-8') as f:
                json.dump(st.session_state.resultados_memoria["proyeccion"], f, indent=4)
            st.success("Sobrantes guardados en inventario.")
            st.rerun()

        c2.download_button("📥 DESCARGAR REPORTE (.txt)", data=st.session_state.resultados_memoria["txt"], file_name="compras_semanales.txt", use_container_width=True)