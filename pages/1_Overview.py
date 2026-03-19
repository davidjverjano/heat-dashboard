"""Page 1 — Overview: Team dashboard with KPIs, timeline, and schedule."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_schedule, load_team_info
from utils.calculations import last_n_record, current_streak, win_pct
from components.metrics import hero_stats_strip, kpi_row, streak_badge
from components.charts import win_loss_timeline, point_diff_trend
from components.tables import schedule_table

st.markdown("# OVERVIEW")

# ── Load Data ─────────────────────────────────────────────────────────────────
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

# ── Hero Stats Strip ───────────────────────────────────────────────────────────
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)

hero_stats_strip([
    {"label": "Record", "value": f"{total_w}-{total_l}"},
    {"label": "Win %", "value": f"{wp:.3f}"},
    {"label": "Avg +/-", "value": f"{avg_diff:+.1f}"},
    {"label": "Net Rtg", "value": f"{net_rtg:+.1f}"},
    {"label": "Last 10", "value": f"{l10_w}-{l10_l}"},
    {"label": "Streak", "value": f"{s_type}{s_count}"},
    {"label": "East Rank", "value": east_rank},
])

# ── Win/Loss Timeline ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Season Timeline</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
st.plotly_chart(win_loss_timeline(game_log), use_container_width=True)

# ── Layout: Upcoming + Point Diff ─────────────────────────────────────────────
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown(
        '<div class="cc-section-header"><h2>Upcoming</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    upcoming = schedule.head(5).copy()
    upcoming["game_date"] = upcoming["game_date"].dt.strftime("%b %-d")

    # Parse ISO game_time into friendly ET format (e.g., "7:30 PM ET")
    def format_game_time(raw):
        if not raw or raw == "TBD" or str(raw) == "nan":
            return "TBD"
        try:
            t = pd.to_datetime(str(raw))
            return t.strftime("%-I:%M %p ET").replace(":00 ", " ")
        except Exception:
            return str(raw)

    upcoming["game_time"] = upcoming["game_time"].apply(format_game_time)
    display = upcoming[["game_date", "home_away", "opponent", "game_time"]].rename(
        columns={"game_date": "Date", "home_away": "H/A", "opponent": "Opponent", "game_time": "Time"}
    )
    schedule_table(display)

with col_b:
    st.markdown(
        '<div class="cc-section-header"><h2>Pt Diff Trend</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(point_diff_trend(game_log, window=7), use_container_width=True)
