"""Page 3 — Weekly Trends: Rolling metrics, four factors, period record."""

import pathlib
import streamlit as st
import pandas as pd
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_league_averages
from utils.calculations import four_factors, opponent_four_factors
from components.metrics import kpi_row
import plotly.graph_objects as go
from components.charts import rolling_line_chart, win_loss_timeline, four_factors_bar
from components.theme import COLORS, apply_plotly_theme

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

st.plotly_chart(four_factors_bar(team_ff, opp_ff, title="Team vs Opponent"), use_container_width=True)

# ── Four Factors Rolling Trends ──────────────────────────────────────────────
st.markdown("### Four Factors — Rolling Trends")

gl_sorted = game_log.sort_values("game_date")
factor_defs = [
    ("eFG%", "efg_pct", 100),
    ("TOV%", "tov_pct", 1),
    ("OREB%", "oreb_pct", 1),
    ("FT Rate", "ft_rate", 1),
]

for label, col_name, multiplier in factor_defs:
    current_val = gl_sorted[col_name].iloc[-5:].mean() * multiplier
    season_avg = gl_sorted[col_name].mean() * multiplier
    delta = current_val - season_avg
    delta_good = (delta > 0) if col_name != "tov_pct" else (delta < 0)

    col_stat, col_chart = st.columns([1, 3])
    with col_stat:
        fmt = f"{current_val:.1f}{'%' if multiplier == 100 else ''}"
        delta_fmt = f"{delta:+.1f}"
        st.metric(label, fmt, delta_fmt, delta_color="normal" if delta_good else "inverse")
    with col_chart:
        rolling = gl_sorted[col_name].rolling(5, min_periods=1).mean() * multiplier
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=gl_sorted["game_date"], y=rolling,
            mode="lines", line=dict(color=COLORS["accent_primary"], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(247,178,103,0.08)",
            hovertemplate=f"{label}: " + "%{y:.1f}<extra></extra>",
        ))
        fig.add_hline(y=season_avg, line_dash="dot", line_color=COLORS["text_muted"], opacity=0.4)
        fig.update_layout(
            height=120, margin=dict(l=0, r=0, t=8, b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            showlegend=False,
        )
        apply_plotly_theme(fig)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
