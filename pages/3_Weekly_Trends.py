"""Page 3 — Weekly Trends: Rolling metrics, four factors, period record."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log
from utils.calculations import last_n_record, rolling_metrics
from components.charts import rolling_ratings_chart, four_factors_bar

st.markdown("# WEEKLY TRENDS")

# ── Load Data ────────────────────────────────────────────────────────────────
game_log = load_game_log()

# ── Period Selector ───────────────────────────────────────────────────────────
period = st.selectbox("Lookback Window", [7, 14, 21, 30], index=0, format_func=lambda x: f"Last {x} Days")

# Filter to period
if "game_date" in game_log.columns:
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=period)
    period_games = game_log[game_log["game_date"] >= cutoff].copy()
else:
    period_games = game_log.tail(period).copy()

if period_games.empty:
    st.warning("No games found in the selected window.")
    st.stop()

# ── Period Record ─────────────────────────────────────────────────────────────
w = int((period_games["result"] == "W").sum())
l = int((period_games["result"] == "L").sum())
avg_ortg = period_games["ortg"].mean()
avg_drtg = period_games["drtg"].mean()
avg_net = avg_ortg - avg_drtg
avg_pace = period_games["pace"].mean()

st.markdown(
    '<div class="cc-section-header"><h2>Period Summary</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Record", f"{w}-{l}")
with col2:
    st.metric("Avg ORtg", f"{avg_ortg:.1f}")
with col3:
    st.metric("Avg DRtg", f"{avg_drtg:.1f}")
with col4:
    st.metric("Avg Net", f"{avg_net:+.1f}")

# ── Rolling Ratings Chart ─────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Rolling Ratings</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
st.plotly_chart(rolling_ratings_chart(game_log, window=min(period, len(game_log))), use_container_width=True)

# ── Four Factors ─────────────────────────────────────────────────────────────
ff_cols = ["efg_pct", "tov_pct", "orb_pct", "ft_rate"]
if all(c in period_games.columns for c in ff_cols):
    st.markdown(
        '<div class="cc-section-header"><h2>Four Factors</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(four_factors_bar(period_games), use_container_width=True)

# ── Game Log Table ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Game Log</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
log_cols = ["game_date", "home_away", "opponent", "result", "pts_for", "pts_against", "plus_minus", "ortg", "drtg", "pace"]
avail = [c for c in log_cols if c in period_games.columns]
display = period_games[avail].copy()
if "game_date" in display.columns:
    display["game_date"] = display["game_date"].dt.strftime("%b %d")
st.dataframe(display, use_container_width=True, hide_index=True)
