"""Page 6 — Narratives: Live pulse feed — news, beat writer tweets, data-driven facts."""

import json
import pathlib
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from utils.data_loader import load_game_log, load_player_game_log, load_player_season_stats
from utils.calculations import last_n_record, current_streak
from components.theme import COLORS

st.markdown("# NARRATIVES")

# ── Load Narrative Data ───────────────────────────────────────────────────────
_narr_path = ROOT / "data" / "narratives.json"
try:
    with open(_narr_path) as _f:
        narr = json.load(_f)
except Exception:
    narr = {"news": [], "beat_writers": [], "data_facts": [], "featured_tweet_urls": [],
            "heat_record": {"w": 0, "l": 0}, "last_14_record": {"w": 0, "l": 0}}

# Also load raw game data for the auto-generated narrative cards
game_log = load_game_log()
player_gl = load_player_game_log()
season_stats = load_player_season_stats()

# ── Timestamps ────────────────────────────────────────────────────────────────
_gen = narr.get("generated_at", "")
try:
    _gen_dt = datetime.fromisoformat(_gen)
    _gen_str = _gen_dt.strftime("%b %d, %Y at %I:%M %p ET")
except Exception:
    _gen_str = "Unknown"

st.markdown(
    f'<p style="color:#6e6b64;font-size:11px;font-family:var(--font-data);'
    f'letter-spacing:0.3px;margin-top:-10px;">'
    f'Live pulse — last refreshed {_gen_str}</p>',
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════════════
# HELPER: strip indent so Streamlit doesn't treat HTML as code blocks
# ═════════════════════════════════════════════════════════════════════════════
def _html(raw: str):
    """Render HTML with Streamlit, stripping leading whitespace."""
    clean = "\n".join(line.lstrip() for line in raw.strip().splitlines())
    st.markdown(clean, unsafe_allow_html=True)


def section_header(title, subtitle=None):
    sub_html = ""
    if subtitle:
        sub_html = f'<span style="color:#6e6b64;font-size:11px;letter-spacing:0.5px;font-family:var(--font-data);margin-left:12px;">{subtitle}</span>'
    _html(f'<div class="cc-section-heading">{title}{sub_html}</div>')


# ═════════════════════════════════════════════════════════════════════════════
# 1. PULSE HEADER — Record + 14-Day Snapshot
# ═════════════════════════════════════════════════════════════════════════════
hr = narr.get("heat_record", {})
l14 = narr.get("last_14_record", {})

l14_color = '#3fb950' if l14.get('w',0) > l14.get('l',0) else '#F25C54' if l14.get('l',0) > l14.get('w',0) else '#FFFCF2'

_html(f"""
<div style="display:flex;gap:16px;margin:12px 0 24px 0;flex-wrap:wrap;">
<div style="background:#2a2926;border:1px solid rgba(247,178,103,0.12);border-radius:10px;padding:14px 20px;display:flex;align-items:center;gap:12px;flex:1;min-width:200px;">
<div style="font-family:var(--font-data);font-size:28px;font-weight:800;color:#FFFCF2;font-variant-numeric:tabular-nums;">{hr.get('w',0)}-{hr.get('l',0)}</div>
<div style="font-family:'Hyperspace Wide','Hyperspace',sans-serif;font-size:10px;letter-spacing:2px;color:#6e6b64;text-transform:uppercase;">Season Record</div>
</div>
<div style="background:#2a2926;border:1px solid rgba(247,178,103,0.12);border-radius:10px;padding:14px 20px;display:flex;align-items:center;gap:12px;flex:1;min-width:200px;">
<div style="font-family:var(--font-data);font-size:28px;font-weight:800;color:{l14_color};font-variant-numeric:tabular-nums;">{l14.get('w',0)}-{l14.get('l',0)}</div>
<div style="font-family:'Hyperspace Wide','Hyperspace',sans-serif;font-size:10px;letter-spacing:2px;color:#6e6b64;text-transform:uppercase;">Last 14 Days</div>
</div>
</div>
""")


# ═════════════════════════════════════════════════════════════════════════════
# 2. DATA-DRIVEN FACTS — Stat Cards Grid
# ═════════════════════════════════════════════════════════════════════════════
section_header("BY THE NUMBERS", "Last 14 days")

facts = narr.get("data_facts", [])

_cat_colors = {
    "hot_streak": "#3fb950", "cold_streak": "#F25C54", "record": "#F7B267",
    "offense": "#F4845F", "defense": "#C75146", "player_spotlight": "#F7B267",
    "trend": "#CCC5B9", "standings": "#b0ada6",
}

# Render facts in rows of 3 to avoid oversized HTML blocks
if facts:
    # Split into chunks of 3
    for i in range(0, len(facts), 3):
        chunk = facts[i:i+3]
        cards = ""
        for f in chunk:
            accent = _cat_colors.get(f.get("category", ""), "#F7B267")
            icon = f.get("icon", "")
            title = f.get("title", "")
            body = f.get("body", "")
            cat = f.get("category", "").replace("_", " ").upper()

            cards += (
                f'<div style="background:#2a2926;border:1px solid rgba(255,252,242,0.06);'
                f'border-top:3px solid {accent};border-radius:10px;padding:16px 18px;'
                f'min-width:280px;flex:1 1 300px;max-width:400px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
                f'<span style="font-size:20px;">{icon}</span>'
                f'<span style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:9px;'
                f'letter-spacing:1.5px;color:{accent};opacity:0.7;">{cat}</span>'
                f'</div>'
                f'<div style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:13px;'
                f'letter-spacing:1px;color:#FFFCF2;margin-bottom:6px;">{title}</div>'
                f'<div style="font-family:var(--font-data);font-size:13px;color:#b0ada6;line-height:1.5;">'
                f'{body}</div></div>'
            )

        _html(f'<div style="display:flex;flex-wrap:wrap;gap:14px;margin-bottom:14px;">{cards}</div>')


st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 3. LATEST NEWS — ESPN Headlines (2-column: featured left, list right)
# ═════════════════════════════════════════════════════════════════════════════
section_header("LATEST NEWS", "via ESPN")

news = narr.get("news", [])
if news:
    # Split: featured article (first with image) vs rest
    featured = None
    rest = []
    for n in news:
        if not featured and n.get("image_url"):
            featured = n
        else:
            rest.append(n)

    col_feat, col_list = st.columns([5, 4])

    # ── Left column: Featured Story Card ─────────────────────────────────
    with col_feat:
        if featured:
            pub = featured.get("published", "")[:10]
            try:
                pub_dt = datetime.fromisoformat(pub)
                pub_str = pub_dt.strftime("%b %d")
            except Exception:
                pub_str = pub

            _html(
                f'<a href="{featured.get("link", "#")}" target="_blank" style="text-decoration:none;">'
                f'<div style="background:#2a2926;border:1px solid rgba(255,252,242,0.06);border-radius:12px;'
                f'overflow:hidden;height:100%;">'
                f'<div style="width:100%;aspect-ratio:16/9;overflow:hidden;">'
                f'<img src="{featured.get("image_url","")}" style="width:100%;height:100%;object-fit:cover;display:block;"'
                f' onerror="this.parentElement.style.display=\'none\'" /></div>'
                f'<div style="padding:16px 20px;">'
                f'<div style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:9px;'
                f'letter-spacing:2px;color:#F7B267;margin-bottom:8px;">{featured.get("source","ESPN")} &middot; {pub_str}</div>'
                f'<div style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:15px;'
                f'letter-spacing:0.5px;color:#FFFCF2;line-height:1.4;margin-bottom:10px;">{featured.get("headline","")}</div>'
                f'<div style="font-family:var(--font-data);font-size:13px;color:#b0ada6;line-height:1.5;">'
                f'{featured.get("description","")[:220]}</div></div></div></a>'
            )

    # ── Right column: Headline List ──────────────────────────────────────
    with col_list:
        if rest:
            items = ""
            for n in rest[:7]:
                pub = n.get("published", "")[:10]
                try:
                    pub_dt = datetime.fromisoformat(pub)
                    pub_str = pub_dt.strftime("%b %d")
                except Exception:
                    pub_str = pub
                link = n.get("link", "#")
                headline = n.get("headline", "")
                ntype = n.get("type", "").upper()
                type_color = "#F25C54" if ntype == "RECAP" else "#F7B267" if ntype == "STORY" else "#CCC5B9"

                items += (
                    f'<a href="{link}" target="_blank" style="text-decoration:none;display:block;">'
                    f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;'
                    f'border-bottom:1px solid rgba(255,252,242,0.04);transition:background 0.15s;">'
                    f'<div style="flex-shrink:0;min-width:44px;">'
                    f'<span style="font-family:var(--font-data);font-size:10px;color:#6e6b64;">{pub_str}</span><br>'
                    f'<span style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:8px;'
                    f'letter-spacing:1px;color:{type_color};">{ntype}</span></div>'
                    f'<div style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:12px;'
                    f'letter-spacing:0.3px;color:#FFFCF2;line-height:1.35;">{headline}</div>'
                    f'</div></a>'
                )

            _html(
                f'<div style="background:#2a2926;border:1px solid rgba(255,252,242,0.06);'
                f'border-radius:12px;overflow:hidden;">{items}</div>'
            )
else:
    st.markdown('<p style="color:#6e6b64;">No recent news available.</p>', unsafe_allow_html=True)


st.markdown("---")

# ═════════════════════════════════════════════════════════════════════════════
# 4. BEAT WRITER TRACKER — X Feeds
# ═════════════════════════════════════════════════════════════════════════════
section_header("BEAT WRITER TRACKER", "Live from X")

writers = narr.get("beat_writers", [])

if writers:
    # Render writer cards in rows of 5
    for i in range(0, len(writers), 5):
        chunk = writers[i:i+5]
        cards = ""
        for w in chunk:
            name = w.get("name", "")
            handle = w.get("handle", "")
            outlet = w.get("outlet", "")
            role = w.get("role", "")
            x_url = w.get("x_url", f"https://x.com/{handle.replace('@','')}")

            cards += (
                f'<a href="{x_url}" target="_blank" style="text-decoration:none;">'
                f'<div style="background:#2a2926;border:1px solid rgba(255,252,242,0.06);border-radius:10px;'
                f'padding:12px 16px;display:flex;align-items:center;gap:12px;min-width:220px;flex:1 1 220px;">'
                f'<div style="width:36px;height:36px;border-radius:50%;background:#353432;'
                f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
                f'<svg width="16" height="16" viewBox="0 0 24 24" fill="#b0ada6">'
                f'<path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>'
                f'</svg></div>'
                f'<div>'
                f'<div style="font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:11px;'
                f'letter-spacing:0.5px;color:#FFFCF2;">{name}</div>'
                f'<div style="font-family:var(--font-data);font-size:11px;color:#F7B267;">{handle}</div>'
                f'<div style="font-family:var(--font-data);font-size:10px;color:#6e6b64;margin-top:2px;">'
                f'{outlet} &middot; {role}</div></div></div></a>'
            )

        _html(f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px;">{cards}</div>')


st.markdown('---')

# ═════════════════════════════════════════════════════════════════════════════
# 5. AUTO-GENERATED NARRATIVE CARDS (from raw data)
# ═════════════════════════════════════════════════════════════════════════════
section_header("HEAT CHECK", "Auto-generated analysis")


def narrative_card(title: str, body: str, accent_color: str = COLORS["accent_primary"]):
    _html(
        f'<div style="background:#2a2926;border:1px solid rgba(255,252,242,0.06);'
        f'border-left:3px solid {accent_color};border-radius:12px;padding:20px 24px;margin-bottom:16px;">'
        f'<h3 style="color:#F7B267;margin:0 0 12px 0;border:none !important;padding:0 !important;'
        f'font-family:\'Hyperspace Wide\',\'Hyperspace\',sans-serif;font-size:14px;'
        f'letter-spacing:2px;text-transform:uppercase;">{title}</h3>'
        f'<div style="color:#FFFCF2;line-height:1.7;font-size:0.95rem;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',system-ui,sans-serif;">{body}</div></div>'
    )


# Recent Form
recent = game_log.tail(10).copy()
r_w, r_l = last_n_record(game_log, 10)
s_type, s_count = current_streak(game_log)
recent_ortg = round(recent["ortg"].mean(), 1)
recent_drtg = round(recent["drtg"].mean(), 1)
recent_net = round(recent_ortg - recent_drtg, 1)
recent_ppg = round(recent["team_score"].mean(), 1)

streak_text = f"on a {s_count}-game {'winning' if s_type == 'W' else 'losing'} streak" if s_count >= 2 else ""
form_text = "strong form" if r_w >= 7 else "solid form" if r_w >= 5 else "mixed results" if r_w >= 4 else "struggling"

body = (
    f"The Heat are <b>{r_w}-{r_l}</b> over their last 10 games, showing <b>{form_text}</b>"
    + (f' and are currently <b>{streak_text}</b>' if streak_text else '')
    + f". They're averaging <b>{recent_ppg} points per game</b> in this stretch with an offensive rating of "
    f"<b>{recent_ortg}</b> and defensive rating of <b>{recent_drtg}</b> (net: <b>{recent_net:+.1f}</b>)."
)
narrative_card("Recent Form", body)

# Key Performers
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

hottest = player_avgs.iloc[0] if not player_avgs.empty else None
if hottest is not None:
    season_ppg = season_stats[season_stats["player_name"] == hottest.player_name]["ppg"].values
    if len(season_ppg) > 0 and hottest.pts > season_ppg[0] * 1.1:
        body += f"<br><br>{hottest.player_name} has been particularly hot, averaging <b>{hottest.pts:.1f} PPG</b> \u2014 well above their season average of {season_ppg[0]:.1f}."

narrative_card("Key Performers", body, COLORS["yellow_flame"])

# Offensive & Defensive Trends
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

body = (
    f"<b>Offense:</b> The Heat's season offensive rating is <b>{full_ortg}</b>. The offense has <b>{o_trend}</b> "
    f"from the first half ({h1_ortg}) to the second half ({h2_ortg}).<br><br>"
    f"<b>Defense:</b> The defensive rating sits at <b>{full_drtg}</b> for the season. The defense has <b>{d_trend}</b> "
    f"from {h1_drtg} (first half) to {h2_drtg} (second half).<br><br>"
    f"The team's four factors show an eFG% of <b>{game_log['efg_pct'].mean():.1%}</b> and a turnover rate of "
    f"<b>{game_log['tov_pct'].mean():.1f}%</b> \u2014 {'solid ball security' if game_log['tov_pct'].mean() < 13.5 else 'an area to watch'}."
)
narrative_card("Offensive & Defensive Trends", body, COLORS["warm_coral"])

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
_html(
    f'<div class="cc-footer">'
    f'Narratives auto-generated from live data &amp; ESPN &nbsp;|&nbsp; '
    f'Updated through {game_log["game_date"].max().strftime("%B %d, %Y")}</div>'
)
