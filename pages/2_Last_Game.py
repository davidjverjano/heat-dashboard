"""Page 2 — Last Game / Daily: Box score, advanced stats, top performer."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_game_log
from components.metrics import kpi_row
from components.tables import box_score_table
from components.charts import four_factors_bar
from components.theme import COLORS

st.markdown("# LAST GAME")

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
player_gl = load_player_game_log()

# Game selector
game_dates = game_log.sort_values("game_date", ascending=False)["game_date"]
game_options = {
    f"{row.game_date.strftime('%b %d')} — {'vs' if row.home_away == 'Home' else '@'} {row.opponent} ({row.result} {row.team_score}-{row.opponent_score})": row.game_id
    for _, row in game_log.sort_values("game_date", ascending=False).iterrows()
}
selected_label = st.selectbox("Select Game", list(game_options.keys()))
selected_id = game_options[selected_label]

game = game_log[game_log["game_id"] == selected_id].iloc[0]
players = player_gl[player_gl["game_id"] == selected_id]

# ── Header ────────────────────────────────────────────────────────────────────
prefix = "vs" if game.home_away == "Home" else "@"
badge_color = COLORS["win_green"] if game.result == "W" else COLORS["loss_red"]

st.markdown(
    f"""
    <div class="cc-game-header">
        <span class="cc-game-header-badge" style="background:{badge_color};">{game.result}</span>
        <div class="cc-game-header-info">
            <span class="cc-game-header-score">Miami Heat {game.team_score} — {game.opponent_score} {game.opponent}</span>
            <span class="cc-game-header-meta">{game.game_date.strftime('%B %d, %Y')} &nbsp;|&nbsp; {game.home_away}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Team Advanced Stats ───────────────────────────────────────────────────────
kpi_row([
    {"label": "Off Rating", "value": f"{game.ortg:.1f}"},
    {"label": "Def Rating", "value": f"{game.drtg:.1f}"},
    {"label": "Pace", "value": f"{game.pace:.1f}"},
    {"label": "TS%", "value": f"{game.ts_pct:.1%}"},
    {"label": "eFG%", "value": f"{game.efg_pct:.1%}"},
])

st.markdown("---")

# ── Box Score ─────────────────────────────────────────────────────────────────
st.markdown('<div class="cc-section-heading">BOX SCORE</div>', unsafe_allow_html=True)
box_score_table(players)

# ── Top Performer ─────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Top Performer")
    if not players.empty:
        top = players.loc[players["game_score"].idxmax()]
        st.markdown(
            f"""
            <div class="cc-kpi-card">
                <div style="font-size:1.3rem; font-weight:700; color:#F7B267; font-family:'Orbitron','Barlow Condensed',sans-serif;">{top.player_name}</div>
                <div style="color:#FFFCF2; font-size:1.1rem; margin-top:8px; font-family:-apple-system,system-ui,sans-serif; font-variant-numeric:tabular-nums;">
                    {int(top.pts)} PTS &nbsp;|&nbsp; {int(top.reb)} REB &nbsp;|&nbsp; {int(top.ast)} AST
                </div>
                <div style="color:#b0ada6; margin-top:4px; font-family:-apple-system,system-ui,sans-serif; font-variant-numeric:tabular-nums;">
                    {top.fg}/{top.fga} FG &nbsp;|&nbsp; {top.fg3}/{top.fg3a} 3P &nbsp;|&nbsp;
                    Game Score: {top.game_score:.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Four Factors ──────────────────────────────────────────────────────────────
with col2:
    st.markdown("### Four Factors")
    team_ff = {
        "eFG%": round(game.efg_pct * 100, 1),
        "TOV%": round(game.tov_pct, 1),
        "OREB%": round(game.oreb_pct, 1),
        "FT Rate": round(game.ft_rate, 3),
    }
    opp_ff = {
        "eFG%": round(game.opp_efg_pct * 100, 1),
        "TOV%": round(game.opp_tov_pct, 1),
        "OREB%": round(game.opp_oreb_pct, 1),
        "FT Rate": round(game.opp_ft_rate, 3),
    }
    st.plotly_chart(four_factors_bar(team_ff, opp_ff, title=""), use_container_width=True)
