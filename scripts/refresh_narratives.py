#!/usr/bin/env python3
"""
refresh_narratives.py
Collects Miami Heat narrative data from public APIs and local data files,
saves results to /home/user/workspace/data/narratives.json
"""

import csv
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = Path("/home/user/workspace/data")
OUTPUT_FILE = DATA_DIR / "narratives.json"


def ts(msg: str) -> None:
    """Print a timestamped progress message."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ─── 1. ESPN News Headlines ───────────────────────────────────────────────────
def fetch_espn_news() -> list[dict]:
    """Fetch Miami Heat news from ESPN public API."""
    url = (
        "https://site.web.api.espn.com/apis/site/v2/sports/basketball/nba/news"
        "?team=14&limit=15"
    )
    ts("Fetching ESPN news headlines…")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        ts(f"  WARNING: ESPN news fetch failed — {exc}")
        return []

    articles = data.get("articles", [])
    ts(f"  Retrieved {len(articles)} ESPN articles.")

    news = []
    for a in articles:
        # Extract image URL from first image object
        images = a.get("images", [])
        image_url = images[0].get("url", "") if images else ""

        # Extract web link
        link = a.get("links", {}).get("web", {}).get("href", "")

        news.append(
            {
                "headline": a.get("headline", ""),
                "description": a.get("description", ""),
                "published": a.get("published", ""),
                "link": link,
                "image_url": image_url,
                "type": a.get("type", ""),
                "source": "ESPN",
            }
        )
    return news


# ─── 2. Beat Writer Roster (static) ──────────────────────────────────────────
def get_beat_writers() -> list[dict]:
    """Return hardcoded list of prominent Miami Heat beat writers."""
    ts("Building beat writer roster (static)…")
    writers_raw = [
        ("Anthony Chiang",   "Anthony_Chiang",  "Miami Herald",              "Beat Writer"),
        ("Ira Winderman",    "IraHeatBeat",     "Sun Sentinel",              "Beat Writer"),
        ("Barry Jackson",    "flasportsbuzz",   "Miami Herald",              "Columnist"),
        ("Brady Hawk",       "BradyHawk305",    "Five Reasons Sports / OnSI","Writer/Analyst"),
        ("Wes Goldberg",     "wcgoldberg",      "Locked On Heat / RealGM",   "Podcast Host"),
        ("Ethan Skolnick",   "EthanJSkolnick",  "Five on the Floor",         "Podcast Host"),
        ("David Ramil",      "dramil13",        "Locked On Heat",            "Podcast Host"),
        ("Will Manso",       "WillManso",       "WPLG Local 10",             "Reporter"),
        ("Greg Sylvander",   "GregSylvander",   "Five on the Floor",         "Co-Host"),
        ("Couper Moorhead",  "CoupNBA",         "NBA.com / Heat.com",        "Writer"),
    ]
    writers = [
        {
            "name":    name,
            "handle":  f"@{handle}",
            "outlet":  outlet,
            "role":    role,
            "x_url":   f"https://x.com/{handle}",
        }
        for name, handle, outlet, role in writers_raw
    ]
    ts(f"  {len(writers)} beat writers loaded.")
    return writers


# ─── 3. Featured Tweet URLs (placeholder) ─────────────────────────────────────
def get_featured_tweet_urls() -> list:
    """Return empty list; X timeline embeds are handled by the frontend."""
    ts("Featured tweet URLs: skipping oEmbed calls (handled by frontend).")
    return []


# ─── 4. Data-Driven Facts (last 14 days) ─────────────────────────────────────
def load_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def safe_float(val, default=0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def safe_int(val, default=0) -> int:
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default


def compute_14_day_facts() -> tuple[list[dict], dict, dict]:
    """
    Generate data-driven insight objects from the last 14 days of game data.
    Returns: (facts_list, heat_record, last_14_record)
    """
    ts("Loading game log CSVs and standings…")

    team_log    = load_csv(DATA_DIR / "team_game_log.csv")
    player_log  = load_csv(DATA_DIR / "player_game_log.csv")
    season_stats = load_csv(DATA_DIR / "player_season_stats.csv")
    standings   = load_json(DATA_DIR / "east_standings.json")

    # Season averages lookup by player name
    season_avg = {r["player_name"]: r for r in season_stats}

    # Sort team log by date
    team_log.sort(key=lambda r: r["game_date"])

    # Determine cut-off: 14 days before the most recent game date in file
    most_recent_str = max(r["game_date"] for r in team_log)
    most_recent_dt  = datetime.strptime(most_recent_str, "%Y-%m-%d")
    cutoff_dt       = most_recent_dt - timedelta(days=14)
    cutoff_str      = cutoff_dt.strftime("%Y-%m-%d")

    ts(f"  Most recent game: {most_recent_str}  |  14-day cutoff: {cutoff_str}")

    recent_team   = [r for r in team_log   if r["game_date"] >= cutoff_str]
    recent_player = [r for r in player_log if r["game_date"] >= cutoff_str]

    # ── Overall Heat season record ──────────────────────────────────────────
    mia_standing = next((t for t in standings if t["team"] == "MIA"), {})
    heat_record = {
        "w": mia_standing.get("w", 0),
        "l": mia_standing.get("l", 0),
    }

    # ── Last-14-day record ──────────────────────────────────────────────────
    wins14  = sum(1 for r in recent_team if r["result"] == "W")
    losses14 = sum(1 for r in recent_team if r["result"] == "L")
    last_14_record = {"w": wins14, "l": losses14}

    ts(f"  Last 14 days: {wins14}-{losses14}  (season: {heat_record['w']}-{heat_record['l']})")

    facts: list[dict] = []

    # ── Fact 1: 14-day record ───────────────────────────────────────────────
    record_emoji = "🔥" if wins14 > losses14 else ("❄️" if losses14 > wins14 else "⚖️")
    facts.append(
        {
            "category":   "record",
            "title":      f"{wins14}-{losses14} Over the Last Two Weeks",
            "body":       (
                f"Miami has gone {wins14}-{losses14} over the past 14 days, "
                f"sitting at {heat_record['w']}-{heat_record['l']} on the season. "
                f"The Heat are the {_ordinal(mia_standing.get('seed', 0))} seed in the Eastern Conference."
            ),
            "stat_value": f"{wins14}-{losses14}",
            "icon":       record_emoji,
        }
    )

    # ── Fact 2: Current standing / seed ────────────────────────────────────
    seed  = mia_standing.get("seed", "?")
    gb    = mia_standing.get("gb", 0)
    strk  = mia_standing.get("strk", "")
    pct   = mia_standing.get("pct", 0)
    facts.append(
        {
            "category":   "standings",
            "title":      f"{_ordinal(seed)} Seed in the East",
            "body":       (
                f"Miami holds the {_ordinal(seed)} seed in the Eastern Conference "
                f"with a {heat_record['w']}-{heat_record['l']} record ({pct:.3f}), "
                f"{gb} games back of first. Current streak: {strk}."
            ),
            "stat_value": f"#{seed} seed",
            "icon":       "📊",
        }
    )

    # ── Fact 3: Win/loss streak ─────────────────────────────────────────────
    streak_type = "W" if strk.startswith("W") else "L"
    streak_num  = strk[1:] if len(strk) > 1 else "1"
    streak_word = "winning" if streak_type == "W" else "losing"
    facts.append(
        {
            "category":   "hot_streak" if streak_type == "W" else "cold_streak",
            "title":      f"On a {streak_num}-Game {streak_word.title()} Streak",
            "body":       (
                f"The Heat are currently on a {streak_num}-game {streak_word} streak. "
                + (
                    f"Miami has lost their last {streak_num} game(s) and will look to "
                    "bounce back in upcoming matchups."
                    if streak_type == "L" else
                    f"Miami has won {streak_num} consecutive game(s) and appears to be "
                    "hitting their stride heading into the final stretch of the season."
                )
            ),
            "stat_value": f"{strk} streak",
            "icon":       "🔥" if streak_type == "W" else "🧊",
        }
    )

    # ── Fact 4: Biggest win ─────────────────────────────────────────────────
    wins_list = [r for r in recent_team if r["result"] == "W"]
    if wins_list:
        biggest_win = max(
            wins_list,
            key=lambda r: safe_int(r["team_score"]) - safe_int(r["opponent_score"]),
        )
        margin = safe_int(biggest_win["team_score"]) - safe_int(biggest_win["opponent_score"])
        facts.append(
            {
                "category":   "record",
                "title":      f"+{margin}-Point Blowout vs {biggest_win['opponent']}",
                "body":       (
                    f"Miami's biggest win of the last 14 days was a {margin}-point "
                    f"blowout of {biggest_win['opponent']} on {biggest_win['game_date']} "
                    f"({biggest_win['team_score']}-{biggest_win['opponent_score']}). "
                    f"The Heat posted an offensive rating of {biggest_win['ortg']} in that game."
                ),
                "stat_value": f"+{margin}",
                "icon":       "💪",
            }
        )

    # ── Fact 5: Worst loss ──────────────────────────────────────────────────
    losses_list = [r for r in recent_team if r["result"] == "L"]
    if losses_list:
        worst_loss = max(
            losses_list,
            key=lambda r: safe_int(r["opponent_score"]) - safe_int(r["team_score"]),
        )
        deficit = safe_int(worst_loss["opponent_score"]) - safe_int(worst_loss["team_score"])
        facts.append(
            {
                "category":   "cold_streak",
                "title":      f"Tough {deficit}-Point Loss vs {worst_loss['opponent']}",
                "body":       (
                    f"Miami's worst defeat in the last 14 days was a {deficit}-point loss to "
                    f"{worst_loss['opponent']} on {worst_loss['game_date']} "
                    f"({worst_loss['team_score']}-{worst_loss['opponent_score']}). "
                    f"Miami's defensive rating ballooned to {worst_loss['drtg']} in that game."
                ),
                "stat_value": f"-{deficit}",
                "icon":       "😤",
            }
        )

    # ── Fact 6: 3-point shooting trend ─────────────────────────────────────
    season_fg3 = [safe_float(r["fg3_pct"]) for r in team_log if r["fg3_pct"]]
    season_fg3_avg = sum(season_fg3) / len(season_fg3) if season_fg3 else 0
    recent_fg3 = [safe_float(r["fg3_pct"]) for r in recent_team if r["fg3_pct"]]
    recent_fg3_avg = sum(recent_fg3) / len(recent_fg3) if recent_fg3 else 0
    fg3_delta = recent_fg3_avg - season_fg3_avg
    fg3_hot = fg3_delta >= 0
    facts.append(
        {
            "category":   "offense" if fg3_hot else "trend",
            "title":      f"3-Point Shooting Running {'Hot' if fg3_hot else 'Cold'}",
            "body":       (
                f"Miami is shooting {recent_fg3_avg:.1%} from three over the last 14 days, "
                f"{'above' if fg3_hot else 'below'} their season average of {season_fg3_avg:.1%} "
                f"(delta: {'+' if fg3_delta >= 0 else ''}{fg3_delta:.1%}). "
                + (
                    "The Heat's hot shooting has fueled their recent run."
                    if fg3_hot else
                    "Improved perimeter shooting could be key for a deeper playoff run."
                )
            ),
            "stat_value": f"{recent_fg3_avg:.1%} 3P%",
            "icon":       "🎯" if fg3_hot else "❄️",
        }
    )

    # ── Fact 7: Offensive rating trend ─────────────────────────────────────
    season_ortg = [safe_float(r["ortg"]) for r in team_log if r["ortg"]]
    season_ortg_avg = sum(season_ortg) / len(season_ortg) if season_ortg else 0
    recent_ortg = [safe_float(r["ortg"]) for r in recent_team if r["ortg"]]
    recent_ortg_avg = sum(recent_ortg) / len(recent_ortg) if recent_ortg else 0
    ortg_delta = recent_ortg_avg - season_ortg_avg

    season_drtg = [safe_float(r["drtg"]) for r in team_log if r["drtg"]]
    season_drtg_avg = sum(season_drtg) / len(season_drtg) if season_drtg else 0
    recent_drtg = [safe_float(r["drtg"]) for r in recent_team if r["drtg"]]
    recent_drtg_avg = sum(recent_drtg) / len(recent_drtg) if recent_drtg else 0
    drtg_delta = recent_drtg_avg - season_drtg_avg

    facts.append(
        {
            "category":   "offense",
            "title":      f"Offense Surging at {recent_ortg_avg:.1f} ORtg Over 14 Days",
            "body":       (
                f"Miami's offensive rating over the last 14 days is {recent_ortg_avg:.1f}, "
                f"{'up' if ortg_delta >= 0 else 'down'} {abs(ortg_delta):.1f} points "
                f"from their season average of {season_ortg_avg:.1f}. "
                f"The defensive rating sits at {recent_drtg_avg:.1f} "
                f"({'better' if drtg_delta < 0 else 'worse'} than the season avg of {season_drtg_avg:.1f})."
            ),
            "stat_value": f"{recent_ortg_avg:.1f} ORtg",
            "icon":       "📈" if ortg_delta >= 0 else "📉",
        }
    )

    # ── Fact 8: Home / Away split ───────────────────────────────────────────
    home_w = sum(1 for r in recent_team if r["home_away"] == "Home" and r["result"] == "W")
    home_l = sum(1 for r in recent_team if r["home_away"] == "Home" and r["result"] == "L")
    away_w = sum(1 for r in recent_team if r["home_away"] == "Away" and r["result"] == "W")
    away_l = sum(1 for r in recent_team if r["home_away"] == "Away" and r["result"] == "L")
    facts.append(
        {
            "category":   "trend",
            "title":      f"Home: {home_w}-{home_l} | Road: {away_w}-{away_l} (Last 14 Days)",
            "body":       (
                f"Miami has been a fortress at home, going {home_w}-{home_l} in their last "
                f"{home_w + home_l} home games. On the road they are {away_w}-{away_l} over "
                "the same stretch."
            ),
            "stat_value": f"{home_w}-{home_l} home",
            "icon":       "🏠",
        }
    )

    # ── Fact 9: Best individual defensive game ──────────────────────────────
    # Best defensive team game = lowest drtg
    if recent_team:
        best_def = min(recent_team, key=lambda r: safe_float(r["drtg"]))
        facts.append(
            {
                "category":   "defense",
                "title":      f"Elite Defense vs {best_def['opponent']}: {best_def['drtg']} DRtg",
                "body":       (
                    f"Miami's best defensive performance in the last 14 days came against "
                    f"{best_def['opponent']} on {best_def['game_date']}, holding their opponent "
                    f"to a defensive rating of {best_def['drtg']}. "
                    f"Miami won {best_def['team_score']}-{best_def['opponent_score']} in that game."
                ),
                "stat_value": f"{best_def['drtg']} DRtg",
                "icon":       "🛡️",
            }
        )

    # ── Fact 10: Top scorer in last 14 days (by avg ppg) ───────────────────
    # Group recent player games by player name
    player_pts: dict[str, list[int]] = {}
    for r in recent_player:
        name = r["player_name"]
        player_pts.setdefault(name, []).append(safe_int(r["pts"]))

    if player_pts:
        top_scorer_name = max(player_pts, key=lambda n: sum(player_pts[n]) / len(player_pts[n]))
        pts_list  = player_pts[top_scorer_name]
        avg_14    = sum(pts_list) / len(pts_list)
        seas_avg  = safe_float(season_avg.get(top_scorer_name, {}).get("ppg", 0))
        delta_pts = avg_14 - seas_avg
        facts.append(
            {
                "category":   "player_spotlight",
                "title":      f"{top_scorer_name} Averaging {avg_14:.1f} PPG Over 14 Days",
                "body":       (
                    f"{top_scorer_name} leads Miami with {avg_14:.1f} points per game over "
                    f"the last 14 days ({len(pts_list)} game{'s' if len(pts_list) != 1 else ''}), "
                    + (
                        f"{'above' if delta_pts >= 0 else 'below'} their season average of "
                        f"{seas_avg:.1f} PPG ({'+' if delta_pts >= 0 else ''}{delta_pts:.1f})."
                        if seas_avg > 0 else "leading the team in scoring."
                    )
                ),
                "stat_value": f"{avg_14:.1f} PPG",
                "icon":       "⭐",
            }
        )

    # ── Fact 11: Notable single-game performance (highest pts) ─────────────
    if recent_player:
        top_game = max(recent_player, key=lambda r: safe_int(r["pts"]))
        top_pts  = safe_int(top_game["pts"])
        top_reb  = safe_int(top_game["reb"])
        top_ast  = safe_int(top_game["ast"])
        seas_ppg = safe_float(season_avg.get(top_game["player_name"], {}).get("ppg", 0))
        facts.append(
            {
                "category":   "player_spotlight",
                "title":      f"{top_game['player_name']} Drops {top_pts} Points",
                "body":       (
                    f"{top_game['player_name']} had the standout individual performance of the "
                    f"stretch, dropping {top_pts} points, {top_reb} rebounds, and {top_ast} "
                    f"assists on {top_game['game_date']}. "
                    + (
                        f"Their season average is {seas_ppg:.1f} PPG."
                        if seas_ppg > 0 else ""
                    )
                ),
                "stat_value": f"{top_pts} PTS",
                "icon":       "💥",
            }
        )

    # ── Fact 12: Pelle Larsson breakout / emerging player ──────────────────
    # Find any player who significantly outperformed their season average
    best_delta_name = None
    best_delta_val  = 0.0
    best_delta_avg  = 0.0
    best_delta_seas = 0.0
    for name, pts_list in player_pts.items():
        if len(pts_list) < 2:
            continue  # need at least 2 games
        avg_recent = sum(pts_list) / len(pts_list)
        seas = safe_float(season_avg.get(name, {}).get("ppg", 0))
        if seas > 0:
            delta = avg_recent - seas
            if delta > best_delta_val and avg_recent >= 12:
                best_delta_val  = delta
                best_delta_name = name
                best_delta_avg  = avg_recent
                best_delta_seas = seas

    if best_delta_name and best_delta_name != top_scorer_name:
        facts.append(
            {
                "category":   "trend",
                "title":      f"{best_delta_name} Emerging as Surprise Contributor",
                "body":       (
                    f"{best_delta_name} is averaging {best_delta_avg:.1f} PPG over the last 14 days, "
                    f"a significant jump from their season average of {best_delta_seas:.1f} PPG "
                    f"(+{best_delta_val:.1f}). Their elevated play has been a key factor in Miami's "
                    "recent stretch of wins."
                ),
                "stat_value": f"+{best_delta_val:.1f} vs avg",
                "icon":       "🚀",
            }
        )

    # ── Fact 13: High-scoring game highlight ───────────────────────────────
    # Game with highest team_score
    if recent_team:
        highest_scoring = max(recent_team, key=lambda r: safe_int(r["team_score"]))
        facts.append(
            {
                "category":   "offense",
                "title":      f"Season-High Offensive Output: {highest_scoring['team_score']} Points",
                "body":       (
                    f"Miami lit up the scoreboard against {highest_scoring['opponent']} on "
                    f"{highest_scoring['game_date']}, putting up {highest_scoring['team_score']} points "
                    f"on a True Shooting percentage of {highest_scoring['ts_pct']} and an "
                    f"offensive rating of {highest_scoring['ortg']}."
                ),
                "stat_value": f"{highest_scoring['team_score']} PTS",
                "icon":       "🔥",
            }
        )

    ts(f"  Generated {len(facts)} data facts.")
    return facts, heat_record, last_14_record


# ─── Helper ───────────────────────────────────────────────────────────────────
def _ordinal(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n if n <= 20 else n % 10, "th")
    return f"{n}{suffix}"


# ─── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    ts("=== Miami Heat Narratives Refresh ===")

    news           = fetch_espn_news()
    beat_writers   = get_beat_writers()
    tweet_urls     = get_featured_tweet_urls()
    facts, heat_record, last_14_record = compute_14_day_facts()

    payload = {
        "generated_at":      datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "news":              news,
        "beat_writers":      beat_writers,
        "featured_tweet_urls": tweet_urls,
        "data_facts":        facts,
        "heat_record":       heat_record,
        "last_14_record":    last_14_record,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    ts(f"=== Done. Output saved to {OUTPUT_FILE} ===")
    ts(f"    ESPN articles : {len(news)}")
    ts(f"    Beat writers  : {len(beat_writers)}")
    ts(f"    Data facts    : {len(facts)}")
    ts(f"    Heat record   : {heat_record['w']}-{heat_record['l']}")
    ts(f"    Last 14 days  : {last_14_record['w']}-{last_14_record['l']}")


if __name__ == "__main__":
    main()
