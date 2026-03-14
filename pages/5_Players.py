"""Page 5 — Players: Roster stats, deep dives, usage/efficiency charts."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_player_stats
from components.charts import usage_efficiency_scatter, player_comparison_radar

st.markdown("# PLAYERS")

# ── Load Data ────────────────────────────────────────────────────────────────
player_stats = load_player_stats()

if player_stats.empty:
    st.warning("No player data available.")
    st.stop()

# ── Season Averages Table ─────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Season Averages</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

# Aggregate per player
agg_cols = {"pts": "mean", "reb": "mean", "ast": "mean", "stl": "mean",
            "blk": "mean", "to": "mean", "min": "mean"}
avail_agg = {k: v for k, v in agg_cols.items() if k in player_stats.columns}

if "player" in player_stats.columns and avail_agg:
    season_avgs = player_stats.groupby("player").agg(avail_agg).round(1).reset_index()
    season_avgs = season_avgs.sort_values("pts", ascending=False)
    st.dataframe(season_avgs, use_container_width=True, hide_index=True)
else:
    st.dataframe(player_stats.head(20), use_container_width=True, hide_index=True)

# ── Usage / Efficiency Scatter ────────────────────────────────────────────────
if all(c in player_stats.columns for c in ["player", "usg_pct", "ts_pct"]):
    st.markdown(
        '<div class="cc-section-header"><h2>Usage vs Efficiency</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(usage_efficiency_scatter(player_stats), use_container_width=True)

# ── Player Deep Dive ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Player Deep Dive</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

if "player" in player_stats.columns:
    players = sorted(player_stats["player"].unique().tolist())
    selected = st.selectbox("Select Player", players)

    p_data = player_stats[player_stats["player"] == selected].copy()

    # Per-game trend
    if "game_date" in p_data.columns and "pts" in p_data.columns:
        p_data = p_data.sort_values("game_date")
        st.markdown("**Points per Game**")
        st.line_chart(p_data.set_index("game_date")["pts"])

    # Season stat line
    stat_cols = ["pts", "reb", "ast", "stl", "blk", "to", "fg_pct", "fg3_pct", "ft_pct", "min"]
    avail_stat = [c for c in stat_cols if c in p_data.columns]
    if avail_stat:
        avg_row = p_data[avail_stat].mean().round(2).to_frame(name="Season Avg").T
        st.dataframe(avg_row, use_container_width=True)

    # Radar comparison
    radar_stats = ["pts", "reb", "ast", "stl", "blk"]
    if all(c in player_stats.columns for c in radar_stats) and len(players) >= 2:
        compare_player = st.selectbox("Compare Against", [p for p in players if p != selected])
        st.plotly_chart(
            player_comparison_radar(player_stats, selected, compare_player),
            use_container_width=True,
        )
