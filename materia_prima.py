import streamlit as st
import json
import os

def mostrar_pantalla():
    # TÍTULO DEL MÓDULO
    st.title("🎛️ Maestro de Materia Prima")
    
    FOLDER = "recetas_maestras"
    if not os.path.exists(FOLDER): os.makedirs(FOLDER)

    # MEMORIA COMPARTIDA
    if 'insumos_globales' not in st.session_state:
        st.session_state.insumos_globales = {}
    if 'nombre_receta_tmp' not in st.session_state:
        st.session_state.nombre_receta_tmp = ""
    if 'peso_receta_tmp' not in st.session_state:
        st.session_state.peso_receta_tmp = 1.0
    if 'edit_key' not in st.session_state:
        st.session_state.edit_key = None

    # --- BOTONES DE GESTIÓN (CARGAR / NUEVA) ---
    col_sel, col_btn_c, col_btn_n = st.columns([2, 1, 1])
    
    with col_sel:
        archivos = [f.replace(".json", "") for f in os.listdir(FOLDER) if f.endswith(".json")]
        seleccion = st.selectbox("Recetas guardadas:", ["---"] + archivos)
    
    with col_btn_c:
        st.write(" ")
        if st.button("📂 Cargar", use_container_width=True):
            if seleccion != "---":
                with open(f"{FOLDER}/{seleccion}.json", "r", encoding='utf-8') as f:
                    datos = json.load(f)
                    st.session_state.nombre_receta_tmp = datos.get("nombre", "")
                    st.session_state.peso_receta_tmp = datos.get("cantidad_base", 1.0)
                    st.session_state.insumos_globales = {i['insumo']: {
                        "nombre": i['insumo'], "cantidad_receta": i['cantidad'],
                        "unidad": i['unidad'], "peso_bulto": i['bulto'],
                        "cant_bultos": i.get('cantidad_bultos', 1), "rendimiento": i['rendimiento']
                    } for i in datos.get("insumos", [])}
                st.rerun()

    with col_btn_n:
        st.write(" ")
        if st.button("✨ Nueva", use_container_width=True):
            st.session_state.insumos_globales = {}
            st.session_state.nombre_receta_tmp = ""
            st.session_state.peso_receta_tmp = 1.0
            st.session_state.edit_key = None
            st.rerun()

    st.divider()

    # --- DATOS DE LA RECETA ---
    c_nom, c_pes = st.columns([3, 1])
    nombre_r = c_nom.text_input("Nombre de la Receta", value=st.session_state.nombre_receta_tmp)
    st.session_state.nombre_receta_tmp = nombre_r
    peso_r = c_pes.number_input("Peso Final (Kg)", value=st.session_state.peso_receta_tmp)
    st.session_state.peso_receta_tmp = peso_r

    # --- AGREGAR / MODIFICAR INSUMOS ---
    st.subheader("🛒 Gestión de Insumos")
    
    # Lógica para precargar datos si estamos editando
    v_nom, v_cant, v_uni, v_bul, v_cant_b, v_rend = "", 0.0, "Kg", 20.0, 1, 65
    if st.session_state.edit_key:
        item = st.session_state.insumos_globales[st.session_state.edit_key]
        v_nom, v_cant, v_uni = item['nombre'], item['cantidad_receta'], item['unidad']
        v_bul, v_cant_b, v_rend = item['peso_bulto'], item['cant_bultos'], item['rendimiento']
        st.warning(f"Modificando: {v_nom}")

    f1, f2, f3 = st.columns([2, 1, 1])
    in_nom = f1.text_input("Nombre Insumo", value=v_nom)
    in_cant = f2.number_input("Cant. p/ Receta", min_value=0.0, value=v_cant, format="%.3f")
    in_uni = f3.selectbox("Unidad", ["Kg", "gr", "Unidades"], index=["Kg", "gr", "Unidades"].index(v_uni))

    f4, f5, f6 = st.columns(3)
    in_bul = f4.number_input("Peso Bulto (Kg)", min_value=0.1, value=v_bul)
    in_cant_b = f5.number_input("Cant. Bultos", min_value=1, value=v_cant_b)
    in_rend = f6.number_input("Rendimiento (%)", min_value=1, max_value=100, value=v_rend)

    if st.session_state.edit_key is None:
        if st.button("➕ Cargar Insumo", use_container_width=True):
            if in_nom:
                st.session_state.insumos_globales[in_nom] = {
                    "nombre": in_nom, "cantidad_receta": in_cant, "unidad": in_uni,
                    "peso_bulto": in_bul, "cant_bultos": in_cant_b, "rendimiento": in_rend
                }
                st.rerun()
    else:
        c_edit1, c_edit2 = st.columns(2)
        if c_edit1.button("✅ Confirmar Cambio", use_container_width=True):
            # Eliminar el viejo si cambió el nombre y crear el nuevo
            if in_nom != st.session_state.edit_key:
                del st.session_state.insumos_globales[st.session_state.edit_key]
            st.session_state.insumos_globales[in_nom] = {
                "nombre": in_nom, "cantidad_receta": in_cant, "unidad": in_uni,
                "peso_bulto": in_bul, "cant_bultos": in_cant_b, "rendimiento": in_rend
            }
            st.session_state.edit_key = None
            st.rerun()
        if c_edit2.button("❌ Cancelar", use_container_width=True):
            st.session_state.edit_key = None
            st.rerun()

    # --- LISTA Y GUARDADO FINAL ---
    if st.session_state.insumos_globales:
        st.write("---")
        for k in list(st.session_state.insumos_globales.keys()):
            l1, l2, l3 = st.columns([4, 1, 1])
            l1.write(f"✅ {k} ({st.session_state.insumos_globales[k]['cantidad_receta']} {st.session_state.insumos_globales[k]['unidad']})")
            if l2.button("📝", key=f"editbtn_{k}"):
                st.session_state.edit_key = k
                st.rerun()
            if l3.button("🗑️", key=f"del_{k}"):
                if st.session_state.edit_key == k: st.session_state.edit_key = None
                del st.session_state.insumos_globales[k]
                st.rerun()

        st.divider()
        if st.button("💾 GUARDAR RECETA MAESTRA", type="primary", use_container_width=True):
            if nombre_r:
                lista_ins = [{"insumo": v['nombre'], "cantidad": v['cantidad_receta'], "unidad": v['unidad'], 
                              "bulto": v['peso_bulto'], "cantidad_bultos": v['cant_bultos'], 
                              "rendimiento": v['rendimiento']} for v in st.session_state.insumos_globales.values()]
                final_data = {"nombre": nombre_r, "cantidad_base": peso_r, "insumos": lista_ins}
                with open(f"{FOLDER}/{nombre_r}.json", "w", encoding='utf-8') as f:
                    json.dump(final_data, f, indent=4)
                st.success(f"Receta '{nombre_r}' guardada.")