"""Courtside Cre8ives — Heat Analytics Dashboard."""

import pathlib
import base64
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent

# ── Page Config (must be first Streamlit call) ────────────────────────────────────────────
st.set_page_config(
    page_title="Courtside Cre8ives — Heat Analytics",
    page_icon=str(ROOT / "assets" / "CC-Icon-Black-4x-4.jpg") if (ROOT / "assets" / "CC-Icon-Black-4x-4.jpg").exists() else "🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ───────────────────────────────────────────────────────────────
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar Branding ─────────────────────────────────────────────────────────────
# Read CC icon SVG and render with white fill
def _load_cc_icon_b64():
    icon_path = ROOT / "assets" / "cc-icon.svg"
    if not icon_path.exists():
        return None
    svg_text = icon_path.read_text()
    # Force white fill for dark sidebar
    svg_text = svg_text.replace('<svg ', '<svg fill="#FFFCF2" ', 1)
    return base64.b64encode(svg_text.encode()).decode()

with st.sidebar:
    icon_b64 = _load_cc_icon_b64()
    if icon_b64:
        st.markdown(
            f'''<div style="display:flex; align-items:center; gap:12px; padding:14px 10px 8px;">
                <img src="data:image/svg+xml;base64,{icon_b64}" style="width:36px; height:auto;"/>
                <span style="
                    font-family:'Hyperspace Wide','Hyperspace','Barlow Condensed',sans-serif;
                    font-weight:700; font-size:14px; letter-spacing:2px; color:#FFFCF2;
                ">COURTSIDE<span style="color:#F7B267; margin-left:4px;">CRE8IVES</span></span>
            </div>''',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown(
        '''<div style="text-align:center; opacity:0.6; font-size:0.75rem; margin-top:4px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;">
            MIAMI HEAT ANALYTICS<br>
            <span style="color:#F7B267; font-weight:700; letter-spacing:2px;">2025-26 SEASON</span>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown("---")

# ── Main Content ──────────────────────────────────────────────────────────────────
st.markdown("# COURTSIDE CRE8IVES")
st.markdown(
    '<p style="color:#b0ada6; font-size:1rem; letter-spacing:0.5px;">'
    'Miami Heat team and player analytics for the 2025-26 season.</p>',
    unsafe_allow_html=True,
)

# Quick stats on landing page
from utils.data_loader import load_game_log, load_team_info
from utils.calculations import last_n_record, current_streak, win_pct
from components.metrics import hero_stats_strip

game_log = load_game_log()
team_info = load_team_info()

total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
avg_diff = round(game_log["plus_minus"].mean(), 1)

hero_stats_strip([
    {"label": "Record", "value": f"{total_w}-{total_l}"},
    {"label": "Win %", "value": f"{win_pct(total_w, total_l):.3f}"},
    {"label": "Avg +/-", "value": f"{avg_diff:+.1f}"},
    {"label": "Last 10", "value": f"{l10_w}-{l10_l}"},
    {"label": "Streak", "value": f"{s_type}{s_count}"},
])

st.markdown("---")
st.markdown(
    '''<div class="cc-footer">
        Built by <b>COURTSIDE CRE8IVES</b> &nbsp;|&nbsp;
        Data: Live NBA API (2025-26 season)
    </div>''',
    unsafe_allow_html=True,
)
