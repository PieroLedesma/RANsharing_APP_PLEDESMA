# =============================================================================
# utils/master_table.py — Carga de tabla maestra desde PostgreSQL
# =============================================================================

import pandas as pd
import streamlit as st
import logging
from utils.db import execute_query
from config.settings import TABLE_MASTER

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600, show_spinner=False)
def load_master_table() -> pd.DataFrame:
    """
    Carga la tabla maestra desde la tabla configurada en PostgreSQL.
    """
    try:
        query = f"SELECT * FROM {TABLE_MASTER}"
        df = execute_query(query)

        # Limpieza de coordenadas si vienen con comillas y comas (ej: "-34,359219")
        for col in ['LATITUD', 'LONGITUD', 'LAT', 'LON', 'LATITUDE', 'LONGITUDE']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('"', '').str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Limpieza básica de filas vacías
        df = df.dropna(how='all')

        logger.info(f"✅ Tabla maestra cargada desde {TABLE_MASTER}: {len(df)} filas")
        return df

    except Exception as e:
        logger.error(f"Error cargando datos de {TABLE_MASTER}: {e}")
        st.error(f"⚠️ **Error al cargar la tabla maestra ({TABLE_MASTER}):**\n\n`{e}`")
        return pd.DataFrame()
