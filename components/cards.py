# =============================================================================
# components/cards.py — Tarjetas HTML estilo WOM/Entel
# =============================================================================

import streamlit as st


def render_audit_card(label: str, value, sublabel: str = "", color: str = "#E91E8C"):
    """
    Tarjeta de auditoría: estilo PowerBI con borde izquierdo de color.
    Usada en el sidebar para Q Sitios RS, Sin KPI, Con Fallas.
    """
    st.markdown(f"""
    <div style="
        background: white;
        border-left: 5px solid {color};
        border-radius: 0 10px 10px 0;
        padding: 10px 14px 8px 14px;
        margin: 6px 0 8px 0;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
    ">
        <div style="font-size:11px; font-weight:700; color:{color};
                    text-transform:uppercase; letter-spacing:0.6px; margin-bottom:2px;">
            {label}
        </div>
        <div style="font-size:30px; font-weight:800; color:#1A1A2E; line-height:1;">
            {value}
        </div>
        {"<div style='font-size:10px; color:#999; margin-top:3px;'>" + sublabel + "</div>" if sublabel else ""}
    </div>
    """, unsafe_allow_html=True)


def render_faltantes_card(titulo: str, items: list, max_items: int = 10):
    """
    Tarjeta estilo rosa WOM para mostrar la lista de sitios faltantes/con fallas.
    """
    if not items:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#E8F5E9,#C8E6C9);
                    border:2px solid #2ECC71; border-radius:12px;
                    padding:14px 16px; margin:8px 0;">
            <div style="font-size:13px; font-weight:700; color:#1B5E20;">
                ✅ Sin faltantes
            </div>
            <div style="font-size:12px; color:#2E7D32; margin-top:4px;">
                Todos los sitios reportan datos correctamente.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    displayed = items[:max_items]
    extra = len(items) - max_items if len(items) > max_items else 0

    items_html = "".join(
        f'<div style="font-size:11.5px; color:#880E4F; padding:3px 0; '
        f'border-bottom:1px solid rgba(136,14,79,0.1);">📍 {s}</div>'
        for s in displayed
    )
    extra_html = (
        f'<div style="font-size:10px; color:#AD1457; margin-top:4px; font-style:italic;">'
        f'... y {extra} más</div>'
        if extra > 0 else ""
    )

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FCE4EC,#F8BBD0);
                border:2px solid #E91E8C; border-radius:12px;
                padding:14px 16px; margin:8px 0;
                font-family:'Segoe UI',sans-serif;">
        <div style="font-size:13px; font-weight:700; color:#880E4F; margin-bottom:8px;">
            ⚠️ {titulo}
        </div>
        {items_html}
        {extra_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_metric(label: str, value: str, delta: str = None,
                       delta_color: str = "normal", help_text: str = ""):
    """Métrica KPI estilizada."""
    icon_map = {
        "normal":  ("↗", "#2ECC71"),
        "inverse": ("↘", "#E74C3C"),
        "off":     ("─",  "#999999"),
    }
    arrow, arrow_color = icon_map.get(delta_color, ("─", "#999"))
    delta_html = (
        f'<span style="font-size:12px; color:{arrow_color}; font-weight:600;">'
        f'{arrow} {delta}</span>'
        if delta else ""
    )
    help_html = (
        f'<span title="{help_text}" style="cursor:help; color:#aaa; margin-left:4px;">ℹ️</span>'
        if help_text else ""
    )
    st.markdown(f"""
    <div style="background:white; border-radius:10px; padding:12px 16px;
                box-shadow:0 2px 8px rgba(123,45,139,0.1);
                border-top:3px solid #7B2D8B; text-align:center;">
        <div style="font-size:11px; color:#888; font-weight:600;
                    text-transform:uppercase; letter-spacing:0.5px;">
            {label} {help_html}
        </div>
        <div style="font-size:28px; font-weight:800; color:#2D0A5E; margin:4px 0;">
            {value}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = ""):
    """Encabezado de sección con gradiente."""
    sub_html = (
        f'<p style="margin:4px 0 0 0; font-size:12px; opacity:0.8;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#7B2D8B 0%,#E91E8C 100%);
                border-radius:10px; padding:14px 20px; color:white;
                margin-bottom:14px;
                box-shadow:0 4px 16px rgba(123,45,139,0.3);">
        <h2 style="margin:0; font-size:18px; font-weight:700; letter-spacing:-0.3px;">
            {title}
        </h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_connection_status(db_ok: bool, ch_ok: bool):
    """Indicadores de estado de conexión en el sidebar."""
    db_icon  = "🟢" if db_ok    else "🔴"
    ch_icon  = "🟢" if ch_ok    else "🔴"
    db_text  = "PostgreSQL: OK" if db_ok    else "PostgreSQL: ERROR"
    ch_text  = "ClickHouse: OK" if ch_ok    else "ClickHouse: ERROR"

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.07); border-radius:8px;
                padding:10px 12px; margin:6px 0; font-size:11px; color:rgba(255,255,255,0.85);">
        <div style="margin-bottom:4px;">{db_icon} {db_text}</div>
        <div>{ch_icon} {ch_text}</div>
    </div>
    """, unsafe_allow_html=True)
