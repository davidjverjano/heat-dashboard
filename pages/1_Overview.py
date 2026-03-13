"""Page 1 — Overview: Team dashboard with KPIs, timeline, and schedule."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

from utils.data_loader import load_game_log, load_schedule, load_team_info
from utils.calculations import last_n_record, current_streak, win_pct
from components.metrics import kpi_row, streak_badge
from components.charts import win_loss_timeline, point_diff_trend

st.markdown("# OVERVIEW")

# ── Load Data ─────────────────────────────────────────────────────────────────────────────
game_log = load_game_log()
schedule = load_schedule()
team_info = load_team_info()

total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
avg_diff = round(game_log["plus_minus"].mean(), 1)
net_rtg = round(game_log["ortg"].mean() - game_log["drtg"].mean(), 1)

# Approximate East Rank based on win%
wp = win_pct(total_w, total_l)
if wp >= 0.650:
    east_rank = "3rd"
elif wp >= 0.580:
    east_rank = "5th"
elif wp >= 0.520:
    east_rank = "7th"
else:
    east_rank = "9th"

# ── Top KPI Row ─────────────────────────────────────────────────────────────────────────
kpi_row([
    {"label": "Record", "value": f"{total_w}-{total_l}"},
    {"label": "Win %", "value": f"{wp:.3f}"},
    {"label": "Avg Pt Diff", "value": f"{avg_diff:+.1f}", "delta_good": avg_diff > 0},
    {"label": "Net Rating", "value": f"{net_rtg:+.1f}", "delta_good": net_rtg > 0},
    {"label": "East Rank", "value": east_rank},
])

# ── Second Row: Last 10 + Streak ────────────────────────────────────────────────────────
st.markdown("---")
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)

col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    st.markdown("**Last 10**")
    st.markdown(f"### {l10_w}-{l10_l}")
with col2:
    st.markdown("**Streak**")
    streak_badge(s_type, s_count)

# ── Win/Loss Timeline ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.plotly_chart(win_loss_timeline(game_log), use_container_width=True)

# ── Layout: Upcoming + Point Diff ────────────────────────────────────────────────────────
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown("### Upcoming Games")
    upcoming = schedule.head(5).copy()
    upcoming["game_date"] = upcoming["game_date"].dt.strftime("%b %d")
    display = upcoming[["game_date", "home_away", "opponent", "game_time"]].rename(
        columns={"game_date": "Date", "home_away": "H/A", "opponent": "Opponent", "game_time": "Time"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

with col_b:
    st.plotly_chart(point_diff_trend(game_log, window=7), use_container_width=True)
