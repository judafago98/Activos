import streamlit as st
import pandas as pd
import mysql.connector
import time
import datetime

# ==========================================
# 1. CONFIGURACIÓN GLOBAL
# ==========================================
st.set_page_config(
    page_title="Gestión de Activos e Inmuebles | Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. MOTOR CSS ULTRA PREMIUM (ANTI-BORDES ROJOS)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .stApp { background: linear-gradient(-45deg, #020617, #0A192F, #020813, #001E3C); background-size: 300% 300%; animation: gradientBG 25s ease infinite; color: #F8FAFC; }
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 198, 255, 0.3); border-radius: 10px; }
        
        /* 🛡️ ELIMINACIÓN DE BORDES ROJOS Y NATIVOS DE STREAMLIT */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
            background-color: rgba(4, 13, 30, 0.7) !important;
            border: 1px solid rgba(0, 198, 255, 0.2) !important;
            border-radius: 8px !important;
            outline: none !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #00C6FF !important;
            box-shadow: 0 0 12px rgba(0, 198, 255, 0.3) !important;
            outline: none !important;
        }
        input, select, textarea, div[data-baseweb="select"] span {
            color: white !important;
            background: transparent !important;
            outline: none !important;
        }
        
        /* Formularios y Tarjetas */
        div[data-testid="stForm"] { background: rgba(4, 13, 30, 0.6) !important; backdrop-filter: blur(15px) !important; border: 1px solid rgba(0, 198, 255, 0.15) !important; border-radius: 16px !important; padding: 25px !important; box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5); }
        [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.85) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 198, 255, 0.15); }
        [data-testid="stMetric"] { background: rgba(10, 20, 40, 0.6); backdrop-filter: blur(15px); border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 24px; border-top: 3px solid #00C6FF; }
        
        /* Botones Intergalácticos */
        .stButton>button { background: linear-gradient(135deg, #0066FF 0%, #00C6FF 100%); color: #FFFFFF !important; border: none; border-radius: 8px; font-weight: 600; width: 100%; transition: all 0.3s ease;}
        .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0, 198, 255, 0.5); }

        [data-testid="stDataFrame"] { background-color: rgba(255, 255, 255, 0.02); border-radius: 8px; padding: 10px; border: 1px solid rgba(255,255,255,0.05); }
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 600 !important; }
        .fade-in { animation: fadeIn 0.6s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ESTADO DE SESIÓN
# ==========================================
if 'logeado' not in st.session_state:
    st.session_state['logeado'] = False
    st.session_state['rol'] = None
    st.session_state['nombre_usuario'] = None

# ==========================================
# 4. UTILIDADES FINANCIERAS
# ==========================================
def fmt_cop(val):
    try: val_int = int(float(val))
    except: return "$0"
    return f"${val_int:,}".replace(',', '.')

def get_color_estado(val):
    if val in ['Vigente', 'Aplicado', 'Ocupado', 'Activo']: return 'background-color: rgba(16, 185, 129, 0.15); color: #34D399; font-weight: bold;'
    if val in ['Cancelado', 'Anulado', 'Mora', 'Inactivo']: return 'background-color: rgba(245, 158, 11, 0.15); color: #F87171; font-weight: bold;'
    if val in ['Disponible']: return 'background-color: rgba(0, 198, 255, 0.15); color: #00C6FF; font-weight: bold;'
    return ''

# ==========================================
# 5. MOTOR DE BASE DE DATOS Y AUTO-HEALING
# ==========================================
@st.cache_resource(ttl=300)
def init_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"], port=st.secrets["DB_PORT"], 
            user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"], 
            database=st.secrets["DB_NAME"], ssl_verify_cert=False, autocommit=True
        )
    except: return None

def run_query(query, params=None):
    conn = init_connection()
    if not conn: return pd.DataFrame()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    except: return pd.DataFrame()
    finally: cursor.close()

def run_transact(query, params=None):
    conn = init_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        return True
    except: return False
    finally: cursor.close()

@st.cache_data
def auto_instalar_sistema():
    """El sistema se cura a sí mismo: Si no hay tabla de usuarios, la crea y mete al Admin"""
    query_crear = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), 
        nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    run_transact(query_crear)
    df = run_query("SELECT id FROM usuarios WHERE username='admin'")
    if df.empty:
        run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

# Llamada silenciosa de autocuración al arrancar
auto_instalar_sistema()

# ==========================================
# 6. PANTALLA DE LOGIN
# ==========================================
def pantalla_login():
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; color: #00C6FF; font-size: 2.2rem;'>Portal de Acceso</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94A3B8; margin-bottom: 20px;'>Gestión de Activos Corporativos</p>", unsafe_allow_html=True)
            
            usuario = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Clave de Seguridad", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("Validar Credenciales"):
                df_user = run_query("SELECT id, nombre_completo, rol FROM usuarios WHERE username = %s AND password = %s AND activo = TRUE", (usuario, password))
                if not df_user.empty:
                    st.session_state['logeado'] = True
                    st.session_state['nombre_usuario'] = df_user.iloc[0]['nombre_completo']
                    st.session_state['rol'] = df_user.iloc[0]['rol']
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas o inactivas.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 7. APLICATIVO PRINCIPAL (APP)
# ==========================================
def app_principal():
    st.sidebar.markdown(f"""
        <div style='padding: 15px; background: rgba(0, 198, 255, 0.05); border-radius: 12px; border: 1px solid rgba(0,198,255,0.2); margin-bottom: 20px; text-align: center;'>
            <b style='color:#F8FAFC; font-size: 16px;'>{st.session_state['nombre_usuario']}</b><br>
            <span style='color:#00C6FF; font-size: 11px; font-weight: 600; letter-spacing: 1px;'>{str(st.session_state['rol']).upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    menu = {"📊 Panel Gerencial": "dash", "🏢 Gestión de Activos": "activos", "👥 Contratos": "contratos", "💰 Tesorería": "tesoreria", "🔑 Disponibilidad": "vacancia"}
    if st.session_state['rol'] == 'Administrador': menu["⚙️ Seguridad IAM"] = "seguridad"

    nav = st.sidebar.radio("Navegación", list(menu.keys()), label_visibility="collapsed")
    mod = menu[nav]
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['logeado'] = False
        st.rerun()

    # MÓDULO: DASHBOARD
    if mod == "dash":
        st.markdown("<h2 class='fade-in'>Panel Gerencial de Activos 📊</h2>", unsafe_allow_html=True)
        t_contratos = run_query("SELECT COUNT(*) as t FROM contratos WHERE estado_contrato = 'Vigente'")
        t_ingresos = run_query("SELECT SUM(monto_pagado) as t FROM pagos WHERE estado_pago = 'Aplicado'")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🏢 Contratos Activos", f"{t_contratos.iloc[0]['t'] if not t_contratos.empty else 0}")
        c2.metric("💰 Flujo Histórico Neto", fmt_cop(t_ingresos.iloc[0]['t'] if not t_ingresos.empty and pd.notna(t_ingresos.iloc[0]['t']) else 0))
        c3.metric("🟢 Estatus de Nube", "Sincronizado")
        
        st.divider()
        st.subheader("Auditoría de Últimos Recaudos")
        df_pagos = run_query("SELECT p.fecha_registro as Fecha, u.nombre_unidad as Unidad, p.monto_pagado as Ingreso, p.estado_pago as Estado FROM pagos p JOIN contratos c ON p.contrato_id = c.id JOIN unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 5")
        if not df_pagos.empty:
            df_pagos['Ingreso'] = df_pagos['Ingreso'].apply(fmt_cop)
            st.dataframe(df_pagos.style.applymap(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)
        else: st.info("Caja en ceros. Aún no hay movimientos.")

    # MÓDULO: ACTIVOS
    elif mod == "activos":
        st.markdown("<h2 class='fade-in'>Portafolio Físico 🏢</h2>", unsafe_allow_html=True)
        t_prop, t_unid = st.tabs(["🏛️ Estructuras Matrices", "🚪 Unidades de Renta"])
        
        with t_prop:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_prop", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Alta de Propiedad</h4>", unsafe_allow_html=True)
                    nom = st.text_input("Nombre (Ej: Edificio Norte)")
                    dir = st.text_input("Dirección Oficial")
                    if st.form_submit_button("Crear Estructura") and nom:
                        if run_transact("INSERT INTO propiedades (nombre, direccion) VALUES (%s, %s)", (nom, dir)):
                            st.toast("Propiedad registrada.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_p = run_query("SELECT id as ID, nombre as Nombre, direccion as Dirección FROM propiedades")
                if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

        with t_unid:
            df_props = run_query("SELECT id, nombre FROM propiedades")
            if df_props.empty: st.warning("Crea una Propiedad Matriz primero.")
            else:
                c1, c2 = st.columns([1, 2], gap="large")
                opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
                with c1:
                    with st.form("f_uni", clear_on_submit=True):
                        sel_p = st.selectbox("Estructura:", list(opc_p.keys()))
                        n_uni = st.text_input("Unidad (Ej: Apto 101)")
                        can_b = st.number_input("Canon Base Sugerido ($)", step=50000)
                        if st.form_submit_button("Añadir Unidad") and n_uni:
                            if run_transact("INSERT INTO unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (opc_p[sel_p], n_uni, can_b)):
                                st.toast("Unidad lista.", icon="✅"); time.sleep(1); st.rerun()
                with c2:
                    df_u = run_query("SELECT p.nombre as Propiedad, u.nombre_unidad as Unidad, u.canon_base as 'Precio', u.estado_vacancia as Estatus FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                    if not df_u.empty:
                        df_u['Precio'] = df_u['Precio'].apply(fmt_cop)
                        st.dataframe(df_u.style.applymap(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)

    # MÓDULO: CONTRATOS
    elif mod == "contratos":
        st.markdown("<h2 class='fade-in'>Titulares y Contratos 👥</h2>", unsafe_allow_html=True)
        t_inq, t_con = st.tabs(["👤 Directorio de Titulares", "📄 Firmar Contrato"])
        
        with t_inq:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_inq", clear_on_submit=True):
                    ced = st.text_input("Cédula / NIT")
                    nom = st.text_input("Nombre Completo")
                    tel = st.text_input("Contacto")
                    if st.form_submit_button("Consolidar Titular") and ced and nom:
                        if run_transact("INSERT INTO inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (ced, nom, tel)):
                            st.toast("Cliente formalizado.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_i = run_query("SELECT documento_identidad as Cédula, nombre_completo as Nombre FROM inquilinos ORDER BY id DESC")
                if not df_i.empty: st.dataframe(df_i, use_container_width=True, hide_index=True)

        with t_con:
            df_inqs = run_query("SELECT id, nombre_completo, documento_identidad FROM inquilinos")
            df_unis = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
            
            if df_inqs.empty or df_unis.empty: st.warning("Requiere Titulares registrados y Unidades Disponibles.")
            else:
                with st.form("f_con", clear_on_submit=True):
                    c_a, c_b = st.columns(2)
                    opc_i = {f"{r['documento_identidad']} - {r['nombre_completo']}": r['id'] for _, r in df_inqs.iterrows()}
                    opc_u = {f"{r['nombre']} - {r['nombre_unidad']}": r['id'] for _, r in df_unis.iterrows()}
                    
                    with c_a:
                        sel_i = st.selectbox("Arrendatario", list(opc_i.keys()))
                        sel_u = st.selectbox("Activo a Rentar", list(opc_u.keys()))
                        dia_p = st.number_input("Día de Corte (1-31)", value=5)
                    with c_b:
                        can_p = st.number_input("Valor Mensual Pactado ($)", step=50000)
                        f_ini = st.date_input("Fecha Inicio")
                        f_fin = st.date_input("Fecha Fin", value=f_ini + datetime.timedelta(days=365))
                    
                    if st.form_submit_button("Sellar Contrato") and can_p > 0:
                        if run_transact("INSERT INTO contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (opc_u[sel_u], opc_i[sel_i], can_p, dia_p, f_ini, f_fin)):
                            run_transact("UPDATE unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (opc_u[sel_u],))
                            st.toast("Activo Rentado.", icon="📜"); time.sleep(1); st.rerun()

    # MÓDULO: TESORERIA
    elif mod == "tesoreria":
        st.markdown("<h2 class='fade-in'>Centro de Caja 💰</h2>", unsafe_allow_html=True)
        df_activos = run_query("SELECT c.id, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM contratos c JOIN unidades u ON c.unidad_id = u.id JOIN propiedades p ON u.propiedad_id = p.id JOIN inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        
        if df_activos.empty: st.info("No hay carteras vigentes para cobrar.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"[{r['prop']} - {r['uni']}] {r['inq']} (Debe: {fmt_cop(r['canon_pactado'])})": r['id'] for _, r in df_activos.iterrows()}
            
            with c1:
                with st.form("f_pago", clear_on_submit=True):
                    st.markdown("<h4 style='color:#34D399;'>Procesar Ingreso</h4>", unsafe_allow_html=True)
                    sel_c = st.selectbox("Cuenta Cobrable", list(opc_c.keys()))
                    mes = st.selectbox("Mes", [1,2,3,4,5,6,7,8,9,10,11,12], index=datetime.date.today().month-1)
                    anio = st.number_input("Año", value=datetime.date.today().year)
                    monto = st.number_input("Recibido ($)", step=50000)
                    if st.form_submit_button("Asentar Pago") and monto > 0:
                        if run_transact("INSERT INTO pagos (contrato_id, periodo_pagado_mes, periodo_pagado_anio, monto_pagado) VALUES (%s, %s, %s, %s)", (opc_c[sel_c], mes, anio, monto)):
                            st.toast("Recaudo procesado.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_hist = run_query("SELECT p.fecha_registro as Fecha, u.nombre_unidad as Unidad, p.monto_pagado as Ingreso, p.estado_pago as Estado FROM pagos p JOIN contratos c ON p.contrato_id = c.id JOIN unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 10")
                if not df_hist.empty:
                    df_hist['Ingreso'] = df_hist['Ingreso'].apply(fmt_cop)
                    st.dataframe(df_hist.style.applymap(get_color_estado, subset=['Estado']), use_container_width=True, hide_index=True)

    # MÓDULO: DISPONIBILIDAD
    elif mod == "vacancia":
        st.markdown("<h2 class='fade-in'>Vacancia y Disponibilidad 🔑</h2>", unsafe_allow_html=True)
        df_libres = run_query("SELECT p.nombre as Propiedad, u.nombre_unidad as Unidad, u.canon_base as 'Renta Sugerida' FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
        if not df_libres.empty:
            df_libres['Renta Sugerida'] = df_libres['Renta Sugerida'].apply(fmt_cop)
            st.dataframe(df_libres, use_container_width=True, hide_index=True)
        else: st.success("Ocupación al 100%. Rentabilidad máxima operativa.")

    # MÓDULO: SEGURIDAD
    elif mod == "seguridad":
        st.markdown("<h2 class='fade-in'>Configuración IAM ⚙️</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_nuevo_usuario", clear_on_submit=True):
                st.markdown("<h4 style='color:#00C6FF;'>Alta de Nuevo Perfil</h4>", unsafe_allow_html=True)
                n_u = st.text_input("Usuario")
                n_p = st.text_input("Contraseña", type="password")
                n_n = st.text_input("Nombre Completo")
                n_r = st.selectbox("Acceso", ["Administrador", "Asesor Comercial"])
                if st.form_submit_button("Crear Credencial") and n_u and n_p:
                    if run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_u, n_p, n_n, n_r)):
                        st.toast("Usuario añadido.", icon="✅"); time.sleep(1); st.rerun()
        with c2:
            df_users = run_query("SELECT username as Usuario, nombre_completo as Nombre, rol as Rol, IF(activo, 'Activo', 'Inactivo') as Estatus FROM usuarios")
            if not df_users.empty: st.dataframe(df_users.style.applymap(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
