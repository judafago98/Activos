import os
import uuid
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import pooling
import time
import datetime
from dateutil.relativedelta import relativedelta

# ==========================================
# 1. CONFIGURACIÓN GLOBAL Y DIRECTORIOS
# ==========================================
st.set_page_config(page_title="Gestión de Activos", layout="wide", initial_sidebar_state="collapsed", page_icon="🏢")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================
# 2. INYECCIÓN NUCLEAR DE TEMA CLARO
# ==========================================
def inyectar_tema_nativo():
    config_dir = ".streamlit"
    config_path = f"{config_dir}/config.toml"
    tema_config = """
[theme]
base="light"
primaryColor="#2563EB"
backgroundColor="#F4F7F9"
secondaryBackgroundColor="#FFFFFF"
textColor="#0F172A"
font="sans serif"
"""
    os.makedirs(config_dir, exist_ok=True)
    necesita_reinicio = False
    if not os.path.exists(config_path):
        with open(config_path, "w") as f: f.write(tema_config)
        necesita_reinicio = True
    else:
        with open(config_path, "r") as f:
            if 'primaryColor="#2563EB"' not in f.read():
                with open(config_path, "w") as fw: fw.write(tema_config)
                necesita_reinicio = True
    if necesita_reinicio: st.rerun()

inyectar_tema_nativo()

# ==========================================
# 3. MOTOR CSS
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        
        button[kind="secondary"] {
            background: linear-gradient(135deg, #2563EB 0%, #06B6D4 100%) !important;
            color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
            font-weight: 700 !important; text-transform: uppercase !important; transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important; }

        button[kind="primary"] {
            background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%) !important;
            color: #FFFFFF !important; border: none !important; border-radius: 8px !important;
            font-weight: 700 !important; text-transform: uppercase !important; transition: all 0.2s ease !important;
        }
        button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important; }

        [data-testid="stMetric"] { 
            background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important; padding: 20px !important; 
            border-top: 4px solid #2563EB !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important; transition: transform 0.2s ease !important;
        }
        [data-testid="stMetric"]:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 16px rgba(0,0,0,0.08) !important; border-top: 4px solid #06B6D4 !important;}
        
        div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 10px; background: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);}
        div.row-widget.stRadio > div > label { background-color: #F8FAFC !important; padding: 10px 20px !important; border-radius: 8px !important; cursor: pointer !important; border: 1px solid #E2E8F0 !important; }
        div.row-widget.stRadio > div > label:hover { background-color: #E2E8F0 !important; }
        div.row-widget.stRadio > div > label[data-checked="true"] { background-color: #EFF6FF !important; border: 1px solid #BFDBFE !important; }
        div.row-widget.stRadio > div > label p { color: #475569 !important; font-weight: 600 !important; margin: 0 !important; }
        div.row-widget.stRadio > div > label[data-checked="true"] p { color: #1D4ED8 !important; font-weight: 800 !important; }
        div.row-widget.stRadio > div > label div[data-baseweb="radio"] { display: none !important; }
        
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05) !important; padding: 10px !important;
        }
        [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

def render_logo():
    col1, col2 = st.columns([3, 1], vertical_alignment="center")
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=220)
        else: st.markdown("<h1 style='color: #2563EB; font-size: 2.2rem; font-weight: 800; margin:0;'>🏢 GESTIÓN DE ACTIVOS</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align: right; background: #FFFFFF; padding: 10px 15px; border-radius: 8px; border: 1px solid #E2E8F0;'><b style='color:#0F172A;'>{st.session_state.get('nombre_usuario', '')}</b><br><span style='color:#2563EB; font-size:11px; font-weight:bold;'>{st.session_state.get('rol', '').upper()}</span></div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #E2E8F0;'>", unsafe_allow_html=True)

def estilizar_df(df):
    if df.empty: return df
    return df.style.set_properties(**{'background-color': '#FFFFFF', 'color': '#0F172A', 'border-color': '#E2E8F0', 'font-family': 'Outfit'})

def guardar_archivo(uploaded_file):
    if uploaded_file is None: return None
    file_ext = uploaded_file.name.split('.')[-1]
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# ==========================================
# 4. BASE DE DATOS Y AUTO-HEALING
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
    df_check = run_query("SHOW TABLES LIKE 'ap_contratos'")
    if not df_check.empty:
        df_cols = run_query("SHOW COLUMNS FROM ap_contratos LIKE 'url_contrato'")
        if df_cols.empty:
            run_transact("DROP TABLE IF EXISTS ap_pagos, ap_contratos, ap_unidades, ap_propiedades, ap_usuarios, ap_inquilinos")

    tablas = [
        "CREATE TABLE IF NOT EXISTS ap_inquilinos (id INT AUTO_INCREMENT PRIMARY KEY, documento_identidad VARCHAR(50) UNIQUE, nombre_completo VARCHAR(150), telefono VARCHAR(50))",
        "CREATE TABLE IF NOT EXISTS ap_usuarios (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE, inquilino_id INT NULL)",
        "CREATE TABLE IF NOT EXISTS ap_propiedades (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150), direccion VARCHAR(255), activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS ap_unidades (id INT AUTO_INCREMENT PRIMARY KEY, propiedad_id INT, nombre_unidad VARCHAR(100), canon_base DECIMAL(15,2), estado_vacancia VARCHAR(50) DEFAULT 'Disponible', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS ap_contratos (id INT AUTO_INCREMENT PRIMARY KEY, unidad_id INT, inquilino_id INT, canon_pactado DECIMAL(15,2), dia_pago_mensual INT, fecha_inicio DATE, fecha_fin DATE, estado_contrato VARCHAR(50) DEFAULT 'Vigente', url_contrato VARCHAR(500) NULL)",
        "CREATE TABLE IF NOT EXISTS ap_pagos (id INT AUTO_INCREMENT PRIMARY KEY, contrato_id INT, periodo_pagado VARCHAR(20), monto_pagado DECIMAL(15,2), id_referencia_banco VARCHAR(100), fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, fecha_pago_real DATE NULL, url_comprobante VARCHAR(500) NULL, estado_pago VARCHAR(50) DEFAULT 'Aprobado')"
    ]
    for t in tablas: run_transact(t)
    if run_query("SELECT id FROM ap_usuarios WHERE username='admin'").empty:
        run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

inicializar_bd()

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

# ==========================================
# 5. LOGIN Y ENRUTADOR SUPREMO
# ==========================================
if 'logeado' not in st.session_state: st.session_state.update({'logeado': False, 'rol': None, 'nombre_usuario': None, 'inquilino_id': None})

if not st.session_state['logeado']:
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if os.path.exists("logo.png"): st.image("logo.png", width=300)
        else: st.markdown("<h1 style='color: #2563EB; text-align: center; font-size: 3rem;'>🏢 GESTIÓN DE ACTIVOS</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            u = st.text_input("👤 Identidad de Usuario (NIT/Cédula para Inquilinos)")
            p = st.text_input("🔒 Contraseña", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Ingresar al Sistema", type="secondary"):
                df_u = run_query("SELECT nombre_completo, rol, inquilino_id FROM ap_usuarios WHERE username=%s AND password=%s AND activo=TRUE", (u, p))
                if not df_u.empty:
                    inq_raw = df_u.iloc[0]['inquilino_id']
                    inq_val = int(inq_raw) if pd.notna(inq_raw) else None
                    
                    st.session_state.update({
                        'logeado': True, 
                        'nombre_usuario': df_u.iloc[0]['nombre_completo'], 
                        'rol': df_u.iloc[0]['rol'], 
                        'inquilino_id': inq_val
                    })
                    st.rerun()
                else: st.error("Acceso denegado. Verifique credenciales.")
    st.stop()

render_logo()

# LÓGICA DE MULTI-TENANT: Permisos de navegación
if st.session_state['rol'] == 'Inquilino':
    menu_dict = {"📱 Mi Portal de Pagos": "portal_inquilino"}
else:
    menu_dict = {"📊 Panel General": "dash", "🏢 Inmuebles": "activos", "👥 Contratos": "contratos", "💰 Tesorería (Conciliación)": "tesoreria"}
    if st.session_state['rol'] == 'Administrador': 
        menu_dict["📁 Archivos"] = "archivos"
        menu_dict["⚙️ Seguridad y Sistema"] = "seguridad"

opciones_menu = list(menu_dict.keys())
nav_seleccionada = st.radio("Navegación", opciones_menu, horizontal=True, label_visibility="collapsed")
mod = menu_dict[nav_seleccionada]

col_espacio, col_salir = st.columns([8, 1])
with col_salir:
    if st.button("🚪 SALIR", type="primary"):
        st.session_state['logeado'] = False; st.rerun()

st.divider()

# ==========================================
# 6. MÓDULOS OPERATIVOS
# ==========================================

# ----------------------------------------
# PORTAL DEL INQUILINO
# ----------------------------------------
if mod == "portal_inquilino":
    st.markdown("<h3>Tu Portal de Autogestión 📱</h3>", unsafe_allow_html=True)
    st.write("Bienvenido. Aquí puedes reportar tus pagos y subir tus comprobantes bancarios.")
    
    inq_id = int(st.session_state['inquilino_id'])
    df_mis_contratos = run_query("SELECT c.id, c.canon_pactado, u.nombre_unidad, p.nombre as prop, c.fecha_inicio, c.fecha_fin FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE c.inquilino_id = %s AND c.estado_contrato = 'Vigente'", (inq_id,))
    
    if df_mis_contratos.empty:
        st.info("No tienes contratos activos vinculados a tu cuenta.")
    else:
        for _, contrato in df_mis_contratos.iterrows():
            with st.container(border=True):
                st.markdown(f"<h4 style='color:#2563EB;'>🏠 {contrato['prop']} - {contrato['nombre_unidad']}</h4>", unsafe_allow_html=True)
                st.write(f"**Canon Mensual Base:** {fmt_cop(contrato['canon_pactado'])}")
                
                canon_base = float(contrato['canon_pactado'])
                df_pagos = run_query("SELECT periodo_pagado, SUM(monto_pagado) as total_pagado FROM ap_pagos WHERE contrato_id = %s AND estado_pago != 'Rechazado' GROUP BY periodo_pagado", (int(contrato['id']),))
                pagos_map = {r['periodo_pagado']: float(r['total_pagado']) for _, r in df_pagos.iterrows()} if not df_pagos.empty else {}
                
                periodos_todos = generar_periodos_contrato(contrato['fecha_inicio'], contrato['fecha_fin'])
                
                hoy = datetime.date.today()
                mes_siguiente_str = (hoy + relativedelta(months=1)).strftime("%Y-%m")
                
                periodos_pendientes = []
                for p in periodos_todos:
                    if (canon_base - pagos_map.get(p, 0.0)) > 0:
                        if p <= mes_siguiente_str:
                            periodos_pendientes.append(p)
                
                if not periodos_pendientes:
                    st.success("¡Felicidades! Estás completamente al día con este inmueble.")
                else:
                    with st.form(f"form_pago_{contrato['id']}"):
                        st.markdown("**Reportar Nuevo Pago**")
                        c1, c2 = st.columns(2)
                        with c1:
                            per_sel = st.selectbox("Mes que estás pagando", periodos_pendientes)
                            monto = st.number_input("Valor exacto transferido ($)", min_value=0.0, value=canon_base, step=10000.0)
                            metodo_pago = st.selectbox("Medio de Pago", ["Nequi", "DaviPlata", "Llave", "Cuenta de Ahorros", "Cuenta Corriente", "Efectivo"])
                        with c2:
                            fecha_real = st.date_input("Fecha en la que hiciste el pago")
                            ref_txt = st.text_input("Número de Aprobación / Referencia (Opcional)")
                            archivo_comprobante = st.file_uploader("Subir soporte de pago (Obligatorio excepto Efectivo, máx 5MB)", type=["png", "jpg", "jpeg", "pdf"])
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Enviar Reporte para Aprobación"):
                            if monto <= 0: st.error("❌ El monto transferido debe ser mayor a cero.")
                            elif metodo_pago != "Efectivo" and archivo_comprobante is None: 
                                st.error(f"❌ Es obligatorio adjuntar el soporte de pago para transacciones por {metodo_pago}.")
                            elif archivo_comprobante is not None and archivo_comprobante.size > (5 * 1024 * 1024): 
                                st.error("❌ El archivo es demasiado pesado. El máximo permitido es 5MB.")
                            else:
                                path_archivo = guardar_archivo(archivo_comprobante) if archivo_comprobante else None
                                f_real_str = fecha_real.strftime('%Y-%m-%d')
                                ref_final = f"{metodo_pago}" + (f" - {ref_txt}" if ref_txt.strip() else "")
                                
                                if run_transact("INSERT INTO ap_pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco, fecha_pago_real, url_comprobante, estado_pago) VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')", (int(contrato['id']), str(per_sel), float(monto), str(ref_final), f_real_str, path_archivo)):
                                    st.success("✅ ¡Pago reportado exitosamente! El administrador lo revisará muy pronto.")
                                    st.balloons()
                                    time.sleep(3)
                                    st.rerun()

# ----------------------------------------
# PANEL GENERAL (DASHBOARD)
# ----------------------------------------
elif mod == "dash":
    st.markdown("<h3>Mando Gerencial 📊</h3>", unsafe_allow_html=True)
    t_con = run_query("SELECT COUNT(*) as t FROM ap_contratos WHERE estado_contrato = 'Vigente'")
    t_ing = run_query("SELECT SUM(monto_pagado) as t FROM ap_pagos WHERE estado_pago = 'Aprobado'")
    df_libres = run_query("SELECT COUNT(*) as t FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Contratos Vigentes", f"{t_con.iloc[0]['t'] if not t_con.empty else 0}")
    c2.metric("Recaudo Histórico Efectivo", fmt_cop(t_ing.iloc[0]['t'] if not t_ing.empty and pd.notna(t_ing.iloc[0]['t']) else 0))
    c3.metric("Unidades Disponibles", f"{df_libres.iloc[0]['t'] if not df_libres.empty else 0}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📈 Histórico a 13 Meses", "📅 Flujo de Caja Proyectado", "🚨 Radar de Mora"])
    
    with t1:
        st.markdown("#### Curva de Recaudo (Pagos Aprobados)")
        df_13m = run_query("SELECT DATE_FORMAT(fecha_pago_real, '%Y-%m') as Mes, SUM(monto_pagado) as Total FROM ap_pagos WHERE estado_pago = 'Aprobado' GROUP BY Mes ORDER BY Mes DESC LIMIT 13")
        if not df_13m.empty:
            df_13m = df_13m.sort_values(by='Mes')
            st.bar_chart(df_13m.set_index('Mes'))
        else: st.info("No hay data histórica suficiente para graficar.")

    with t2:
        st.markdown("#### Distribución de Ingresos por Día del Mes")
        df_flujo = run_query("SELECT dia_pago_mensual as Día, SUM(canon_pactado) as 'Monto Proyectado', COUNT(*) as 'Contratos' FROM ap_contratos WHERE estado_contrato = 'Vigente' GROUP BY dia_pago_mensual ORDER BY dia_pago_mensual ASC")
        if not df_flujo.empty:
            df_flujo['Monto Proyectado (Texto)'] = df_flujo['Monto Proyectado'].apply(fmt_cop)
            st.dataframe(estilizar_df(df_flujo[['Día', 'Monto Proyectado (Texto)', 'Contratos']]), use_container_width=True, hide_index=True)
            st.line_chart(df_flujo.set_index('Día')['Monto Proyectado'])
        else: st.info("No hay contratos vigentes para proyectar.")

    with t3:
        st.markdown("#### Cuentas Pendientes por Cobrar Hoy")
        df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, c.dia_pago_mensual, c.canon_pactado, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_propiedades p ON u.propiedad_id = p.id JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        df_pagos_totales = run_query("SELECT contrato_id, periodo_pagado, SUM(monto_pagado) as total_pagado FROM ap_pagos WHERE estado_pago != 'Rechazado' GROUP BY contrato_id, periodo_pagado")
        
        pagos_dict = {}
        if not df_pagos_totales.empty:
            for _, r in df_pagos_totales.iterrows(): pagos_dict[(r['contrato_id'], r['periodo_pagado'])] = float(r['total_pagado'])
                
        hoy = datetime.date.today()
        mes_actual_str = hoy.strftime("%Y-%m")
        mora_list = []

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
                            dias_atraso = "Mes anterior" if p < mes_actual_str else f"{hoy.day - int(c['dia_pago_mensual'])} días"
                            mora_list.append({"Cliente": c['nombre_completo'], "Inmueble": f"{c['prop']} - {c['nombre_unidad']}", "Periodo": p, "Atraso": dias_atraso, "Deuda Real": deuda_restante})

        if mora_list:
            df_mora = pd.DataFrame(mora_list)
            df_mora['Deuda Real'] = df_mora['Deuda Real'].apply(fmt_cop)
            st.dataframe(estilizar_df(df_mora), use_container_width=True, hide_index=True)
        else: st.success("🎉 Libro de cobros limpio.")

# ----------------------------------------
# INMUEBLES Y ACTIVOS
# ----------------------------------------
elif mod == "activos":
    st.markdown("<h2>Gestión de Inmuebles 🏢</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🏛️ Edificios", "🚪 Apartamentos", "⚙️ Mantenimiento"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.container(border=True):
                nom = st.text_input("Alias del Edificio")
                dir = st.text_input("Dirección Legal")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Indexar Edificio", type="secondary") and nom:
                    if run_transact("INSERT INTO ap_propiedades (nombre, direccion) VALUES (%s, %s)", (str(nom), str(dir))):
                        st.success("✅ ¡Edificio registrado con éxito en el inventario!")
                        time.sleep(2)
                        st.rerun()
        with c2:
            df_p = run_query("SELECT id as ID, nombre as Complejo, direccion as Dirección, IF(activo,'Activo','Inactivo') as Estado FROM ap_propiedades")
            if not df_p.empty: st.dataframe(estilizar_df(df_p), use_container_width=True, hide_index=True)

    with t2:
        df_props = run_query("SELECT id, nombre FROM ap_propiedades WHERE activo = TRUE")
        if df_props.empty: st.warning("Requiere un Edificio activo primero.")
        else:
            c1, c2 = st.columns([1, 2], gap="large")
            opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
            with c1:
                with st.container(border=True):
                    sel_p = st.selectbox("Pertenece al Edificio:", list(opc_p.keys()))
                    n_uni = st.text_input("Nomenclatura (Ej: Apto 101)")
                    can_b = st.number_input("Canon Sugerido ($)", step=50000.0)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Crear Inmueble", type="secondary") and n_uni:
                        if run_transact("INSERT INTO ap_unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (int(opc_p[sel_p]), str(n_uni), float(can_b))):
                            st.success("✅ ¡Apartamento/Unidad creada exitosamente!")
                            time.sleep(2)
                            st.rerun()
            with c2:
                df_u = run_query("SELECT p.nombre as Complejo, u.nombre_unidad as Unidad, u.canon_base as 'Tarifa', IF(u.activo,'Activo','Inactivo') as Operatividad, u.estado_vacancia as Vacancia FROM ap_unidades u JOIN ap_propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                if not df_u.empty:
                    df_u['Tarifa'] = df_u['Tarifa'].apply(fmt_cop)
                    st.dataframe(estilizar_df(df_u), use_container_width=True, hide_index=True)
                    
    with t3:
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### Activar/Inactivar Edificios")
            df_all_p = run_query("SELECT id, nombre, activo FROM ap_propiedades")
            if not df_all_p.empty:
                with st.container(border=True):
                    sel_tog_p = st.selectbox("Seleccionar Edificio:", [f"[{'Activo' if r['activo'] else 'Inactivo'}] {r['nombre']}" for _, r in df_all_p.iterrows()], key="tog_prop_1")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Alternar Estado del Edificio", type="primary"):
                        nom_p = sel_tog_p.split("] ")[1]
                        nuevo_estado = 0 if "Activo" in sel_tog_p else 1
                        run_transact("UPDATE ap_propiedades SET activo = %s WHERE nombre = %s", (nuevo_estado, nom_p))
                        st.toast("Estado del edificio actualizado."); time.sleep(1); st.rerun()
        with colB:
            st.markdown("#### Activar/Inactivar Apartamentos")
            if not df_all_p.empty:
                with st.container(border=True):
                    prop_filtro = st.selectbox("1. Filtrar por Edificio:", df_all_p['nombre'].tolist())
                    id_prop_filtro = df_all_p[df_all_p['nombre'] == prop_filtro].iloc[0]['id']
                    
                    df_all_u = run_query("SELECT id, nombre_unidad, activo FROM ap_unidades WHERE propiedad_id = %s", (int(id_prop_filtro),))
                    if not df_all_u.empty:
                        sel_tog_u = st.selectbox("2. Seleccionar Apartamento:", [f"[{'Activa' if r['activo'] else 'Inactiva'}] {r['nombre_unidad']}" for _, r in df_all_u.iterrows()])
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Alternar Estado del Apartamento", type="primary"):
                            nom_u = sel_tog_u.split("] ")[1]
                            nuevo_estado = 0 if "Activa" in sel_tog_u else 1
                            run_transact("UPDATE ap_unidades SET activo = %s WHERE nombre_unidad = %s AND propiedad_id = %s", (nuevo_estado, nom_u, int(id_prop_filtro)))
                            st.toast("Estado del apartamento actualizado."); time.sleep(1); st.rerun()
                    else: st.info("Edificio sin apartamentos.")

# ----------------------------------------
# CONTRATOS Y PRÓRROGAS
# ----------------------------------------
elif mod == "contratos":
    st.markdown("<h2>Originación y Cierre Contractual 👥</h2>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["👤 Crear Inquilino", "📄 Nuevo Contrato", "🛑 Terminación", "⏳ Alargar Contrato"])
    
    with t1:
        st.write("⚠️ *Al crear un inquilino, el sistema le genera automáticamente una cuenta de acceso al portal usando su Cédula/NIT como usuario y contraseña.*")
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.container(border=True):
                ced = st.text_input("Cédula / NIT")
                nom = st.text_input("Nombre / Razón Social")
                tel = st.text_input("Teléfono")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Almacenar Cliente y Crear Acceso", type="secondary") and ced and nom:
                    if run_transact("INSERT INTO ap_inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (str(ced), str(nom), str(tel))):
                        inq_id_creado = run_query("SELECT id FROM ap_inquilinos ORDER BY id DESC LIMIT 1").iloc[0]['id']
                        run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol, inquilino_id) VALUES (%s, %s, %s, 'Inquilino', %s)", (str(ced), str(ced), str(nom), int(inq_id_creado)))
                        st.success("✅ ¡Cliente y credenciales de acceso creadas con éxito!")
                        st.balloons()
                        time.sleep(2.5)
                        st.rerun()
        with c2:
            df_i = run_query("SELECT documento_identidad as ID, nombre_completo as Razón, telefono as Contacto FROM ap_inquilinos")
            if not df_i.empty: st.dataframe(estilizar_df(df_i), use_container_width=True, hide_index=True)

    with t2:
        df_i = run_query("SELECT id, nombre_completo, documento_identidad FROM ap_inquilinos")
        df_p_activas = run_query("SELECT id, nombre FROM ap_propiedades WHERE activo = TRUE")
        
        if df_i.empty or df_p_activas.empty: st.warning("Faltan clientes o edificios activos.")
        else:
            ca, cb = st.columns(2)
            opc_i = {f"{r['documento_identidad']} - {r['nombre_completo']}": int(r['id']) for _, r in df_i.iterrows()}
            
            with ca:
                with st.container(border=True):
                    sel_i = st.selectbox("Arrendatario", list(opc_i.keys()))
                    sel_p_con = st.selectbox("1. Filtrar por Edificio", df_p_activas['nombre'].tolist())
                    id_p_con = df_p_activas[df_p_activas['nombre'] == sel_p_con].iloc[0]['id']
                    
                    df_u_libres = run_query("SELECT id, nombre_unidad FROM ap_unidades WHERE propiedad_id = %s AND estado_vacancia = 'Disponible' AND activo = TRUE", (int(id_p_con),))
                    if not df_u_libres.empty:
                        opc_u = {r['nombre_unidad']: int(r['id']) for _, r in df_u_libres.iterrows()}
                        sel_u = st.selectbox("2. Apartamento Objetivo", list(opc_u.keys()))
                    else:
                        st.warning("No hay apartamentos libres en este edificio.")
                        sel_u = None
                        
                    dia = st.number_input("Día de Corte Mensual", value=5, min_value=1, max_value=31)

            with cb:
                with st.container(border=True):
                    can = st.number_input("Carga Monetaria Mensual ($)", step=50000.0)
                    fi = st.date_input("Fecha Inicio")
                    ff = st.date_input("Fecha Fin")
                    archivo_pdf = st.file_uploader("Adjuntar PDF del Contrato Físico (Opcional)", type=["pdf", "png", "jpg"])
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if st.button("Formalizar Contrato", type="secondary"):
                        if can > 0 and sel_u is not None:
                            path_pdf = guardar_archivo(archivo_pdf) if archivo_pdf else None
                            str_fi = fi.strftime('%Y-%m-%d')
                            str_ff = ff.strftime('%Y-%m-%d')
                            
                            if run_transact("INSERT INTO ap_contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin, url_contrato) VALUES (%s, %s, %s, %s, %s, %s, %s)", (opc_u[sel_u], opc_i[sel_i], float(can), int(dia), str_fi, str_ff, path_pdf)):
                                run_transact("UPDATE ap_unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (opc_u[sel_u],))
                                st.balloons()
                                st.success("✅ ¡CONTRATO FORMALIZADO Y APARTAMENTO OCUPADO!")
                                time.sleep(2.5) 
                                st.rerun()
                        else: st.error("Verifica el apartamento y el monto.")
                        
    with t3:
        df_activos = run_query("SELECT c.id, c.unidad_id, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id=u.id JOIN ap_propiedades p ON u.propiedad_id=p.id JOIN ap_inquilinos i ON c.inquilino_id=i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("No hay contratos vigentes para terminar.")
        else:
            st.markdown("<div style='background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; width: 60%;'>", unsafe_allow_html=True)
            opc_kill = {f"[{r['prop']} - {r['nombre_unidad']}] | {r['nombre_completo']}": (int(r['id']), int(r['unidad_id'])) for _, r in df_activos.iterrows()}
            sel_kill = st.selectbox("Seleccionar contrato a terminar:", list(opc_kill.keys()))
            f_real = st.date_input("Fecha real de entrega del inmueble:")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning("⚠️ **¡ATENCIÓN!** Al finalizar este contrato, el apartamento volverá a quedar 'Disponible' inmediatamente.")
            seguro = st.checkbox("Entiendo la advertencia, deseo finalizar este contrato.")
            if seguro:
                if st.button("🛑 Ejecutar Terminación Definitiva", type="primary"):
                    id_con, id_uni = opc_kill[sel_kill]
                    str_f_real = f_real.strftime('%Y-%m-%d')
                    if run_transact("UPDATE ap_contratos SET estado_contrato = 'Finalizado', fecha_fin = %s WHERE id = %s", (str_f_real, id_con)):
                        run_transact("UPDATE ap_unidades SET estado_vacancia = 'Disponible' WHERE id = %s", (id_uni,))
                        st.success("✅ ¡El contrato ha sido cerrado y el apartamento vuelve a estar libre!")
                        time.sleep(2.5)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with t4:
        st.markdown("#### Prórroga de Contratos Vigentes")
        df_activos_prorroga = run_query("SELECT c.id, c.fecha_fin, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id=u.id JOIN ap_propiedades p ON u.propiedad_id=p.id JOIN ap_inquilinos i ON c.inquilino_id=i.id WHERE c.estado_contrato = 'Vigente'")
        
        if df_activos_prorroga.empty: 
            st.info("No hay contratos vigentes.")
        else:
            st.markdown("<div style='background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; width: 60%;'>", unsafe_allow_html=True)
            opc_ext = {f"[{r['prop']} - {r['nombre_unidad']}] | {r['nombre_completo']} | Vence: {r['fecha_fin']}": (int(r['id']), r['fecha_fin']) for _, r in df_activos_prorroga.iterrows()}
            sel_ext = st.selectbox("Seleccionar contrato a prorrogar:", list(opc_ext.keys()))
            
            meses_prorroga = st.number_input("¿Cuántos meses adicionales deseas agregar al contrato?", min_value=1, value=6, step=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⏳ Aplicar Prórroga", type="secondary"):
                id_con, f_fin_actual = opc_ext[sel_ext]
                nueva_f_fin = f_fin_actual + relativedelta(months=meses_prorroga)
                
                if run_transact("UPDATE ap_contratos SET fecha_fin = %s WHERE id = %s", (nueva_f_fin.strftime('%Y-%m-%d'), id_con)):
                    st.balloons()
                    st.success(f"✅ ¡Contrato extendido exitosamente! Nueva fecha de finalización: {nueva_f_fin.strftime('%Y-%m-%d')}")
                    time.sleep(2.5)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
# TESORERÍA (CON VALIDACIÓN DE MEDIOS DE PAGO)
# ----------------------------------------
elif mod == "tesoreria":
    st.markdown("<h2>Tesorería y Conciliación 💰</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["✅ Bandeja de Aprobaciones (Inquilinos)", "📥 Registrar Ingreso (Caja Fuerte)", "🗑️ Anular Pagos"])
    
    with t1:
        df_pendientes = run_query("SELECT p.id, p.fecha_registro, p.fecha_pago_real, u.nombre_unidad, i.nombre_completo, p.periodo_pagado, p.id_referencia_banco, p.monto_pagado, p.url_comprobante FROM ap_pagos p JOIN ap_contratos c ON p.contrato_id = c.id JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE p.estado_pago = 'Pendiente'")
        
        if df_pendientes.empty: st.success("No hay pagos pendientes de aprobación. Todo al día.")
        else:
            for _, pend in df_pendientes.iterrows():
                with st.container(border=True):
                    c_a, c_b, c_c = st.columns([2, 1, 1])
                    with c_a:
                        st.markdown(f"**Cliente:** {pend['nombre_completo']} | **Inmueble:** {pend['nombre_unidad']}")
                        st.write(f"Reporta haber pagado **{fmt_cop(pend['monto_pagado'])}** del periodo **{pend['periodo_pagado']}** (Ref: **{pend['id_referencia_banco']}**).")
                        
                        ruta_archivo = pend['url_comprobante']
                        if isinstance(ruta_archivo, str) and os.path.exists(ruta_archivo):
                            if ruta_archivo.lower().endswith('.pdf'):
                                with open(ruta_archivo, "rb") as pdf_file:
                                    st.download_button(label="📄 Descargar PDF Soporte", data=pdf_file, file_name=f"soporte_{pend['id']}.pdf", mime="application/pdf", key=f"dl_{pend['id']}")
                            else:
                                st.image(ruta_archivo, width=250, caption="Comprobante Adjunto")
                        else:
                            st.info("Sin comprobante adjunto")
                            
                    with c_b:
                        st.write(f"Fecha Reportada: {pend['fecha_pago_real']}")
                    with c_c:
                        if st.button("✅ Aprobar Ingreso a Caja", key=f"ok_{pend['id']}", type="secondary"):
                            run_transact("UPDATE ap_pagos SET estado_pago = 'Aprobado' WHERE id = %s", (int(pend['id']),))
                            st.toast("Pago validado."); time.sleep(1); st.rerun()
                        if st.button("❌ Rechazar Falso Positivo", key=f"bad_{pend['id']}", type="primary"):
                            run_transact("UPDATE ap_pagos SET estado_pago = 'Rechazado' WHERE id = %s", (int(pend['id']),))
                            st.toast("Pago denegado."); time.sleep(1); st.rerun()
    
    with t2:
        df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM ap_contratos c JOIN ap_unidades u ON c.unidad_id = u.id JOIN ap_propiedades p ON u.propiedad_id = p.id JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("Sin contratos vigentes.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"{r['prop']} {r['uni']} - {r['inq']}": r for _, r in df_activos.iterrows()}
            
            with c1:
                with st.container(border=True):
                    sel_c = st.selectbox("Obligación Vigente", list(opc_c.keys()))
                    dat_con = opc_c[sel_c]
                    canon_base = float(dat_con['canon_pactado'])
                    
                    df_pagos_contrato = run_query("SELECT periodo_pagado, SUM(monto_pagado) as total_pagado FROM ap_pagos WHERE contrato_id = %s AND estado_pago != 'Rechazado' GROUP BY periodo_pagado", (int(dat_con['id']),))
                    pagos_map = {row['periodo_pagado']: float(row['total_pagado']) for _, row in df_pagos_contrato.iterrows()} if not df_pagos_contrato.empty else {}
                    
                    periodos_todos = generar_periodos_contrato(dat_con['fecha_inicio'], dat_con['fecha_fin'])
                    periodos_pendientes = [p for p in periodos_todos if (canon_base - pagos_map.get(p, 0.0)) > 0]
                    
                    if not periodos_pendientes: st.success("Contrato completamente al día.")
                    else:
                        per_sel = st.selectbox("Periodo a Pagar", periodos_pendientes)
                        saldo_pendiente = canon_base - pagos_map.get(per_sel, 0.0)
                        
                        monto = st.number_input("Capital Recibido ($)", min_value=0.0, max_value=saldo_pendiente, value=saldo_pendiente, step=10000.0)
                        f_real = st.date_input("Fecha en la que entró la plata:")
                        
                        metodo_pago_admin = st.selectbox("Medio de Pago", ["Nequi", "DaviPlata", "Llave", "Cuenta de Ahorros", "Cuenta Corriente", "Efectivo"])
                        ref_txt_admin = st.text_input("Número de Aprobación (Opcional)")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Asentar Directo en Caja", type="secondary") and monto > 0:
                            f_real_str = f_real.strftime('%Y-%m-%d')
                            ref_final_admin = f"{metodo_pago_admin}" + (f" - {ref_txt_admin}" if ref_txt_admin.strip() else "")
                            
                            if run_transact("INSERT INTO ap_pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco, fecha_pago_real, estado_pago) VALUES (%s, %s, %s, %s, %s, 'Aprobado')", (int(dat_con['id']), str(per_sel), float(monto), str(ref_final_admin), f_real_str)):
                                st.success("✅ ¡Pago asentado en la caja fuerte con éxito!")
                                st.balloons()
                                time.sleep(2.5)
                                st.rerun()

            with c2:
                df_hist = run_query("SELECT p.fecha_pago_real as 'Fecha Ingreso', u.nombre_unidad as Origen, p.periodo_pagado as Periodo, p.monto_pagado as Volumen FROM ap_pagos p LEFT JOIN ap_contratos c ON p.contrato_id = c.id LEFT JOIN ap_unidades u ON c.unidad_id = u.id WHERE p.estado_pago = 'Aprobado' ORDER BY p.id DESC LIMIT 15")
                if not df_hist.empty:
                    df_hist['Volumen'] = df_hist['Volumen'].apply(fmt_cop)
                    st.dataframe(estilizar_df(df_hist), use_container_width=True, hide_index=True)

    with t3:
        if st.session_state['rol'] != 'Administrador':
            st.error("Privilegio insuficiente para anular transacciones.")
        else:
            df_pagos_del = run_query("SELECT p.id, p.fecha_pago_real, p.monto_pagado, IFNULL(u.nombre_unidad, 'Desconocido') as nombre_unidad, IFNULL(i.nombre_completo, 'Desconocido') as nombre_completo, p.periodo_pagado FROM ap_pagos p LEFT JOIN ap_contratos c ON p.contrato_id = c.id LEFT JOIN ap_unidades u ON c.unidad_id = u.id LEFT JOIN ap_inquilinos i ON c.inquilino_id = i.id WHERE p.estado_pago = 'Aprobado' ORDER BY p.id DESC LIMIT 50")
            if not df_pagos_del.empty:
                st.markdown("<div style='background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; width: 60%;'>", unsafe_allow_html=True)
                opc_p = {f"[{str(r['fecha_pago_real'])}] {r['nombre_unidad']} - {r['nombre_completo']} | {r['periodo_pagado']} | {fmt_cop(r['monto_pagado'])}": int(r['id']) for _, r in df_pagos_del.iterrows()}
                sel_p = st.selectbox("Seleccionar Pago Aprobado a Revertir", list(opc_p.keys()))
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Eliminar Definitivamente", type="primary"):
                    if run_transact("DELETE FROM ap_pagos WHERE id = %s", (opc_p[sel_p],)):
                        st.toast("Pago eliminado."); time.sleep(1); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else: st.info("No hay pagos registrados.")

# ----------------------------------------
# GESTOR DE ARCHIVOS
# ----------------------------------------
elif mod == "archivos":
    st.markdown("<h2>Gestor de Archivos Físicos 📁</h2>", unsafe_allow_html=True)
    st.write("Aquí puedes visualizar y eliminar comprobantes y PDFs para liberar espacio del servidor.")
    
    archivos = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
    
    if not archivos:
        st.info("El disco está completamente limpio. No hay archivos alojados en el servidor.")
    else:
        datos_archivos = []
        for arch in archivos:
            ruta_completa = os.path.join(UPLOAD_DIR, arch)
            peso_mb = os.path.getsize(ruta_completa) / (1024 * 1024)
            datos_archivos.append({"Nombre del Archivo": arch, "Peso (MB)": round(peso_mb, 2)})
            
        df_arch = pd.DataFrame(datos_archivos)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.dataframe(estilizar_df(df_arch), use_container_width=True, hide_index=True)
        with c2:
            with st.container(border=True):
                st.markdown("#### Eliminar Archivos")
                archivo_a_borrar = st.selectbox("Seleccionar archivo", df_arch["Nombre del Archivo"].tolist())
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Eliminar Archivo", type="primary"):
                    try:
                        os.remove(os.path.join(UPLOAD_DIR, archivo_a_borrar))
                        st.toast(f"Archivo {archivo_a_borrar} eliminado.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {e}")

# ----------------------------------------
# SEGURIDAD IAM & GENERADOR DATA SEMILLA
# ----------------------------------------
elif mod == "seguridad":
    st.markdown("<h2>Seguridad y Base de Datos ⚙️</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🛡️ Control de Nodos", "🌱 Data Semilla (Pruebas)"])
    
    with t1:
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.container(border=True):
                nu = st.text_input("Alias")
                np = st.text_input("Hash Secreto", type="password")
                nn = st.text_input("Nombre Real")
                nr = st.selectbox("Jerarquía", ["Administrador", "Asesor Comercial"])
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Crear Perfil Interno", type="secondary") and nu and np:
                    if run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (str(nu), str(np), str(nn), str(nr))):
                        st.success("✅ ¡Usuario/Perfil creado con éxito en el sistema!")
                        time.sleep(2.5)
                        st.rerun()
        with c2:
            df_u = run_query("SELECT username as Alias, nombre_completo as Nombre, rol as Privilegios FROM ap_usuarios")
            if not df_u.empty: st.dataframe(estilizar_df(df_u), use_container_width=True, hide_index=True)
            
    with t2:
        st.markdown("#### Generador Masivo (Data Semilla)")
        if st.button("🚀 INYECTAR INFRAESTRUCTURA DE PRUEBA", type="secondary"):
            with st.spinner("Minando... esto tomará unos segundos"):
                for i in range(1, 6):
                    run_transact("INSERT INTO ap_propiedades (nombre, direccion) VALUES (%s, %s)", (f"Torre Omega {i}", f"Distrito {i}"))
                    pid = int(run_query("SELECT id FROM ap_propiedades ORDER BY id DESC LIMIT 1").iloc[0]['id'])
                    for j in range(1, 5):
                        run_transact("INSERT INTO ap_unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (pid, f"Apto {j}01", float(700000 + (j*100000))))
                
                nombres = ["Bruce Wayne", "Tony Stark", "Lex Luthor", "Oliver Queen", "Norman Osborn"]
                for i, nom in enumerate(nombres):
                    doc = f"9004{i}"
                    run_transact("INSERT INTO ap_inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (doc, nom, f"+57 300 440{i}"))
                    inq_id = int(run_query("SELECT id FROM ap_inquilinos ORDER BY id DESC LIMIT 1").iloc[0]['id'])
                    run_transact("INSERT INTO ap_usuarios (username, password, nombre_completo, rol, inquilino_id) VALUES (%s, %s, %s, 'Inquilino', %s)", (doc, doc, nom, inq_id))
                
                clientes_id = run_query("SELECT id FROM ap_inquilinos ORDER BY id DESC LIMIT 5")['id'].tolist()
                unidades_id = run_query("SELECT id, canon_base FROM ap_unidades WHERE estado_vacancia='Disponible' LIMIT 5")
                hoy = datetime.date.today()
                
                for idx, row in unidades_id.iterrows():
                    f_ini = (hoy - relativedelta(months=5)).strftime('%Y-%m-%d')
                    f_fin = (hoy + relativedelta(months=7)).strftime('%Y-%m-%d')
                    uid = int(row['id'])
                    cid = int(clientes_id[idx])
                    canon = float(row['canon_base'])
                    
                    run_transact("INSERT INTO ap_contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (uid, cid, canon, 5, f_ini, f_fin))
                    run_transact("UPDATE ap_unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (uid,))
                    
                    con_id = int(run_query("SELECT id FROM ap_contratos ORDER BY id DESC LIMIT 1").iloc[0]['id'])
                    for m_atras in [5, 4, 3]:
                        per_pago = (hoy - relativedelta(months=m_atras)).strftime('%Y-%m')
                        f_real = (hoy - relativedelta(months=m_atras)).replace(day=5).strftime('%Y-%m-%d')
                        run_transact("INSERT INTO ap_pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco, fecha_pago_real, estado_pago) VALUES (%s, %s, %s, %s, %s, 'Aprobado')", (con_id, per_pago, canon, "DATA-SEMILLA", f_real))
                
                st.success("✅ Estructuras indexadas."); time.sleep(3); st.rerun()
