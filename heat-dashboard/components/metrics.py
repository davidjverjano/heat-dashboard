"""KPI card components for the Heat dashboard."""

import streamlit as st
from components.theme import COLORS


def kpi_card(label: str, value: str, delta: str | None = None, delta_good: bool = True):
    """Render a single KPI card using Streamlit markdown with custom styling."""
    delta_html = ""
    if delta:
        arrow = "▲" if delta_good else "▼"
        color = COLORS["yellow_flame"] if delta_good else COLORS["mamey"]
        delta_html = f'<div style="font-size:0.85rem;color:{color};margin-top:2px">{arrow} {delta}</div>'

    st.markdown(
        f"""
        <div style="
            background: {COLORS['bg_secondary']};
            border-left: 4px solid {COLORS['rich_red']};
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 8px;
        ">
            <div style="font-size:0.8rem;color:{COLORS['warm_grey']};text-transform:uppercase;letter-spacing:1px">{label}</div>
            <div style="font-size:1.8rem;font-weight:700;color:{COLORS['off_white']};margin-top:4px">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(metrics: list[dict]):
    """Render a row of KPI cards. Each dict has keys: label, value, delta (optional), delta_good (optional)."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(m["label"], m["value"], m.get("delta"), m.get("delta_good", True))


def record_badge(wins: int, losses: int):
    """Show a W-L record badge."""
    pct = wins / (wins + losses) if (wins + losses) > 0 else 0
    color = COLORS["win_green"] if pct >= 0.5 else COLORS["mamey"]
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:#fff;
            padding:4px 14px;
            border-radius:20px;
            font-weight:700;
            font-size:1rem;
        ">{wins}-{losses}</span>
        """,
        unsafe_allow_html=True,
    )


def streak_badge(streak_type: str, streak_count: int):
    """Show current streak badge (W3 or L2 etc.)."""
    color = COLORS["win_green"] if streak_type == "W" else COLORS["mamey"]
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:#fff;
            padding:4px 14px;
            border-radius:20px;
            font-weight:700;
            font-size:0.9rem;
        ">{streak_type}{streak_count}</span>
        """,
        unsafe_allow_html=True,
    )
