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
st.markdown('<p style="color:#b0ada6; letter-spacing:0.5px;">End-of-season analysis of the 2025-26 Miami Heat campaign.</p>', unsafe_allow_html=True)

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


# ══════════════════════════════════════════════════════════════════════════════
# HEAT CHECK: SEASON IN REVIEW
# ══════════════════════════════════════════════════════════════════════════════

# Compute full-season stats
total_games = len(game_log)
reg_season = game_log[game_log["game_id"] != "espn_401866755"].copy()
full_wins = int((reg_season["result"] == "W").sum())
full_losses = int((reg_season["result"] == "L").sum())
home_games = reg_season[reg_season["home_away"].str.contains("Home")]
away_games = reg_season[reg_season["home_away"].str.contains("Away")]
home_w = int((home_games["result"] == "W").sum())
home_l = int((home_games["result"] == "L").sum())
away_w = int((away_games["result"] == "W").sum())
away_l = int((away_games["result"] == "L").sum())
season_ppg = round(reg_season["team_score"].mean(), 1)
season_opp_ppg = round(reg_season["opponent_score"].mean(), 1)
season_ortg = round(reg_season["ortg"].mean(), 1)
season_drtg = round(reg_season["drtg"].mean(), 1)
season_net = round(season_ortg - season_drtg, 1)

# Top scorer
top_player = season_stats.iloc[0] if len(season_stats) > 0 else None
top_name = top_player["player_name"] if top_player is not None else "N/A"
top_ppg = top_player["ppg"] if top_player is not None else 0

# ── Heat Check: The Big Picture ─────────────────────────────────────────────
st.markdown(
    '<h2 style="color:#F7B267; font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif; '
    'font-size:20px; letter-spacing:3px; text-transform:uppercase; margin:20px 0 16px;">'
    'Heat Check: Season in Review</h2>',
    unsafe_allow_html=True,
)

body = f"""
The 2025-26 Miami Heat season ended with a <b>{full_wins}-{full_losses}</b> record and a gutting
<b>126-127 overtime loss to the Charlotte Hornets</b> in the play-in tournament, marking the franchise's
earliest postseason exit in seven years. It was a season defined by flashes of brilliance, persistent
injury setbacks, and the creeping sense that this roster, as constructed, has reached its ceiling.
<br><br>
Miami improved by six wins over the prior season, was <b>2nd in the NBA in scoring at {season_ppg} PPG</b>,
and posted a <b>{season_net:+.1f} net rating</b> ({season_ortg} ORtg / {season_drtg} DRtg). But the gap
between the Heat and the Eastern Conference elite was never more apparent \u2014 the team went <b>0-13 against
Toronto, Boston, and Orlando</b>, a damning stat that underscored their inability to compete with the
top tier.
"""
narrative_card("The Big Picture", body, COLORS["rich_red"])

# ── Bam Adebayo ─────────────────────────────────────────────────────────────
bam = season_stats[season_stats["player_name"] == "Bam Adebayo"]
bam_ppg = float(bam["ppg"].values[0]) if len(bam) > 0 else 0
bam_rpg = float(bam["rpg"].values[0]) if len(bam) > 0 else 0
bam_apg = float(bam["apg"].values[0]) if len(bam) > 0 else 0
bam_games = int(bam["games"].values[0]) if len(bam) > 0 else 0

body = f"""
<b>Bam Adebayo</b> anchored the season with <b>{bam_ppg} PPG, {bam_rpg} RPG, {bam_apg} APG</b> across
{bam_games} games, earning yet another All-Defensive caliber campaign. The defining moment: his
<b>historic 83-point eruption on March 10 against Washington</b> \u2014 a performance that made him
just the fourth player in NBA history to reach that threshold and the first Heat player since
LeBron James to have a scoring night of that magnitude.
<br><br>
But the season ended on a bitter note. In the play-in game at Charlotte, <b>LaMelo Ball tripped
Adebayo</b> early in the second quarter, causing a back injury that forced him out. The NBA fined
Ball $35,000 for the reckless contact but didn't suspend him \u2014 a decision that left Heat Nation
fuming as their best player watched the final three quarters from the locker room.
"""
narrative_card("Bam Adebayo: MVP-Level, Unlucky Ending", body, COLORS["yellow_flame"])

# ── Tyler Herro & Injuries ──────────────────────────────────────────────────
herro = season_stats[season_stats["player_name"] == "Tyler Herro"]
herro_ppg = float(herro["ppg"].values[0]) if len(herro) > 0 else 0
herro_games = int(herro["games"].values[0]) if len(herro) > 0 else 0
herro_missed = total_games - herro_games

body = f"""
The <b>Tyler Herro question</b> loomed over the season from start to finish. After offseason ankle
surgery, he missed the first 17 games, then a nagging right toe injury cost him more time.
He played just <b>{herro_games} of {total_games} games</b> ({herro_missed} missed), averaging
<b>{herro_ppg} PPG</b> when available \u2014 efficient, but far short of the volume that earned
him an All-Star nod last season (23.9 PPG).
<br><br>
With <b>$33M on his deal next year</b> and extension eligibility this summer, Herro's future in
Miami is the franchise's most pressing decision. Can you build around a max-level guard who
has yet to stay healthy for a full season?
"""
narrative_card("Tyler Herro: The Availability Problem", body, COLORS["warm_coral"])

# ── Breakout Performers ─────────────────────────────────────────────────────
jjj = season_stats[season_stats["player_name"] == "Jaime Jaquez Jr."]
jjj_ppg = float(jjj["ppg"].values[0]) if len(jjj) > 0 else 0
jjj_apg = float(jjj["apg"].values[0]) if len(jjj) > 0 else 0
larsson = season_stats[season_stats["player_name"] == "Pelle Larsson"]
larsson_ppg = float(larsson["ppg"].values[0]) if len(larsson) > 0 else 0
ware = season_stats[season_stats["player_name"] == "Kel'el Ware"]
ware_ppg = float(ware["ppg"].values[0]) if len(ware) > 0 else 0
ware_rpg = float(ware["rpg"].values[0]) if len(ware) > 0 else 0

body = f"""
<b>Jaime Jaquez Jr.</b> authored the best bounce-back story on the roster, averaging
<b>{jjj_ppg} PPG and {jjj_apg} APG</b> while shooting <b>41.8% from three over his final
18 games</b> \u2014 a dramatic leap from 30.2% over his first 197 career games. If he carries
that shooting into Year 4, his extension-eligible contract becomes a bargain.
<br><br>
<b>Pelle Larsson</b> ({larsson_ppg} PPG) went from second-round afterthought to legitimate
starting candidate with his defensive tenacity and offensive aggression.
<b>Kel'el Ware</b> ({ware_ppg} PPG, {ware_rpg} RPG) flashed elite upside in his second year
as Bam's frontcourt partner.
<b>Kasparas Jakucionis</b>, the rookie point guard, surprised with immediate NBA-level
playmaking \u2014 positioning himself as the long-term answer at the one.
"""
narrative_card("Breakout Performers", body, "#3fb950")

# ── Offseason Crossroads ────────────────────────────────────────────────────
body = """
The front office faces a <b>pivotal offseason</b> with several critical decisions:<br><br>
\u2022 <b>Andrew Wiggins</b> holds a <b>$30.2M player option</b> for 2026-27. If he opts out,
Miami opens significant cap space.<br>
\u2022 <b>Norman Powell</b> enters unrestricted free agency after a first-time All-Star campaign
(21.7 PPG midseason). Retaining him at a reasonable number is far from guaranteed.<br>
\u2022 <b>Tyler Herro's extension eligibility</b> forces a franchise-defining conversation
about committing $200M+ to a player who has missed 100+ games over the last three seasons.<br>
\u2022 <b>Nikola Jovic's $16.2M salary</b> kicks in next year on a four-year deal \u2014 concerning
given his regression and the coaching staff's eroding trust.<br>
\u2022 The <b>trade deadline inactivity</b> \u2014 another failed Giannis pursuit and no fallback plan \u2014
has drawn sharp criticism from fans and media alike.<br><br>
The Heat's 2027 first-round pick is top-14 protected (owed to Charlotte if 15-30), adding
urgency to improving quickly. Pat Riley and Erik Spoelstra must decide: double down on
incremental improvement, or pursue the seismic roster shakeup this team may need to
re-enter contention.
"""
narrative_card("Offseason Crossroads", body, COLORS["dark_red"])

st.markdown("---")

# ── Auto-generated Narratives ───────────────────────────────────────────────
st.markdown(
    '<h2 style="color:#F7B267; font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif; '
    'font-size:16px; letter-spacing:2px; text-transform:uppercase; margin:20px 0 12px;">'
    'By The Numbers</h2>',
    unsafe_allow_html=True,
)

# ── 1. Season Snapshot ──────────────────────────────────────────────────────
recent = game_log.tail(10).copy()
r_w, r_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
recent_ortg = round(recent["ortg"].mean(), 1)
recent_drtg = round(recent["drtg"].mean(), 1)
recent_net = round(recent_ortg - recent_drtg, 1)
recent_ppg = round(recent["team_score"].mean(), 1)

body = f"""
The Heat finished <b>{r_w}-{r_l}</b> over their final 10 games, averaging <b>{recent_ppg} PPG</b>
with an offensive rating of <b>{recent_ortg}</b> and defensive rating of <b>{recent_drtg}</b>
(net: <b>{recent_net:+.1f}</b>). Home record: <b>{home_w}-{home_l}</b>. Road record: <b>{away_w}-{away_l}</b>.
"""
narrative_card("Final Stretch", body)

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

# ── 4. Season Summary ───────────────────────────────────────────────────────
first_half = game_log.head(len(game_log) // 2)
second_half_for_split = game_log.tail(len(game_log) // 2)
h1w = int((first_half["result"] == "W").sum())
h1l = len(first_half) - h1w
h2w = int((second_half_for_split["result"] == "W").sum())
h2l = len(second_half_for_split) - h2w

# Best/worst months
import pandas as pd
game_log_copy = game_log.copy()
game_log_copy["month"] = pd.to_datetime(game_log_copy["game_date"]).dt.strftime("%B %Y")
monthly = game_log_copy.groupby("month").agg(
    wins=("result", lambda x: (x == "W").sum()),
    games=("result", "count")
).reset_index()
monthly["pct"] = monthly["wins"] / monthly["games"]
best_month = monthly.loc[monthly["pct"].idxmax()]
worst_month = monthly.loc[monthly["pct"].idxmin()]

body = f"""
<b>First half:</b> {h1w}-{h1l} &nbsp;|&nbsp; <b>Second half:</b> {h2w}-{h2l}<br>
<b>Best month:</b> {best_month['month']} ({int(best_month['wins'])}-{int(best_month['games'] - best_month['wins'])})<br>
<b>Worst month:</b> {worst_month['month']} ({int(worst_month['wins'])}-{int(worst_month['games'] - worst_month['wins'])})<br><br>
The 2025-26 season is in the books. The offseason begins now.
"""
narrative_card("Season Split", body, COLORS["dark_red"])

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
