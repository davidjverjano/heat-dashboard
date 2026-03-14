"""Courtside Cre8ives — Heat Analytics Dashboard."""

import pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Courtside Cre8ives — Heat Analytics",
    page_icon=str(ROOT / "assets" / "CC-Icon-Black-4x-4.jpg") if (ROOT / "assets" / "CC-Icon-Black-4x-4.jpg").exists() else "🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load Fonts (base64 data URIs) + Custom CSS ───────────────────────────────
from build_font_css import build_font_css

font_css = build_font_css()
css_file = ROOT / "assets" / "style.css"
main_css = css_file.read_text() if css_file.exists() else ""

st.markdown(f"<style>{font_css}\n{main_css}</style>", unsafe_allow_html=True)

# ── Top Navigation Bar ───────────────────────────────────────────────────
from components.nav import render_top_nav
render_top_nav()

# ── Main Content ──────────────────────────────────────────────────────────
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
