"""KPI card components — Courtside Cre8ives design system."""

import streamlit as st
from components.theme import COLORS


def kpi_card(label: str, value: str, delta: str | None = None, delta_good: bool = True):
    """Render a single KPI card with Asphalt Black design."""
    delta_html = ""
    if delta:
        arrow = "▲" if delta_good else "▼"
        color = COLORS["positive"] if delta_good else COLORS["negative"]
        delta_html = f'<div class="cc-kpi-delta" style="color:{color}">{arrow} {delta}</div>'

    st.markdown(
        f"""
        <div class="cc-kpi-card">
            <div class="cc-kpi-label">{label}</div>
            <div class="cc-kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(metrics: list[dict]):
    """Render a row of KPI cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(m["label"], m["value"], m.get("delta"), m.get("delta_good", True))


def hero_stats_strip(stats: list[dict]):
    """Render a Ringer-style horizontal stats strip with large numbers.

    Each dict has keys: label, value.
    """
    items = []
    for i, s in enumerate(stats):
        if i > 0:
            items.append('<div class="cc-hero-sep"></div>')
        items.append(
            f'<div class="cc-hero-stat">'
            f'<div class="cc-hero-stat-value">{s["value"]}</div>'
            f'<div class="cc-hero-stat-label">{s["label"]}</div>'
            f'</div>'
        )
    html = f'<div class="cc-hero-strip">{"".join(items)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def record_badge(wins: int, losses: int):
    """Show a W-L record badge."""
    pct = wins / (wins + losses) if (wins + losses) > 0 else 0
    color = COLORS["win_green"] if pct >= 0.5 else COLORS["loss_red"]
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:#fff;
            padding:4px 14px;
            border-radius:20px;
            font-weight:700;
            font-size:1rem;
            font-family:-apple-system,system-ui,sans-serif;
            font-variant-numeric:tabular-nums;
        ">{wins}-{losses}</span>
        """,
        unsafe_allow_html=True,
    )


def streak_badge(streak_type: str, streak_count: int):
    """Show current streak badge."""
    color = COLORS["win_green"] if streak_type == "W" else COLORS["loss_red"]
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:#fff;
            padding:4px 14px;
            border-radius:20px;
            font-weight:700;
            font-size:0.9rem;
            font-family:-apple-system,system-ui,sans-serif;
        ">{streak_type}{streak_count}</span>
        """,
        unsafe_allow_html=True,
    )


def rating_card(rank: int, name: str, value: str, compare: str | None = None, compare_positive: bool = True):
    """Ringer-style big-number rating card.

    rank: league rank (e.g. 8)
    name: metric name (e.g. 'OFF RTG')
    value: metric value (e.g. '113.4')
    compare: comparison text (e.g. '+2.3 vs LG')
    """
    suffix = _ordinal_suffix(rank)
    compare_html = ""
    if compare:
        cls = "positive" if compare_positive else "negative"
        compare_html = f'<div style="font-family:-apple-system,system-ui,sans-serif;font-size:11px;font-weight:700;margin-top:4px;color:{COLORS["positive"] if compare_positive else COLORS["negative"]}">{compare}</div>'

    st.markdown(
        f"""
        <div class="cc-rating-card">
            <div style="display:flex;align-items:baseline;gap:1px;flex-shrink:0;">
                <span class="cc-rank-number">{rank}</span>
                <span class="cc-rank-suffix">{suffix}</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:2px;padding-top:8px;">
                <div class="cc-rating-value">{value}</div>
                <div class="cc-rating-name">{name}</div>
                {compare_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _ordinal_suffix(n: int) -> str:
    """Return ordinal suffix for a number: 1→st, 2→nd, etc."""
    if 11 <= (n % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
