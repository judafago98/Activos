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
st.set_page_config(page_title="Activos Pro | Asset Management", layout="wide", initial_sidebar_state="expanded", page_icon="🏢")

# ==========================================
# 2. MOTOR CSS ULTRA PREMIUM Y ANTI-BORDES ROJOS
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

        /* Fondo Cibernético y Oscuro */
        .stApp {
            background-color: #020617 !important;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 229, 255, 0.15) 0%, transparent 50%),
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px) !important;
            background-size: 100% 100%, 40px 40px, 40px 40px !important;
            color: #F8FAFC !important;
        }
        
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 229, 255, 0.3); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0, 229, 255, 0.8); }

        /* ELIMINAR BORDES ROJOS Y APLICAR NEÓN */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
            background-color: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #00E5FF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important;
            background-color: rgba(10, 15, 30, 0.9) !important;
        }
        input, select, textarea { color: white !important; outline: none !important; background: transparent !important; }

        /* Formularios Glassmorphism */
        [data-testid="stForm"] {
            background: rgba(10, 15, 30, 0.6) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 229, 255, 0.2) !important;
            border-radius: 16px !important;
            padding: 30px !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5) !important;
        }

        /* Botones Premium con Degradado */
        .stButton>button {
            background: linear-gradient(135deg, #0052D4 0%, #4364F7 50%, #6FB1FC 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            padding: 0.7rem 1.5rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 15px rgba(0, 82, 212, 0.4) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 229, 255, 0.6) !important;
            background: linear-gradient(135deg, #4364F7 0%, #00E5FF 100%) !important;
        }

        /* Sidebar Responsive / Modo Celular */
        [data-testid="stSidebar"] {
            background-color: rgba(3, 7, 18, 0.9) !important;
            backdrop-filter: blur(25px) !important;
            border-right: 1px solid rgba(0, 229, 255, 0.15) !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(15, 23, 42, 0.4) !important;
            border-radius: 10px !important;
            padding: 12px 16px !important; margin: 4px 8px !important;
            transition: all 0.3s ease !important; cursor: pointer !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label div[data-baseweb="radio"] { display: none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label p { color: #8B9BB4 !important; font-weight: 600 !important; margin: 0 !important; }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(0, 229, 255, 0.2) 0%, transparent 100%) !important;
            border-left: 3px solid #00E5FF !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] p { color: #FFFFFF !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5) !important; }

        /* Tarjetas (Metrics) */
        [data-testid="stMetric"] { 
            background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 229, 255, 0.2); 
            border-radius: 16px; padding: 20px; border-top: 3px solid #00E5FF; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.3); transition: transform 0.3s ease;
        }
        [data-testid="stMetric"]:hover { transform: translateY(-5px); border-top: 3px solid #34D399; }
        
        [data-testid="stDataFrame"] { background-color: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 10px; border: 1px solid rgba(255,255,255,0.05); }
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

def render_logo():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, rgba(2, 6, 23, 0.8), rgba(0, 20, 40, 0.6)); border-radius: 16px; border: 1px solid rgba(0, 229, 255, 0.3); padding: 20px; box-shadow: inset 0 0 15px rgba(0, 229, 255, 0.05); margin-bottom: 20px;'>
            <h1 style='color: #FFFFFF; font-size: 2rem; font-weight: 800; letter-spacing: 2px; margin:0; text-shadow: 0px 0px 15px rgba(0, 229, 255, 0.7);'>🏢 ACTIVOS PRO</h1>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DATOS (POOLING MULTI-SESIÓN)
# ==========================================
@st.cache_resource
def get_pool():
    return pooling.MySQLConnectionPool(
        pool_name="activos_pool", pool_size=10, pool_reset_session=True,
        host=st.secrets["DB_HOST"], port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"], ssl_verify_cert=False,
        autocommit=True, connection_timeout=15, use_pure=True
    )

try: pool = get_pool()
except Exception as e: st.error(f"Falla de red matriz: {e}"); st.stop()

def run_query(query, params=None):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    except Exception as e: return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

def run_transact(query, params=None):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        return True
    except Exception as e: st.error(f"Error DML: {e}"); return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# --- AUTO HEALING (Crea las tablas si no existen para evitar módulos vacíos) ---
def inicializar_bd():
    tablas = [
        "CREATE TABLE IF NOT EXISTS Usuarios (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS Propiedades (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150), direccion VARCHAR(255))",
        "CREATE TABLE IF NOT EXISTS Unidades (id INT AUTO_INCREMENT PRIMARY KEY, propiedad_id INT, nombre_unidad VARCHAR(100), canon_base DECIMAL(15,2), estado_vacancia VARCHAR(50) DEFAULT 'Disponible')",
        "CREATE TABLE IF NOT EXISTS Inquilinos (id INT AUTO_INCREMENT PRIMARY KEY, documento_identidad VARCHAR(50) UNIQUE, nombre_completo VARCHAR(150), telefono VARCHAR(50))",
        "CREATE TABLE IF NOT EXISTS Contratos (id INT AUTO_INCREMENT PRIMARY KEY, unidad_id INT, inquilino_id INT, canon_pactado DECIMAL(15,2), dia_pago_mensual INT, fecha_inicio DATE, fecha_fin DATE, estado_contrato VARCHAR(50) DEFAULT 'Vigente')",
        "CREATE TABLE IF NOT EXISTS Pagos (id INT AUTO_INCREMENT PRIMARY KEY, contrato_id INT, periodo_pagado VARCHAR(20), monto_pagado DECIMAL(15,2), id_referencia_banco VARCHAR(100), fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado_pago VARCHAR(50) DEFAULT 'Aplicado')"
    ]
    for t in tablas: run_transact(t)
    if run_query("SELECT id FROM Usuarios WHERE username='admin'").empty:
        run_transact("INSERT INTO Usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

inicializar_bd()

# ==========================================
# 4. FUNCIONES DE LÓGICA DE NEGOCIO
# ==========================================
def fmt_cop(val):
    try: return f"${int(float(val)):,}".replace(',', '.')
    except: return "$0"

def get_color_estado(val):
    if val in ['Vigente', 'Aplicado', 'Ocupado', 'Activo']: return 'background-color: rgba(16, 185, 129, 0.15); color: #34D399; font-weight: bold;'
    if val in ['Cancelado', 'Finalizado', 'Anulado', 'Inactivo']: return 'background-color: rgba(245, 158, 11, 0.15); color: #F87171; font-weight: bold;'
    if val in ['Disponible']: return 'background-color: rgba(0, 229, 255, 0.15); color: #00E5FF; font-weight: bold;'
    return ''

def generar_periodos_contrato(fecha_ini, fecha_fin):
    periodos = []
    actual = fecha_ini.replace(day=1)
    fin = fecha_fin.replace(day=1)
    while actual <= fin:
        periodos.append(actual.strftime("%Y-%m"))
        actual += relativedelta(months=1)
    return periodos

# ==========================================
# 5. CONTROL DE SESIÓN
# ==========================================
if 'logeado' not in st.session_state:
    st.session_state.update({'logeado': False, 'rol': None, 'nombre_usuario': None})

if not st.session_state['logeado']:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        render_logo()
        with st.form("login_form"):
            u = st.text_input("👤 Credencial Operativa")
            p = st.text_input("🔒 Hash de Seguridad", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Inicializar Enlace"):
                df_u = run_query("SELECT nombre_completo, rol FROM Usuarios WHERE username=%s AND password=%s AND activo=TRUE", (u, p))
                if not df_u.empty:
                    st.session_state.update({'logeado': True, 'nombre_usuario': df_u.iloc[0]['nombre_completo'], 'rol': df_u.iloc[0]['rol']})
                    st.rerun()
                else: st.error("Acceso denegado.")
    st.stop()

# ==========================================
# 6. ENRUTADOR PRINCIPAL (APP)
# ==========================================
with st.sidebar:
    render_logo()
    st.markdown(f"<div style='background: rgba(0,229,255,0.1); border: 1px solid rgba(0,229,255,0.3); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px;'><b style='color:white;'>{st.session_state['nombre_usuario']}</b><br><span style='color:#00E5FF; font-size:12px; font-weight:bold;'>{st.session_state['rol'].upper()}</span></div>", unsafe_allow_html=True)
    
    menu = {"📊 Centro de Mando": "dash", "🏢 Nodos Físicos (Propiedades)": "activos", "👥 Originación Contractual": "contratos", "💰 Hub de Tesorería": "tesoreria", "🔑 Vacancia y Disponibilidad": "vacancia"}
    if st.session_state['rol'] == 'Administrador': menu["⚙️ Core IAM (Seguridad)"] = "seguridad"
    
    mod = menu[st.radio("Navegación", list(menu.keys()), label_visibility="collapsed")]
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Cortar Enlace (Salir)"):
        st.session_state['logeado'] = False; st.rerun()

# ----------------------------------------
# DASHBOARD
# ----------------------------------------
if mod == "dash":
    st.markdown("<h2>Mando Gerencial 📊</h2>", unsafe_allow_html=True)
    t_con = run_query("SELECT COUNT(*) as t FROM Contratos WHERE estado_contrato = 'Vigente'")
    t_ing = run_query("SELECT SUM(monto_pagado) as t FROM Pagos WHERE estado_pago = 'Aplicado'")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🏢 Contratos Activos", f"{t_con.iloc[0]['t'] if not t_con.empty else 0}")
    c2.metric("💰 Absorción de Caja", fmt_cop(t_ing.iloc[0]['t'] if not t_ing.empty and pd.notna(t_ing.iloc[0]['t']) else 0))
    c3.metric("🟢 Servidor", "Sincronizado y Estable")
    
    st.divider()
    st.markdown("#### Radar de Transacciones")
    df_p = run_query("SELECT p.fecha_registro as Fecha, u.nombre_unidad as Unidad, p.periodo_pagado as 'Periodo Cubierto', p.monto_pagado as Ingreso, p.estado_pago as Estado FROM Pagos p JOIN Contratos c ON p.contrato_id = c.id JOIN Unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 8")
    if not df_p.empty:
        df_p['Ingreso'] = df_p['Ingreso'].apply(fmt_cop)
        st.dataframe(df_p.style.map(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)
    else: st.info("Registro contable en ceros.")

# ----------------------------------------
# ACTIVOS
# ----------------------------------------
elif mod == "activos":
    st.markdown("<h2>Gestión de Activos 🏢</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🏛️ Estructuras Base", "🚪 Sub-Unidades Comerciales"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_p"):
                nom = st.text_input("Alias del Complejo")
                dir = st.text_input("Dirección Legal")
                if st.form_submit_button("Indexar Propiedad") and nom:
                    if run_transact("INSERT INTO Propiedades (nombre, direccion) VALUES (%s, %s)", (nom, dir)):
                        st.toast("Propiedad listada.", icon="✅"); time.sleep(1); st.rerun()
        with c2:
            df_p = run_query("SELECT id as ID, nombre as Complejo, direccion as Dirección FROM Propiedades")
            if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

    with t2:
        df_props = run_query("SELECT id, nombre FROM Propiedades")
        if df_props.empty: st.warning("Requiere matriz estructural inicial.")
        else:
            c1, c2 = st.columns([1, 2], gap="large")
            opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
            with c1:
                with st.form("f_u"):
                    sel_p = st.selectbox("Nodo Padre:", list(opc_p.keys()))
                    n_uni = st.text_input("Nomenclatura (Ej: Local 1)")
                    can_b = st.number_input("Valor de Salida ($)", step=50000)
                    if st.form_submit_button("Liberar al Mercado") and n_uni:
                        if run_transact("INSERT INTO Unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (opc_p[sel_p], n_uni, can_b)):
                            st.toast("Unidad en circulación.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_u = run_query("SELECT p.nombre as Complejo, u.nombre_unidad as Unidad, u.canon_base as 'Tarifa', u.estado_vacancia as Estado FROM Unidades u JOIN Propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                if not df_u.empty:
                    df_u['Tarifa'] = df_u['Tarifa'].apply(fmt_cop)
                    st.dataframe(df_u.style.map(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)

# ----------------------------------------
# CONTRATOS E INQUILINOS (Y FINALIZAR)
# ----------------------------------------
elif mod == "contratos":
    st.markdown("<h2>Originación y Cierre Contractual 👥</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["👤 Identidades Clientes", "📄 Despliegue de Contrato", "🛑 Liquidación Anticipada (Corte)"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_i"):
                ced = st.text_input("Identidad Oficial (NIT/CC)")
                nom = st.text_input("Razón Social")
                tel = st.text_input("Enlace Móvil")
                if st.form_submit_button("Almacenar Nodo") and ced and nom:
                    if run_transact("INSERT INTO Inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (ced, nom, tel)):
                        st.toast("Cliente en red.", icon="✅"); time.sleep(1); st.rerun()
        with c2:
            df_i = run_query("SELECT documento_identidad as ID, nombre_completo as Razón, telefono as Contacto FROM Inquilinos")
            if not df_i.empty: st.dataframe(df_i, use_container_width=True, hide_index=True)

    with t2:
        df_i = run_query("SELECT id, nombre_completo, documento_identidad FROM Inquilinos")
        df_u = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM Unidades u JOIN Propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
        if df_i.empty or df_u.empty: st.warning("El despliegue requiere clientes y activos libres en el sistema.")
        else:
            with st.form("f_c"):
                ca, cb = st.columns(2)
                opc_i = {f"{r['documento_identidad']} - {r['nombre_completo']}": r['id'] for _, r in df_i.iterrows()}
                opc_u = {f"{r['nombre']} - {r['nombre_unidad']}": r['id'] for _, r in df_u.iterrows()}
                with ca:
                    sel_i = st.selectbox("Arrendatario", list(opc_i.keys()))
                    sel_u = st.selectbox("Activo Objetivo", list(opc_u.keys()))
                    dia = st.number_input("Día de Corte Mensual", value=5, min_value=1, max_value=31)
                with cb:
                    can = st.number_input("Carga Monetaria ($)", step=50000)
                    fi = st.date_input("Encendido")
                    ff = st.date_input("Caducidad", value=fi + datetime.timedelta(days=365))
                if st.form_submit_button("Inyectar Contrato") and can > 0:
                    if run_transact("INSERT INTO Contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (opc_u[sel_u], opc_i[sel_i], can, dia, fi, ff)):
                        run_transact("UPDATE Unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (opc_u[sel_u],))
                        st.toast("Contrato blindado.", icon="📜"); time.sleep(1); st.rerun()
                        
    with t3:
        st.markdown("<br><p style='color:#F87171; font-weight:bold;'>Advertencia: Esta acción anula el contrato vigente y libera inmediatamente el inmueble.</p>", unsafe_allow_html=True)
        df_activos = run_query("SELECT c.id, c.unidad_id, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM Contratos c JOIN Unidades u ON c.unidad_id=u.id JOIN Propiedades p ON u.propiedad_id=p.id JOIN Inquilinos i ON c.inquilino_id=i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("No hay contratos vigentes para cortar.")
        else:
            with st.form("f_kill"):
                opc_kill = {f"[{r['id']}] {r['prop']} - {r['nombre_unidad']} | {r['nombre_completo']}": (r['id'], r['unidad_id']) for _, r in df_activos.iterrows()}
                sel_kill = st.selectbox("Seleccionar enlace a destruir:", list(opc_kill.keys()))
                if st.form_submit_button("🛑 Ejecutar Terminación Definitiva"):
                    id_con, id_uni = opc_kill[sel_kill]
                    if run_transact("UPDATE Contratos SET estado_contrato = 'Finalizado' WHERE id = %s", (id_con,)):
                        run_transact("UPDATE Unidades SET estado_vacancia = 'Disponible' WHERE id = %s", (id_uni,))
                        st.toast("Contrato destruido. Unidad liberada.", icon="✅"); time.sleep(1.5); st.rerun()

# ----------------------------------------
# TESORERÍA CON CONCATENADO DE MES Y AÑO
# ----------------------------------------
elif mod == "tesoreria":
    st.markdown("<h2>Hub de Tesorería Dinámica 💰</h2>", unsafe_allow_html=True)
    df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM Contratos c JOIN Unidades u ON c.unidad_id = u.id JOIN Propiedades p ON u.propiedad_id = p.id JOIN Inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
    
    if df_activos.empty: st.info("Sin contratos vigentes que auditar.")
    else:
        c1, c2 = st.columns([1.2, 2], gap="large")
        opc_c = {f"{r['prop']} {r['uni']} - {r['inq']} (Debe: {fmt_cop(r['canon_pactado'])})": r for _, r in df_activos.iterrows()}
        
        with c1:
            sel_c = st.selectbox("Seleccionar Obligación Vigente", list(opc_c.keys()))
            dat_con = opc_c[sel_c]
            
            # MAGIA: Generación del concatenado exacto del ciclo del contrato
            periodos_validos = generar_periodos_contrato(dat_con['fecha_inicio'], dat_con['fecha_fin'])
            
            with st.form("f_pago", clear_on_submit=True):
                st.markdown("<h4 style='color:#00E5FF;'>Absorber Fondos</h4>", unsafe_allow_html=True)
                per_sel = st.selectbox("Periodo Contractual Restante (Año-Mes)", periodos_validos)
                monto = st.number_input("Inyección de Capital ($)", step=50000, value=float(dat_con['canon_pactado']))
                ref = st.text_input("Hash Bancario (Ref/Nequi)")
                if st.form_submit_button("Asentar Transacción") and monto > 0:
                    if run_transact("INSERT INTO Pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco) VALUES (%s, %s, %s, %s)", (dat_con['id'], per_sel, monto, ref)):
                        st.toast("Bloque indexado en caja.", icon="✅"); time.sleep(1); st.rerun()
        with c2:
            df_hist = run_query("SELECT p.fecha_registro as Timestamp, u.nombre_unidad as Origen, p.periodo_pagado as Periodo, p.monto_pagado as Volumen, p.estado_pago as Estado FROM Pagos p JOIN Contratos c ON p.contrato_id = c.id JOIN Unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 10")
            if not df_hist.empty:
                df_hist['Volumen'] = df_hist['Volumen'].apply(fmt_cop)
                st.dataframe(df_hist.style.map(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)

# ----------------------------------------
# VACANCIA
# ----------------------------------------
elif mod == "vacancia":
    st.markdown("<h2>Mapeo de Disponibilidad 🔑</h2>", unsafe_allow_html=True)
    df_l = run_query("SELECT p.nombre as Estructura, u.nombre_unidad as Unidad, u.canon_base as 'Canon Mercado' FROM Unidades u JOIN Propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
    if not df_l.empty:
        df_l['Canon Mercado'] = df_l['Canon Mercado'].apply(fmt_cop)
        st.dataframe(df_l, use_container_width=True, hide_index=True)
    else: st.success("Rentabilidad máxima operativa. Cero vacancia en la red.")

# ----------------------------------------
# SEGURIDAD IAM
# ----------------------------------------
elif mod == "seguridad":
    st.markdown("<h2>Seguridad y Nodos IAM ⚙️</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        with st.form("f_u", clear_on_submit=True):
            nu = st.text_input("Alias")
            np = st.text_input("Hash Secreto", type="password")
            nn = st.text_input("Identidad Oficial")
            nr = st.selectbox("Jerarquía", ["Administrador", "Asesor Comercial"])
            if st.form_submit_button("Inyectar Permisos") and nu and np:
                if run_transact("INSERT INTO Usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (nu, np, nn, nr)):
                    st.toast("Identidad blindada.", icon="✅"); time.sleep(1); st.rerun()
    with c2:
        df_u = run_query("SELECT username as Alias, nombre_completo as Identidad, rol as Privilegios, IF(activo, 'Activo', 'Inactivo') as Estatus FROM Usuarios")
        if not df_u.empty: st.dataframe(df_u.style.map(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)
