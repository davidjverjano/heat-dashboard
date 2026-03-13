"""Miami Heat Analytics Dashboard — Main Entry Point."""

import pathlib
import base64
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Courtside Cre8ives — Heat Analytics",
    page_icon=str(ROOT / "assets" / "CC-Icon-Black-4x-4.jpg"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ───────────────────────────────────────────────────────────
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar Branding ─────────────────────────────────────────────────────────
with st.sidebar:
    # Logo — use white SVG rendered inline for clean display on dark sidebar
    wordmark_svg = ROOT / "assets" / "logo_wordmark_white.svg"
    if wordmark_svg.exists():
        svg_data = wordmark_svg.read_text()
        b64 = base64.b64encode(svg_data.encode()).decode()
        st.markdown(
            f'<div style="text-align:center; padding:12px 10px 4px;">'
            f'<img src="data:image/svg+xml;base64,{b64}" style="width:100%; max-width:220px;"/>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; opacity:0.7; font-size:0.8rem; margin-top:8px;">
            MIAMI HEAT<br>ANALYTICS DASHBOARD<br>
            <span style="color:#F7B267">2025-26 Season</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Icon at bottom
    icon_svg = ROOT / "assets" / "logo_icon_white.svg"
    if icon_svg.exists():
        svg_data = icon_svg.read_text()
        b64 = base64.b64encode(svg_data.encode()).decode()
        st.markdown(
            f'<div style="padding:4px 0;">'
            f'<img src="data:image/svg+xml;base64,{b64}" style="width:50px;"/>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("# MIAMI HEAT ANALYTICS")
st.markdown(
    '<p style="color:#CCC5B9; font-size:1.1rem;">Select a page from the sidebar to explore team and player analytics for the 2025-26 season.</p>',
    unsafe_allow_html=True,
)

# Quick stats on landing page
from utils.data_loader import load_game_log, load_team_info
from utils.calculations import last_n_record, current_streak, win_pct
from components.metrics import kpi_row

game_log = load_game_log()
team_info = load_team_info()

total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
avg_diff = round(game_log["plus_minus"].mean(), 1)

kpi_row([
    {"label": "Record", "value": f"{total_w}-{total_l}"},
    {"label": "Win %", "value": f"{win_pct(total_w, total_l):.3f}"},
    {"label": "Avg +/-", "value": f"{avg_diff:+.1f}", "delta_good": avg_diff > 0},
    {"label": "Last 10", "value": f"{l10_w}-{l10_l}"},
    {"label": "Streak", "value": f"{s_type}{s_count}"},
])

st.markdown("---")
st.markdown(
    """
    <div style="color:#CCC5B9; font-size:0.9rem; text-align:center; padding: 20px 0;">
        Built by <b style="color:#F7B267">Courtside Cre8ives</b> &nbsp;|&nbsp;
        Data: Live NBA API data (2025-26 season)
    </div>
    """,
    unsafe_allow_html=True,
)
