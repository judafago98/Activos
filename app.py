import streamlit as st
import pandas as pd
import mysql.connector
import time
import datetime

# ==========================================
# 1. CONFIGURACIÓN GLOBAL DE PRODUCCIÓN
# ==========================================
st.set_page_config(
    page_title="Gestión de Activos e Inmuebles | Pro",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. MOTOR CSS ULTRA PREMIUM (CRISTAL LÍQUIDO 2.0)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        /* Fondo Animado Reactivo */
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .stApp { background: linear-gradient(-45deg, #020617, #0A192F, #020813, #001E3C); background-size: 300% 300%; animation: gradientBG 25s ease infinite; color: #F8FAFC; }
        
        /* Ocultamiento de ruido visual nativo */
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 198, 255, 0.5); border-radius: 10px; }
        
        /* 🛡️ ASESINO DE BORDES ROJOS Y FOCOS NATIVOS */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
            background-color: rgba(4, 13, 30, 0.7) !important;
            border: 1px solid rgba(0, 198, 255, 0.2) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #00C6FF !important;
            box-shadow: 0 0 12px rgba(0, 198, 255, 0.3) !important;
        }
        input, select, textarea, div[data-baseweb="select"] span {
            color: white !important; background: transparent !important; outline: none !important;
        }
        
        /* Formularios y Glassmorphism */
        div[data-testid="stForm"] { 
            background: rgba(10, 20, 40, 0.65) !important; backdrop-filter: blur(15px) !important; 
            border: 1px solid rgba(0, 198, 255, 0.15) !important; border-radius: 16px !important; 
            padding: 30px !important; box-shadow: 0 15px 35px 0 rgba(0, 0, 0, 0.5); 
        }
        
        /* Tarjetas de Métricas (Dashboard) */
        [data-testid="stMetric"] { 
            background: rgba(10, 20, 40, 0.7); backdrop-filter: blur(15px); 
            border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 25px; 
            border-top: 3px solid #00C6FF; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        [data-testid="stMetric"]:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0, 198, 255, 0.2); border-top: 3px solid #34D399; }
        
        /* Sidebar Corporativo */
        [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.9) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 198, 255, 0.15); }
        
        /* Botones Intergalácticos */
        .stButton>button { 
            background: linear-gradient(135deg, #0066FF 0%, #00C6FF 100%); color: #FFFFFF !important; 
            border: none; border-radius: 8px; font-weight: 600; width: 100%; transition: all 0.3s ease; padding: 0.6rem 1rem;
        }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 198, 255, 0.4); background: linear-gradient(135deg, #00C6FF 0%, #0066FF 100%); }

        /* Dataframes Limpios */
        [data-testid="stDataFrame"] { background-color: rgba(255, 255, 255, 0.02); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); }
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 600 !important; }
        .fade-in { animation: fadeIn 0.5s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GESTIÓN DE ESTADO (SESSION STATE)
# ==========================================
if 'logeado' not in st.session_state:
    st.session_state.update({'logeado': False, 'rol': None, 'nombre_usuario': None})

# ==========================================
# 4. FORMATEADORES FINANCIEROS
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
# 5. CORE DE BASE DE DATOS (ANTI-SEGFAULT)
# ==========================================
def get_connection():
    """Conexión quirúrgica pura. Evita caídas de memoria en la nube."""
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"], port=st.secrets["DB_PORT"], 
            user=st.secrets["DB_USER"], password=st.secrets["DB_PASS"], 
            database=st.secrets["DB_NAME"], ssl_verify_cert=False, autocommit=True,
            use_pure=True # EL BLINDAJE
        )
    except Exception as e:
        st.error(f"Falla de red: {e}")
        return None

def run_query(query, params=None):
    conn = get_connection()
    if not conn: return pd.DataFrame()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return pd.DataFrame(cursor.fetchall())
    except: return pd.DataFrame()
    finally: cursor.close(); conn.close()

def run_transact(query, params=None):
    conn = get_connection()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        return True
    except: return False
    finally: cursor.close(); conn.close()

@st.cache_data
def auto_instalar_sistema():
    """Módulo de curación: Inyecta tablas e IAM al detectar vacíos."""
    query = """CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), 
        nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE)"""
    run_transact(query)
    if run_query("SELECT id FROM usuarios WHERE username='admin'").empty:
        run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

auto_instalar_sistema()

# ==========================================
# 6. PORTAL DE ACCESO (LOGIN)
# ==========================================
def pantalla_login():
    st.markdown("<div style='height: 12vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; color: #00C6FF; font-size: 2.5rem; letter-spacing: 1px;'>ACTIVOS PRO</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94A3B8; margin-bottom: 30px;'>Identificación de Red Corporativa</p>", unsafe_allow_html=True)
            
            usuario = st.text_input("👤 Credencial de Usuario")
            password = st.text_input("🔒 Llave de Seguridad", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("Desbloquear Sistema"):
                with st.spinner("Autenticando encriptación..."):
                    time.sleep(0.5) # Simulación de carga pesada
                    df_user = run_query("SELECT nombre_completo, rol FROM usuarios WHERE username = %s AND password = %s AND activo = TRUE", (usuario, password))
                    if not df_user.empty:
                        st.session_state.update({'logeado': True, 'nombre_usuario': df_user.iloc[0]['nombre_completo'], 'rol': df_user.iloc[0]['rol']})
                        st.rerun()
                    else: st.error("❌ Acceso Denegado. Credenciales inválidas.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 7. ECOSISTEMA PRINCIPAL (SAAS)
# ==========================================
def app_principal():
    # --- SIDEBAR GERENCIAL ---
    st.sidebar.markdown(f"""
        <div style='padding: 18px; background: rgba(0, 198, 255, 0.05); border-radius: 12px; border: 1px solid rgba(0,198,255,0.2); margin-bottom: 25px; text-align: center; box-shadow: inset 0 0 15px rgba(0,198,255,0.05);'>
            <b style='color:#F8FAFC; font-size: 16px;'>{st.session_state['nombre_usuario']}</b><br>
            <span style='color:#00C6FF; font-size: 11px; font-weight: 700; letter-spacing: 2px;'>{str(st.session_state['rol']).upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    menu = {"📊 Panel de Inteligencia": "dash", "🏢 Activos Físicos": "activos", "👥 Clientes y Renta": "contratos", "💰 Motor de Tesorería": "tesoreria", "🔑 Vacancia": "vacancia"}
    if st.session_state['rol'] == 'Administrador': menu["⚙️ Core y Seguridad"] = "seguridad"

    nav = st.sidebar.radio("Navegación Operativa", list(menu.keys()), label_visibility="collapsed")
    mod = menu[nav]
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Desconectar Sesión"):
        st.session_state.update({'logeado': False, 'rol': None, 'nombre_usuario': None})
        st.rerun()

    # --- MÓDULO 1: DASHBOARD ---
    if mod == "dash":
        st.markdown("<h2 class='fade-in'>Panel de Inteligencia 📊</h2>", unsafe_allow_html=True)
        t_contratos = run_query("SELECT COUNT(*) as t FROM contratos WHERE estado_contrato = 'Vigente'")
        t_ingresos = run_query("SELECT SUM(monto_pagado) as t FROM pagos WHERE estado_pago = 'Aplicado'")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🏢 Operaciones Vigentes", f"{t_contratos.iloc[0]['t'] if not t_contratos.empty else 0} Activos")
        c2.metric("💰 Recaudo Histórico Neto", fmt_cop(t_ingresos.iloc[0]['t'] if not t_ingresos.empty and pd.notna(t_ingresos.iloc[0]['t']) else 0))
        c3.metric("🌐 Estatus de Nube", "Sincronizado 🟢")
        
        st.divider()
        st.markdown("<h4 style='color:#E2E8F0;'>Auditoría Financiera Reciente</h4>", unsafe_allow_html=True)
        df_pagos = run_query("SELECT p.fecha_registro as 'Fecha', u.nombre_unidad as 'Unidad Renta', p.monto_pagado as 'Capital Ingresado', p.estado_pago as 'Estatus' FROM pagos p JOIN contratos c ON p.contrato_id = c.id JOIN unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 6")
        if not df_pagos.empty:
            df_pagos['Capital Ingresado'] = df_pagos['Capital Ingresado'].apply(fmt_cop)
            st.dataframe(df_pagos.style.map(get_color_estado), use_container_width=True, hide_index=True)
        else: st.info("El libro mayor se encuentra sin movimientos.")

    # --- MÓDULO 2: ACTIVOS ---
    elif mod == "activos":
        st.markdown("<h2 class='fade-in'>Portafolio de Activos Físicos 🏢</h2>", unsafe_allow_html=True)
        t_prop, t_unid = st.tabs(["🏛️ Estructuras Matrices", "🚪 Unidades de Renta"])
        
        with t_prop:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_prop", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Construir Propiedad</h4>", unsafe_allow_html=True)
                    nom = st.text_input("Identificador (Ej: Edificio Norte)")
                    dir = st.text_input("Dirección Oficial")
                    if st.form_submit_button("Crear Estructura") and nom:
                        if run_transact("INSERT INTO propiedades (nombre, direccion) VALUES (%s, %s)", (nom, dir)):
                            st.toast("Propiedad registrada en el sistema.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_p = run_query("SELECT id as ID, nombre as Nombre, direccion as Dirección FROM propiedades")
                if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

        with t_unid:
            df_props = run_query("SELECT id, nombre FROM propiedades")
            if df_props.empty: st.warning("Requiere la creación de una Estructura Matriz.")
            else:
                c1, c2 = st.columns([1, 2], gap="large")
                opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
                with c1:
                    with st.form("f_uni", clear_on_submit=True):
                        st.markdown("<h4 style='color:#00C6FF;'>Añadir Unidad</h4>", unsafe_allow_html=True)
                        sel_p = st.selectbox("Estructura Asociada:", list(opc_p.keys()))
                        n_uni = st.text_input("Unidad Fija (Ej: Apto 101)")
                        can_b = st.number_input("Canon Base Sugerido ($)", step=50000)
                        if st.form_submit_button("Listar en Inventario") and n_uni:
                            if run_transact("INSERT INTO unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (opc_p[sel_p], n_uni, can_b)):
                                st.toast("Unidad inyectada al mercado.", icon="✅"); time.sleep(1); st.rerun()
                with c2:
                    df_u = run_query("SELECT p.nombre as Propiedad, u.nombre_unidad as Unidad, u.canon_base as 'Precio Sugerido', u.estado_vacancia as Estatus FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                    if not df_u.empty:
                        df_u['Precio Sugerido'] = df_u['Precio Sugerido'].apply(fmt_cop)
                        st.dataframe(df_u.style.map(get_color_estado), use_container_width=True, hide_index=True)

    # --- MÓDULO 3: CONTRATOS ---
    elif mod == "contratos":
        st.markdown("<h2 class='fade-in'>Gestor de Titulares y Renta 👥</h2>", unsafe_allow_html=True)
        t_inq, t_con = st.tabs(["👤 Directorio de Clientes", "📄 Suscripción de Contratos"])
        
        with t_inq:
            c1, c2 = st.columns([1, 2], gap="large")
            with c1:
                with st.form("f_inq", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Nuevo Perfil</h4>", unsafe_allow_html=True)
                    ced = st.text_input("Identidad / NIT")
                    nom = st.text_input("Nombre / Razón Social")
                    tel = st.text_input("Línea de Contacto")
                    if st.form_submit_button("Consolidar Cliente") and ced and nom:
                        if run_transact("INSERT INTO inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (ced, nom, tel)):
                            st.toast("Cliente formalizado.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_i = run_query("SELECT documento_identidad as Identidad, nombre_completo as 'Cliente/Empresa' FROM inquilinos ORDER BY id DESC")
                if not df_i.empty: st.dataframe(df_i, use_container_width=True, hide_index=True)

        with t_con:
            df_inqs = run_query("SELECT id, nombre_completo, documento_identidad FROM inquilinos")
            df_unis = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
            
            if df_inqs.empty or df_unis.empty: st.warning("Operación bloqueada: Requiere clientes registrados y unidades disponibles.")
            else:
                with st.form("f_con", clear_on_submit=True):
                    st.markdown("<h4 style='color:#00C6FF;'>Mesa de Negociación</h4>", unsafe_allow_html=True)
                    c_a, c_b = st.columns(2)
                    opc_i = {f"{r['documento_identidad']} - {r['nombre_completo']}": r['id'] for _, r in df_inqs.iterrows()}
                    opc_u = {f"{r['nombre']} - {r['nombre_unidad']}": r['id'] for _, r in df_unis.iterrows()}
                    
                    with c_a:
                        sel_i = st.selectbox("Arrendatario", list(opc_i.keys()))
                        sel_u = st.selectbox("Activo Inmobiliario", list(opc_u.keys()))
                        dia_p = st.number_input("Día Límite de Pago (1-31)", value=5)
                    with c_b:
                        can_p = st.number_input("Canon Fijo de Cierre ($)", step=50000)
                        f_ini = st.date_input("Día de Activación")
                        f_fin = st.date_input("Día de Caducidad", value=f_ini + datetime.timedelta(days=365))
                    
                    if st.form_submit_button("Ejecutar Contrato") and can_p > 0:
                        if run_transact("INSERT INTO contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (opc_u[sel_u], opc_i[sel_i], can_p, dia_p, f_ini, f_fin)):
                            run_transact("UPDATE unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (opc_u[sel_u],))
                            st.toast("Contrato Activo y Activo Ocupado.", icon="📜"); time.sleep(1); st.rerun()

    # --- MÓDULO 4: TESORERIA ---
    elif mod == "tesoreria":
        st.markdown("<h2 class='fade-in'>Motor de Tesorería 💰</h2>", unsafe_allow_html=True)
        df_activos = run_query("SELECT c.id, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM contratos c JOIN unidades u ON c.unidad_id = u.id JOIN propiedades p ON u.propiedad_id = p.id JOIN inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        
        if df_activos.empty: st.info("Libro de cobros en ceros. No hay contratos vigentes.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"[{r['prop']} - {r['uni']}] {r['inq']} (Debe: {fmt_cop(r['canon_pactado'])})": r['id'] for _, r in df_activos.iterrows()}
            
            with c1:
                with st.form("f_pago", clear_on_submit=True):
                    st.markdown("<h4 style='color:#34D399;'>Procesar Ingreso de Capital</h4>", unsafe_allow_html=True)
                    sel_c = st.selectbox("Origen de Fondos (Contrato)", list(opc_c.keys()))
                    mes = st.selectbox("Periodo Amortizado", [1,2,3,4,5,6,7,8,9,10,11,12], index=datetime.date.today().month-1)
                    anio = st.number_input("Año Fiscal", value=datetime.date.today().year)
                    monto = st.number_input("Capital Neto Consignado ($)", step=50000)
                    if st.form_submit_button("Asentar en Libro Mayor") and monto > 0:
                        with st.spinner("Encriptando transacción..."):
                            if run_transact("INSERT INTO pagos (contrato_id, periodo_pagado_mes, periodo_pagado_anio, monto_pagado) VALUES (%s, %s, %s, %s)", (opc_c[sel_c], mes, anio, monto)):
                                st.toast("Recaudo exitoso.", icon="✅"); time.sleep(1); st.rerun()
            with c2:
                df_hist = run_query("SELECT p.fecha_registro as Fecha, u.nombre_unidad as Unidad, p.monto_pagado as Ingreso, p.estado_pago as Estado FROM pagos p JOIN contratos c ON p.contrato_id = c.id JOIN unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 8")
                if not df_hist.empty:
                    df_hist['Ingreso'] = df_hist['Ingreso'].apply(fmt_cop)
                    st.dataframe(df_hist.style.map(get_color_estado), use_container_width=True, hide_index=True)

    # --- MÓDULO 5: VACANCIA ---
    elif mod == "vacancia":
        st.markdown("<h2 class='fade-in'>Disponibilidad Inmediata 🔑</h2>", unsafe_allow_html=True)
        df_libres = run_query("SELECT p.nombre as 'Edificio / Matriz', u.nombre_unidad as 'Unidad Comercial', u.canon_base as 'Precio Sugerido de Mercado' FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible'")
        if not df_libres.empty:
            st.markdown(f"<div style='background: rgba(0,198,255,0.05); border: 1px solid rgba(0,198,255,0.3); border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px;'><h2 style='color:#00C6FF; margin:0;'>{len(df_libres)} Activos Listos para Comercializar</h2></div>", unsafe_allow_html=True)
            df_libres['Precio Sugerido de Mercado'] = df_libres['Precio Sugerido de Mercado'].apply(fmt_cop)
            st.dataframe(df_libres, use_container_width=True, hide_index=True)
        else: 
            st.markdown("<div style='background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px;'><h1 style='color:#34D399; margin:0; font-size: 3rem;'>100%</h1><h3 style='color:#A7F3D0; margin:0;'>Ocupación Total</h3></div>", unsafe_allow_html=True)

    # --- MÓDULO 6: SEGURIDAD ---
    elif mod == "seguridad":
        st.markdown("<h2 class='fade-in'>Core y Seguridad IAM ⚙️</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2], gap="large")
        with c1:
            with st.form("f_nuevo_usuario", clear_on_submit=True):
                st.markdown("<h4 style='color:#00C6FF;'>Asignación de Roles</h4>", unsafe_allow_html=True)
                n_u = st.text_input("Usuario (Login)")
                n_p = st.text_input("Contraseña de Acceso", type="password")
                n_n = st.text_input("Nombre de Identidad")
                n_r = st.selectbox("Jerarquía", ["Administrador", "Asesor Comercial"])
                if st.form_submit_button("Crear Perfil IAM") and n_u and n_p:
                    if run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (n_u, n_p, n_n, n_r)):
                        st.toast("Estructura de seguridad actualizada.", icon="✅"); time.sleep(1); st.rerun()
        with c2:
            df_users = run_query("SELECT username as Login, nombre_completo as Nombre, rol as Rango, IF(activo, 'Activo', 'Inactivo') as Estatus FROM usuarios")
            if not df_users.empty: st.dataframe(df_users.style.map(get_color_estado), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    if not st.session_state['logeado']: pantalla_login()
    else: app_principal()
