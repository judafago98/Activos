import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import pooling
import time
import datetime
from dateutil.relativedelta import relativedelta

# ==========================================
# 1. CONFIGURACIÓN GLOBAL
# ==========================================
st.set_page_config(page_title="Activos Pro", layout="wide", initial_sidebar_state="collapsed", page_icon="🏢")

# ==========================================
# 2. MOTOR CSS PREMIUM (GRIS PIZARRA & AZUL CIBERNÉTICO)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

        /* Fondo Gris Pizarra (Previene el efecto gelatina en pantallas OLED de iPhone) */
        .stApp { background-color: #1E293B !important; color: #F8FAFC !important; }
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #38BDF8; }

        *:focus { outline: none !important; box-shadow: none !important; }
        
        /* INPUTS Y SELECTS: GRIS PROFUNDO CON FOCUS CIAN */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"], .stDateInput > div {
            background-color: #0F172A !important; 
            border: 1px solid #334155 !important;
            border-radius: 8px !important; 
            color: #F8FAFC !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within, .stDateInput > div:focus-within {
            border-color: #38BDF8 !important; 
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important; 
            background-color: #1E293B !important;
        }
        input, select, textarea { color: #F8FAFC !important; background: transparent !important; outline: none !important; }
        li[role="option"] { color: #F8FAFC !important; }

        /* PESTAÑAS (TABS) - AZUL CIAN / CERO ROJO */
        div[data-testid="stTabs"] button[role="tab"] { color: #94A3B8 !important; font-weight: 600 !important; border-bottom: 2px solid transparent !important; background: transparent !important;}
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #38BDF8 !important; border-bottom-color: #38BDF8 !important; background: transparent !important;}
        div[data-baseweb="tab-highlight"] { display: none !important;}

        /* Formularios y Cajas con Sombra Suave */
        [data-testid="stForm"] {
            background: #0F172A !important; border: 1px solid #334155 !important;
            border-radius: 12px !important; padding: 30px !important; 
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
        }

        /* Botones Normales (Azul y Cian) */
        button[kind="secondary"] {
            background: linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%) !important;
            color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
            font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1px !important;
            padding: 0.6rem 1.5rem !important; transition: all 0.2s ease !important; width: 100% !important;
        }
        button[kind="secondary"]:hover {
            transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4) !important;
        }

        /* Botones de Destrucción (Único rojo permitido por seguridad) */
        button[kind="primary"] {
            background: linear-gradient(135deg, #EF4444 0%, #991B1B 100%) !important;
            color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
            font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1px !important;
            padding: 0.6rem 1.5rem !important; transition: all 0.2s ease !important; width: 100% !important;
        }
        button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 15px rgba(239, 68, 68, 0.4) !important; }

        /* Tarjetas de Métricas */
        [data-testid="stMetric"] { 
            background: #0F172A; border: 1px solid #334155; border-radius: 12px; padding: 20px; 
            border-top: 3px solid #3B82F6; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: transform 0.2s ease;
        }
        [data-testid="stMetric"]:hover { transform: translateY(-3px); border-top: 3px solid #38BDF8; box-shadow: 0 8px 15px rgba(0,0,0,0.3); }
        [data-testid="stMetric"] label { color: #94A3B8 !important; font-weight: 500 !important; }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #F8FAFC !important; }
        
        /* Dataframes Integrados */
        [data-testid="stDataFrame"] { background-color: #0F172A; border-radius: 8px; padding: 10px; border: 1px solid #334155; }
        
        /* Alertas limpias */
        [data-testid="stAlert"] { background-color: #0F172A !important; border: 1px solid #334155 !important; color: #F8FAFC !important; }
        
        /* Forzar color claro en textos base */
        h1, h2, h3, h4, p, span, div { color: #F8FAFC; }
        h1, h2, h3, h4 { font-weight: 700 !important; }
        .stMarkdown p { color: #CBD5E1 !important; }
    </style>
""", unsafe_allow_html=True)

def render_logo():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; background: #0F172A; border-radius: 12px; border: 1px solid #334155; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
            <h1 style='color: #F8FAFC; font-size: 1.8rem; font-weight: 800; letter-spacing: 2px; margin:0;'>🏢 ACTIVOS PRO</h1>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DATOS Y AUTO-HEALING
# ==========================================
@st.cache_resource
def get_pool():
    return pooling.MySQLConnectionPool(
        pool_name="activos_pool", pool_size=10, pool_reset_session=True,
        host=st.secrets["DB_HOST"], port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"], ssl_verify_cert=False, autocommit=True, connection_timeout=15, use_pure=True
    )

try: pool = get_pool()
except Exception as e: st.error(f"Falla de red: {e}"); st.stop()

def run_query(query, params=None):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    except Exception: return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

def run_transact(query, params=None):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit() 
        return True
    except Exception as e: st.error(f"Error DB: {e}"); return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

@st.cache_resource
def inicializar_bd():
    tablas = [
        "CREATE TABLE IF NOT EXISTS ap_usuarios (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS ap_propiedades (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150), direccion VARCHAR(255), activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS ap_unidades (id INT AUTO_INCREMENT PRIMARY KEY, propiedad_id INT, nombre_unidad VARCHAR(100), canon_base DECIMAL(15,2), estado_vacancia VARCHAR(50) DEFAULT 'Disponible', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS ap_inquilinos (id INT AUTO_INCREMENT PRIMARY KEY, documento_identidad VARCHAR(50) UNIQUE, nombre_completo VARCHAR(150), telefono VARCHAR(50))",
        "CREATE TABLE IF NOT EXISTS ap_contratos (id INT AUTO_INCREMENT PRIMARY KEY, unidad_id INT, inquilino_id INT, canon_pactado DECIMAL(15,2), dia_pago_mensual INT, fecha_inicio DATE, fecha_fin DATE, estado_contrato VARCHAR(50) DEFAULT 'Vigente')",
        "CREATE TABLE IF NOT EXISTS ap_pagos (id INT AUTO_INCREMENT PRIMARY KEY, contrato_id INT, periodo_pagado VARCHAR(20), monto_pagado DECIMAL(15,2), id_referencia_banco VARCHAR(100), fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado_pago VARCHAR(50) DEFAULT 'Aplicado')"
    ]
    for t in tablas: run_transact(t)
    if run_query("SELECT id FROM ap_usuarios WHERE username='admin'").empty:
        run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

inicializar_bd()

# ==========================================
# 4. UTILS FINANCIEROS Y DE CARTERA
# ==========================================
def fmt_cop(val):
    try: return f"${int(float(val)):,}".replace(',', '.')
    except: return "$0"

def generar_periodos_contrato(fecha_ini, fecha_fin):
    periodos = []
    actual = fecha_ini.replace(day=1)
    fin = fecha_fin.replace(day=1)
    while actual <= fin:
        periodos.append(actual.strftime("%Y-%m"))
        actual += relativedelta(months=1)
    return periodos

def get_color_estado(val):
    if val in ['Vigente', 'Aplicado', 'Ocupado', 'Activo']: return 'background-color: rgba(16, 185, 129, 0.15); color: #34D399; font-weight: bold;'
    if val in ['Cancelado', 'Finalizado', 'Anulado', 'Inactivo']: return 'background-color: rgba(239, 68, 68, 0.15); color: #EF4444; font-weight: bold;'
    if val in ['Disponible']: return 'background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; font-weight: bold;'
    return ''

# ==========================================
# 5. CONTROL DE ACCESO
# ==========================================
if 'logeado' not in st.session_state: st.session_state.update({'logeado': False, 'rol': None, 'nombre_usuario': None})

if not st.session_state['logeado']:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        render_logo()
        with st.form("login_form"):
            u = st.text_input("👤 Credencial Operativa")
            p = st.text_input("🔒 Hash de Seguridad", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Ingresar al Sistema"):
                df_u = run_query("SELECT nombre_completo, rol FROM ap_usuarios WHERE username=%s AND password=%s AND activo=TRUE", (u, p))
                if not df_u.empty:
                    st.session_state.update({'logeado': True, 'nombre_usuario': df_u.iloc[0]['nombre_completo'], 'rol': df_u.iloc[0]['rol']})
                    st.rerun()
                else: st.error("Acceso denegado. Verifique credenciales.")
    st.stop()

# ==========================================
# 6. ENRUTADOR SUPREMO (NAVBAR SUPERIOR MÓVIL)
# ==========================================
render_logo()

menu = {
    "📊 Panel General": "dash", 
    "🏢 Inmuebles y Activos": "activos", 
    "👥 Contratos": "contratos", 
    "💰 Tesorería": "tesoreria"
}
if st.session_state['rol'] == 'Administrador': 
    menu["⚙️ Seguridad e Inyección IAM"] = "seguridad"

c_nav, c_out = st.columns([5, 1])
with c_nav:
    nav_seleccionada = st.selectbox("MÓDULO DE OPERACIÓN", list(menu.keys()), label_visibility="collapsed")
    mod = menu[nav_seleccionada]
with c_out:
    if st.button("🚪 SALIR"):
        st.session_state['logeado'] = False; st.rerun()

st.divider()

# ==========================================
# 7. MÓDULOS OPERATIVOS
# ==========================================

# ----------------------------------------
# PANEL GENERAL
# ----------------------------------------
if mod == "dash":
    st.markdown("<h3>Mando Gerencial 📊</h3>", unsafe_allow_html=True)
    
    t_con = run_query("SELECT COUNT(*) as t FROM ap_contratos WHERE estado_contrato = 'Vigente'")
    t_ing = run_query("SELECT SUM(monto_pagado) as t FROM ap_pagos WHERE estado_pago = 'Aplicado'")
    df_libres = run_query("SELECT COUNT(*) as t FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
    
    df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, c.dia_pago_mensual, c.canon_pactado, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_propiedades p ON u.propiedad_id = p.id JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
    df_pagos_totales = run_query("SELECT contrato_id, periodo_pagado, SUM(monto_pagado) as total_pagado FROM ap_pagos GROUP BY contrato_id, periodo_pagado")
    
    pagos_dict = {}
    if not df_pagos_totales.empty:
        for _, r in df_pagos_totales.iterrows(): 
            pagos_dict[(r['contrato_id'], r['periodo_pagado'])] = float(r['total_pagado'])
            
    hoy = datetime.date.today()
    mes_actual_str = hoy.strftime("%Y-%m")
    mora_list = []
    deuda_total = 0.0

    if not df_activos.empty:
        for _, c in df_activos.iterrows():
            canon = float(c['canon_pactado'])
            periodos = generar_periodos_contrato(c['fecha_inicio'], c['fecha_fin'])
            for p in periodos:
                vencido = False
                if p < mes_actual_str: vencido = True
                elif p == mes_actual_str and hoy.day > int(c['dia_pago_mensual']): vencido = True
                
                if vencido:
                    pagado = pagos_dict.get((c['id'], p), 0.0)
                    if pagado < canon:
                        deuda_restante = canon - pagado
                        deuda_total += deuda_restante
                        dias_atraso = "Mes vencido"
                        if p == mes_actual_str: dias_atraso = f"{hoy.day - int(c['dia_pago_mensual'])} días"
                        
                        mora_list.append({
                            "Cliente / Deudor": c['nombre_completo'],
                            "Inmueble": f"{c['prop']} - {c['nombre_unidad']}",
                            "Periodo Vencido": p,
                            "Atraso": dias_atraso,
                            "Saldo en Mora": deuda_restante
                        })

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contratos Activos", f"{t_con.iloc[0]['t'] if not t_con.empty else 0}")
    c2.metric("Recaudo Histórico", fmt_cop(t_ing.iloc[0]['t'] if not t_ing.empty and pd.notna(t_ing.iloc[0]['t']) else 0))
    c3.metric("Cartera en Mora", fmt_cop(deuda_total))
    c4.metric("Unidades Disponibles", f"{df_libres.iloc[0]['t'] if not df_libres.empty else 0}")
    
    st.divider()
    t1, t2, t3 = st.tabs(["🚨 Centro de Cobros (Mora)", "🏢 Estado del Inventario", "📈 Radar de Transacciones"])
    
    with t1:
        st.markdown("#### Cuentas Pendientes por Cobrar Hoy")
        if mora_list:
            df_mora = pd.DataFrame(mora_list)
            df_mora['Saldo en Mora'] = df_mora['Saldo en Mora'].apply(fmt_cop)
            st.dataframe(df_mora, use_container_width=True, hide_index=True)
        else: st.success("🎉 Libro de cobros limpio. No hay deudores en mora.")
            
    with t2:
        ca, cb = st.columns(2)
        with ca:
            st.markdown("<h4 style='color:#38BDF8;'>Disponibles (Listas para rentar)</h4>", unsafe_allow_html=True)
            df_l = run_query("SELECT p.nombre as Estructura, u.nombre_unidad as Unidad, u.canon_base as 'Canon Base' FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
            if not df_l.empty:
                df_l['Canon Base'] = df_l['Canon Base'].apply(fmt_cop)
                st.dataframe(df_l, use_container_width=True, hide_index=True)
            else: st.info("Inventario ocupado al 100%.")
        with cb:
            st.markdown("<h4 style='color:#94A3B8;'>Inactivos / Fuera de Servicio</h4>", unsafe_allow_html=True)
            df_inact = run_query("SELECT p.nombre as Estructura, u.nombre_unidad as Unidad FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE u.activo = FALSE OR p.activo = FALSE")
            if not df_inact.empty: st.dataframe(df_inact, use_container_width=True, hide_index=True)
            else: st.info("Todos los complejos inmobiliarios están activos.")

    with t3:
        st.markdown("#### Historial Reciente de Caja")
        df_p = run_query("SELECT p.fecha_registro as Fecha, IFNULL(u.nombre_unidad, 'Unidad Borrada') as Origen, p.periodo_pagado as 'Periodo Cubierto', p.monto_pagado as Ingreso FROM ap_pagos p LEFT JOIN ap_contratos c ON p.contrato_id = c.id LEFT JOIN ap_unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 15")
        if not df_p.empty:
            df_p['Ingreso'] = df_p['Ingreso'].apply(fmt_cop)
            st.dataframe(df_p, use_container_width=True, hide_index=True)
        else: st.info("No hay transacciones registradas.")

# ----------------------------------------
# INMUEBLES Y ACTIVOS
# ----------------------------------------
elif mod == "activos":
    st.markdown("<h2>Gestión de Inmuebles 🏢</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🏛️ Propiedades Matrices", "🚪 Unidades Comerciales", "⚙️ Activar/Inactivar"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_p"):
                nom = st.text_input("Alias del Complejo")
                dir = st.text_input("Dirección Legal")
                if st.form_submit_button("Indexar Propiedad") and nom:
                    if run_transact("INSERT INTO ap_propiedades (nombre, direccion) VALUES (%s, %s)", (str(nom), str(dir))):
                        st.toast("Propiedad listada."); time.sleep(1); st.rerun()
        with c2:
            df_p = run_query("SELECT id as ID, nombre as Complejo, direccion as Dirección, IF(activo,'Activo','Inactivo') as Estado FROM ap_propiedades")
            if not df_p.empty: st.dataframe(df_p.style.map(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)

    with t2:
        df_props = run_query("SELECT id, nombre FROM ap_propiedades WHERE activo = TRUE")
        if df_props.empty: st.warning("Requiere matriz estructural activa.")
        else:
            c1, c2 = st.columns([1, 2], gap="large")
            opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
            with c1:
                with st.form("f_u"):
                    sel_p = st.selectbox("Nodo Padre:", list(opc_p.keys()))
                    n_uni = st.text_input("Nomenclatura (Ej: Local 1)")
                    can_b = st.number_input("Valor de Salida ($)", step=50000.0)
                    if st.form_submit_button("Liberar al Mercado") and n_uni:
                        if run_transact("INSERT INTO ap_unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (int(opc_p[sel_p]), str(n_uni), float(can_b))):
                            st.toast("Unidad en circulación."); time.sleep(1); st.rerun()
            with c2:
                df_u = run_query("SELECT p.nombre as Complejo, u.nombre_unidad as Unidad, u.canon_base as 'Tarifa', IF(u.activo,'Activo','Inactivo') as Operatividad, u.estado_vacancia as Vacancia FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                if not df_u.empty:
                    df_u['Tarifa'] = df_u['Tarifa'].apply(fmt_cop)
                    st.dataframe(df_u.style.map(get_color_estado, subset=['Operatividad', 'Vacancia']), use_container_width=True, hide_index=True)
                    
    with t3:
        colA, colB = st.columns(2)
        with colA:
            with st.form("f_tog_prop"):
                df_all_p = run_query("SELECT id, nombre, activo FROM ap_propiedades")
                if not df_all_p.empty:
                    sel_tog_p = st.selectbox("Seleccionar Propiedad", [f"[{'Activo' if r['activo'] else 'Inactivo'}] {r['nombre']}" for _, r in df_all_p.iterrows()])
                    if st.form_submit_button("Alternar Estado"):
                        nom_p = sel_tog_p.split("] ")[1]
                        nuevo_estado = 0 if "Activo" in sel_tog_p else 1
                        run_transact("UPDATE ap_propiedades SET activo = %s WHERE nombre = %s", (nuevo_estado, nom_p))
                        st.rerun()
        with colB:
            with st.form("f_tog_uni"):
                df_all_u = run_query("SELECT id, nombre_unidad, activo FROM ap_unidades")
                if not df_all_u.empty:
                    sel_tog_u = st.selectbox("Seleccionar Unidad", [f"[{'Activa' if r['activo'] else 'Inactiva'}] {r['nombre_unidad']}" for _, r in df_all_u.iterrows()])
                    if st.form_submit_button("Alternar Estado "):
                        nom_u = sel_tog_u.split("] ")[1]
                        nuevo_estado = 0 if "Activa" in sel_tog_u else 1
                        run_transact("UPDATE ap_unidades SET activo = %s WHERE nombre_unidad = %s", (nuevo_estado, nom_u))
                        st.rerun()

# ----------------------------------------
# CONTRATOS
# ----------------------------------------
elif mod == "contratos":
    st.markdown("<h2>Originación y Cierre Contractual 👥</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["👤 Identidades", "📄 Nuevo Contrato", "🛑 Terminación"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_i"):
                ced = st.text_input("Identidad Oficial (NIT/CC)")
                nom = st.text_input("Razón Social")
                tel = st.text_input("Enlace Móvil")
                if st.form_submit_button("Almacenar Nodo") and ced and nom:
                    if run_transact("INSERT INTO ap_inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (str(ced), str(nom), str(tel))):
                        st.toast("Cliente en red."); time.sleep(1); st.rerun()
        with c2:
            df_i = run_query("SELECT documento_identidad as ID, nombre_completo as Razón, telefono as Contacto FROM ap_inquilinos")
            if not df_i.empty: st.dataframe(df_i, use_container_width=True, hide_index=True)

    with t2:
        df_i = run_query("SELECT id, nombre_completo, documento_identidad FROM ap_inquilinos")
        df_u = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
        
        if df_i.empty or df_u.empty: st.warning("Requiere clientes y activos libres para operar.")
        else:
            with st.form("f_c"):
                ca, cb = st.columns(2)
                opc_i = {f"{r['documento_identidad']} - {r['nombre_completo']}": r['id'] for _, r in df_i.iterrows()}
                opc_u = {f"{r['nombre']} - {r['nombre_unidad']}": r['id'] for _, r in df_u.iterrows()}
                with ca:
                    sel_i = st.selectbox("Arrendatario", list(opc_i.keys()))
                    sel_u = st.selectbox("Activo Objetivo", list(opc_u.keys()))
                    dia = st.number_input("Día de Corte Mensual (Límite)", value=5, min_value=1, max_value=31)
                with cb:
                    can = st.number_input("Carga Monetaria Mensual ($)", step=50000.0)
                    fi = st.date_input("Fecha Inicio")
                    ff = st.date_input("Fecha Fin Teórica", value=fi + datetime.timedelta(days=365))
                
                if st.form_submit_button("Inyectar Contrato") and can > 0:
                    str_fi = fi.strftime('%Y-%m-%d')
                    str_ff = ff.strftime('%Y-%m-%d')
                    if run_transact("INSERT INTO ap_contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (int(opc_u[sel_u]), int(opc_i[sel_i]), float(can), int(dia), str_fi, str_ff)):
                        run_transact("UPDATE ap_unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (int(opc_u[sel_u]),))
                        st.toast("Contrato blindado."); time.sleep(1); st.rerun()
                        
    with t3:
        df_activos = run_query("SELECT c.id, c.unidad_id, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id=u.id JOIN ap_propiedades p ON u.propiedad_id=p.id JOIN ap_inquilinos i ON c.inquilino_id=i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("No hay contratos vigentes.")
        else:
            with st.form("f_kill"):
                opc_kill = {f"[{r['id']}] {r['prop']} - {r['nombre_unidad']} | {r['nombre_completo']}": (r['id'], r['unidad_id']) for _, r in df_activos.iterrows()}
                sel_kill = st.selectbox("Seleccionar contrato a terminar:", list(opc_kill.keys()))
                f_real = st.date_input("Fecha real de entrega del inmueble:")
                if st.form_submit_button("🛑 Ejecutar Terminación Definitiva", type="primary"):
                    id_con, id_uni = opc_kill[sel_kill]
                    str_f_real = f_real.strftime('%Y-%m-%d')
                    if run_transact("UPDATE ap_contratos SET estado_contrato = 'Finalizado', fecha_fin = %s WHERE id = %s", (str_f_real, int(id_con))):
                        run_transact("UPDATE ap_unidades SET estado_vacancia = 'Disponible' WHERE id = %s", (int(id_uni),))
                        st.toast("Contrato cerrado."); time.sleep(1.5); st.rerun()

# ----------------------------------------
# TESORERÍA
# ----------------------------------------
elif mod == "tesoreria":
    st.markdown("<h2>Tesorería 💰</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📥 Registrar Ingreso", "🗑️ Revertir Pagos"])
    
    with t1:
        df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_propiedades p ON u.propiedad_id = p.id JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("Sin contratos vigentes que auditar.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"{r['prop']} {r['uni']} - {r['inq']} (Canon: {fmt_cop(r['canon_pactado'])})": r for _, r in df_activos.iterrows()}
            
            with c1:
                sel_c = st.selectbox("Obligación Vigente", list(opc_c.keys()))
                dat_con = opc_c[sel_c]
                canon_base = float(dat_con['canon_pactado'])
                
                df_pagos_contrato = run_query("SELECT periodo_pagado, SUM(monto_pagado) as total_pagado FROM ap_pagos WHERE contrato_id = %s GROUP BY periodo_pagado", (int(dat_con['id']),))
                pagos_map = {row['periodo_pagado']: float(row['total_pagado']) for _, row in df_pagos_contrato.iterrows()} if not df_pagos_contrato.empty else {}
                
                periodos_todos = generar_periodos_contrato(dat_con['fecha_inicio'], dat_con['fecha_fin'])
                periodos_pendientes = []
                deuda_por_periodo = {}
                
                for p in periodos_todos:
                    pagado = pagos_map.get(p, 0.0)
                    pendiente = canon_base - pagado
                    if pendiente > 0:
                        periodos_pendientes.append(p)
                        deuda_por_periodo[p] = pendiente
                
                if not periodos_pendientes: st.success("Contrato completamente al día.")
                else:
                    with st.form("f_pago", clear_on_submit=True):
                        per_sel = st.selectbox("Periodo a Pagar", periodos_pendientes)
                        saldo_pendiente = float(deuda_por_periodo.get(per_sel, canon_base))
                        
                        monto = st.number_input("Capital Recibido ($)", min_value=0.0, max_value=saldo_pendiente, value=saldo_pendiente, step=10000.0)
                        ref = st.text_input("Referencia Bancaria")
                        
                        if st.form_submit_button("Asentar Transacción") and monto > 0:
                            with st.spinner("Confirmando..."):
                                if run_transact("INSERT INTO ap_pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco) VALUES (%s, %s, %s, %s)", (int(dat_con['id']), str(per_sel), float(monto), str(ref))):
                                    st.toast("Pago registrado."); time.sleep(1); st.rerun()
            with c2:
                df_hist = run_query("SELECT p.fecha_registro as Timestamp, IFNULL(u.nombre_unidad, 'Borrado') as Origen, p.periodo_pagado as Periodo, p.monto_pagado as Volumen FROM ap_pagos p LEFT JOIN ap_contratos c ON p.contrato_id = c.id LEFT JOIN ap_unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 15")
                if not df_hist.empty:
                    df_hist['Volumen'] = df_hist['Volumen'].apply(fmt_cop)
                    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    with t2:
        df_pagos_del = run_query("SELECT p.id, p.fecha_registro, p.monto_pagado, IFNULL(u.nombre_unidad, 'Desconocido') as nombre_unidad, IFNULL(i.nombre_completo, 'Desconocido') as nombre_completo, p.periodo_pagado FROM ap_pagos p LEFT JOIN ap_contratos c ON p.contrato_id = c.id LEFT JOIN ap_unidades u ON c.unidad_id = u.id LEFT JOIN ap_inquilinos i ON c.inquilino_id = i.id ORDER BY p.id DESC LIMIT 50")
        if not df_pagos_del.empty:
            with st.form("f_del_pago"):
                opc_p = {f"[{str(r['fecha_registro'])[:10]}] {r['nombre_unidad']} - {r['nombre_completo']} | {r['periodo_pagado']} | {fmt_cop(r['monto_pagado'])}": r['id'] for _, r in df_pagos_del.iterrows()}
                sel_p = st.selectbox("Seleccionar Pago a Revertir", list(opc_p.keys()))
                if st.form_submit_button("🗑️ Eliminar Pago de Base de Datos", type="primary"):
                    if run_transact("DELETE FROM ap_pagos WHERE id = %s", (int(opc_p[sel_p]),)):
                        st.toast("Pago eliminado."); time.sleep(1); st.rerun()
        else: st.info("No hay pagos registrados.")

# ----------------------------------------
# SEGURIDAD IAM (Y DATA SEMILLA)
# ----------------------------------------
elif mod == "seguridad":
    st.markdown("<h2>Seguridad IAM ⚙️</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🛡️ Control de Nodos", "🌱 Data Semilla (Pruebas)"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_u", clear_on_submit=True):
                nu = st.text_input("Alias")
                np = st.text_input("Hash Secreto", type="password")
                nn = st.text_input("Nombre Real")
                nr = st.selectbox("Jerarquía", ["Administrador", "Asesor Comercial"])
                if st.form_submit_button("Crear Perfil") and nu and np:
                    if run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (str(nu), str(np), str(nn), str(nr))):
                        st.toast("Usuario guardado."); time.sleep(1); st.rerun()
        with c2:
            df_u = run_query("SELECT username as Alias, nombre_completo as Nombre, rol as Privilegios, IF(activo, 'Activo', 'Inactivo') as Estado FROM ap_usuarios")
            if not df_u.empty: st.dataframe(df_u.style.map(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)
            
    with t2:
        st.markdown("#### Generador Masivo de Infraestructura y Clientes")
        st.write("Este comando inyectará de golpe 5 Torres comerciales, 20 Suites de apartamentos e inquilinos corporativos con historial financiero cruzado.")
        if st.button("🚀 INYECTAR 5 EDIFICIOS Y CONTRATOS (DEMO)"):
            with st.spinner("Minando infraestructura de prueba..."):
                # 1. Inyectar Propiedades y Unidades
                for i in range(1, 6):
                    run_transact("INSERT INTO ap_propiedades (nombre, direccion) VALUES (%s, %s)", (f"Torre Omega {i}", f"Distrito Financiero #{i}"))
                    pid = run_query("SELECT id FROM ap_propiedades ORDER BY id DESC LIMIT 1").iloc[0]['id']
                    for j in range(1, 5):
                        run_transact("INSERT INTO ap_unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (int(pid), f"Apto {j}01", float(700000 + (j*100000))))
                
                # 2. Inyectar Inquilinos
                nombres = ["Bruce Wayne", "Tony Stark", "Lex Luthor", "Oliver Queen", "Norman Osborn"]
                for i, nom in enumerate(nombres):
                    run_transact("INSERT INTO ap_inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (f"NIT-9004{i}", nom, f"+57 300 440{i}"))
                
                # 3. Firmar Contratos con desfase temporal para provocar alarmas de Mora
                clientes_id = run_query("SELECT id FROM ap_inquilinos ORDER BY id DESC LIMIT 5")['id'].tolist()
                unidades_id = run_query("SELECT id, canon_base FROM ap_unidades WHERE estado_vacancia='Disponible' LIMIT 5")
                hoy = datetime.date.today()
                
                for idx, row in unidades_id.iterrows():
                    # Hace 2 meses para que el algoritmo detecte deudas anteriores
                    f_ini = (hoy - relativedelta(months=2)).strftime('%Y-%m-%d')
                    f_fin = (hoy + relativedelta(months=10)).strftime('%Y-%m-%d')
                    uid = int(row['id'])
                    cid = int(clientes_id[idx])
                    canon = float(row['canon_base'])
                    
                    run_transact("INSERT INTO ap_contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (uid, cid, canon, 5, f_ini, f_fin))
                    run_transact("UPDATE ap_unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (uid,))
                    
                    # El primer cliente abona algo, los otros quedan en mora absoluta
                    con_id = run_query("SELECT id FROM ap_contratos ORDER BY id DESC LIMIT 1").iloc[0]['id']
                    if idx == 0: 
                        per_pago = (hoy - relativedelta(months=2)).strftime('%Y-%m')
                        run_transact("INSERT INTO ap_pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco) VALUES (%s, %s, %s, %s)", (int(con_id), per_pago, canon, "COBRO-SEDE-CENTRAL"))
                
                st.success("✅ Estructuras indexadas. Dirígete al módulo 'Panel General' para validar el cobrador de mora.")
                time.sleep(1.5)
                st.rerun()
