import streamlit as st
import pandas as pd
import mysql.connector
import time
import datetime

# ==========================================
# 1. CONFIGURACIÓN GLOBAL (OBLIGATORIO LÍNEA 1)
# ==========================================
st.set_page_config(
    page_title="Gestión de Activos Físicos | Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. MOTOR CSS ULTRA PREMIUM (ASSET MANAGEMENT)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        /* Fondo Animado Corporativo */
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .stApp { background: linear-gradient(-45deg, #020617, #0A192F, #020813, #001E3C); background-size: 300% 300%; animation: gradientBG 25s ease infinite; color: #F8FAFC; }
        
        /* Ocultar basura nativa */
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        
        /* Scrollbar Premium */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 198, 255, 0.4); border-radius: 10px; }
        
        /* Formularios Glassmorphism */
        div[data-testid="stForm"] {
            background: rgba(4, 13, 30, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(0, 198, 255, 0.2) !important;
            border-radius: 16px !important;
            padding: 25px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        /* Sidebar y Tarjetas */
        [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.9) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 198, 255, 0.15); }
        [data-testid="stMetric"] { background: rgba(10, 20, 40, 0.6); border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 20px; border-top: 3px solid #00C6FF; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        
        /* Botones e Inputs */
        .stButton>button { background: linear-gradient(135deg, #0066FF 0%, #00C6FF 100%); color: #FFFFFF !important; border: none; border-radius: 8px; font-weight: 600; width: 100%; transition: all 0.3s ease; padding: 0.5rem 1rem;}
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4); }
        input, select, textarea { background-color: rgba(0, 0, 0, 0.4) !important; color: white !important; border: 1px solid rgba(0, 198, 255, 0.3) !important; border-radius: 8px !important; }
        
        /* Dataframes */
        [data-testid="stDataFrame"] { background-color: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; border: 1px solid rgba(255,255,255,0.05);}
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. UTILIDADES FINANCIERAS
# ==========================================
def fmt_cop(val):
    try: val_int = int(float(val))
    except (ValueError, TypeError): return "$0"
    s = f"{val_int:,}".replace(',', '.')
    return f"${s}"

def get_color_estado(val):
    if val in ['Vigente', 'Aplicado', 'Ocupado']: return 'background-color: rgba(16, 185, 129, 0.15); color: #34D399; font-weight: 600;'
    if val in ['Cancelado', 'Anulado', 'Mora']: return 'background-color: rgba(245, 158, 11, 0.15); color: #F87171; font-weight: 600;'
    if val in ['Disponible']: return 'background-color: rgba(0, 198, 255, 0.15); color: #00C6FF; font-weight: 600;'
    return ''

# ==========================================
# 4. MOTOR DE BASE DE DATOS ROBUSTO
# ==========================================
@st.cache_resource(ttl=300)
def init_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"], 
            port=st.secrets["DB_PORT"], 
            user=st.secrets["DB_USER"], 
            password=st.secrets["DB_PASS"], 
            database=st.secrets["DB_NAME"], 
            ssl_verify_cert=False, 
            autocommit=True
        )
    except Exception as e:
        st.error(f"Falla Crítica de Red: {e}")
        return None

conn = init_connection()
if conn is None or not conn.is_connected():
    st.cache_resource.clear()
    st.stop()

def run_query(query, params=None):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        res = cursor.fetchall()
        return pd.DataFrame(res)
    except Exception as e:
        st.error(f"Error de lectura: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def run_transact(query, params=None):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        return True
    except Exception as e:
        st.error(f"Error de escritura: {e}")
        return False
    finally:
        cursor.close()

# ==========================================
# 5. ENRUTADOR Y MÓDULOS
# ==========================================
def main():
    st.sidebar.markdown("<br><div style='text-align: center;'><h2 style='color:#00C6FF; font-weight:700; letter-spacing: 1px;'>ACTIVOS PRO</h2><p style='color:#94A3B8; font-size: 0.9rem;'>Asset Management</p></div><br>", unsafe_allow_html=True)
    
    menu = {
        "📊 Centro de Mando": "dash",
        "🏢 Inventario de Activos": "activos",
        "👥 Base de Contratos": "contratos",
        "💰 Control de Caja": "tesoreria",
        "🔑 Disponibilidad": "vacancia"
    }
    nav = st.sidebar.radio("Navegación", list(menu.keys()), label_visibility="collapsed")
    mod = menu[nav]

    # ----------------------------------------
    # MÓDULO 1: DASHBOARD
    # ----------------------------------------
    if mod == "dash":
        st.markdown("<h2>Centro de Mando 📊</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8;'>Resumen operativo y financiero del portafolio.</p>", unsafe_allow_html=True)
        
        df_activos = run_query("SELECT COUNT(*) as t FROM contratos WHERE estado_contrato = 'Vigente'")
        t_contratos = df_activos.iloc[0]['t'] if not df_activos.empty else 0
        
        df_ingresos = run_query("SELECT SUM(monto_pagado) as t FROM pagos WHERE estado_pago = 'Aplicado'")
        t_ingresos = df_ingresos.iloc[0]['t'] if not df_ingresos.empty and pd.notna(df_ingresos.iloc[0]['t']) else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Contratos Vigentes", f"{t_contratos} Activos")
        c2.metric("Recaudo Histórico Global", fmt_cop(t_ingresos))
        c3.metric("Estado del Sistema", "En Línea 🟢")
        
        st.divider()
        st.subheader("Auditoría de Últimos Recaudos")
        df_pagos = run_query("""
            SELECT p.id_referencia_banco as 'Ref. Bancaria', p.fecha_registro as 'Fecha de Operación', u.nombre_unidad as 'Activo Físico', p.monto_pagado as 'Monto Recibido', p.estado_pago as 'Estado'
            FROM pagos p 
            JOIN contratos c ON p.contrato_id = c.id
            JOIN unidades u ON c.unidad_id = u.id
            ORDER BY p.id DESC LIMIT 5
        """)
        if not df_pagos.empty:
            df_pagos['Monto Recibido'] = df_pagos['Monto Recibido'].apply(fmt_cop)
            st.dataframe(df_pagos.style.applymap(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)
        else:
            st.info("La caja registradora está en blanco. No hay pagos procesados.")

    # ----------------------------------------
    # MÓDULO 2: GESTIÓN DE ACTIVOS
    # ----------------------------------------
    elif mod == "activos":
        st.markdown("<h2>Gestión del Portafolio Físico 🏢</h2>", unsafe_allow_html=True)
        t_prop, t_unid = st.tabs(["🏛️ Estructuras Matrices (Edificios/Casas)", "🚪 Unidades de Renta (Apartamentos/Locales)"])
        
        with t_prop:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_prop", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Alta de Nueva Propiedad</h4>", unsafe_allow_html=True)
                    nom = st.text_input("Nombre de Identificación (Ej: Edificio Norte)")
                    dir = st.text_input("Dirección Oficial")
                    if st.form_submit_button("Crear Estructura"):
                        if nom and dir:
                            if run_transact("INSERT INTO propiedades (nombre, direccion) VALUES (%s, %s)", (nom, dir)):
                                st.toast("Estructura añadida al portafolio.", icon="✅")
                                time.sleep(1); st.rerun()
                        else: st.warning("⚠️ Los campos de texto son obligatorios.")
            with c2:
                df_p = run_query("SELECT id as ID, nombre as Nombre, direccion as Dirección FROM propiedades")
                if not df_p.empty:
                    st.dataframe(df_p, use_container_width=True, hide_index=True)
                else:
                    st.info("No existen propiedades matrices registradas en el ecosistema.")

        with t_unid:
            df_props = run_query("SELECT id, nombre FROM propiedades")
            if df_props.empty:
                st.warning("⚠️ Requisito: Debes dar de alta una Propiedad Matriz antes de poder crear unidades de renta.")
            else:
                c1, c2 = st.columns([1, 2], gap="large")
                opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
                with c1:
                    with st.form("f_uni", clear_on_submit=True):
                        st.markdown("<h4 style='color:#00C6FF;'>Alta de Unidad</h4>", unsafe_allow_html=True)
                        sel_p = st.selectbox("Estructura a la que pertenece:", list(opc_p.keys()))
                        n_uni = st.text_input("Identificador (Ej: Apto 101, Local B)")
                        can_b = st.number_input("Canon Base Sugerido ($)", min_value=0, step=50000)
                        if st.form_submit_button("Añadir al Inventario"):
                            if n_uni and can_b > 0:
                                if run_transact("INSERT INTO unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (opc_p[sel_p], n_uni, can_b)):
                                    st.toast("Unidad listada para renta.", icon="✅")
                                    time.sleep(1); st.rerun()
                            else: st.error("⚠️ Defina un nombre y un precio base válido.")
                with c2:
                    df_u = run_query("""
                        SELECT u.id as ID, p.nombre as 'Propiedad Matriz', u.nombre_unidad as 'Unidad', u.canon_base as 'Precio Base', u.estado_vacancia as 'Estatus' 
                        FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC
                    """)
                    if not df_u.empty:
                        df_u['Precio Base'] = df_u['Precio Base'].apply(fmt_cop)
                        st.dataframe(df_u.style.applymap(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)
                    else:
                        st.info("No hay unidades configuradas. Utiliza el formulario lateral.")

    # ----------------------------------------
    # MÓDULO 3: CONTRATOS
    # ----------------------------------------
    elif mod == "contratos":
        st.markdown("<h2>Gestor de Contratos y Titulares 👥</h2>", unsafe_allow_html=True)
        t_inq, t_con = st.tabs(["👤 Padrón de Titulares", "📄 Originación de Contratos"])
        
        with t_inq:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_inq", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Registrar Cliente</h4>", unsafe_allow_html=True)
                    ced = st.text_input("Documento / NIT")
                    nom = st.text_input("Nombre Completo o Razón Social")
                    tel = st.text_input("Número de Contacto")
                    if st.form_submit_button("Consolidar Titular"):
                        if ced and nom:
                            if run_transact("INSERT INTO inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (ced, nom, tel)):
                                st.toast("Cliente formalizado.", icon="✅")
                                time.sleep(1); st.rerun()
                        else: st.warning("⚠️ Documento y Nombre son campos críticos.")
            with c2:
                df_i = run_query("SELECT documento_identidad as 'Identificación', nombre_completo as 'Titular', telefono as 'Contacto' FROM inquilinos ORDER BY id DESC")
                if not df_i.empty:
                    st.dataframe(df_i, use_container_width=True, hide_index=True)
                else:
                    st.info("El directorio de clientes está vacío.")

        with t_con:
            df_inqs = run_query("SELECT id, nombre_completo, documento_identidad FROM inquilinos")
            df_unis = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
            
            if df_inqs.empty or df_unis.empty:
                st.warning("⚠️ Requisito: Para formalizar un contrato, debe existir al menos un Titular registrado y una Unidad en estado 'Disponible'.")
            else:
                with st.form("f_con", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Términos Contractuales</h4>", unsafe_allow_html=True)
                    c_a, c_b = st.columns(2)
                    opc_inq = {f"{r['documento_identidad']} - {r['nombre_completo']}": r['id'] for _, r in df_inqs.iterrows()}
                    opc_uni = {f"{r['nombre']} - {r['nombre_unidad']}": r['id'] for _, r in df_unis.iterrows()}
                    
                    with c_a:
                        sel_i = st.selectbox("Arrendatario (Cliente)", list(opc_inq.keys()))
                        sel_u = st.selectbox("Activo a Rentar", list(opc_uni.keys()))
                        dia_p = st.number_input("Día de Corte Mensual (1-31)", min_value=1, max_value=31, value=5)
                    with c_b:
                        can_p = st.number_input("Valor Negociado Mensual ($)", min_value=0, step=50000)
                        f_ini = st.date_input("Fecha de Inicio")
                        f_fin = st.date_input("Fecha de Finalización", value=f_ini + datetime.timedelta(days=365))
                    
                    if st.form_submit_button("Sellar Contrato y Entregar Activo"):
                        if can_p > 0:
                            q_con = "INSERT INTO contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)"
                            q_upd = "UPDATE unidades SET estado_vacancia = 'Ocupado' WHERE id = %s"
                            if run_transact(q_con, (opc_uni[sel_u], opc_inq[sel_i], can_p, dia_p, f_ini, f_fin)):
                                run_transact(q_upd, (opc_uni[sel_u],))
                                st.toast("Contrato Ejecutado.", icon="📜")
                                time.sleep(1); st.rerun()
                        else: st.error("⚠️ El canon no puede ser cero.")

    # ----------------------------------------
    # MÓDULO 4: TESORERÍA
    # ----------------------------------------
    elif mod == "tesoreria":
        st.markdown("<h2>Centro de Caja y Recaudos 💰</h2>", unsafe_allow_html=True)
        df_activos = run_query("""
            SELECT c.id, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado
            FROM contratos c
            JOIN unidades u ON c.unidad_id = u.id
            JOIN propiedades p ON u.propiedad_id = p.id
            JOIN inquilinos i ON c.inquilino_id = i.id
            WHERE c.estado_contrato = 'Vigente'
        """)
        
        if df_activos.empty:
            st.info("No existen operaciones de renta activas para generar cobros.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"[{r['prop']} - {r['uni']}] {r['inq']} (Debe: {fmt_cop(r['canon_pactado'])})": r['id'] for _, r in df_activos.iterrows()}
            
            with c1:
                with st.form("f_pago", clear_on_submit=True):
                    st.markdown("<h4 style='color:#34D399;'>Procesar Ingreso</h4>", unsafe_allow_html=True)
                    sel_c = st.selectbox("Seleccionar Cuenta Cobrable", list(opc_c.keys()))
                    mes = st.selectbox("Periodo Amortizado (Mes)", [1,2,3,4,5,6,7,8,9,10,11,12], index=datetime.date.today().month-1)
                    anio = st.number_input("Año Fiscal", value=datetime.date.today().year)
                    monto = st.number_input("Capital Recibido ($)", min_value=0, step=50000)
                    ref = st.text_input("ID Transacción (Nequi / Banco)")
                    
                    if st.form_submit_button("Asentar Pago en Caja"):
                        if monto > 0:
                            q_pago = "INSERT INTO pagos (contrato_id, periodo_pagado_mes, periodo_pagado_anio, monto_pagado, id_referencia_banco) VALUES (%s, %s, %s, %s, %s)"
                            if run_transact(q_pago, (opc_c[sel_c], mes, anio, monto, ref)):
                                st.toast("Recaudo procesado con éxito.", icon="✅")
                                time.sleep(1); st.rerun()
                        else: st.error("⚠️ El capital recibido debe ser mayor a cero.")
            
            with c2:
                st.markdown("#### Movimientos Recientes")
                df_hist = run_query("""
                    SELECT p.id_referencia_banco as 'Ref. Banco', p.fecha_registro as 'Fecha', u.nombre_unidad as 'Activo', p.monto_pagado as 'Ingreso', p.estado_pago as 'Estatus'
                    FROM pagos p JOIN contratos c ON p.contrato_id = c.id JOIN unidades u ON c.unidad_id = u.id
                    ORDER BY p.id DESC LIMIT 10
                """)
                if not df_hist.empty:
                    df_hist['Ingreso'] = df_hist['Ingreso'].apply(fmt_cop)
                    st.dataframe(df_hist.style.applymap(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)
                else:
                    st.info("Sin registros de transacciones.")

    # ----------------------------------------
    # MÓDULO 5: DISPONIBILIDAD
    # ----------------------------------------
    elif mod == "vacancia":
        st.markdown("<h2>Índice de Disponibilidad (Vacancia) 🔑</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8;'>Monitoreo de activos libres para comercialización inmediata.</p>", unsafe_allow_html=True)
        
        df_libres = run_query("""
            SELECT p.nombre as 'Propiedad Matriz', u.nombre_unidad as 'Unidad Física', u.canon_base as 'Expectativa de Renta'
            FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id
            WHERE u.estado_vacancia = 'Disponible'
        """)
        
        if not df_libres.empty:
            st.markdown(f"""
            <div style="background: rgba(0,198,255,0.05); border: 1px solid rgba(0,198,255,0.3); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;">
                <h2 style="color:#00C6FF; margin:0;">{len(df_libres)} Activos Listos para Contrato</h2>
            </div>
            """, unsafe_allow_html=True)
            df_libres['Expectativa de Renta'] = df_libres['Expectativa de Renta'].apply(fmt_cop)
            st.dataframe(df_libres, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px;">
                <h1 style="color:#34D399; margin:0; font-size: 3rem;">100%</h1>
                <h3 style="color:#A7F3D0; margin:0;">Ocupación Total</h3>
                <p style="color:#64748B; margin-top: 10px;">Todos los activos físicos se encuentran rentando actualmente. Rentabilidad máxima operativa.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()