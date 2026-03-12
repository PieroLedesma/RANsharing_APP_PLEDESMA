# =============================================================================
# components/charts.py — Gráficos Plotly para cada módulo KPI
# =============================================================================

import plotly.graph_objects as go
import pandas as pd
from config.settings import PALETTE, CHART_COLORS

# ── Config base del layout Plotly ─────────────────────────────────────────────
_LAYOUT_BASE = dict(
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(family="Inter, Segoe UI, sans-serif", size=11, color='#1A1A2E'),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02,
        xanchor='left', x=0,
        font=dict(size=10),
        bgcolor='rgba(255,255,255,0)',
    ),
    margin=dict(l=40, r=20, t=40, b=50),
    hovermode='x unified',
    xaxis=dict(
        showgrid=True, gridcolor='#F0EBF8', gridwidth=1,
        zeroline=False, tickfont=dict(size=9),
    ),
    yaxis=dict(
        showgrid=True, gridcolor='#F0EBF8', gridwidth=1,
        zeroline=False, tickfont=dict(size=10),
    ),
)


def _empty_chart(msg: str = "Sin datos para el período seleccionado"):
    """Chart vacío con mensaje."""
    fig = go.Figure()
    fig.add_annotation(
        text=msg, x=0.5, y=0.5, xref='paper', yref='paper',
        showarrow=False, font=dict(size=14, color='#7B2D8B'),
    )
    fig.update_layout(**_LAYOUT_BASE, height=300)
    return fig


def _ts_col(df: pd.DataFrame):
    """Detecta la columna de timestamp."""
    for c in ('timestamp_id', 'datetime_id', 'timestamp', 'fecha'):
        if c in df.columns:
            return c
    return df.columns[0]


def _hex_to_rgb(hex_color: str):
    """Convierte #RRGGBB → (R, G, B)."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ─────────────────────────────────────────────────────────────────────────────
# 1. ACCESIBILIDAD
# ─────────────────────────────────────────────────────────────────────────────

def render_accesibilidad_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    cols = [c for c in ('E_RAB_Setup_SR', 'E_RAB_Setup_SR_QCI5', 'RRC_Setup_SR', 'S1_Sig_Conn_Setup_SR') if c in df.columns]
    
    fig = go.Figure()
    for i, col in enumerate(cols):
        color = CHART_COLORS[i % len(CHART_COLORS)]
        fig.add_trace(go.Scatter(
            x=df[ts], y=df[col], name=col,
            mode='lines',
            line=dict(color=color, width=2),
            hovertemplate='%{y:.2f} %'
        ))

    # Línea de umbral 80%
    fig.add_hline(y=80, line_dash='dash', line_color='#E74C3C', line_width=1.5)

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Accesibilidad (4 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='%', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. DOWNTIME / DISPONIBILIDAD (4 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_downtime_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    # KPIs: Downtime_Auto, Downtime_Manual, SleepTime, Cell_Availability_Rate
    fig = go.Figure()

    cols = ['Downtime_Auto', 'Downtime_Manual', 'SleepTime']
    colors = [PALETTE['primary'], PALETTE['secondary'], '#F39C12']
    
    for i, col in enumerate(cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[ts], y=df[col], name=col,
                mode='lines', line=dict(color=colors[i], width=2),
                hovertemplate='%{y:.1f} seg'
            ))

    if 'Cell_Availability_Rate' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[ts], y=df['Cell_Availability_Rate'], name='Cell_Availability_Rate',
            mode='lines', line=dict(color='#2ECC71', width=3),
            yaxis='y2',
            hovertemplate='%{y:.2f} %'
        ))
        fig.update_layout(
            yaxis2=dict(
                title='% Disponibilidad', overlaying='y', side='right',
                range=[0, 105], showgrid=False
            )
        )

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Downtime & Disponibilidad (4 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='Segundos', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. DROP (1 KPI)
# ─────────────────────────────────────────────────────────────────────────────

def render_drop_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    fig = go.Figure()
    
    if 'Ret_ERabDrop' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[ts], y=df['Ret_ERabDrop'], name='Ret_ERabDrop',
            mode='lines+markers', line=dict(color=PALETTE['primary'], width=2),
            fill='tozeroy', fillcolor='rgba(123,45,139,0.1)',
            hovertemplate='%{y:.2f} %'
        ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Tasa de DROP (1 KPI)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='% Drop', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. VELOCIDAD / THROUGHPUT (4 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_velocidad_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    cols = ['Avg_DL_Cell_Tput', 'Avg_DL_User_Tput', 'Avg_UL_Cell_Tput', 'Avg_UL_User_Tput']
    
    fig = go.Figure()
    for i, col in enumerate(cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[ts], y=df[col], name=col,
                mode='lines', line=dict(color=CHART_COLORS[i+1], width=2),
                hovertemplate='%{y:.1f} kbps'
            ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Velocidad - Throughput (4 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='kbps', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5. USUARIOS (3 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_usuarios_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    cols = ['Avg_Active_UE_DL', 'Avg_Active_UE_UL', 'Avg_RRC_Users']
    
    fig = go.Figure()
    for i, col in enumerate(cols):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[ts], y=df[col], name=col,
                mode='lines', line=dict(color=CHART_COLORS[i], width=2),
                hovertemplate='%{y:.1f} (us)'
            ))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Usuarios (3 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='Usuarios', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6. PRB (2 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_prb_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    fig = go.Figure()
    
    if 'DL_PRB_Util' in df.columns:
        fig.add_trace(go.Bar(x=df[ts], y=df['DL_PRB_Util'], name='DL_PRB_Util', marker_color=PALETTE['primary'], hovertemplate='%{y:.2f} %'))
    if 'UL_PRB_Util' in df.columns:
        fig.add_trace(go.Bar(x=df[ts], y=df['UL_PRB_Util'], name='UL_PRB_Util', marker_color=PALETTE['secondary'], hovertemplate='%{y:.2f} %'))

    fig.update_layout(
        **_LAYOUT_BASE, barmode='group',
        title=dict(text='<b>Utilización PRB (2 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='%', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 7. TRÁFICO (2 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_trafico_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    fig = go.Figure()
    
    if 'DL_TRAFFIC_VOLUME' in df.columns:
        fig.add_trace(go.Scatter(x=df[ts], y=df['DL_TRAFFIC_VOLUME'], name='DL_TRAFFIC_VOLUME', fill='tozeroy', line_color=PALETTE['primary'], hovertemplate='%{y:.2f} GB'))
    if 'UL_TRAFFIC_VOLUME' in df.columns:
        fig.add_trace(go.Scatter(x=df[ts], y=df['UL_TRAFFIC_VOLUME'], name='UL_TRAFFIC_VOLUME', line_color=PALETTE['secondary'], hovertemplate='%{y:.2f} GB'))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>Vólumen de Tráfico (2 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='GB', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 8. VoLTE (2 KPIs)
# ─────────────────────────────────────────────────────────────────────────────

def render_volte_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_chart()

    ts = _ts_col(df)
    fig = go.Figure()
    
    if 'VoLTE_min' in df.columns:
        fig.add_trace(go.Scatter(x=df[ts], y=df['VoLTE_min'], name='VoLTE_min', line_color=PALETTE['primary'], hovertemplate='%{y:.1f} min'))
    
    if 'VoLTE_Traffic_Erl' in df.columns:
        fig.add_trace(go.Scatter(x=df[ts], y=df['VoLTE_Traffic_Erl'], name='VoLTE_Traffic_Erl', line_color=PALETTE['secondary'], yaxis='y2', hovertemplate='%{y:.2f} Erl'))
        fig.update_layout(yaxis2=dict(title='Erlangs', overlaying='y', side='right', showgrid=False))

    fig.update_layout(
        **_LAYOUT_BASE,
        title=dict(text='<b>VoLTE (2 KPIs)</b>', font=dict(size=14, color=PALETTE['dark'])),
        yaxis_title='Minutos', height=380,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 9. MAPA INTERACTIVO
# ─────────────────────────────────────────────────────────────────────────────

def render_map(df_map: pd.DataFrame) -> go.Figure:
    if df_map.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sin coordenadas disponibles", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=500)
        return fig

    center_lat = df_map['lat'].mean()
    center_lon = df_map['lon'].mean()

    fig = go.Figure()
    for estado, group in df_map.groupby('estado'):
        color = group['color'].iloc[0]
        icon = {'OK': '✅', 'Falla': '⚠️', 'Sin Datos': '❌'}.get(estado, '📍')
        fig.add_trace(go.Scattermapbox(
            lat=group['lat'], lon=group['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=12, color=color, opacity=0.9),
            text=group['tooltip'],
            hoverinfo='text',
            name=f"{icon} {estado} ({len(group)})"
        ))

    fig.update_layout(
        mapbox=dict(style='open-street-map', center=dict(lat=center_lat, lon=center_lon), zoom=5),
        margin=dict(l=0, r=0, t=0, b=0), height=480,
        legend=dict(orientation='v', x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.85)'),
    )
    return fig
