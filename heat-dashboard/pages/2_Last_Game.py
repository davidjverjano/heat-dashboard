"""Page 2 — Last Game / Daily: Box score, advanced stats, top performer."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
css_file = ROOT / "assets" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

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
badge_color = COLORS["win_green"] if game.result == "W" else COLORS["mamey"]

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:20px; margin-bottom:20px;">
        <span style="background:{badge_color}; color:#fff; padding:8px 20px; border-radius:24px; font-size:1.3rem; font-weight:700;">
            {game.result}
        </span>
        <div>
            <span style="font-size:1.5rem; font-weight:700; color:#FFFCF2;">
                Miami Heat {game.team_score} — {game.opponent_score} {game.opponent}
            </span><br>
            <span style="color:#CCC5B9;">{game.game_date.strftime('%B %d, %Y')} &nbsp;|&nbsp; {game.home_away}</span>
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
st.markdown("### Box Score")
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
            <div style="background:#1a1816; border-left:4px solid #F7B267; border-radius:8px; padding:16px 20px;">
                <div style="font-size:1.4rem; font-weight:700; color:#F7B267;">{top.player_name}</div>
                <div style="color:#FFFCF2; font-size:1.1rem; margin-top:8px;">
                    {int(top.pts)} PTS &nbsp;|&nbsp; {int(top.reb)} REB &nbsp;|&nbsp; {int(top.ast)} AST
                </div>
                <div style="color:#CCC5B9; margin-top:4px;">
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
