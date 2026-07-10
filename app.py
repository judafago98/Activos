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
# 2. DISEÑO ULTRA PREMIUM (CRISTAL LÍQUIDO)
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
        
        div[data-testid="stForm"] { background: rgba(4, 13, 30, 0.6) !important; backdrop-filter: blur(15px) !important; border: 1px solid rgba(0, 198, 255, 0.2) !important; border-radius: 16px !important; padding: 25px !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4); }
        [data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.85) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(0, 198, 255, 0.15); }
        [data-testid="stMetric"] { background: rgba(10, 20, 40, 0.6); backdrop-filter: blur(15px); border: 1px solid rgba(0, 198, 255, 0.1); border-radius: 16px; padding: 24px; border-top: 3px solid #00C6FF; }
        
        .stButton>button { background: linear-gradient(135deg, #0066FF 0%, #00C6FF 100%); color: #FFFFFF !important; border: none; border-radius: 8px; font-weight: 600; width: 100%; transition: all 0.3s ease;}
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4); }
        input, select, textarea { background-color: rgba(4, 13, 30, 0.7) !important; color: white !important; border: 1px solid rgba(0, 198, 255, 0.2) !important; border-radius: 8px !important; }
        input:focus, select:focus, textarea:focus { border-color: #00E5FF !important; box-shadow: 0 0 12px rgba(0, 198, 255, 0.3) !important; }

        [data-testid="stDataFrame"] { background-color: rgba(255, 255, 255, 0.02); border-radius: 8px; padding: 10px; }
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 600 !important; }
        
        .fade-in { animation: fadeIn 0.6s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ESTADO DE SESIÓN Y SEGURIDAD
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
    except (ValueError, TypeError): return "$0"
    s = f"{val_int:,}".replace(',', '.')
    return f"${s}"

def get_color_estado(val):
    if val in ['Vigente', 'Aplicado', 'Ocupado', 'Activo']: return 'background-color: rgba(16, 185, 129, 0.1); color: #34D399;'
    if val in ['Cancelado', 'Anulado', 'Mora', 'Inactivo']: return 'background-color: rgba(245, 158, 11, 0.1); color: #F59E0B;'
    if val in ['Disponible']: return 'background-color: rgba(0, 198, 255, 0.1); color: #00C6FF;'
    return ''

# ==========================================
# 5. MOTOR DE BASE DE DATOS
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
        st.error(f"Error de conexión: {e}")
        return None

def run_query(query, params=None):
    conn = init_connection()
    if conn is None or not conn.is_connected(): return pd.DataFrame()
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
    conn = init_connection()
    if conn is None or not conn.is_connected(): return False
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        return True
    except Exception as e:
        st.error(f"Error transaccional: {e}")
        return False
    finally:
        cursor.close()

# ==========================================
# 6. PANTALLA DE LOGIN (AUTENTICACIÓN REAL)
# ==========================================
def pantalla_login():
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("<h2 style='text-align: center; color: #00C6FF; font-size: 2.2rem; margin-bottom: 5px;'>Portal de Acceso</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94A3B8; margin-bottom: 25px;'>Identificación Corporativa</p>", unsafe_allow_html=True)
            
            usuario = st.text_input("👤 Usuario")
            password = st.text_input("🔒 Clave de Seguridad", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Validar Credenciales"):
                if usuario and password:
                    # Consulta directa a la base de datos blindada
                    query = "SELECT id, nombre_completo, rol FROM usuarios WHERE username = %s AND password = %s AND activo = TRUE"
                    df_user = run_query(query, (usuario, password))
                    
                    if not df_user.empty:
                        st.session_state['logeado'] = True
                        st.session_state['nombre_usuario'] = df_user.iloc[0]['nombre_completo']
                        st.session_state['rol'] = df_user.iloc[0]['rol']
                        st.toast(f"Bienvenido, {st.session_state['nombre_usuario']}", icon="✅")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas o usuario inactivo.")
                else:
                    st.warning("Ingrese usuario y contraseña.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 7. ENRUTADOR PRINCIPAL (APP)
# ==========================================
def app_principal():
    st.sidebar.markdown(f"""
        <div style='padding: 15px; background: rgba(0, 198, 255, 0.05); border-radius: 12px; border: 1px solid rgba(0,198,255,0.2); margin-bottom: 20px; text-align: center;'>
            <b style='color:#F8FAFC; font-size: 16px;'>{st.session_state['nombre_usuario']}</b><br>
            <span style='color:#00C6FF; font-size: 11px; font-weight: 600; letter-spacing: 1px;'>{str(st.session_state['rol']).upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    menu = {
        "📊 Panel Gerencial": "dash",
        "🏢 Gestión de Activos": "activos",
        "👥 Contratos e Inquilinos": "contratos",
        "💰 Flujo de Tesorería": "tesoreria",
        "🔑 Disponibilidad": "vacancia"
    }
    
    # Añadimos el módulo de seguridad solo si es Administrador
    if st.session_state['rol'] == 'Administrador':
        menu["⚙️ Seguridad y Usuarios"] = "seguridad"

    nav = st.sidebar.radio("Navegación", list(menu.keys()), label_visibility="collapsed")
    mod = menu[nav]
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state['logeado'] = False
        st.session_state['rol'] = None
        st.session_state['nombre_usuario'] = None
        st.rerun()

    # ----------------------------------------
    # MÓDULOS 1 al 5 (Sin Cambios Estructurales, ocultados por brevedad visual aquí, DEBES MANTENERLOS)
    # ----------------------------------------
    if mod == "dash":
        st.markdown("<h2 class='fade-in'>Panel Gerencial de Activos 📊</h2>", unsafe_allow_html=True)
        # ... (Tu código actual del dashboard)
        df_activos = run_query("SELECT COUNT(*) as t FROM contratos WHERE estado_contrato = 'Vigente'")
        t_contratos = df_activos.iloc[0]['t'] if not df_activos.empty else 0
        df_ingresos = run_query("SELECT SUM(monto_pagado) as t FROM pagos WHERE estado_pago = 'Aplicado'")
        t_ingresos = df_ingresos.iloc[0]['t'] if not df_ingresos.empty and pd.notna(df_ingresos.iloc[0]['t']) else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Contratos Vigentes", f"{t_contratos} Activos")
        c2.metric("Recaudo Histórico", fmt_cop(t_ingresos))
        c3.metric("Estado Operativo", "En Línea 🟢")

    elif mod == "activos":
        st.markdown("<h2 class='fade-in'>Gestión de Activos Físicos 🏢</h2>", unsafe_allow_html=True)
        # ... (Tu código actual de activos)
        st.info("Módulo de activos en línea.")

    elif mod == "contratos":
        st.markdown("<h2 class='fade-in'>Contratos e Inquilinos 👥</h2>", unsafe_allow_html=True)
        # ... (Tu código actual de contratos)
        st.info("Módulo de contratos en línea.")

    elif mod == "tesoreria":
        st.markdown("<h2 class='fade-in'>Flujo de Tesorería 💰</h2>", unsafe_allow_html=True)
        # ... (Tu código actual de tesorería)
        st.info("Módulo de tesorería en línea.")

    elif mod == "vacancia":
        st.markdown("<h2 class='fade-in'>Índice de Disponibilidad 🔑</h2>", unsafe_allow_html=True)
        # ... (Tu código actual de vacancia)
        st.info("Módulo de disponibilidad en línea.")

    # ----------------------------------------
    # MÓDULO 6: SEGURIDAD (NUEVO)
    # ----------------------------------------
    elif mod == "seguridad":
        st.markdown("<h2 class='fade-in'>Configuración y Accesos IAM ⚙️</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8;'>Gestión de usuarios, roles y perímetro de seguridad del ecosistema.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 2], gap="large")
        
        with c1:
            with st.form("f_nuevo_usuario", clear_on_submit=True):
                st.markdown("<h4 style='color:#00C6FF;'>Alta de Nuevo Perfil</h4>", unsafe_allow_html=True)
                n_user = st.text_input("Usuario (Login corto)")
                n_pass = st.text_input("Contraseña Asignada", type="password")
                n_nombre = st.text_input("Nombre Completo (Real)")
                n_rol = st.selectbox("Nivel de Acceso", ["Administrador", "Asesor Comercial", "Contador"])
                
                if st.form_submit_button("Crear Credencial"):
                    if n_user and n_pass and n_nombre:
                        query = "INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)"
                        if run_transact(query, (n_user, n_pass, n_nombre, n_rol)):
                            st.toast("Usuario autorizado en el sistema.", icon="✅")
                            time.sleep(1); st.rerun()
                    else:
                        st.error("⚠️ La matriz de seguridad exige llenar todos los campos.")

        with c2:
            st.markdown("#### Directorio Corporativo Activo")
            df_users = run_query("""
                SELECT id as ID, username as Usuario, nombre_completo as Nombre, rol as Rol, IF(activo, 'Activo', 'Inactivo') as Estatus 
                FROM usuarios ORDER BY id DESC
            """)
            if not df_users.empty:
                st.dataframe(df_users.style.applymap(get_color_estado, subset=['Estatus']), use_container_width=True, hide_index=True)
            else:
                st.info("Error de lectura del directorio.")

# ==========================================
# 8. EJECUCIÓN
# ==========================================
def main():
    if not st.session_state['logeado']:
        pantalla_login()
    else:
        app_principal()

if __name__ == "__main__":
    main()
