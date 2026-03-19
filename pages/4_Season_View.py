"""Page 4 — Season View: Team metrics, radar chart, rankings, splits."""

import pathlib
import streamlit as st
import pandas as pd
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import (
    load_game_log, load_league_averages, load_league_team_ratings,
    load_team_rankings, load_east_standings,
)
from utils.calculations import season_splits
from components.tables import comparison_table
from components.charts import radar_chart, scatter_plot, bar_chart
from components.metrics import rating_card
from components.theme import COLORS, apply_plotly_theme
import plotly.graph_objects as go

st.markdown("# SEASON VIEW")

# ── Load Data ─────────────────────────────────────────────────────────────────
game_log = load_game_log()
league_avg = load_league_averages()
east_standings = load_east_standings()

# ── Load refresh metadata for "last updated" disclaimer ─────────────────────
import json
from datetime import datetime as _dt
_refresh_path = ROOT / "data" / "last_refresh.json"
try:
    with open(_refresh_path) as _f:
        _meta = json.load(_f)
    _ts = _dt.fromisoformat(_meta["last_refresh"])
    _last_updated_str = _ts.strftime("%b %d, %Y at %I:%M %p ET")
except Exception:
    _last_updated_str = None

# ══════════════════════════════════════════════════════════════════════════════
# EASTERN CONFERENCE STANDINGS & PLAYOFF PICTURE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Eastern Conference Standings")
if _last_updated_str:
    st.markdown(
        f'<p style="color:#6e6b64;font-size:11px;font-family:var(--font-data);'
        f'letter-spacing:0.3px;margin-top:-10px;">'
        f'Last updated: {_last_updated_str}</p>',
        unsafe_allow_html=True,
    )


def _standings_table_html(standings: list) -> str:
    """Build a branded HTML standings table."""
    # Tier breaks: 1-6 playoff, 7-8 play-in guaranteed, 9-10 play-in, 11+ out
    rows = []
    for t in standings:
        is_heat = t["team"] == "MIA"
        seed = t["seed"]

        # Row background
        if is_heat:
            bg = "rgba(247,178,103,0.10)"
            border_left = "3px solid #F7B267"
        else:
            bg = "#2a2926" if seed % 2 == 1 else "#252422"
            border_left = "3px solid transparent"

        # Seed badge color
        if seed <= 6:
            seed_color = "#3fb950"  # playoff lock
        elif seed <= 10:
            seed_color = "#F7B267"  # play-in
        else:
            seed_color = "#6e6b64"  # out

        # Team name styling
        name_color = "#F7B267" if is_heat else "#FFFCF2"
        name_weight = "800" if is_heat else "600"

        # GB formatting
        gb = t["gb"]
        if gb == "-" or gb == 0 or gb == 0.0:
            gb_str = "—"
        else:
            gb_str = str(gb)

        # Streak color
        strk = t["strk"]
        strk_color = "#3fb950" if strk.startswith("W") else "#F25C54"

        # Diff color
        diff = t["diff"]
        diff_color = "#3fb950" if diff > 0 else "#F25C54" if diff < 0 else "#b0ada6"
        diff_str = f"+{diff}" if diff > 0 else str(diff)

        # Clinch indicator
        clinch = t.get("clinch", "")
        clinch_html = ""
        if "ps" in clinch:
            clinch_html = '<span style="font-size:9px;color:#3fb950;margin-left:4px;">★</span>'
        elif "o" in clinch:
            clinch_html = '<span style="font-size:9px;color:#F25C54;margin-left:4px;">✗</span>'

        rows.append(f'''
            <tr style="background:{bg};border-left:{border_left};">
                <td style="text-align:center;width:36px;">
                    <span style="background:{seed_color};color:#1a1917;font-weight:800;
                        font-size:11px;width:22px;height:22px;border-radius:4px;
                        display:inline-flex;align-items:center;justify-content:center;
                        font-family:var(--font-data);">{seed}</span>
                </td>
                <td style="text-align:left;font-weight:{name_weight};color:{name_color};
                    font-family:'Orbitron',sans-serif;font-size:12px;
                    letter-spacing:1px;">
                    {t["city"]} {t["name"]}{clinch_html}
                </td>
                <td style="font-variant-numeric:tabular-nums;">{t["w"]}</td>
                <td style="font-variant-numeric:tabular-nums;">{t["l"]}</td>
                <td style="font-variant-numeric:tabular-nums;">{t["pct"]:.3f}</td>
                <td style="color:#6e6b64;font-variant-numeric:tabular-nums;">{gb_str}</td>
                <td style="font-variant-numeric:tabular-nums;">{t["home"]}</td>
                <td style="font-variant-numeric:tabular-nums;">{t["road"]}</td>
                <td style="font-variant-numeric:tabular-nums;">{t["l10"]}</td>
                <td style="color:{strk_color};font-weight:700;font-variant-numeric:tabular-nums;">{strk}</td>
                <td style="color:{diff_color};font-weight:600;font-variant-numeric:tabular-nums;">{diff_str}</td>
            </tr>''')

    # Separator rows after seed 6 (playoff) and seed 10 (play-in)
    sep_after = {6, 10}
    final_rows = []
    for i, row in enumerate(rows):
        final_rows.append(row)
        seed = standings[i]["seed"]
        if seed in sep_after:
            label = "PLAY-IN" if seed == 6 else "OUT"
            final_rows.append(f'''
                <tr style="background:transparent;height:4px;">
                    <td colspan="11" style="padding:0;border-bottom:1px dashed rgba(247,178,103,0.2);
                        font-size:9px;color:#6e6b64;letter-spacing:2px;text-align:left;padding-left:38px;
                        font-family:'Orbitron',sans-serif;">{label}</td>
                </tr>''')

    return f'''
    <div style="overflow-x:auto;border-radius:12px;border:1px solid rgba(255,252,242,0.06);">
    <table style="width:100%;border-collapse:collapse;font-family:var(--font-data);font-size:13px;
        color:#b0ada6;line-height:1;">
        <thead>
            <tr style="background:#201f1d;border-bottom:2px solid rgba(247,178,103,0.15);">
                <th style="padding:10px 6px;text-align:center;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;"></th>
                <th style="padding:10px 8px;text-align:left;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">TEAM</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">W</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">L</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">PCT</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">GB</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">HOME</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">ROAD</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">L10</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">STRK</th>
                <th style="padding:10px 8px;font-size:10px;letter-spacing:1.5px;
                    color:#6e6b64;font-family:'Orbitron',sans-serif;">DIFF</th>
            </tr>
        </thead>
        <tbody>
            {''.join(final_rows)}
        </tbody>
    </table>
    </div>
    '''


def _strip_indent(html: str) -> str:
    """Remove leading whitespace from each line so Markdown doesn't treat it as code."""
    return "\n".join(line.lstrip() for line in html.splitlines())

_standings_with_legend = _standings_table_html(east_standings) + '''
<div style="font-size:11px;color:#6e6b64;margin-top:8px;font-family:var(--font-data);">
<span style="color:#3fb950;">■</span> Playoff &nbsp;&nbsp;
<span style="color:#F7B267;">■</span> Play-In &nbsp;&nbsp;
<span style="color:#6e6b64;">■</span> Out &nbsp;&nbsp;
<span style="color:#3fb950;">★</span> Clinched Playoff &nbsp;&nbsp;
<span style="color:#F25C54;">✗</span> Eliminated
</div>
'''
st.markdown(_strip_indent(_standings_with_legend), unsafe_allow_html=True)

st.markdown("---")

# ── Projected Playoff Bracket ────────────────────────────────────────────────
st.markdown("### Projected Playoff Picture")
st.markdown(
    '<p style="color:#6e6b64;font-size:12px;letter-spacing:0.5px;">'
    'Based on current Eastern Conference seedings</p>',
    unsafe_allow_html=True,
)


def _bracket_html(standings: list) -> str:
    """Build an NBA-style projected playoff bracket using current seedings."""
    # Seeds 1-6: direct playoff, 7-8: play-in upper, 9-10: play-in lower
    teams = {t["seed"]: t for t in standings}

    def _team_row(seed, record, highlight=False, winner=False):
        t = teams[seed]
        is_heat = t["team"] == "MIA"
        bg = "rgba(247,178,103,0.10)" if is_heat else "#2a2926"
        border = "2px solid #F7B267" if is_heat else "1px solid rgba(255,252,242,0.06)"
        name_color = "#F7B267" if is_heat else "#FFFCF2"
        seed_bg = "#3fb950" if seed <= 6 else "#F7B267"
        return f'''
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                background:{bg};border:{border};border-radius:6px;min-width:200px;">
                <span style="background:{seed_bg};color:#1a1917;font-weight:800;
                    font-size:11px;width:20px;height:20px;border-radius:3px;
                    display:inline-flex;align-items:center;justify-content:center;
                    font-family:var(--font-data);flex-shrink:0;">{seed}</span>
                <span style="font-family:'Orbitron',sans-serif;
                    font-size:11px;letter-spacing:1px;color:{name_color};
                    font-weight:700;flex:1;white-space:nowrap;">{t["name"]}</span>
                <span style="font-family:var(--font-data);font-size:12px;
                    color:#b0ada6;font-weight:600;font-variant-numeric:tabular-nums;
                    flex-shrink:0;">{t["w"]}-{t["l"]}</span>
            </div>'''

    def _vs_label():
        return '<div style="text-align:center;font-size:10px;color:#6e6b64;letter-spacing:1px;font-family:var(--font-data);padding:2px 0;">vs</div>'

    def _tbd_row(label):
        return f'''
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                background:#201f1d;border:1px dashed rgba(255,252,242,0.08);border-radius:6px;min-width:200px;">
                <span style="font-family:'Orbitron',sans-serif;
                    font-size:11px;letter-spacing:1px;color:#6e6b64;
                    font-weight:700;">{label}</span>
            </div>'''

    def _section_label(text):
        return f'''
            <div style="font-family:'Orbitron',sans-serif;
                font-size:10px;letter-spacing:2px;color:#6e6b64;text-align:center;
                padding:8px 0 12px 0;text-transform:uppercase;">{text}</div>'''

    # First Round matchups (1v8, 4v5, 3v6, 2v7)
    first_round = f'''
        <div style="display:flex;flex-direction:column;gap:16px;">
            {_section_label("First Round")}
            <div style="display:flex;flex-direction:column;gap:4px;">
                {_team_row(1, None)}
                {_vs_label()}
                {_tbd_row("8 Seed")}
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;">
                {_team_row(4, None)}
                {_vs_label()}
                {_team_row(5, None)}
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;">
                {_team_row(3, None)}
                {_vs_label()}
                {_team_row(6, None)}
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;">
                {_team_row(2, None)}
                {_vs_label()}
                {_tbd_row("7 Seed")}
            </div>
        </div>'''

    # Play-In section
    play_in = f'''
        <div style="display:flex;flex-direction:column;gap:16px;">
            {_section_label("Play-In Tournament")}
            <div style="display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:10px;color:#F7B267;letter-spacing:1px;
                    font-family:'Orbitron',sans-serif;
                    padding-bottom:4px;">7/8 GAME → 7 SEED</div>
                {_team_row(7, None)}
                {_vs_label()}
                {_team_row(8, None)}
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:10px;color:#F7B267;letter-spacing:1px;
                    font-family:'Orbitron',sans-serif;
                    padding-bottom:4px;">9/10 GAME</div>
                {_team_row(9, None)}
                {_vs_label()}
                {_team_row(10, None)}
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:10px;color:#6e6b64;letter-spacing:1px;
                    font-family:'Orbitron',sans-serif;
                    padding-bottom:4px;">LOSER 7/8 vs WINNER 9/10 → 8 SEED</div>
                {_tbd_row("Loser 7/8")}
                {_vs_label()}
                {_tbd_row("Winner 9/10")}
            </div>
        </div>'''

    return f'''
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
        {first_round}
        {play_in}
    </div>'''


st.markdown(_strip_indent(_bracket_html(east_standings)), unsafe_allow_html=True)

st.markdown("---")

# ── Team Season Averages ──────────────────────────────────────────────────────
heat = {
    "ORtg": round(game_log["ortg"].mean(), 1),
    "DRtg": round(game_log["drtg"].mean(), 1),
    "Pace": round(game_log["pace"].mean(), 1),
    "TS%": round(game_log["ts_pct"].mean(), 3),
    "eFG%": round(game_log["efg_pct"].mean(), 3),
    "TOV%": round(game_log["tov_pct"].mean(), 1),
    "OREB%": round(game_log["oreb_pct"].mean(), 1),
    "FT Rate": round(game_log["ft_rate"].mean(), 3),
    "FG%": round(game_log["fg_pct"].mean(), 3),
    "3P%": round(game_log["fg3_pct"].mean(), 3),
    "FT%": round(game_log["ft_pct"].mean(), 3),
    "PPG": round(game_log["team_score"].mean(), 1),
    "RPG": round(game_log["reb"].mean(), 1),
    "APG": round(game_log["ast"].mean(), 1),
}

league = league_avg["league"]
east = league_avg["eastern_conference"]

league_mapped = {
    "ORtg": league["ortg"], "DRtg": league["drtg"], "Pace": league["pace"],
    "TS%": league["ts_pct"], "eFG%": league["efg_pct"], "TOV%": league["tov_pct"],
    "OREB%": league["oreb_pct"], "FT Rate": league["ft_rate"],
    "FG%": league["fg_pct"], "3P%": league["fg3_pct"], "FT%": league["ft_pct"],
    "PPG": league["ppg"], "RPG": league["rpg"], "APG": league["apg"],
}

east_mapped = {
    "ORtg": east["ortg"], "DRtg": east["drtg"], "Pace": east["pace"],
    "TS%": east["ts_pct"], "eFG%": east["efg_pct"], "TOV%": east["tov_pct"],
    "OREB%": east["oreb_pct"], "FT Rate": east["ft_rate"],
    "FG%": east["fg_pct"], "3P%": east["fg3_pct"], "FT%": east["ft_pct"],
    "PPG": east["ppg"], "RPG": east["rpg"], "APG": east["apg"],
}

metrics = ["ORtg", "DRtg", "Pace", "TS%", "eFG%", "FG%", "3P%", "FT%", "PPG", "RPG", "APG"]

st.markdown('<div class="cc-section-heading">TEAM METRICS COMPARISON</div>', unsafe_allow_html=True)
comparison_table(heat, league_mapped, east_mapped, metrics)

st.markdown("---")

# ── Radar Chart & Scatter ─────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Team Profile")
    radar_cats = ["ORtg", "eFG%", "FT Rate", "OREB%", "Pace", "AST", "DRtg"]
    # Normalize to 0-100 scale for radar
    def normalize(val, metric):
        ranges = {
            "ORtg": (105, 120), "eFG%": (0.48, 0.58), "FT Rate": (0.18, 0.32),
            "OREB%": (20, 32), "Pace": (95, 105), "AST": (22, 30), "DRtg": (105, 120),
        }
        lo, hi = ranges.get(metric, (0, 1))
        raw = heat.get(metric, game_log["ast"].mean() if metric == "AST" else 0)
        # For DRtg, lower is better — invert
        if metric == "DRtg":
            return round(100 - (raw - lo) / (hi - lo) * 100, 1)
        return round(clamp((raw - lo) / (hi - lo) * 100, 0, 100), 1)

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    radar_vals = [normalize(None, c) for c in radar_cats]
    st.plotly_chart(radar_chart(radar_cats, radar_vals, title=""), use_container_width=True)

with col2:
    st.markdown("### ORtg vs DRtg")
    # Real NBA team ratings
    league_ratings = load_league_team_ratings()
    heat_idx = league_ratings.index[league_ratings["team"] == "MIA"].tolist()[0]
    st.plotly_chart(
        scatter_plot(league_ratings, "ortg", "drtg", text_col="team", title="", highlight_idx=heat_idx),
        use_container_width=True,
    )

st.markdown("---")

# ── Category Rankings ─────────────────────────────────────────────────────────
st.markdown("### Category Rankings")
team_ranks = load_team_rankings()
rank_cats = ["PPG", "RPG", "APG", "FG%", "3P%"]
col_list = st.columns(len(rank_cats))
for col, cat in zip(col_list, rank_cats):
    with col:
        heat_val = heat[cat]
        rank_num = team_ranks[cat]["rank"]
        league_val = league_mapped[cat]
        diff = heat_val - league_val
        diff_sign = "+" if diff > 0 else ""
        diff_good = diff > 0 if cat != "TOV%" else diff < 0
        # Ordinal suffix for rank
        _r = rank_num
        _suf = "th" if 11 <= _r <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(_r % 10, "th")
        rating_card(
            rank=rank_num,
            name=cat,
            value=f"{heat_val}",
            compare=f"{_r}{_suf} in the NBA",
            compare_positive=_r <= 10,
        )

# ── Season Splits ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Season Splits")

splits = season_splits(game_log)

col_h, col_a = st.columns(2)
with col_h:
    st.markdown("**Home**")
    st.markdown(f"### {splits['home']['wins']}-{splits['home']['losses']}")
with col_a:
    st.markdown("**Away**")
    st.markdown(f"### {splits['away']['wins']}-{splits['away']['losses']}")

st.markdown("#### Monthly Breakdown")
months = list(splits["monthly"].keys())
m_wins = [splits["monthly"][m]["wins"] for m in months]
m_losses = [splits["monthly"][m]["losses"] for m in months]

fig = go.Figure()
fig.add_trace(go.Bar(name="Wins", x=months, y=m_wins, marker_color=COLORS["win_green"]))
fig.add_trace(go.Bar(name="Losses", x=months, y=m_losses, marker_color=COLORS["loss_red"]))
fig.update_layout(barmode="stack", height=300, title="", xaxis_title="", yaxis_title="Games")
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)
