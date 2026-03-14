"""Page 6 — Narratives: Auto-generated text insights and analysis report."""

import pathlib
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_game_log, load_player_season_stats, load_schedule
from utils.calculations import last_n_record, current_streak
from components.theme import COLORS

st.markdown("# NARRATIVES")
st.markdown('<p style="color:#b0ada6; letter-spacing:0.5px;">Auto-generated insights from the 2025-26 Miami Heat season data.</p>', unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
player_gl = load_player_game_log()
season_stats = load_player_season_stats()
schedule = load_schedule()


def narrative_card(title: str, body: str, accent_color: str = COLORS["accent_primary"]):
    """Render a narrative card."""
    st.markdown(
        f"""
        <div style="
            background: #2a2926;
            border: 1px solid rgba(255,252,242,0.06);
            border-left: 3px solid {accent_color};
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
        ">
            <h3 style="color:#F7B267; margin:0 0 12px 0; border:none !important; padding:0 !important;
                font-family:'Hyperspace Wide','Hyperspace',sans-serif; font-size:14px;
                letter-spacing:2px; text-transform:uppercase;">{title}</h3>
            <div style="color:#FFFCF2; line-height:1.7; font-size:0.95rem;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── 1. Recent Form ───────────────────────────────────────────────────────────
recent = game_log.tail(10).copy()
r_w, r_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
recent_ortg = round(recent["ortg"].mean(), 1)
recent_drtg = round(recent["drtg"].mean(), 1)
recent_net = round(recent_ortg - recent_drtg, 1)
recent_ppg = round(recent["team_score"].mean(), 1)

streak_text = f"on a {s_count}-game {'winning' if s_type == 'W' else 'losing'} streak" if s_count >= 2 else ""
form_text = "strong form" if r_w >= 7 else "solid form" if r_w >= 5 else "mixed results" if r_w >= 4 else "struggling"

body = f"""
The Heat are <b>{r_w}-{r_l}</b> over their last 10 games, showing <b>{form_text}</b>
{f'and are currently <b>{streak_text}</b>' if streak_text else ''}.
They're averaging <b>{recent_ppg} points per game</b> in this stretch with an offensive rating of
<b>{recent_ortg}</b> and defensive rating of <b>{recent_drtg}</b> (net: <b>{recent_net:+.1f}</b>).
"""
narrative_card("Recent Form", body)

# ── 2. Key Player Performances ────────────────────────────────────────────────
last5_ids = game_log.tail(5)["game_id"].tolist()
last5_players = player_gl[player_gl["game_id"].isin(last5_ids)]
player_avgs = last5_players.groupby("player_name").agg(
    pts=("pts", "mean"), reb=("reb", "mean"), ast=("ast", "mean"),
    ts=("ts_pct", "mean"), games=("game_id", "count")
).reset_index()
player_avgs = player_avgs[player_avgs["games"] >= 3].sort_values("pts", ascending=False)

top_3 = player_avgs.head(3)
player_lines = []
for _, p in top_3.iterrows():
    player_lines.append(
        f"<b>{p.player_name}</b>: {p.pts:.1f} PPG / {p.reb:.1f} RPG / {p.ast:.1f} APG ({p.ts:.1%} TS%)"
    )

body = "Over the last 5 games, the top performers have been:<br><br>" + "<br>".join(player_lines)

# Find a hot player
hottest = player_avgs.iloc[0]
season_ppg = season_stats[season_stats["player_name"] == hottest.player_name]["ppg"].values
if len(season_ppg) > 0 and hottest.pts > season_ppg[0] * 1.1:
    body += f"<br><br>{hottest.player_name} has been particularly hot, averaging <b>{hottest.pts:.1f} PPG</b> \u2014 well above their season average of {season_ppg[0]:.1f}."

narrative_card("Key Performers", body, COLORS["yellow_flame"])

# ── 3. Offensive & Defensive Trends ──────────────────────────────────────────
full_ortg = round(game_log["ortg"].mean(), 1)
full_drtg = round(game_log["drtg"].mean(), 1)
first_half = game_log.head(len(game_log) // 2)
second_half = game_log.tail(len(game_log) // 2)
h1_ortg = round(first_half["ortg"].mean(), 1)
h2_ortg = round(second_half["ortg"].mean(), 1)
h1_drtg = round(first_half["drtg"].mean(), 1)
h2_drtg = round(second_half["drtg"].mean(), 1)

o_trend = "improved" if h2_ortg > h1_ortg else "declined"
d_trend = "improved" if h2_drtg < h1_drtg else "declined"

body = f"""
<b>Offense:</b> The Heat's season offensive rating is <b>{full_ortg}</b>. The offense has <b>{o_trend}</b>
from the first half ({h1_ortg}) to the second half ({h2_ortg}).
<br><br>
<b>Defense:</b> The defensive rating sits at <b>{full_drtg}</b> for the season. The defense has <b>{d_trend}</b>
from {h1_drtg} (first half) to {h2_drtg} (second half).
<br><br>
The team's four factors show an eFG% of <b>{game_log['efg_pct'].mean():.1%}</b> and a turnover rate of
<b>{game_log['tov_pct'].mean():.1f}%</b> \u2014 {'solid ball security' if game_log['tov_pct'].mean() < 13.5 else 'an area to watch'}.
"""
narrative_card("Offensive & Defensive Trends", body, COLORS["warm_coral"])

# ── 4. Upcoming Schedule ─────────────────────────────────────────────────────
upcoming = schedule.head(5)
strong_teams = {"BOS", "CLE", "MIL", "NYK", "OKC", "DEN", "MIN"}
tough_games = upcoming[upcoming["opponent_abbr"].isin(strong_teams)]
home_games = len(upcoming[upcoming["home_away"] == "Home"])
away_games = len(upcoming[upcoming["home_away"] == "Away"])

difficulty = "challenging" if len(tough_games) >= 3 else "moderate" if len(tough_games) >= 1 else "favorable"

upcoming_text = "<br>".join([
    f"\u2022 {row.game_date.strftime('%b %d')} \u2014 {'vs' if row.home_away == 'Home' else '@'} {row.opponent}"
    for _, row in upcoming.iterrows()
])

body = f"""
The next 5 games present a <b>{difficulty}</b> stretch with <b>{home_games} home</b> and <b>{away_games} away</b> games.
{f'Notably, {len(tough_games)} of these are against top contenders.' if len(tough_games) > 0 else ''}
<br><br>
{upcoming_text}
"""
narrative_card("Schedule Ahead", body, COLORS["dark_red"])

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""
    <div class="cc-footer">
        Narratives auto-generated from local data &nbsp;|&nbsp; Updated through {game_log['game_date'].max().strftime('%B %d, %Y')}
    </div>
    """,
    unsafe_allow_html=True,
)
