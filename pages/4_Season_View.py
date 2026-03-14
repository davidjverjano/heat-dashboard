"""Page 4 — Season View: Team metrics, radar chart, rankings, splits."""

import pathlib
import streamlit as st
import pandas as pd
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_league_averages, load_league_team_ratings, load_team_rankings
from utils.calculations import season_splits
from components.tables import comparison_table
from components.charts import radar_chart, scatter_plot, bar_chart
from components.metrics import rating_card
from components.theme import COLORS, apply_plotly_theme
import plotly.graph_objects as go

st.markdown("# SEASON VIEW")

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
league_avg = load_league_averages()

# ── Team Season Averages ──────────────────────────────────────────────────────
heat = {
    "ORtg": round(game_log["ortg"].mean(), 1),
    "DRtg": round(game_log["drtg"].mean(), 1),
    "Pace": round(game_log["pace"].mean(), 1),
    "TS%": round(game_log["ts_pct"].mean(), 3),
    "eFG%": round(game_log["efg_pct"].mean(), 3),
    "TOV%": round(game_log["tov_pct"].mean(), 1),
    "OREB%": round(game_log["oreb_pct"].mean(), 1),
    "FT Rate": round(game_log["ft_rate"].mean(), 3),
    "FG%": round(game_log["fg_pct"].mean(), 3),
    "3P%": round(game_log["fg3_pct"].mean(), 3),
    "FT%": round(game_log["ft_pct"].mean(), 3),
    "PPG": round(game_log["team_score"].mean(), 1),
    "RPG": round(game_log["reb"].mean(), 1),
    "APG": round(game_log["ast"].mean(), 1),
}

league = league_avg["league"]
east = league_avg["eastern_conference"]

league_mapped = {
    "ORtg": league["ortg"], "DRtg": league["drtg"], "Pace": league["pace"],
    "TS%": league["ts_pct"], "eFG%": league["efg_pct"], "TOV%": league["tov_pct"],
    "OREB%": league["oreb_pct"], "FT Rate": league["ft_rate"],
    "FG%": league["fg_pct"], "3P%": league["fg3_pct"], "FT%": league["ft_pct"],
    "PPG": league["ppg"], "RPG": league["rpg"], "APG": league["apg"],
}

east_mapped = {
    "ORtg": east["ortg"], "DRtg": east["drtg"], "Pace": east["pace"],
    "TS%": east["ts_pct"], "eFG%": east["efg_pct"], "TOV%": east["tov_pct"],
    "OREB%": east["oreb_pct"], "FT Rate": east["ft_rate"],
    "FG%": east["fg_pct"], "3P%": east["fg3_pct"], "FT%": east["ft_pct"],
    "PPG": east["ppg"], "RPG": east["rpg"], "APG": east["apg"],
}

metrics = ["ORtg", "DRtg", "Pace", "TS%", "eFG%", "FG%", "3P%", "FT%", "PPG", "RPG", "APG"]

st.markdown("### Team Metrics Comparison")
comparison_table(heat, league_mapped, east_mapped, metrics)

st.markdown("---")

# ── Radar Chart & Scatter ─────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Team Profile")
    radar_cats = ["ORtg", "eFG%", "FT Rate", "OREB%", "Pace", "AST", "DRtg"]
    # Normalize to 0-100 scale for radar
    def normalize(val, metric):
        ranges = {
            "ORtg": (105, 120), "eFG%": (0.48, 0.58), "FT Rate": (0.18, 0.32),
            "OREB%": (20, 32), "Pace": (95, 105), "AST": (22, 30), "DRtg": (105, 120),
        }
        lo, hi = ranges.get(metric, (0, 1))
        raw = heat.get(metric, game_log["ast"].mean() if metric == "AST" else 0)
        # For DRtg, lower is better — invert
        if metric == "DRtg":
            return round(100 - (raw - lo) / (hi - lo) * 100, 1)
        return round(clamp((raw - lo) / (hi - lo) * 100, 0, 100), 1)

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    radar_vals = [normalize(None, c) for c in radar_cats]
    st.plotly_chart(radar_chart(radar_cats, radar_vals, title=""), use_container_width=True)

with col2:
    st.markdown("### ORtg vs DRtg")
    # Real NBA team ratings
    league_ratings = load_league_team_ratings()
    heat_idx = league_ratings.index[league_ratings["team"] == "MIA"].tolist()[0]
    st.plotly_chart(
        scatter_plot(league_ratings, "ortg", "drtg", text_col="team", title="", highlight_idx=heat_idx),
        use_container_width=True,
    )

st.markdown("---")

# ── Category Rankings ─────────────────────────────────────────────────────────
st.markdown("### Category Rankings")
team_ranks = load_team_rankings()
rank_cats = ["PPG", "RPG", "APG", "FG%", "3P%"]
col_list = st.columns(len(rank_cats))
for col, cat in zip(col_list, rank_cats):
    with col:
        heat_val = heat[cat]
        rank_num = team_ranks[cat]["rank"]
        league_val = league_mapped[cat]
        diff = heat_val - league_val
        diff_sign = "+" if diff > 0 else ""
        diff_good = diff > 0 if cat != "TOV%" else diff < 0
        rating_card(
            rank=rank_num,
            name=cat,
            value=f"{heat_val}",
            compare=f"{diff_sign}{diff:.1f} vs Lg Avg",
            compare_positive=diff_good,
        )

# ── Season Splits ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Season Splits")

splits = season_splits(game_log)

col_h, col_a = st.columns(2)
with col_h:
    st.markdown("**Home**")
    st.markdown(f"### {splits['home']['wins']}-{splits['home']['losses']}")
with col_a:
    st.markdown("**Away**")
    st.markdown(f"### {splits['away']['wins']}-{splits['away']['losses']}")

st.markdown("#### Monthly Breakdown")
months = list(splits["monthly"].keys())
m_wins = [splits["monthly"][m]["wins"] for m in months]
m_losses = [splits["monthly"][m]["losses"] for m in months]

fig = go.Figure()
fig.add_trace(go.Bar(name="Wins", x=months, y=m_wins, marker_color=COLORS["win_green"]))
fig.add_trace(go.Bar(name="Losses", x=months, y=m_losses, marker_color=COLORS["loss_red"]))
fig.update_layout(barmode="stack", height=300, title="", xaxis_title="", yaxis_title="Games")
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)
