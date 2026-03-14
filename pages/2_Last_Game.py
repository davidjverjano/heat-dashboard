"""Page 2 — Last Game / Daily: Box score, advanced stats, top performer."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_stats
from utils.calculations import win_pct
from components.metrics import hero_stats_strip
from components.charts import shot_zone_chart, player_comparison_radar

st.markdown("# LAST GAME")

# ── Load Data ────────────────────────────────────────────────────────────────
game_log = load_game_log()
player_stats = load_player_stats()

# Most recent game
last = game_log.iloc[-1]

# ── Hero Strip ────────────────────────────────────────────────────────────────
result_color = "#3fb950" if last["result"] == "W" else "#F25C54"
opp_label = f"{'vs' if last['home_away'] == 'H' else '@'} {last['opponent']}"

hero_stats_strip([
    {"label": "Result", "value": last["result"]},
    {"label": "Opponent", "value": opp_label},
    {"label": "Score", "value": f"{last['pts_for']}-{last['pts_against']}"},
    {"label": "+/-", "value": f"{last['plus_minus']:+d}"},
    {"label": "ORtg", "value": f"{last['ortg']:.1f}"},
    {"label": "DRtg", "value": f"{last['drtg']:.1f}"},
    {"label": "Pace", "value": f"{last['pace']:.1f}"},
])

# ── Box Score ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Box Score</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

# Filter player stats for last game date
last_date = last["game_date"]
game_players = player_stats[player_stats["game_date"] == last_date].copy()

if game_players.empty:
    st.info("No player data available for this game.")
else:
    display_cols = ["player", "min", "pts", "reb", "ast", "stl", "blk", "to", "fg_pct", "fg3_pct", "plus_minus"]
    available = [c for c in display_cols if c in game_players.columns]
    box = game_players[available].sort_values("pts", ascending=False)
    st.dataframe(box, use_container_width=True, hide_index=True)

# ── Advanced Stats ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Advanced Stats</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Off Rating", f"{last['ortg']:.1f}")
with col2:
    st.metric("Def Rating", f"{last['drtg']:.1f}")
with col3:
    st.metric("Net Rating", f"{last['ortg'] - last['drtg']:.1f}")
with col4:
    st.metric("Pace", f"{last['pace']:.1f}")

# ── Four Factors ─────────────────────────────────────────────────────────────
if all(c in last.index for c in ["efg_pct", "tov_pct", "orb_pct", "ft_rate"]):
    st.markdown(
        '<div class="cc-section-header"><h2>Four Factors</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("eFG%", f"{last['efg_pct']:.3f}")
    with col2:
        st.metric("TOV%", f"{last['tov_pct']:.1f}")
    with col3:
        st.metric("ORB%", f"{last['orb_pct']:.1f}")
    with col4:
        st.metric("FT Rate", f"{last['ft_rate']:.3f}")

# ── Top Performers ─────────────────────────────────────────────────────────────
if not game_players.empty and "pts" in game_players.columns:
    st.markdown(
        '<div class="cc-section-header"><h2>Top Performers</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    top3 = game_players.nlargest(3, "pts")
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            pts = int(row.get("pts", 0))
            reb = int(row.get("reb", 0))
            ast = int(row.get("ast", 0))
            st.markdown(
                f"""
                <div class="cc-kpi-card">
                    <div class="cc-kpi-label">{row.get('player', 'Player')}</div>
                    <div class="cc-kpi-value">{pts} PTS</div>
                    <div class="cc-kpi-delta">{reb} REB · {ast} AST</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
