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
st.set_page_config(page_title="Activos Pro", layout="wide", initial_sidebar_state="expanded", page_icon="🏢")

# ==========================================
# 2. MOTOR CSS PREMIUM (MONOCROMÁTICO Y NEÓN MORADO - CERO ROJOS)
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

        /* Fondo Dark Premium */
        .stApp { background-color: #050505 !important; color: #FAFAFA !important; }
        #MainMenu, footer, header, [data-testid="stHeader"] {display: none !important;}
        
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-thumb { background: #222222; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #8B5CF6; }

        /* INPUTS Y SELECTS: FOCUS MORADO NEÓN */
        div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
            background-color: #111111 !important;
            border: 1px solid #222222 !important;
            border-radius: 8px !important;
            color: white !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.4) !important;
            background-color: #161616 !important;
        }
        input, select, textarea { color: white !important; outline: none !important; background: transparent !important; }

        /* ASESINATO DE LA LÍNEA ROJA EN LAS PESTAÑAS (TABS) */
        .stTabs [data-baseweb="tab-highlight"] { background-color: #8B5CF6 !important; }
        .stTabs [data-baseweb="tab-border"] { background-color: #222222 !important; }
        .stTabs button[role="tab"] { color: #A1A1AA !important; font-weight: 600 !important; }
        .stTabs button[role="tab"][aria-selected="true"] { color: #FFFFFF !important; }

        /* Formularios Modernos */
        [data-testid="stForm"] {
            background: #0A0A0A !important;
            border: 1px solid #222222 !important;
            border-radius: 12px !important;
            padding: 30px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.9) !important;
        }

        /* Botones de Acción */
        .stButton>button {
            background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 20px rgba(139, 92, 246, 0.6) !important;
            background: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%) !important;
        }

        /* REMOCIÓN DEL PUNTO ROJO DEL MENÚ LATERAL Y REFACTORIZACIÓN VISUAL */
        [data-testid="stSidebar"] {
            background-color: #09090B !important;
            border-right: 1px solid #1F1F22 !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label div[data-baseweb="radio"] { display: none !important; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child { display: none !important; }
        
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            background: transparent !important;
            border-radius: 6px !important;
            padding: 12px 15px !important; margin: 2px 8px !important;
            transition: all 0.2s ease !important; cursor: pointer !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #A1A1AA !important; font-weight: 500 !important; margin: 0 !important; }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
            background: rgba(139, 92, 246, 0.15) !important;
            border-left: 4px solid #8B5CF6 !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] p { color: #FFFFFF !important; font-weight: 700 !important;}

        /* Tarjetas de Métricas */
        [data-testid="stMetric"] { 
            background: #111111; border: 1px solid #222222; 
            border-radius: 12px; padding: 20px; border-top: 2px solid #8B5CF6; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: transform 0.2s ease;
        }
        [data-testid="stMetric"]:hover { transform: translateY(-3px); border-top: 2px solid #10B981; }
        
        [data-testid="stDataFrame"] { background-color: #0A0A0A; border-radius: 8px; padding: 10px; border: 1px solid #222222; }
        [data-testid="stAlert"] { background-color: #111111 !important; border: 1px solid #222222 !important; color: #FFFFFF !important; }
        
        h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

def render_logo():
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center; background: #111111; border-radius: 12px; border: 1px solid #222222; padding: 15px; margin-bottom: 20px;'>
            <h1 style='color: #FFFFFF; font-size: 1.8rem; font-weight: 800; letter-spacing: 2px; margin:0;'>🏢 ACTIVOS PRO</h1>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CONEXIÓN OPTIMIZADA POR POOL CENTRAL
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
        return True
    except Exception: return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# --- AUTO HEALING EN MINÚSCULAS STRICT (Previene tablas vacías y error 1054) ---
@st.cache_resource
def inicializar_bd():
    tablas = [
        "CREATE TABLE IF NOT EXISTS usuarios (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(255), nombre_completo VARCHAR(150), rol VARCHAR(50) DEFAULT 'Asesor', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS propiedades (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150), direccion VARCHAR(255), activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS unidades (id INT AUTO_INCREMENT PRIMARY KEY, propiedad_id INT, nombre_unidad VARCHAR(100), canon_base DECIMAL(15,2), estado_vacancia VARCHAR(50) DEFAULT 'Disponible', activo BOOLEAN DEFAULT TRUE)",
        "CREATE TABLE IF NOT EXISTS inquilinos (id INT AUTO_INCREMENT PRIMARY KEY, documento_identidad VARCHAR(50) UNIQUE, nombre_completo VARCHAR(150), telefono VARCHAR(50))",
        "CREATE TABLE IF NOT EXISTS contratos (id INT AUTO_INCREMENT PRIMARY KEY, unidad_id INT, inquilino_id INT, canon_pactado DECIMAL(15,2), dia_pago_mensual INT, fecha_inicio DATE, fecha_fin DATE, estado_contrato VARCHAR(50) DEFAULT 'Vigente')",
        "CREATE TABLE IF NOT EXISTS pagos (id INT AUTO_INCREMENT PRIMARY KEY, contrato_id INT, periodo_pagado VARCHAR(20), monto_pagado DECIMAL(15,2), id_referencia_banco VARCHAR(100), fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, estado_pago VARCHAR(50) DEFAULT 'Aplicado')"
    ]
    for t in tablas: run_transact(t)
    
    # Inyectar alteración de columnas de seguridad sobre las tablas en minúscula
    columnas_parche = [
        ("pagos", "periodo_pagado", "VARCHAR(20)"),
        ("pagos", "contrato_id", "INT"),
        ("pagos", "monto_pagado", "DECIMAL(15,2)"),
        ("pagos", "estado_pago", "VARCHAR(50) DEFAULT 'Aplicado'"),
        ("propiedades", "activo", "BOOLEAN DEFAULT TRUE"),
        ("unidades", "activo", "BOOLEAN DEFAULT TRUE")
    ]
    for tabla, col, tipo in columnas_parche:
        try: run_transact(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")
        except: pass

    if run_query("SELECT id FROM usuarios WHERE username='admin'").empty:
        run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES ('admin', '123', 'Gerencia General', 'Administrador')")

inicializar_bd()

# ==========================================
# 4. UTILS
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
            if st.form_submit_button("Ingresar"):
                df_u = run_query("SELECT nombre_completo, rol FROM usuarios WHERE username=%s AND password=%s AND activo=TRUE", (u, p))
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
    st.markdown(f"<div style='background: #111; border: 1px solid #333; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 20px;'><b style='color:white;'>{st.session_state['nombre_usuario']}</b><br><span style='color:#8B5CF6; font-size:11px; font-weight:bold;'>{st.session_state['rol'].upper()}</span></div>", unsafe_allow_html=True)
    
    menu = {"📊 Panel General": "dash", "🏢 Inmuebles y Activos": "activos", "👥 Contratos": "contratos", "💰 Tesorería": "tesoreria", "🔑 Vacancia": "vacancia"}
    if st.session_state['rol'] == 'Administrador': menu["⚙️ Seguridad IAM"] = "seguridad"
    
    mod = menu[st.radio("Navegación", list(menu.keys()), label_visibility="collapsed")]
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state['logeado'] = False; st.rerun()

# ----------------------------------------
# DASHBOARD (LEER HISTORIAL COMPLETO)
# ----------------------------------------
if mod == "dash":
    st.markdown("<h2>Mando Gerencial 📊</h2>", unsafe_allow_html=True)
    t_con = run_query("SELECT COUNT(*) as t FROM contratos WHERE estado_contrato = 'Vigente'")
    t_ing = run_query("SELECT SUM(monto_pagado) as t FROM pagos WHERE estado_pago = 'Aplicado'")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Contratos Activos", f"{t_con.iloc[0]['t'] if not t_con.empty else 0}")
    c2.metric("Absorción de Caja", fmt_cop(t_ing.iloc[0]['t'] if not t_ing.empty and pd.notna(t_ing.iloc[0]['t']) else 0))
    c3.metric("Servidor", "Operativo 🟢")
    
    st.divider()
    st.markdown("#### Radar de Transacciones")
    df_p = run_query("""
        SELECT p.fecha_registro as Fecha, IFNULL(u.nombre_unidad, 'Unidad Desconocida') as Origen, 
               p.periodo_pagado as 'Periodo Cubierto', p.monto_pagado as Ingreso, p.estado_pago as Estado 
        FROM pagos p 
        LEFT JOIN contratos c ON p.contrato_id = c.id 
        LEFT JOIN unidades u ON c.unidad_id = u.id 
        ORDER BY p.id DESC LIMIT 15
    """)
    if not df_p.empty:
        df_p['Ingreso'] = df_p['Ingreso'].apply(fmt_cop)
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else: st.info("Registro contable en ceros. No hay ingresos registrados.")

# ----------------------------------------
# ACTIVOS
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
                    if run_transact("INSERT INTO propiedades (nombre, direccion) VALUES (%s, %s)", (nom, dir)):
                        st.toast("Propiedad listada."); time.sleep(1); st.rerun()
        with c2:
            df_p = run_query("SELECT id as ID, nombre as Complejo, direccion as Dirección, IF(activo,'Activo','Inactivo') as Estado FROM propiedades")
            if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

    with t2:
        df_props = run_query("SELECT id, nombre FROM propiedades WHERE activo = TRUE")
        if df_props.empty: st.warning("Requiere matriz estructural activa.")
        else:
            c1, c2 = st.columns([1, 2], gap="large")
            opc_p = {row['nombre']: row['id'] for _, row in df_props.iterrows()}
            with c1:
                with st.form("f_u"):
                    sel_p = st.selectbox("Nodo Padre:", list(opc_p.keys()))
                    n_uni = st.text_input("Nomenclatura (Ej: Local 1)")
                    can_b = st.number_input("Valor de Salida ($)", step=50000)
                    if st.form_submit_button("Liberar al Mercado") and n_uni:
                        if run_transact("INSERT INTO unidades (propiedad_id, nombre_unidad, canon_base) VALUES (%s, %s, %s)", (opc_p[sel_p], n_uni, int(can_b))):
                            st.toast("Unidad en circulación."); time.sleep(1); st.rerun()
            with c2:
                df_u = run_query("SELECT p.nombre as Complejo, u.nombre_unidad as Unidad, u.canon_base as 'Tarifa', IF(u.activo,'Activo','Inactivo') as Operatividad, u.estado_vacancia as Vacancia FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id ORDER BY u.id DESC")
                if not df_u.empty:
                    df_u['Tarifa'] = df_u['Tarifa'].apply(fmt_cop)
                    st.dataframe(df_u, use_container_width=True, hide_index=True)
                    
    with t3:
        st.markdown("#### Desactivar o Activar Entidades")
        colA, colB = st.columns(2)
        with colA:
            with st.form("f_tog_prop"):
                df_all_p = run_query("SELECT id, nombre, activo FROM propiedades")
                if not df_all_p.empty:
                    sel_tog_p = st.selectbox("Seleccionar Propiedad", [f"[{'Activo' if r['activo'] else 'Inactivo'}] {r['nombre']}" for _, r in df_all_p.iterrows()])
                    if st.form_submit_button("Alternar Estado"):
                        nom_p = sel_tog_p.split("] ")[1]
                        nuevo_estado = 0 if "Activo" in sel_tog_p else 1
                        run_transact("UPDATE propiedades SET activo = %s WHERE nombre = %s", (nuevo_estado, nom_p))
                        st.rerun()
        with colB:
            with st.form("f_tog_uni"):
                df_all_u = run_query("SELECT id, nombre_unidad, activo FROM unidades")
                if not df_all_u.empty:
                    sel_tog_u = st.selectbox("Seleccionar Unidad", [f"[{'Activa' if r['activo'] else 'Inactiva'}] {r['nombre_unidad']}" for _, r in df_all_u.iterrows()])
                    if st.form_submit_button("Alternar Estado "):
                        nom_u = sel_tog_u.split("] ")[1]
                        nuevo_estado = 0 if "Activa" in sel_tog_u else 1
                        run_transact("UPDATE unidades SET activo = %s WHERE nombre_unidad = %s", (nuevo_estado, nom_u))
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
                    if run_transact("INSERT INTO inquilinos (documento_identidad, nombre_completo, telefono) VALUES (%s, %s, %s)", (ced, nom, tel)):
                        st.toast("Cliente en red."); time.sleep(1); st.rerun()
        with c2:
            df_i = run_query("SELECT documento_identidad as ID, nombre_completo as Razón, telefono as Contacto FROM inquilinos")
            if not df_i.empty: st.dataframe(df_i, use_container_width=True, hide_index=True)

    with t2:
        df_i = run_query("SELECT id, nombre_completo, documento_identidad FROM inquilinos")
        df_u = run_query("SELECT u.id, u.nombre_unidad, p.nombre FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
        
        if df_i.empty or df_u.empty: st.warning("El despliegue requiere clientes y activos activos.")
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
                    fi = st.date_input("Fecha Inicio")
                    ff = st.date_input("Fecha Fin Teórica", value=fi + datetime.timedelta(days=365))
                if st.form_submit_button("Inyectar Contrato") and can > 0:
                    if run_transact("INSERT INTO contratos (unidad_id, inquilino_id, canon_pactado, dia_pago_mensual, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s, %s)", (opc_u[sel_u], opc_i[sel_i], int(can), dia, fi, ff)):
                        run_transact("UPDATE unidades SET estado_vacancia = 'Ocupado' WHERE id = %s", (opc_u[sel_u],))
                        st.toast("Contrato blindado."); time.sleep(1); st.rerun()
                        
    with t3:
        st.markdown("#### Entregar Inmueble y Cerrar Contrato")
        df_activos = run_query("SELECT c.id, c.unidad_id, u.nombre_unidad, p.nombre as prop, i.nombre_completo FROM contratos c JOIN unidades u ON c.unidad_id=u.id JOIN propiedades p ON u.propiedad_id=p.id JOIN inquilinos i ON c.inquilino_id=i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("No hay contratos vigentes.")
        else:
            with st.form("f_kill"):
                opc_kill = {f"[{r['id']}] {r['prop']} - {r['nombre_unidad']} | {r['nombre_completo']}": (r['id'], r['unidad_id']) for _, r in df_activos.iterrows()}
                sel_kill = st.selectbox("Seleccionar contrato a terminar:", list(opc_kill.keys()))
                fecha_terminacion_real = st.date_input("Fecha real de finalización / entrega:")
                if st.form_submit_button("🛑 Ejecutar Terminación"):
                    id_con, id_uni = opc_kill[sel_kill]
                    if run_transact("UPDATE contratos SET estado_contrato = 'Finalizado', fecha_fin = %s WHERE id = %s", (fecha_terminacion_real, id_con)):
                        run_transact("UPDATE unidades SET estado_vacancia = 'Disponible' WHERE id = %s", (id_uni,))
                        st.toast("Contrato cerrado."); time.sleep(1.5); st.rerun()

# ----------------------------------------
# TESORERÍA (PAGOS PARCIALES - PREVENCIÓN COBROS DE MÁS)
# ----------------------------------------
elif mod == "tesoreria":
    st.markdown("<h2>Tesorería 💰</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📥 Registrar Ingreso", "🗑️ Revertir Pagos"])
    
    with t1:
        df_activos = run_query("SELECT c.id, c.fecha_inicio, c.fecha_fin, u.nombre_unidad as uni, p.nombre as prop, i.nombre_completo as inq, c.canon_pactado FROM contratos c JOIN unidades u ON c.unidad_id = u.id JOIN propiedades p ON u.propiedad_id = p.id JOIN inquilinos i ON c.inquilino_id = i.id WHERE c.estado_contrato = 'Vigente'")
        if df_activos.empty: st.info("Sin contratos vigentes que auditar.")
        else:
            c1, c2 = st.columns([1.2, 2], gap="large")
            opc_c = {f"{r['prop']} {r['uni']} - {r['inq']} (Canon: {fmt_cop(r['canon_pactado'])})": r for _, r in df_activos.iterrows()}
            
            with c1:
                sel_c = st.selectbox("Seleccionar Obligación Vigente", list(opc_c.keys()))
                dat_con = opc_c[sel_c]
                canon_base = int(float(dat_con['canon_pactado']))
                
                # Algoritmo estricto de control de saldos y ocultamiento de meses completos
                df_pagos_contrato = run_query("SELECT periodo_pagado, SUM(monto_pagado) as total_pagado FROM pagos WHERE contrato_id = %s GROUP BY periodo_pagado", (int(dat_con['id']),))
                pagos_map = {row['periodo_pagado']: int(float(row['total_pagado'])) for _, row in df_pagos_contrato.iterrows()} if not df_pagos_contrato.empty else {}
                
                periodos_todos = generar_periodos_contrato(dat_con['fecha_inicio'], dat_con['fecha_fin'])
                periodos_pendientes = []
                deuda_por_periodo = {}
                
                for p in periodos_todos:
                    pagado = pagos_map.get(p, 0)
                    pendiente = canon_base - pagado
                    if pendiente > 0:
                        periodos_pendientes.append(p)
                        deuda_por_periodo[p] = pendiente
                
                if not periodos_pendientes: st.success("Este contrato está completamente al día.")
                else:
                    with st.form("f_pago", clear_on_submit=True):
                        per_sel = st.selectbox("Periodo a Pagar (Oculta meses saldados)", periodos_pendientes)
                        saldo_pendiente = int(deuda_por_periodo.get(per_sel, canon_base))
                        
                        # Tipos forzados estrictamente a Integer para prevenir la pantalla roja de Streamlit
                        monto = st.number_input("Capital Recibido ($)", min_value=0, max_value=int(saldo_pendiente), value=int(saldo_pendiente), step=50000)
                        ref = st.text_input("Referencia Bancaria")
                        
                        if st.form_submit_button("Asentar Transacción") and monto > 0:
                            if run_transact("INSERT INTO pagos (contrato_id, periodo_pagado, monto_pagado, id_referencia_banco) VALUES (%s, %s, %s, %s)", (int(dat_con['id']), str(per_sel), int(monto), str(ref))):
                                st.toast("Pago registrado."); time.sleep(1); st.rerun()
            with c2:
                df_hist = run_query("SELECT p.fecha_registro as Timestamp, IFNULL(u.nombre_unidad, 'Unidad Borrada') as Origen, p.periodo_pagado as Periodo, p.monto_pagado as Volumen FROM pagos p LEFT JOIN contratos c ON p.contrato_id = c.id LEFT JOIN unidades u ON c.unidad_id = u.id ORDER BY p.id DESC LIMIT 15")
                if not df_hist.empty:
                    df_hist['Volumen'] = df_hist['Volumen'].apply(fmt_cop)
                    st.dataframe(df_hist, use_container_width=True, hide_index=True)

    with t2:
        st.markdown("#### Anular Transacción del Sistema")
        df_pagos_del = run_query("SELECT p.id, p.fecha_registro, p.monto_pagado, IFNULL(u.nombre_unidad, 'Unidad Desconocida') as nombre_unidad, IFNULL(i.nombre_completo, 'Cliente Desconocido') as nombre_completo, p.periodo_pagado FROM pagos p LEFT JOIN contratos c ON p.contrato_id = c.id LEFT JOIN unidades u ON c.unidad_id = u.id LEFT JOIN inquilinos i ON c.inquilino_id = i.id ORDER BY p.id DESC LIMIT 50")
        if not df_pagos_del.empty:
            with st.form("f_del_pago"):
                opc_p = {f"[{str(r['fecha_registro'])[:10]}] {r['nombre_unidad']} - {r['nombre_completo']} | Periodo: {r['periodo_pagado']} | Monto: {fmt_cop(r['monto_pagado'])}": r['id'] for _, r in df_pagos_del.iterrows()}
                sel_p = st.selectbox("Seleccionar Pago a Revertir", list(opc_p.keys()))
                if st.form_submit_button("🗑️ Eliminar Pago"):
                    if run_transact("DELETE FROM pagos WHERE id = %s", (opc_p[sel_p],)):
                        st.toast("Pago eliminado."); time.sleep(1); st.rerun()

# ----------------------------------------
# VACANCIA
# ----------------------------------------
elif mod == "vacancia":
    st.markdown("<h2>Disponibilidad 🔑</h2>", unsafe_allow_html=True)
    df_l = run_query("SELECT p.nombre as Estructura, u.nombre_unidad as Unidad, u.canon_base as 'Canon Base' FROM unidades u JOIN propiedades p ON u.propiedad_id = p.id WHERE u.estado_vacancia = 'Disponible' AND u.activo = TRUE AND p.activo = TRUE")
    if not df_l.empty:
        df_l['Canon Base'] = df_l['Canon Base'].apply(fmt_cop)
        st.dataframe(df_l, use_container_width=True, hide_index=True)
    else: st.success("Ocupación total de activos habilitados.")

# ----------------------------------------
# SEGURIDAD IAM
# ----------------------------------------
elif mod == "seguridad":
    st.markdown("<h2>Seguridad IAM ⚙️</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        with st.form("f_u", clear_on_submit=True):
            nu = st.text_input("Alias")
            np = st.text_input("Hash Secreto", type="password")
            nn = st.text_input("Nombre Real")
            nr = st.selectbox("Jerarquía", ["Administrador", "Asesor Comercial"])
            if st.form_submit_button("Crear Perfil") and nu and np:
                if run_transact("INSERT INTO usuarios (username, password, nombre_completo, rol) VALUES (%s, %s, %s, %s)", (nu, np, nn, nr)):
                    st.toast("Usuario guardado."); time.sleep(1); st.rerun()
    with c2:
        df_u = run_query("SELECT username as Alias, nombre_completo as Nombre, rol as Privilegios, IF(activo, 'Activo', 'Inactivo') as Estado FROM usuarios")
        if not df_u.empty: st.dataframe(df_u, use_container_width=True, hide_index=True)
