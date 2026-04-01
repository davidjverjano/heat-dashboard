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
        # Compute game score if missing
        for col in ["pts","fg","fga","fta","ft","oreb","dreb","stl","ast","blk","pf","tov"]:
            players[col] = pd.to_numeric(players[col], errors="coerce").fillna(0)
        if players["game_score"].isna().all() or (players["game_score"] == 0).all():
            players["game_score"] = (
                players["pts"] + 0.4 * players["fg"] - 0.7 * players["fga"]
                - 0.4 * (players["fta"] - players["ft"]) + 0.7 * players["oreb"]
                + 0.3 * players["dreb"] + players["stl"] + 0.7 * players["ast"]
                + 0.7 * players["blk"] - 0.4 * players["pf"] - players["tov"]
            )
        top = players.loc[players["game_score"].idxmax()]
        gs_display = f" &nbsp;|&nbsp; Game Score: {top.game_score:.1f}" if pd.notna(top.game_score) else ""
        st.markdown(
            f"""
            <div class="cc-kpi-card">
                <div style="font-size:1.3rem; font-weight:700; color:#F7B267; font-family:'Orbitron','Barlow Condensed',sans-serif;">{top.player_name}</div>
                <div style="color:#FFFCF2; font-size:1.1rem; margin-top:8px; font-family:-apple-system,system-ui,sans-serif; font-variant-numeric:tabular-nums;">
                    {int(top.pts)} PTS &nbsp;|&nbsp; {int(top.reb)} REB &nbsp;|&nbsp; {int(top.ast)} AST
                </div>
                <div style="color:#b0ada6; margin-top:4px; font-family:-apple-system,system-ui,sans-serif; font-variant-numeric:tabular-nums;">
                    {int(top.fg)}/{int(top.fga)} FG &nbsp;|&nbsp; {int(top.fg3)}/{int(top.fg3a)} 3P{gs_display}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Four Factors ──────────────────────────────────────────────────────────────
with col2:
    st.markdown("### Four Factors")
    def _pct(v, mul=100):
        try:
            v = float(v)
            return round(v * mul, 1) if v < 1 else round(v, 1)
        except (TypeError, ValueError):
            return 0.0

    team_ff = {
        "eFG%": _pct(game.efg_pct),
        "TOV%": _pct(game.tov_pct),
        "OREB%": _pct(game.oreb_pct),
        "FT Rate": round(float(game.ft_rate) if game.ft_rate else 0, 3),
    }
    opp_ff = {
        "eFG%": _pct(game.opp_efg_pct),
        "TOV%": _pct(game.opp_tov_pct),
        "OREB%": _pct(game.opp_oreb_pct),
        "FT Rate": round(float(game.opp_ft_rate) if game.opp_ft_rate else 0, 3),
    }
    st.plotly_chart(four_factors_bar(team_ff, opp_ff, title=""), use_container_width=True)
