"""Page 6 — Narratives: AI-style story cards, trends, and game notes."""

import pathlib
import streamlit as st
import pandas as pd
from datetime import timedelta

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_game_log, load_player_season_stats, load_schedule
from utils.calculations import last_n_record, current_streak, win_pct, four_factors, opponent_four_factors
from components.metrics import kpi_row
from components.theme import COLORS

st.markdown("# NARRATIVES")

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
player_gl = load_player_game_log()
player_season = load_player_season_stats()
schedule = load_schedule()

# ── Story Cards ────────────────────────────────────────────────────────────────
def story_card(title: str, body: str, color: str = COLORS["accent_primary"], icon: str = "▸"):
    st.markdown(
        f"""
        <div style="
            background:#1e1d1b;
            border-left: 4px solid {color};
            border-radius: 0 12px 12px 0;
            padding: 18px 22px;
            margin-bottom: 18px;
        ">
            <div style="color:{color}; font-family:'Hyperspace Wide','Hyperspace',sans-serif; font-size:10px; letter-spacing:3px; text-transform:uppercase; margin-bottom:6px;">
                {icon} {title}
            </div>
            <div style="color:#FFFCF2; font-family:-apple-system,system-ui,sans-serif; font-size:0.95rem; line-height:1.6;">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Season Arc ─────────────────────────────────────────────────────────────────
total_w = int((game_log["result"] == "W").sum())
total_l = int((game_log["result"] == "L").sum())
wp = win_pct(total_w, total_l)
l10_w, l10_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)

if wp >= 0.600:
    arc_tone = "contender"
elif wp >= 0.500:
    arc_tone = "bubble team"
else:
    arc_tone = "rebuilding squad"

story_card(
    "Season Arc",
    f"At {total_w}-{total_l} ({wp:.3f}), the Heat project as a <strong>{arc_tone}</strong> this season. "
    f"Their last-10 record of {l10_w}-{l10_l} hints at {'rising momentum' if l10_w > l10_l else 'a recent struggle'}. "
    f"Current streak: <strong>{s_type}{s_count}</strong>.",
    color=COLORS["accent_primary"],
)

# ── Offensive Identity ─────────────────────────────────────────────────────────
avg_ortg = round(game_log["ortg"].mean(), 1)
avg_pace = round(game_log["pace"].mean(), 1)
avg_ts = round(game_log["ts_pct"].mean(), 3)
avg_tov = round(game_log["tov_pct"].mean(), 1)

pace_desc = "up-tempo" if avg_pace > 100 else "methodical"
ts_desc = "efficient" if avg_ts > 0.575 else "league-average"
tov_desc = "careless" if avg_tov > 14 else "disciplined"

story_card(
    "Offensive Identity",
    f"Miami plays a <strong>{pace_desc}</strong> style (pace {avg_pace}) with <strong>{ts_desc}</strong> scoring (TS% {avg_ts:.1%}). "
    f"Ball security has been <strong>{tov_desc}</strong> with a {avg_tov:.1f}% turnover rate. "
    f"Offensive rating: <strong>{avg_ortg}</strong>.",
    color=COLORS["heat_red"],
)

# ── Defensive Narrative ────────────────────────────────────────────────────────
avg_drtg = round(game_log["drtg"].mean(), 1)
avg_opp_efg = round(game_log["opp_efg_pct"].mean(), 3)

def_grade = "elite" if avg_drtg < 110 else ("solid" if avg_drtg < 114 else "below-average")

story_card(
    "Defensive Stand",
    f"Miami's defense grades as <strong>{def_grade}</strong> with a {avg_drtg} DRtg. "
    f"Opponents are shooting {avg_opp_efg:.1%} eFG%, "
    f"{'well below' if avg_opp_efg < 0.52 else 'near'} league average.",
    color="#5B8DD9",
)

# ── Hot Player ─────────────────────────────────────────────────────────────────
recent_games = game_log.sort_values("game_date", ascending=False).head(5)
recent_ids = recent_games["game_id"].tolist()
recent_player_gl = player_gl[player_gl["game_id"].isin(recent_ids)]

if not recent_player_gl.empty:
    player_avg = recent_player_gl.groupby("player_name")["pts"].mean()
    hot_player = player_avg.idxmax()
    hot_ppg = round(player_avg.max(), 1)
    story_card(
        "Hot Hand",
        f"<strong>{hot_player}</strong> has been the standout performer over the last 5 games, "
        f"averaging <strong>{hot_ppg} PPG</strong> in that stretch.",
        color=COLORS["win_green"],
        icon="🔥",
    )

# ── Schedule Outlook ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Schedule Outlook")

upcoming = schedule.head(7).copy()
if not upcoming.empty:
    upcoming["game_date"] = upcoming["game_date"].dt.strftime("%b %d")
    upcoming["H/A"] = upcoming["home_away"].apply(lambda x: "🏠" if x == "Home" else "✈")
    display = upcoming[["game_date", "H/A", "opponent", "game_time"]].rename(
        columns={"game_date": "Date", "opponent": "Opponent", "game_time": "Time"}
    )
    st.dataframe(display, use_container_width=True, hide_index=True)

# ── Game Notes ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Recent Game Notes")

recent_5 = game_log.sort_values("game_date", ascending=False).head(5)
for _, row in recent_5.iterrows():
    result_color = COLORS["win_green"] if row.result == "W" else COLORS["loss_red"]
    margin = abs(row.plus_minus)
    margin_desc = "blowout" if margin > 15 else ("comfortable" if margin > 7 else "close")
    ha = "vs" if row.home_away == "Home" else "@"
    story_card(
        f"{row.game_date.strftime('%b %d')} — {ha} {row.opponent}",
        f"<span style='color:{result_color}; font-weight:700;'>{row.result} {row.team_score}-{row.opponent_score}</span> "
        f"| {margin_desc} {margin}-point {'win' if row.result == 'W' else 'loss'}. "
        f"ORtg {row.ortg:.1f} / DRtg {row.drtg:.1f} / Pace {row.pace:.1f}.",
        color=result_color,
    )
