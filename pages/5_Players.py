"""Page 5 — Players: Roster stats, deep dives, usage/efficiency charts."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

from utils.data_loader import load_player_season_stats, load_player_game_log
from components.tables import styled_table
from components.charts import usage_ts_scatter, bar_chart, plus_minus_distribution, rolling_line_chart
from components.theme import COLORS

st.markdown("# PLAYERS")

# ── Load Data ─────────────────────────────────────────────────────────────────────
season_stats = load_player_season_stats()
player_gl = load_player_game_log()

# ── Sortable Season Stats Table ───────────────────────────────────────────────────────
st.markdown("### Season Averages")
display_cols = ["player_name", "gp", "mpg", "ppg", "rpg", "apg", "spg", "bpg", "topg",
                "fg_pct", "fg3_pct", "ft_pct", "ts_pct", "usage_pct", "per", "bpm", "net_rtg"]
available = [c for c in display_cols if c in season_stats.columns]
display = season_stats[available].copy()
rename = {
    "player_name": "Player", "gp": "GP", "mpg": "MPG", "ppg": "PPG", "rpg": "RPG",
    "apg": "APG", "spg": "SPG", "bpg": "BPG", "topg": "TOPG",
    "fg_pct": "FG%", "fg3_pct": "3P%", "ft_pct": "FT%", "ts_pct": "TS%",
    "usage_pct": "USG%", "per": "PER", "bpm": "BPM", "net_rtg": "NET",
}
display.rename(columns={k: v for k, v in rename.items() if k in display.columns}, inplace=True)
styled_table(display, height=450)

st.markdown("---")

# ── Charts Row ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Usage% vs TS%")
    st.plotly_chart(usage_ts_scatter(season_stats), use_container_width=True)

with col2:
    st.markdown("### PPG Leaders")
    top_scorers = season_stats.head(10)
    st.plotly_chart(
        bar_chart(
            top_scorers["player_name"].tolist(),
            top_scorers["ppg"].tolist(),
            title="",
            highlight_label=top_scorers.iloc[0]["player_name"],
            horizontal=True,
            height=350,
        ),
        use_container_width=True,
    )

st.markdown("---")

# ── Player Deep Dive ──────────────────────────────────────────────────────────────────
st.markdown("### Player Deep Dive")
players = season_stats["player_name"].tolist()
selected_player = st.selectbox("Select Player", players)

if selected_player:
    p_stats = season_stats[season_stats["player_name"] == selected_player].iloc[0]
    p_games = player_gl[player_gl["player_name"] == selected_player].copy()

    # Player Summary
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("PPG", f"{p_stats.ppg:.1f}")
    col_b.metric("RPG", f"{p_stats.rpg:.1f}")
    col_c.metric("APG", f"{p_stats.apg:.1f}")
    col_d.metric("TS%", f"{p_stats.ts_pct:.1%}")
    col_e.metric("Net Rtg", f"{p_stats.net_rtg:+.1f}")

    # On/Off Net Rating
    st.markdown("#### On/Off Court Impact")
    on_off = p_stats.get("on_off_net", 0)
    on_color = COLORS["win_green"] if on_off >= 0 else COLORS["loss_red"]
    st.markdown(
        f"""
        <div style="background:#2a2926; border:1px solid rgba(247,178,103,0.1); border-radius:12px; padding:12px 20px; display:inline-block;">
            <span style="color:#6e6b64; font-family:'Hyperspace Wide','Hyperspace',sans-serif; font-size:10px; letter-spacing:2px; text-transform:uppercase;">On/Off Net: </span>
            <span style="color:{on_color}; font-weight:800; font-size:1.3rem; font-family:-apple-system,system-ui,sans-serif; font-variant-numeric:tabular-nums;">{on_off:+.1f}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Charts
    col_x, col_y = st.columns(2)

    with col_x:
        st.markdown("#### +/- Distribution")
        st.plotly_chart(plus_minus_distribution(player_gl, selected_player), use_container_width=True)

    with col_y:
        st.markdown("#### Rolling Stats")
        if not p_games.empty:
            st.plotly_chart(
                rolling_line_chart(
                    p_games, ["pts", "reb", "ast"],
                    labels=["Points", "Rebounds", "Assists"],
                    title="5-Game Rolling Average",
                    window=5,
                    height=300,
                ),
                use_container_width=True,
            )
