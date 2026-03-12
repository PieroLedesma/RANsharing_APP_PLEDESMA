import pandas as pd
import streamlit as st
import logging
import clickhouse_connect

logger = logging.getLogger(__name__)

CLICKHOUSE_CONFIG = {
    'host': '10.98.103.23',
    'port': '8123',  # <-- ¡CAMBIO CLAVE! AHORA ES UN STRING
    'user': 'reader_roaming',
    'password': 'opt_perf.2021',
    'database': 'mysql_db'
}

@st.cache_data(ttl=3600, show_spinner=False)
def load_master_table() -> pd.DataFrame:
    """
    Carga la tabla maestra desde ClickHouse.
    """
    try:
        # Convertimos a int para clickhouse_connect, aunque se configure como string
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_CONFIG['host'],
            port=int(CLICKHOUSE_CONFIG['port']),
            username=CLICKHOUSE_CONFIG['user'],
            password=CLICKHOUSE_CONFIG['password'],
            database=CLICKHOUSE_CONFIG['database']
        )
        
        # Ejecutamos la consulta que reemplaza al CSV
        query = "SELECT * FROM mysql_db.cell_ransharing"
        df = client.query_df(query)
        
        # Limpieza de coordenadas si vienen con comillas y comas (ej: "-34,359219")
        for col in ['LATITUD', 'LONGITUD', 'LAT', 'LON', 'LATITUDE', 'LONGITUDE']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Limpieza básica de filas vacías (opcional según la db, pero seguro)
        df = df.dropna(how='all')
        
        logger.info(f"✅ Tabla maestra cargada desde ClickHouse: {len(df)} filas")
        return df

    except Exception as e:
        logger.error(f"Error cargando datos de ClickHouse: {e}")
        st.error(f"⚠️ **Error al cargar la tabla maestra (ClickHouse):**\n\n`{e}`")
        return pd.DataFrame()
