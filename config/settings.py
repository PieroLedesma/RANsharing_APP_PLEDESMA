# =============================================================================
# settings.py — Configuración global de la aplicación APP_RANSHARING
# =============================================================================

import streamlit as st

# --- Conexión PostgreSQL ---
# Ahora los datos se leen desde .streamlit/secrets.toml o Variables de Git
try:
    POSTGRES_CONFIG = {
        'host': st.secrets["postgres"]["host"],
        'port': st.secrets["postgres"]["port"],
        'user': st.secrets["postgres"]["user"],
        'password': st.secrets["postgres"]["password"],
        'database': st.secrets["postgres"]["database"]
    }
except Exception:
    # Fallback temporal / seguridad local si no encuentra el archivo secrets
    POSTGRES_CONFIG = {
        'host': '127.0.0.1',
        'port': '5432',
        'user': 'user',
        'password': 'password',
        'database': 'db'
    }

# --- Configuración de Proxy ---
# Si estás en VPN y te da error de conexión, deja 'enabled': False
# Si estás en la oficina y necesitas salir a internet, pon 'enabled': True
PROXY_CONFIG = {
    'enabled': False,
    'ip': '10.120.137.1',
    'port': 8080
}

# --- Google Sheets ---
GSHEETS_URL = "https://docs.google.com/spreadsheets/d/1JWncerFGQL7BazFgtepWlYwVgrNJoF2zyLmUV5mlbII/edit?gid=0#gid=0"
GSHEETS_WORKSHEET = "RANSHARING_CELLS"

# --- Tabla principal en PostgreSQL ---
TABLE_ENTEL = "ransharing.counters_hourly_entel"

# --- Paleta de colores WOM/Entel ---
PALETTE = {
    'primary':    '#7B2D8B',   # Púrpura WOM
    'secondary':  '#E91E8C',   # Magenta/Rosa Entel
    'accent':     '#AB47BC',   # Lila medio
    'light':      '#CE93D8',   # Lila claro
    'dark':       '#2D0A5E',   # Púrpura oscuro
    'success':    '#2ECC71',   # Verde OK
    'danger':     '#E74C3C',   # Rojo Falla
    'warning':    '#F39C12',   # Naranja Alerta
    'bg':         '#F5F0FF',   # Fondo principal
    'white':      '#FFFFFF',
    'text':       '#1A1A2E',
}

# Colores de líneas para los gráficos
CHART_COLORS = [
    '#AB47BC',   # línea 1 - lila
    '#7B2D8B',   # línea 2 - púrpura
    '#E91E8C',   # línea 3 - magenta
    '#FF9800',   # línea 4 - naranja
    '#26C6DA',   # línea 5 - cyan
    '#66BB6A',   # línea 6 - verde
]

# --- Umbrales de KPI para semáforos ---
KPI_THRESHOLDS = {
    'accesibilidad_min':  80.0,   # E_RAB_Setup_SR < 80% → falla
    'disponibilidad_min': 50.0,   # Cell_Availability < 50% → falla
    'intermitencia_downtime_sec': 20.0, # Downtime promedio > 20s/h → intermitencia
}

# --- Opciones de tiempo ---
TIME_OPTIONS = {
    "⏱ Últimas 24 Horas": 1,
    "📅 Últimos 30 Días":  30,
    "📆 Últimos 60 Días":  60,
}

# --- Módulos KPI disponibles ---
KPI_MODULES = [
    "📶 Accesibilidad",
    "🔌 Downtime",
    "📉 DROP",
    "🚀 Velocidad",
    "👥 Usuarios",
    "📊 PRB",
    "📡 Tráfico",
    "🎙️ VoLTE",
]

# Operador a filtrar en la tabla maestra
OPERADOR_FILTER = "Entel"
