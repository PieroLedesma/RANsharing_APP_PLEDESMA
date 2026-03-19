# =============================================================================
# app.py — Monitoreo RanSharing Entel | APP_RANSHARING
# Estilo WOM/Entel: Púrpura · Magenta · Blanco
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# ── Page config (DEBE ir primero) ─────────────────────────────────────────────
st.set_page_config(
    page_title="Monitoreo RANSharing WOM con proveedor Entel",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config.settings import (
    GSHEETS_URL, GSHEETS_WORKSHEET, TIME_OPTIONS, KPI_MODULES, OPERADOR_FILTER, PALETTE
)
from utils.auth import check_password, download_logs_button

# Impedir el renderizado del dashboard si no hay autenticación correcta
if not check_password():
    st.stop()

from utils.db import execute_query, test_connection
from utils.kpis import calculate_audit_kpis, get_site_status_for_map
from utils.master_table import load_master_table
from queries.sql_queries import (
    get_accesibilidad_query, get_usuarios_query, get_prb_query,
    get_trafico_query, get_drop_query, get_downtime_query,
    get_volte_query, get_sites_with_data_query,
    get_table_info_query, get_tables_list_query,
    TABLE_NAME,
)
from components.cards import (
    render_audit_card, render_faltantes_card,
    render_section_header, render_connection_status,
)
from components.charts import (
    render_accesibilidad_chart, render_downtime_chart, render_drop_chart,
    render_velocidad_chart, render_usuarios_chart, render_prb_chart,
    render_trafico_chart, render_volte_chart, render_map,
)

# =============================================================================
# CSS GLOBAL — Diseño WOM/Entel
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset y base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif !important; }

/* ── Fondo principal ── */
.stApp { background-color: #F2EDF9; }

/* ── Ocultar elementos default de Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12012B 0%, #2D0A5E 45%, #5E1896 100%) !important;
    border-right: 2px solid #E91E8C;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] p, 
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] h1,
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] h2,
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] h3 {
    color: white !important;
}

/* Selectbox labels en Sidebar */
[data-testid="stSidebar"] label p {
    color: white !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* Forzar texto de selectbox a ser negro/oscuro (el input en sí) */
div[data-baseweb="select"] * {
    color: #1A1A2E !important;
}
[data-testid="stSidebar"] .stRadio div[role="radio"] label {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 9px 12px;
    margin: 3px 0;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0px !important;
    text-transform: none !important;
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebar"] .stRadio div[role="radio"]:has(input:checked) label {
    background: linear-gradient(90deg, rgba(233,30,140,0.35), rgba(123,45,139,0.2));
    border-color: #E91E8C;
    color: white !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radio"] label:hover {
    background: rgba(233,30,140,0.25);
    border-color: rgba(233,30,140,0.5);
}

/* Sidebar multiselect */
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
    background: rgba(233,30,140,0.5) !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
    margin: 10px 0 !important;
}

/* ── BOTONES GENÉRICOS DE LA APLICACIÓN ── */
.stButton > button {
    background-color: #FFFFFF !important;
    border: 1px solid #7B2D8B !important;
    border-radius: 8px !important;
}
.stButton > button p {
    color: #7B2D8B !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #7B2D8B !important;
}
.stButton > button:hover p {
    color: #FFFFFF !important;
}

/* ── BOTONES EN EL SIDEBAR ── */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #E91E8C, #7B2D8B) !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
}
[data-testid="stSidebar"] .stButton > button p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #7B2D8B, #E91E8C) !important;
    opacity: 0.9;
}


/* ── MAIN CONTENT ── */
/* Botones de periodo temporal */
div[data-testid="stHorizontalBlock"] .stButton > button {
    border-radius: 20px !important;
    padding: 6px 18px !important;
    width: 100% !important;
}

/* ── Charts container ── */
[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 2px 14px rgba(123,45,139,0.1);
    border: 1px solid rgba(123,45,139,0.08);
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7B2D8B !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F2EDF9; }
::-webkit-scrollbar-thumb { background: #7B2D8B; border-radius: 3px; }

/* ── Selectbox / Multiselect general ── */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: rgba(123,45,139,0.3) !important;
}

/* ── Alert boxes ── */
.stAlert { border-radius: 10px !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(123,45,139,0.05) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: #7B2D8B !important;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HELPERS
# =============================================================================

# Tabla maestra se carga via utils/master_table.py (ver load_master_table) desde PostgreSQL ransharing.cell_ransharing


@st.cache_data(ttl=600)
def fetch_max_date() -> datetime:
    try:
        # Usamos ORDER BY DESC LIMIT 1 porque en PostgreSQL con índices suele ser más rápido que MAX()
        df = execute_query(f'SELECT "Timestamp_ID" FROM {TABLE_NAME} ORDER BY "Timestamp_ID" DESC LIMIT 1')
        if not df.empty and df.iloc[0, 0] is not None:
            return pd.to_datetime(df.iloc[0, 0])
    except Exception:
        pass
    return datetime.now()

def get_date_range(days: int):
    """Retorna (start, end) como datetime para el período seleccionado."""
    end   = fetch_max_date()
    start = end - timedelta(days=days)
    return start, end


def format_period_label(days: int) -> str:
    if days == 1:
        return "Últimas 24 horas"
    return f"Últimos {days} días"


# =============================================================================
# ESTADO DE SESIÓN
# =============================================================================
if 'selected_period'  not in st.session_state:
    st.session_state['selected_period'] = 1    # default: 24 horas
if 'selected_module'  not in st.session_state:
    st.session_state['selected_module'] = KPI_MODULES[0]
if 'filter_sites'     not in st.session_state:
    st.session_state['filter_sites'] = []
if 'filter_cells'     not in st.session_state:
    st.session_state['filter_cells'] = []


# =============================================================================
# ▌ SIDEBAR
# =============================================================================
with st.sidebar:

    # ── Logo / Título ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 6px 0;">
        <div style="font-size:26px; font-weight:900; color:white;
                    letter-spacing:-1px; line-height:1;">
            📡 <span style="color:#E91E8C;">RAN</span>Sharing
        </div>
        <div style="font-size:10px; color:rgba(255,255,255,0.45);
                    text-transform:uppercase; letter-spacing:2.5px; margin-top:2px;">
            WOM con proveedor Entel
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón dinámico de cierre de sesión
    st.markdown(f'<div style="text-align:center; font-size:10px; color: #FFF; margin-bottom: 5px;">👤 {st.session_state.get("logged_user", "Usuario")}</div>', unsafe_allow_html=True)
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["password_correct"] = False
        st.session_state["logged_user"] = None
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Cargar datos en el lado del servidor ───────────────────────────────
    with st.spinner("Cargando tabla maestra..."):
        df_maestra = load_master_table()

    db_ok = test_connection()
    render_connection_status(db_ok)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── FILTROS GLOBALES ───────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.5);'
                'text-transform:uppercase;letter-spacing:1px;margin:4px 0 8px 0;">'
                '🔍 Filtros Globales</div>', unsafe_allow_html=True)

    # Obtener listas únicas de la tabla maestra filtradas por operador
    if not df_maestra.empty:
        cols_upper = {c.upper(): c for c in df_maestra.columns}
        op_col   = cols_upper.get('OPERATOR', cols_upper.get('OPERADOR', None))
        site_col = cols_upper.get('SITE', cols_upper.get('SITIO', None))
        cell_col = cols_upper.get('CELLNAME', cols_upper.get('CELL_NAME', cols_upper.get('CELDA', None)))

        df_filt = df_maestra.copy()
        if op_col:
            df_filt = df_filt[df_filt[op_col].str.upper().str.contains(OPERADOR_FILTER.upper(), na=False)]

        sites_list = ["Todos"] + sorted(df_filt[site_col].dropna().unique().tolist()) if site_col else ["Todos"]
    else:
        df_filt = pd.DataFrame()
        site_col = None
        cell_col = None
        sites_list = ["Todos"]

    sel_sites = st.multiselect(
        "SITIO", options=sites_list,
        default=[], placeholder="Todos los sitios",
        key="ms_sites",
    )
    
    # Limpiar el valor "Todos" de las selecciones de sitios
    active_sites = [s for s in sel_sites if s != "Todos"] or []

    # Filtrar la lista de celdas basándonos en los sitios activos
    if not df_filt.empty and cell_col:
        df_cells_filt = df_filt.copy()
        if active_sites and site_col:
            df_cells_filt = df_cells_filt[df_cells_filt[site_col].isin(active_sites)]
        cells_list = ["Todos"] + sorted(df_cells_filt[cell_col].dropna().unique().tolist())
    else:
        cells_list = ["Todos"]

    sel_cells = st.multiselect(
        "CELLNAME", options=cells_list,
        default=[], placeholder="Todas las celdas",
        key="ms_cells",
    )
    # Limpiar el valor "Todos" de las selecciones de celdas
    active_cells = [c for c in sel_cells if c != "Todos"] or []

    if active_sites and not df_maestra.empty:
        site_col_name = next((c for c in df_maestra.columns if c.upper() in ('SITE', 'SITIO')), None)
        if site_col_name:
            df_maestra = df_maestra[df_maestra[site_col_name].str.upper().isin([s.upper() for s in active_sites])]

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── MÓDULOS KPI ────────────────────────────────────────────────────────
    st.markdown('<div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.5);'
                'text-transform:uppercase;letter-spacing:1px;margin:4px 0 8px 0;">'
                '📊 Módulos KPI</div>', unsafe_allow_html=True)

    selected_module = st.radio(
        label="modulo",
        options=KPI_MODULES,
        index=KPI_MODULES.index(st.session_state['selected_module']),
        label_visibility="collapsed",
        key="radio_module",
    )
    st.session_state['selected_module'] = selected_module

    # ── Diagnóstico BD (expandible) ────────────────────────────────────────
    with st.expander("🔧 Diagnóstico BD", expanded=False):
        st.markdown(
            f'<div style="font-size:11px;color:#000000;">'
            f'Tabla configurada: <b>{TABLE_NAME}</b></div>',
            unsafe_allow_html=True
        )
        if st.button("🔍 Ver tablas disponibles", key="btn_diag_tables"):
            df_tables = execute_query(get_tables_list_query())
            if not df_tables.empty:
                st.dataframe(df_tables, height=200)
            else:
                st.warning("Sin resultados o sin acceso.")
        if st.button("📋 Ver columnas de tabla", key="btn_diag_cols"):
            df_cols = execute_query(get_table_info_query())
            if not df_cols.empty:
                st.dataframe(df_cols, height=200)
            else:
                st.warning(f"La tabla '{TABLE_NAME}' no existe o está vacía.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Créditos / Zona Administrativa ──────────────────────────────────────
    logged_user = st.session_state.get("logged_user", "")
    if logged_user == "INTEGRACION":
        st.markdown('<div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.5);'
                    'text-transform:uppercase;letter-spacing:1px;margin:12px 0 8px 0;">'
                    '⚙️ Admin Zone</div>', unsafe_allow_html=True)
        download_logs_button()

    st.markdown("""
    <div style="font-size:9px; color:rgba(255,255,255,0.3); text-align:center; margin-top:16px;">
        v1.1 · WOM Chile · Opt. Performance
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# ▌ MAIN CONTENT
# =============================================================================

# ── Header principal ──────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg, #5E1896 0%, #7B2D8B 50%, #E91E8C 100%);
            border-radius:14px; padding:18px 28px; color:white; margin-bottom:16px;
            box-shadow:0 6px 24px rgba(123,45,139,0.35);">
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:36px;">📡</div>
        <div>
            <h1 style="margin:0; font-size:22px; font-weight:800; letter-spacing:-0.5px;">
                Monitoreo RANSharing WOM con proveedor Entel
            </h1>
            <p style="margin:4px 0 0 0; font-size:12px; opacity:0.75;">
                Supervisión de KPIs LTE · Tabla Maestra RANSHARING_CELLS · PostgreSQL (3T) transload
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Selector de Período ───────────────────────────────────────────────────────
period_col1, period_col2, period_col3, period_col4 = st.columns([1, 1, 1, 3])

with period_col1:
    if st.button("⏱ Últimas 24 Horas", key="btn_24h", use_container_width=True):
        st.session_state['selected_period'] = 1
with period_col2:
    if st.button("📅 Últimos 30 Días", key="btn_30d", use_container_width=True):
        st.session_state['selected_period'] = 30
with period_col3:
    if st.button("📆 Últimos 60 Días", key="btn_60d", use_container_width=True):
        st.session_state['selected_period'] = 60
with period_col4:
    days_selected = st.session_state['selected_period']
    start_dt, end_dt = get_date_range(days_selected)
    st.markdown(f"""
    <div style="background:white; border-radius:8px; padding:8px 14px;
                border-left:4px solid #E91E8C; font-size:12px; color:#555;
                box-shadow:0 1px 6px rgba(123,45,139,0.1); margin-top:2px;">
        <b style="color:#7B2D8B;">Período activo:</b>
        {format_period_label(days_selected)} &nbsp;|&nbsp;
        <span style="color:#888;">{start_dt.strftime('%d/%m/%Y %H:%M')} → {end_dt.strftime('%d/%m/%Y %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)


# =============================================================================
# ── CARGA DE DATOS CON BARRA DE PROGRESO ─────────────────────────────────────
# =============================================================================
start_dt, end_dt = get_date_range(st.session_state['selected_period'])

cellnames_filter = None
if active_cells:
    cellnames_filter = active_cells
elif active_sites and not df_maestra.empty:
    site_col_name = next((c for c in df_maestra.columns if c.upper() in ('SITE', 'SITIO')), None)
    cell_col_name = next((c for c in df_maestra.columns if c.upper() in ('CELLNAME', 'CELL_NAME', 'CELDA')), None)
    if site_col_name and cell_col_name:
        c_filter = df_maestra[df_maestra[site_col_name].isin(active_sites)][cell_col_name].unique().tolist()
        cellnames_filter = c_filter if c_filter else None


with st.status("⏳ Consultando base de datos...", expanded=False) as status_bar:
    st.write("📡 Conectando a PostgreSQL (3T)...")
    time.sleep(0.1)

    # Query de auditoría (evaluación obligatoria sobre las últimas 12h para no arrastrar fallas antiguas y alertar más rápido)
    st.write("🔍 Evaluando diagnóstico de sitios (últimas 12h)...")
    audit_start_dt = end_dt - timedelta(hours=12)
    q_audit = get_sites_with_data_query(audit_start_dt, end_dt)
    df_audit = execute_query(q_audit)

    # Query del módulo seleccionado
    module_name = st.session_state['selected_module']
    st.write(f"📊 Cargando datos de {module_name}...")

    query_map = {
        "📶 Accesibilidad": get_accesibilidad_query,
        "🔌 Downtime":      get_downtime_query,
        "📉 DROP":          get_drop_query,
        "🚀 Velocidad":     get_trafico_query,   # Throughput viene de esta query
        "👥 Usuarios":      get_usuarios_query,
        "📊 PRB":           get_prb_query,
        "📡 Tráfico":       get_trafico_query,
        "🎙️ VoLTE":         get_volte_query,
    }
    query_fn  = query_map.get(module_name, get_accesibilidad_query)
    df_module = execute_query(query_fn(start_dt, end_dt, cellnames_filter))

    # Filtrar por sitio si corresponde (post-filtro sobre df_audit)
    if active_sites and not df_audit.empty and 'sitio' in df_audit.columns:
        df_audit = df_audit[df_audit['sitio'].str.upper().isin([s.upper() for s in active_sites])]

    status_bar.update(label="✅ Datos cargados correctamente", state="complete", expanded=False)


# =============================================================================
# ── FILA SUPERIOR: TARJETAS DE AUDITORÍA ─────────────────────────────────────
# =============================================================================
q_rs, q_sin_kpi, q_fallas, q_intermitencias, lista_sin_kpi, lista_fallas, lista_interm = calculate_audit_kpis(
    df_maestra.copy() if not df_maestra.empty else pd.DataFrame(),
    df_audit.copy()   if not df_audit.empty   else pd.DataFrame(),
)

aud_col1, aud_col2, aud_col3, aud_col4, aud_col5 = st.columns([1, 1, 1, 1, 2.5])

with aud_col1:
    st.markdown(f"""
    <div style="background:white; border-left:5px solid #7B2D8B;
                border-radius:0 10px 10px 0; padding:14px 16px;
                box-shadow:0 2px 10px rgba(123,45,139,0.12);">
        <div style="font-size:11px; font-weight:700; color:#7B2D8B;
                    text-transform:uppercase; letter-spacing:0.7px;">Q Sitios RS</div>
        <div style="font-size:36px; font-weight:800; color:#2D0A5E; line-height:1.1;">{q_rs}</div>
        <div style="font-size:10px; color:#999; margin-top:2px;">Entel en tabla maestra</div>
    </div>
    """, unsafe_allow_html=True)

with aud_col2:
    color2 = "#E74C3C" if q_sin_kpi > 0 else "#2ECC71"
    st.markdown(f"""
    <div style="background:white; border-left:5px solid {color2};
                border-radius:0 10px 10px 0; padding:14px 16px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);">
        <div style="font-size:11px; font-weight:700; color:{color2};
                    text-transform:uppercase; letter-spacing:0.7px;">Q Sitios sin KPI</div>
        <div style="font-size:36px; font-weight:800; color:#2D0A5E; line-height:1.1;">{q_sin_kpi}</div>
        <div style="font-size:10px; color:#999; margin-top:2px;">Sin registros en BD</div>
    </div>
    """, unsafe_allow_html=True)

with aud_col3:
    color3 = "#F39C12" if q_fallas > 0 else "#2ECC71"
    st.markdown(f"""
    <div style="background:white; border-left:5px solid {color3};
                border-radius:0 10px 10px 0; padding:14px 16px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);">
        <div style="font-size:11px; font-weight:700; color:{color3};
                    text-transform:uppercase; letter-spacing:0.7px;">Q Sitios con Fallas</div>
        <div style="font-size:36px; font-weight:800; color:#2D0A5E; line-height:1.1;">{q_fallas}</div>
        <div style="font-size:10px; color:#999; margin-top:2px;">Acc{'<'}80% / Disp{'<'}50%</div>
    </div>
    """, unsafe_allow_html=True)

with aud_col4:
    color4 = "#FFCA28" if q_intermitencias > 0 else "#2ECC71"
    st.markdown(f"""
    <div style="background:white; border-left:5px solid {color4};
                border-radius:0 10px 10px 0; padding:14px 16px;
                box-shadow:0 2px 10px rgba(0,0,0,0.08);">
        <div style="font-size:11px; font-weight:700; color:{color4};
                    text-transform:uppercase; letter-spacing:0.7px;">Q Intermitentes</div>
        <div style="font-size:36px; font-weight:800; color:#2D0A5E; line-height:1.1;">{q_intermitencias}</div>
        <div style="font-size:10px; color:#999; margin-top:2px;">DT prom {'>'} 20seg/h</div>
    </div>
    """, unsafe_allow_html=True)

with aud_col5:
    # Timestamp de actualización
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db_badge   = '<span style="background:#E8F5E9;color:#2E7D32;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700;">● PostgreSQL (3T) OK</span>' if db_ok else '<span style="background:#FFEBEE;color:#C62828;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700;">● PostgreSQL (3T) ERROR</span>'
    st.markdown(f"""
    <div style="background:white; border-radius:10px; padding:8px 14px;
                box-shadow:0 2px 10px rgba(123,45,139,0.08);
                border-top:3px solid #E91E8C;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
            <div style="font-size:11px; color:#888;">Estado del sistema</div>
            <div style="font-size:9px; color:#aaa;">🕐 {now_str}</div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:6px;">
            {db_badge}
        </div>
        <!-- ZONA DE ETIQUETAS Y OBSERVACIONES ESTÁTICAS -->
        <div style="background:#FFF1F8; border:1px solid #F8BBD0; border-left:3px solid #E91E8C; padding:4px 8px; border-radius:4px; margin-top:2px;">
            <div style="font-size:9px; font-weight:800; color:#D81B60; text-transform:uppercase; letter-spacing:0.5px;">📌 Observación Estática</div>
            <div style="font-size:10px; color:#4A148C; font-weight:600; margin-top:1px;">AR10408 debe siempre mantener celdas apagadas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)


# =============================================================================
# ── CONTENIDO PRINCIPAL: GRÁFICO + MAPA ──────────────────────────────────────
# =============================================================================
main_col, map_col = st.columns([2.2, 1], gap="medium")

with main_col:
    # ── Encabezado del módulo ──────────────────────────────────────────────
    st.markdown(f"""<div style="background:linear-gradient(90deg, #7B2D8B, #AB47BC);
border-radius:10px; padding:10px 18px; color:white; margin-bottom:10px;
box-shadow:0 2px 10px rgba(123,45,139,0.2);">
<span style="font-size:15px; font-weight:700;">{module_name}</span>
<span style="font-size:11px; opacity:0.7; margin-left:12px;">Período: {format_period_label(st.session_state['selected_period'])} {' · Filtro: ' + ', '.join(active_cells[:3]) + ('...' if len(active_cells) > 3 else '') if active_cells else ''}</span>
</div>""", unsafe_allow_html=True)

    # ── Gráfico del módulo seleccionado ───────────────────────────────────
    chart_fn_map = {
        "📶 Accesibilidad": render_accesibilidad_chart,
        "🔌 Downtime":      render_downtime_chart,
        "📉 DROP":          render_drop_chart,
        "🚀 Velocidad":     render_velocidad_chart,
        "👥 Usuarios":      render_usuarios_chart,
        "📊 PRB":           render_prb_chart,
        "📡 Tráfico":       render_trafico_chart,
        "🎙️ VoLTE":         render_volte_chart,
    }
    chart_fn = chart_fn_map.get(module_name, render_accesibilidad_chart)
    fig = chart_fn(df_module)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True,
                                                            'displaylogo': False})

    # ── Tabla de datos (expandible) ────────────────────────────────────────
    if not df_module.empty:
        with st.expander(f"📋 Ver datos tabulares — {module_name}", expanded=False):
            ts_col = next((c for c in df_module.columns if 'timestamp' in c.lower() or 'datetime' in c.lower()), df_module.columns[0])
            df_display = df_module.copy()
            if ts_col in df_display.columns:
                df_display[ts_col] = pd.to_datetime(df_display[ts_col]).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(
                df_display,
                use_container_width=True,
                height=200,
            )
    else:
        st.info("ℹ️ No hay datos para el período y filtros seleccionados. Verifica la conexión a PostgreSQL (3T).")

    # ── Sección de Auditoría de Faltantes ────────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    aud1, aud2, aud3 = st.columns(3, gap="medium")
    with aud1:
        render_faltantes_card(
            titulo=f"Sitios sin KPI ({q_sin_kpi})",
            items=lista_sin_kpi,
            max_items=8,
        )
    with aud2:
        render_faltantes_card(
            titulo=f"Sitios con Fallas ({q_fallas})",
            items=lista_fallas,
            max_items=8,
        )
    with aud3:
        render_faltantes_card(
            titulo=f"Sitios Intermitentes ({q_intermitencias})",
            items=lista_interm,
            max_items=8,
        )


with map_col:
    # ── Mapa interactivo ───────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(90deg, #E91E8C, #AB47BC);
                border-radius:10px; padding:10px 18px; color:white; margin-bottom:10px;
                box-shadow:0 2px 10px rgba(233,30,140,0.25);">
        <span style="font-size:15px; font-weight:700;">🗺️ Distribución de Sitios</span>
    </div>
    """, unsafe_allow_html=True)

    df_map_data = get_site_status_for_map(
        df_maestra.copy() if not df_maestra.empty else pd.DataFrame(),
        df_audit.copy()   if not df_audit.empty   else pd.DataFrame(),
    )
    fig_map = render_map(df_map_data)
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

    # ── Leyenda de estados (Removida por solicitud del usuario) ─────────────

    # ── Tabla maestra resumida ────────────────────────────────────────────
    if not df_maestra.empty:
        with st.expander("📋 Tabla Maestra (PostgreSQL)", expanded=False):
            cols_to_show = [c for c in df_maestra.columns if c.upper() in
                            ('SITE', 'SITIO', 'CELLNAME', 'CELL_NAME', 'OPERATOR', 'OPERADOR',
                             'ENODEBID', 'ENODEB_ID', 'ENODEB ID', 'ENODEB',
                             'CODIGO_SERVICIO', 'COD_SERVICIO', 'CÓD. SERVICIO', 'CODIGO SERVICIO',
                             'LAT', 'LON', 'LATITUDE', 'LONGITUDE', 'LATITUD', 'LONGITUD')]
            df_show = df_maestra[cols_to_show].copy() if cols_to_show else df_maestra.copy()
            # Convertir columnas numéricas a entero para evitar comas y .0
            int_candidates = [c for c in df_show.columns
                              if c.upper() in ('ENODEBID', 'ENODEB_ID', 'ENODEB',
                                               'CODIGO_SERVICIO', 'COD_SERVICIO', 'CODIGO SERVICIO')]
            for col in int_candidates:
                df_show[col] = (pd.to_numeric(df_show[col], errors='coerce')
                                .astype('Int64')
                                .astype(str)
                                .replace('<NA>', ''))
            st.dataframe(df_show, use_container_width=True, height=220)
