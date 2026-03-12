# =============================================================================
# sql_queries.py — Consultas SQL modularizadas para counters_hourly_entel
# =============================================================================
from datetime import datetime
from typing import Optional, List
from config.settings import TABLE_ENTEL

# ─── CONFIGURACIÓN — Extraído de settings.py ────────────────────────────────
TABLE_NAME = TABLE_ENTEL

# Identificadores de infraestructura
# Logic: L28LL9898_3 -> sub(4) -> LL9898_3 -> regexp_replace -> LL9898
_NEMONICO_EXPR = 'UPPER(REGEXP_REPLACE(SUBSTRING("Cell_Name" FROM 4), \'_[^_]+$\', \'\'))'
_CELL_EXPR     = '"Cell_Name"'
_TIMESTAMP_COL = '"Timestamp_ID"'


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _cellname_filter(cellnames: Optional[List[str]]) -> str:
    """Genera cláusula AND para CELLNAME. Si lista vacía → sin filtro."""
    if not cellnames:
        return ""
    escaped = ", ".join(f"'{c}'" for c in cellnames)
    return f"AND {_CELL_EXPR} IN ({escaped})"


def _format_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ─────────────────────────────────────────────────────────────────────────────
# QUERY UTILITARIA — descubrir estructura de la tabla
# ─────────────────────────────────────────────────────────────────────────────

def get_table_info_query() -> str:
    """Lista columnas de la tabla para diagnóstico manejando esquemas."""
    if '.' in TABLE_NAME:
        schema, table = TABLE_NAME.split('.')
        where_clause = f"table_schema = '{schema}' AND table_name = '{table}'"
    else:
        where_clause = f"table_name = '{TABLE_NAME}'"
        
    return f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE {where_clause}
    ORDER BY ordinal_position;
    """

def get_tables_list_query() -> str:
    """Lista todas las tablas del schema public para diagnóstico."""
    return """
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema NOT IN ('pg_catalog','information_schema')
    ORDER BY table_schema, table_name
    LIMIT 100;
    """

# ─────────────────────────────────────────────────────────────────────────────
# 1. ACCESIBILIDAD (4 KPIs principales)
# ─────────────────────────────────────────────────────────────────────────────

def get_accesibilidad_query(start: datetime, end: datetime,
                             cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        ROUND((CASE WHEN SUM("pmErabEstabAttInit") > 0 
              THEN 100.0 * SUM("pmErabEstabSuccInit") / SUM("pmErabEstabAttInit") END)::numeric, 2) AS "E_RAB_Setup_SR",
              
        ROUND((CASE WHEN SUM("pmErabEstabAttInitQciIdx5") > 0 
              THEN 100.0 * SUM("pmErabEstabSuccInitQciIdx5") / SUM("pmErabEstabAttInitQciIdx5") END)::numeric, 2) AS "E_RAB_Setup_SR_QCI5",
              
        ROUND((CASE WHEN SUM("pmRrcConnEstabAtt") > 0 
              THEN 100.0 * SUM("pmRrcConnEstabSucc") / SUM("pmRrcConnEstabAtt") END)::numeric, 2) AS "RRC_Setup_SR",
              
        ROUND((CASE WHEN SUM("pmS1SigConnEstabAtt") > 0 
              THEN 100.0 * SUM("pmS1SigConnEstabSucc") / SUM("pmS1SigConnEstabAtt") END)::numeric, 2) AS "S1_Sig_Conn_Setup_SR"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 2. USUARIOS (3 KPIs: Active DL, Active UL, RRC Users)
# ─────────────────────────────────────────────────────────────────────────────

def get_usuarios_query(start: datetime, end: datetime,
                        cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        ROUND((CASE WHEN SUM("pmSchedActivityCellDl") > 0 
              THEN SUM("pmActiveUeDlSum") / SUM("pmSchedActivityCellDl") END)::numeric, 2) AS "Avg_Active_UE_DL",
        ROUND((CASE WHEN SUM("pmSchedActivityCellUl") > 0 
              THEN SUM("pmActiveUeUlSum") / SUM("pmSchedActivityCellUl") END)::numeric, 2) AS "Avg_Active_UE_UL",
        ROUND((CASE WHEN SUM("pmRrcConnLevSamp") > 0 
              THEN SUM("pmRrcConnLevSum") / SUM("pmRrcConnLevSamp") END)::numeric, 2) AS "Avg_RRC_Users"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 3. PRB (2 KPIs: DL/UL Util)
# ─────────────────────────────────────────────────────────────────────────────

def get_prb_query(start: datetime, end: datetime,
                   cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        ROUND((CASE WHEN SUM("pmPrbAvailDl") > 0 
              THEN 100.0 * (SUM("pmPrbUsedDlBcch") + SUM("pmPrbUsedDlDtch") + SUM("pmPrbUsedDlPcch") + SUM("pmPrbUsedDlSrbFirstTrans")) / SUM("pmPrbAvailDl")
              END)::numeric, 2) AS "DL_PRB_Util",
        ROUND((CASE WHEN SUM("pmPrbAvailUl") > 0 
              THEN 100.0 * (SUM("pmPrbUsedUlDtch") + SUM("pmPrbUsedUlSrb")) / SUM("pmPrbAvailUl")
              END)::numeric, 2) AS "UL_PRB_Util"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 4. TRÁFICO Y VELOCIDAD (2 KPIs Tráfico + 4 KPIs Velocidad)
# ─────────────────────────────────────────────────────────────────────────────

def get_trafico_query(start: datetime, end: datetime,
                      cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        
        -- Trafico GB
        ROUND((CASE WHEN SUM("pmPdcpVolDlDrb") > 0 THEN 
            (SUM("pmPdcpVolDlDrb") + SUM("pmPdcpVolDlSrb")) * 125.0 / 1073741824.0 END)::numeric, 2) AS "DL_TRAFFIC_VOLUME",
        ROUND((CASE WHEN SUM("pmPdcpVolUlDrb") > 0 THEN 
            (SUM("pmPdcpVolUlDrb") + SUM("pmPdcpVolUlSrb")) * 125.0 / 1073741824.0 END)::numeric, 2) AS "UL_TRAFFIC_VOLUME",
            
        -- Avg DL User Tput
        ROUND((CASE WHEN SUM("pmUeThpTimeDl") > 0 THEN 
            (SUM("pmPdcpVolDlDrb") - SUM("pmPdcpVolDlDrbLastTTI")) / (SUM("pmUeThpTimeDl") / 1000.0) END)::numeric, 2) AS "Avg_DL_User_Tput",

        -- Avg DL Cell Tput
        ROUND((CASE WHEN SUM("pmSchedActivityCellDl") > 0 THEN 
            SUM("pmPdcpVolDlDrb") / (SUM("pmSchedActivityCellDl") / 1000.0) END)::numeric, 2) AS "Avg_DL_Cell_Tput",
            
        -- Avg UL User Tput
        ROUND((CASE WHEN SUM("pmUeThpTimeUl") > 0 THEN 
            SUM("pmUeThpVolUl") / (SUM("pmUeThpTimeUl") / 1000.0) END)::numeric, 2) AS "Avg_UL_User_Tput",

        -- Avg UL Cell Tput
        ROUND((CASE WHEN SUM("pmSchedActivityCellUl") > 0 THEN 
            SUM("pmPdcpVolUlDrb") / (SUM("pmSchedActivityCellUl") / 1000.0) END)::numeric, 2) AS "Avg_UL_Cell_Tput"

    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 5. DROP (1 KPI: Ret_ERabDrop)
# ─────────────────────────────────────────────────────────────────────────────

def get_drop_query(start: datetime, end: datetime,
                    cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        ROUND((CASE WHEN SUM("pmErabEstabSuccInit") > 0 THEN 
            100.0 * SUM("pmErabRelAbnormalEnbAct" + "pmErabRelAbnormalMmeAct") / SUM("pmErabEstabSuccInit" + "pmErabEstabSuccAdded")
        END)::numeric, 4) AS "Ret_ERabDrop"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 6. DOWNTIME / DISPONIBILIDAD (4 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def get_downtime_query(start: datetime, end: datetime,
                        cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        SUM("pmCellDowntimeAuto") AS "Downtime_Auto",
        SUM("pmCellDowntimeMan")  AS "Downtime_Manual",
        SUM("pmCellSleepTime")    AS "SleepTime",
        ROUND(((1.0 - (COALESCE(SUM("pmCellDowntimeAuto"), 0) + COALESCE(SUM("pmCellDowntimeMan"), 0))::numeric / NULLIF(COUNT(*) * 3600.0, 0)) * 100.0)::numeric, 2) AS "Cell_Availability_Rate"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 7. VoLTE (2 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def get_volte_query(start: datetime, end: datetime,
                     cellnames: Optional[List[str]] = None) -> str:
    cf = _cellname_filter(cellnames)
    return f"""
    SELECT
        date_trunc('hour', {_TIMESTAMP_COL}) AS timestamp_id,
        ROUND((CASE WHEN SUM("pmErabQciLevSumIdx1") > 0 THEN SUM("pmErabQciLevSumIdx1")/3600.0 END)::numeric, 4) AS "VoLTE_Traffic_Erl",
        ROUND((CASE WHEN SUM("pmErabQciLevSumIdx1") > 0 THEN SUM("pmErabQciLevSumIdx1")/60.0 END)::numeric, 4) AS "VoLTE_min"
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
      {cf}
    GROUP BY 1
    ORDER BY 1;
    """


# ─────────────────────────────────────────────────────────────────────────────
# 8. AUDITORÍA — sitios con datos
# ─────────────────────────────────────────────────────────────────────────────

def get_sites_with_data_query(start: datetime, end: datetime) -> str:
    """
    Retorna sitios que tienen registros en el período con KPIs resumidos para auditoría.
    """
    return f"""
    SELECT
        {_NEMONICO_EXPR}                                         AS sitio,
        {_CELL_EXPR}                                             AS eutrancell,
        ROUND((NULLIF(SUM("pmErabEstabSuccInit"), 0)::numeric / NULLIF(SUM("pmErabEstabAttInit"), 0) * 100.0)::numeric, 2) AS acc_prom,
        ROUND(((1.0 - (COALESCE(SUM("pmCellDowntimeAuto"), 0) + COALESCE(SUM("pmCellDowntimeMan"), 0))::numeric / NULLIF(COUNT(*) * 3600.0, 0)) * 100.0)::numeric, 2) AS disp_prom,
        MAX(COALESCE("pmCellDowntimeAuto", 0) + COALESCE("pmCellDowntimeMan", 0)) AS max_downtime_sec,
        COUNT(*)                                                  AS registros
    FROM {TABLE_NAME}
    WHERE {_TIMESTAMP_COL} BETWEEN '{_format_ts(start)}' AND '{_format_ts(end)}'
    GROUP BY 1, 2
    ORDER BY 1, 2;
    """
