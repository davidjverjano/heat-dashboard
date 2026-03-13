"""Page 3 — Weekly Trends: Rolling metrics, four factors, period record."""

import pathlib
import streamlit as st
import pandas as pd
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

from utils.data_loader import load_game_log, load_league_averages
from utils.calculations import four_factors, opponent_four_factors
from components.metrics import kpi_row
from components.charts import rolling_line_chart, win_loss_timeline, sparkline, four_factors_bar
from components.theme import COLORS

st.markdown("# WEEKLY TRENDS")

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
league_avg = load_league_averages()

# ── Date Range Selector ──────────────────────────────────────────────────────
min_date = game_log["game_date"].min().date()
max_date = game_log["game_date"].max().date()
default_start = max_date - timedelta(days=14)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=max(default_start, min_date), min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

mask = (game_log["game_date"].dt.date >= start_date) & (game_log["game_date"].dt.date <= end_date)
period = game_log[mask].copy()

if period.empty:
    st.warning("No games found in this date range.")
    st.stop()

# ── Period Record ─────────────────────────────────────────────────────────────
pw = int((period["result"] == "W").sum())
pl = int((period["result"] == "L").sum())
avg_ortg = round(period["ortg"].mean(), 1)
avg_drtg = round(period["drtg"].mean(), 1)
avg_net = round(avg_ortg - avg_drtg, 1)

kpi_row([
    {"label": "Period Record", "value": f"{pw}-{pl}"},
    {"label": "Games", "value": str(len(period))},
    {"label": "Avg ORtg", "value": f"{avg_ortg:.1f}"},
    {"label": "Avg DRtg", "value": f"{avg_drtg:.1f}"},
    {"label": "Net Rating", "value": f"{avg_net:+.1f}", "delta_good": avg_net > 0},
])

st.markdown("---")

# ── Rolling Charts ────────────────────────────────────────────────────────────
st.plotly_chart(
    rolling_line_chart(
        game_log, ["ortg", "drtg"],
        labels=["Off Rating", "Def Rating"],
        title="Rolling 7-Game Ratings",
        window=7,
        reference_lines={"League Avg": league_avg["league"]["ortg"]},
    ),
    use_container_width=True,
)

col_a, col_b = st.columns(2)

with col_a:
    net = game_log.copy().sort_values("game_date")
    net["net_rtg"] = net["ortg"] - net["drtg"]
    st.plotly_chart(
        rolling_line_chart(net, ["net_rtg"], labels=["Net Rating"], title="Net Rating Trend", window=7, height=300),
        use_container_width=True,
    )

with col_b:
    st.plotly_chart(win_loss_timeline(period), use_container_width=True)

# ── Four Factors Breakdown ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Four Factors — Selected Period")

team_ff = four_factors(period)
opp_ff = opponent_four_factors(period)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(four_factors_bar(team_ff, opp_ff, title="Team vs Opponent"), use_container_width=True)

with col2:
    st.markdown("#### Sparklines")
    for label, col_name in [("eFG%", "efg_pct"), ("TOV%", "tov_pct"), ("OREB%", "oreb_pct"), ("FT Rate", "ft_rate")]:
        vals = game_log.sort_values("game_date")[col_name].tolist()
        st.markdown(f"**{label}**")
        st.plotly_chart(sparkline(vals[-20:], color=COLORS["rich_red"]), use_container_width=True)
