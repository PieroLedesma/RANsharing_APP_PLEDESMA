# =============================================================================
# utils/kpis.py — Lógica de cálculo de KPIs de auditoría
# =============================================================================
import pandas as pd
from typing import Tuple, List, Optional
from config.settings import KPI_THRESHOLDS, OPERADOR_FILTER


def _get_site_col(df: pd.DataFrame) -> Optional[str]:
    """Detecta el nombre de columna SITE/SITIO en df (case-insensitive)."""
    for candidate in ('SITE', 'SITIO', 'site', 'sitio', 'Site', 'Sitio'):
        if candidate in df.columns:
            return candidate
    return None


def _get_operator_col(df: pd.DataFrame) -> Optional[str]:
    for candidate in ('OPERADOR', 'OPERATOR', 'operador', 'operator'):
        if candidate in df.columns:
            return candidate
    return None


def calculate_audit_kpis(
    df_maestra: pd.DataFrame,
    df_sql: pd.DataFrame,
) -> Tuple[int, int, int, int, List[str], List[str], List[str]]:
    """Calcula los 3 KPIs de auditoría principales."""
    if df_maestra.empty:
        return 0, 0, 0, 0, [], [], []

    op_col   = _get_operator_col(df_maestra)
    site_col = _get_site_col(df_maestra)

    df_entel = df_maestra.copy()
    if op_col:
        df_entel = df_entel[
            df_entel[op_col].astype(str).str.upper().str.contains(
                OPERADOR_FILTER.upper(), na=False
            )
        ]

    if site_col and not df_entel.empty:
        sitios_maestra = set(
            df_entel[site_col].dropna()
            .astype(str).str.upper().str.strip().unique()
        )
    else:
        sitios_maestra = set()

    q_sitios_rs = len(sitios_maestra)

    if not df_sql.empty and 'sitio' in df_sql.columns:
        sitios_con_datos = set(
            df_sql['sitio'].dropna()
            .astype(str).str.upper().str.strip().unique()
        )
    else:
        sitios_con_datos = set()

    lista_sin_kpi = sorted(sitios_maestra - sitios_con_datos)
    q_sin_kpi     = len(lista_sin_kpi)

    lista_con_fallas = [f"{s} (Sin datos)" for s in lista_sin_kpi]
    lista_intermitencias = []

    if not df_sql.empty:
        acc_col  = 'acc_prom'  if 'acc_prom'  in df_sql.columns else None
        disp_col = 'disp_prom' if 'disp_prom' in df_sql.columns else None
        dt_max_col = 'max_downtime_sec' if 'max_downtime_sec' in df_sql.columns else None

        site_issues = {}
        site_interm = {}
        
        for _, row in df_sql.iterrows():
            if 'sitio' not in row or pd.isnull(row['sitio']): continue
            s_nom = str(row['sitio']).upper().strip()
            
            reasons = []
            interm_reasons = []
            
            if acc_col and pd.notnull(row[acc_col]) and row[acc_col] < KPI_THRESHOLDS['accesibilidad_min']:
                reasons.append(f"Acc:{row[acc_col]}%")
            if disp_col and pd.notnull(row[disp_col]) and row[disp_col] < KPI_THRESHOLDS['disponibilidad_min']:
                reasons.append(f"Disp:{row[disp_col]}%")
                
            if dt_max_col and pd.notnull(row[dt_max_col]) and row[dt_max_col] > KPI_THRESHOLDS.get('intermitencia_downtime_sec', 20.0):
                interm_reasons.append(f"DTMax:{row[dt_max_col]}s/h")
                
            if reasons and s_nom in (sitios_maestra | sitios_con_datos):
                cell_name = str(row['eutrancell']) if 'eutrancell' in row else ''
                issue_str = f"[{cell_name} {'|'.join(reasons)}]" if cell_name else f"({'|'.join(reasons)})"
                if s_nom not in site_issues:
                    site_issues[s_nom] = []
                site_issues[s_nom].append(issue_str)
                
            if interm_reasons and s_nom in (sitios_maestra | sitios_con_datos):
                cell_name = str(row['eutrancell']) if 'eutrancell' in row else ''
                interm_str = f"[{cell_name} {'|'.join(interm_reasons)}]" if cell_name else f"({'|'.join(interm_reasons)})"
                if s_nom not in site_interm:
                    site_interm[s_nom] = []
                site_interm[s_nom].append(interm_str)
                
        for s_nom, issues in site_issues.items():
            lista_con_fallas.append(f"{s_nom} -> {' '.join(issues)}")
            
        for s_nom, interms in site_interm.items():
            lista_intermitencias.append(f"{s_nom} -> {' '.join(interms)}")

    lista_con_fallas = sorted(lista_con_fallas)
    q_con_fallas = len(lista_con_fallas)
    
    lista_intermitencias = sorted(lista_intermitencias)
    q_intermitencias = len(lista_intermitencias)

    return q_sitios_rs, q_sin_kpi, q_con_fallas, q_intermitencias, lista_sin_kpi, lista_con_fallas, lista_intermitencias


def get_site_status_for_map(
    df_maestra: pd.DataFrame,
    df_sql: pd.DataFrame,
) -> pd.DataFrame:
    """Genera DataFrame para el mapa con tooltips limpios."""
    if df_maestra.empty:
        return pd.DataFrame()

    op_col = _get_operator_col(df_maestra)
    df_filtered = df_maestra.copy()
    if op_col:
        df_filtered = df_filtered[
            df_filtered[op_col].astype(str).str.upper().str.contains(
                OPERADOR_FILTER.upper(), na=False
            )
        ]

    if df_filtered.empty:
        return pd.DataFrame()

    col_map = {c.upper(): c for c in df_filtered.columns}
    lat_col  = next((col_map[k] for k in ('LATITUD', 'LAT', 'LATITUDE')  if k in col_map), None)
    lon_col  = next((col_map[k] for k in ('LONGITUD', 'LON', 'LONGITUDE', 'LNG') if k in col_map), None)
    site_col = _get_site_col(df_filtered)
    
    reg_col  = next((col_map[k] for k in ('REGION', 'REGIÓN') if k in col_map), None)
    com_col  = next((col_map[k] for k in ('COMUNA',) if k in col_map), None)
    tx_col   = next((col_map[k] for k in ('TIPO_TX', 'TIPO TX') if k in col_map), None)
    serv_col = next((col_map[k] for k in ('CODIGO_SERVICIO', 'CÓD. SERVICIO') if k in col_map), None)
    cell_col = next((col_map[k] for k in ('CELLNAME', 'CELDA', 'CELL_NAME') if k in col_map), None)
    op_status_col = next((col_map[k] for k in ('OPERATIVO',) if k in col_map), None)
    enodeb_col = next((col_map[k] for k in ('ENODEBID', 'ENODEB_ID', 'ENODEB ID', 'ENODEB') if k in col_map), None)

    if not lat_col or not lon_col or not site_col:
        return pd.DataFrame()

    sitios_con_datos = set()
    falla_set = set()
    interm_set = set()
    if not df_sql.empty and 'sitio' in df_sql.columns:
        sitios_con_datos = set(df_sql['sitio'].dropna().astype(str).str.upper().str.strip().unique())
        acc_col  = 'acc_prom'  if 'acc_prom'  in df_sql.columns else None
        disp_col = 'disp_prom' if 'disp_prom' in df_sql.columns else None
        dt_max_col = 'max_downtime_sec' if 'max_downtime_sec' in df_sql.columns else None
        
        mask_falla = pd.Series(False, index=df_sql.index)
        if acc_col:
            mask_falla |= df_sql[acc_col].fillna(0) < KPI_THRESHOLDS['accesibilidad_min']
        if disp_col:
            mask_falla |= df_sql[disp_col].fillna(0) < KPI_THRESHOLDS['disponibilidad_min']
        falla_set = set(df_sql.loc[mask_falla, 'sitio'].dropna().astype(str).str.upper().str.strip().unique())
        
        mask_int = pd.Series(False, index=df_sql.index)
        if dt_max_col:
            mask_int |= (df_sql[dt_max_col].fillna(0) > KPI_THRESHOLDS.get('intermitencia_downtime_sec', 20.0))
        interm_set = set(df_sql.loc[mask_int, 'sitio'].dropna().astype(str).str.upper().str.strip().unique())

    site_groups = df_filtered.groupby(site_col)
    rows = []
    
    for sitio, group in site_groups:
        sitio_up = str(sitio).upper().strip()
        
        if sitio_up not in sitios_con_datos:
            estado, color = 'Sin Datos', '#E74C3C'
        elif sitio_up in falla_set:
            estado, color = 'Falla', '#F39C12'
        elif sitio_up in interm_set:
            estado, color = 'Intermitente', '#FFCA28'  # Amarillo para intermitente
        else:
            estado, color = 'OK', '#2ECC71'
            
        cell_info = ""
        if cell_col and op_status_col:
            cells = []
            for _, r in group.iterrows():
                r_st = str(r[op_status_col]).strip().upper()
                is_op = r_st in ('YES', 'SI', 'SÍ', 'TRUE', '1', 'Y')
                s_txt = "Operativo" if is_op else "No Operativo"
                s_ico = "✅" if is_op else "❌"
                cells.append(f"{s_ico} <b>{r[cell_col]}:</b> {s_txt}")
            cell_info = "<br>".join(cells)

        # -------------------------------------------------------------
        # AQUÍ COMIENZA LA CONSTRUCCIÓN DEL TEXTO DEL TOOLTIP DEL MAPA
        # -------------------------------------------------------------
        tooltip = f"<b>Nemonico:</b> {sitio_up}<br>"
        if enodeb_col: tooltip += f"<b>ENODEBID:</b> {group[enodeb_col].iloc[0]}<br>"
        if reg_col:  tooltip += f"<b>REGION:</b> {group[reg_col].iloc[0]}<br>"
        if com_col:  tooltip += f"<b>COMUNA:</b> {group[com_col].iloc[0]}<br>"
        if tx_col:   tooltip += f"<b>TIPO TX:</b> {group[tx_col].iloc[0]}<br>"
        if serv_col:
            v_serv = group[serv_col].iloc[0]
            try: v_serv = int(float(v_serv))
            except: pass
            tooltip += f"<b>COD. SERVICIO:</b> {v_serv}<br>"
            
        # AQUÍ SE ANEXA LA INFORMACIÓN DE CADA CELDA Y SU ESTADO OPERATIVO
        tooltip += "---------------------------<br>"
        tooltip += cell_info
        # -------------------------------------------------------------
        # FIN DEL TOOLTIP
        # -------------------------------------------------------------
        
        rows.append({
            'sitio': sitio_up,
            'lat': group[lat_col].iloc[0],
            'lon': group[lon_col].iloc[0],
            'estado': estado,
            'color': color,
            'tooltip': tooltip
        })

    df_map = pd.DataFrame(rows)
    df_map['lat'] = pd.to_numeric(df_map['lat'], errors='coerce')
    df_map['lon'] = pd.to_numeric(df_map['lon'], errors='coerce')
    return df_map.dropna(subset=['lat', 'lon'])
