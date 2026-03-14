"""Page 6 — Narratives: Auto-generated text insights and analysis report."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_stats
from utils.calculations import win_pct, current_streak, last_n_record

st.markdown("# NARRATIVES")

# ── Load Data ────────────────────────────────────────────────────────────────
game_log = load_game_log()
player_stats = load_player_stats()

# ── Season Storyline ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Season Storyline</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
wp = win_pct(total_w, total_l)
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
avg_pm = game_log["plus_minus"].mean()
net_rtg = game_log["ortg"].mean() - game_log["drtg"].mean()

streak_word = "winning" if s_type == "W" else "losing"
coverage = "above" if wp >= 0.500 else "below"

story = f"""
The Heat are currently **{total_w}-{total_l}** ({wp:.3f}) on the season, sitting {coverage} .500.
They are on a **{s_count}-game {streak_word} streak** and have gone **{l10_w}-{l10_l}** over the last 10 games.

Offensively, the team averages a **{game_log['ortg'].mean():.1f} offensive rating** and defensively a **{game_log['drtg'].mean():.1f} defensive rating**,
for a net rating of **{net_rtg:+.1f}**. Their average scoring margin per game is **{avg_pm:+.1f} points**.
"""
st.markdown(story)

# ── Trend Analysis ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Trend Analysis</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)

# Split first half vs second half
half = len(game_log) // 2
first_half = game_log.iloc[:half]
second_half = game_log.iloc[half:]

if len(first_half) > 0 and len(second_half) > 0:
    fh_net = first_half["ortg"].mean() - first_half["drtg"].mean()
    sh_net = second_half["ortg"].mean() - second_half["drtg"].mean()
    fh_w = int((first_half["result"] == "W").sum())
    fh_l = int((first_half["result"] == "L").sum())
    sh_w = int((second_half["result"] == "W").sum())
    sh_l = int((second_half["result"] == "L").sum())

    direction = "improving" if sh_net > fh_net else "declining"
    delta = abs(sh_net - fh_net)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**First Half of Season**")
        st.metric("Record", f"{fh_w}-{fh_l}")
        st.metric("Net Rating", f"{fh_net:+.1f}")
    with col2:
        st.markdown("**Second Half of Season**")
        st.metric("Record", f"{sh_w}-{sh_l}")
        st.metric("Net Rating", f"{sh_net:+.1f}")

    st.markdown(
        f"The team's net rating is **{direction}** from the first half to the second half, "
        f"shifting by **{delta:.1f} points** ({fh_net:+.1f} → {sh_net:+.1f})."
    )

# ── Key Players ───────────────────────────────────────────────────────────────
if not player_stats.empty and "player" in player_stats.columns and "pts" in player_stats.columns:
    st.markdown(
        '<div class="cc-section-header"><h2>Key Players</h2><div class="cc-section-line"></div></div>',
        unsafe_allow_html=True,
    )

    agg = player_stats.groupby("player").agg(
        pts=("pts", "mean"),
        reb=("reb", "mean") if "reb" in player_stats.columns else ("pts", "mean"),
        ast=("ast", "mean") if "ast" in player_stats.columns else ("pts", "mean"),
    ).round(1).reset_index()

    top3 = agg.nlargest(3, "pts")
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(
                f"""
                <div class="cc-kpi-card">
                    <div class="cc-kpi-label">Top Scorer</div>
                    <div class="cc-kpi-value">{row['player']}</div>
                    <div class="cc-kpi-delta">{row['pts']} PPG · {row.get('reb', '—')} RPG · {row.get('ast', '—')} APG</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ── Notebook / Notes ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="cc-section-header"><h2>Analyst Notes</h2><div class="cc-section-line"></div></div>',
    unsafe_allow_html=True,
)
notes = st.text_area(
    "Add your own observations:",
    placeholder="e.g. Butler has been inconsistent in the 4th quarter...",
    height=120,
)
if notes:
    st.markdown(f"> {notes}")
