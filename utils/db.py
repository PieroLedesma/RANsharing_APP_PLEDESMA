# =============================================================================
# utils/db.py — Conexión y ejecución de queries PostgreSQL
# Usa pg8000 (puro Python) + SQLAlchemy — no requiere compiladores de C
# =============================================================================

import pandas as pd
import streamlit as st
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from config.settings import POSTGRES_CONFIG

logger = logging.getLogger(__name__)


def _get_engine():
    """Crea y retorna un engine SQLAlchemy con pg8000."""
    cfg = POSTGRES_CONFIG
    url = (
        f"postgresql+pg8000://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    return create_engine(url, connect_args={"timeout": 60})


def test_connection() -> bool:
    """Verifica que la conexión a PostgreSQL esté disponible."""
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Test de conexión falló: {e}")
        return False


@st.cache_data(ttl=300, show_spinner=False)
def execute_query(sql: str) -> pd.DataFrame:
    """
    Ejecuta una query SQL y retorna un DataFrame.
    Cachea el resultado por 5 minutos (TTL=300s).

    Args:
        sql: Query SQL como string.
    Returns:
        pd.DataFrame con los resultados, o DataFrame vacío si hay error.
    """
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            df = pd.read_sql_query(text(sql), conn)
        return df
    except OperationalError as e:
        logger.error(f"Error de conexión al ejecutar query: {e}")
        st.error(
            f"❌ **Error de conexión a PostgreSQL** — "
            f"Verifica que el servidor `{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}` "
            f"esté accesible desde esta red.\n\n`{str(e)[:200]}`"
        )
        return pd.DataFrame()
    except SQLAlchemyError as e:
        logger.error(f"Error SQL: {e}")
        st.error(f"❌ **Error en la consulta SQL:** `{str(e)[:300]}`")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        st.error(f"❌ **Error inesperado:** `{str(e)[:200]}`")
        return pd.DataFrame()
