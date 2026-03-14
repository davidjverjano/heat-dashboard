"""Page 4 — Season View: Team metrics, radar chart, rankings, splits."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log
from utils.calculations import win_pct, last_n_record, current_streak
from components.charts import season_radar_chart, home_away_splits_chart

st.markdown("# SEASON VIEW")

# ── Load Data ────────────────────────────────────────────────────────────────
game_log = load_game_log()

# ── Season Averages ───────────────────────────────────────────────────────────
total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
wp = win_pct(total_w, total_l)
avg_ortg = game_log["ortg"].mean()
avg_drtg = game_log["drtg"].mean()
avg_pace = game_log["pace"].mean()
avg_pm = game_log["plus_minus"].mean()
net_rtg = avg_ortg - avg_drtg

st.markdown(
    '<div class="cc-section-header"><h2>Season Averages</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Record", f"{total_w}-{total_l}")
with col2:
    st.metric("Win%", f"{wp:.3f}")
with col3:
    st.metric("Net Rtg", f"{net_rtg:+.1f}")
with col4:
    st.metric("Avg ORtg", f"{avg_ortg:.1f}")
with col5:
    st.metric("Avg DRtg", f"{avg_drtg:.1f}")

# ── Radar Chart ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Team Profile Radar</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
radar_cols = ["ortg", "drtg", "pace", "efg_pct", "tov_pct", "orb_pct"]
if all(c in game_log.columns for c in radar_cols):
    st.plotly_chart(season_radar_chart(game_log), use_container_width=True)
else:
    st.info("Radar chart requires ortg, drtg, pace, efg_pct, tov_pct, orb_pct columns.")

# ── Home / Away Splits ────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Home / Away Splits</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
if "home_away" in game_log.columns:
    home = game_log[game_log["home_away"] == "H"]
    away = game_log[game_log["home_away"] == "A"]

    col_h, col_a = st.columns(2)
    with col_h:
        hw = int((home["result"] == "W").sum())
        hl = int((home["result"] == "L").sum())
        st.metric("Home Record", f"{hw}-{hl}")
        st.metric("Home Net Rtg", f"{(home['ortg'].mean() - home['drtg'].mean()):+.1f}")
    with col_a:
        aw = int((away["result"] == "W").sum())
        al = int((away["result"] == "L").sum())
        st.metric("Away Record", f"{aw}-{al}")
        st.metric("Away Net Rtg", f"{(away['ortg'].mean() - away['drtg'].mean()):+.1f}")

    st.plotly_chart(home_away_splits_chart(game_log), use_container_width=True)

# ── Monthly Splits ────────────────────────────────────────────────────────────
if "game_date" in game_log.columns:
    st.markdown(
        '<div class="cc-section-header"><h2>Monthly Splits</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )
    monthly = game_log.copy()
    monthly["month"] = monthly["game_date"].dt.strftime("%b %Y")
    agg = monthly.groupby("month").agg(
        W=("result", lambda x: (x == "W").sum()),
        L=("result", lambda x: (x == "L").sum()),
        ORtg=("ortg", "mean"),
        DRtg=("drtg", "mean"),
        Pace=("pace", "mean"),
    ).reset_index()
    agg["Net"] = (agg["ORtg"] - agg["DRtg"]).round(1)
    agg["ORtg"] = agg["ORtg"].round(1)
    agg["DRtg"] = agg["DRtg"].round(1)
    agg["Pace"] = agg["Pace"].round(1)
    st.dataframe(agg, use_container_width=True, hide_index=True)

# ── Full Season Game Log ──────────────────────────────────────────────────────
with st.expander("Full Season Game Log"):
    log_cols = ["game_date", "home_away", "opponent", "result", "pts_for", "pts_against",
                "plus_minus", "ortg", "drtg", "pace"]
    avail = [c for c in log_cols if c in game_log.columns]
    display = game_log[avail].copy()
    if "game_date" in display.columns:
        display["game_date"] = display["game_date"].dt.strftime("%b %d")
    st.dataframe(display, use_container_width=True, hide_index=True)
