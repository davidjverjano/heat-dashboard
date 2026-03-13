#!/usr/bin/env python3
"""Generate realistic 2024-25 Miami Heat sample data."""

import json
import random
import csv
import math
from datetime import datetime, timedelta

random.seed(42)

# ── Roster with realistic stat profiles ──────────────────────────────────────
# (player_name, player_id, avg_min, ppg, rpg, apg, spg, bpg, fg_pct, fg3_pct, ft_pct, usage_pct)
ROSTER = [
    ("Tyler Herro",         201, 34.5, 23.8, 5.5, 5.2, 0.9, 0.3, 0.462, 0.395, 0.870, 28.5),
    ("Bam Adebayo",         202, 34.0, 17.5, 10.2, 4.8, 1.2, 0.9, 0.520, 0.150, 0.780, 24.0),
    ("Jimmy Butler",        203, 30.0, 17.0, 5.5, 4.8, 1.3, 0.4, 0.495, 0.350, 0.850, 25.0),
    ("Terry Rozier",        204, 32.0, 15.5, 4.0, 4.5, 0.9, 0.3, 0.430, 0.360, 0.880, 22.0),
    ("Jaime Jaquez Jr.",    205, 30.5, 12.0, 5.0, 2.5, 0.8, 0.4, 0.470, 0.320, 0.810, 17.5),
    ("Duncan Robinson",     206, 26.0, 10.5, 3.2, 2.0, 0.5, 0.2, 0.435, 0.390, 0.900, 14.0),
    ("Nikola Jovic",        207, 22.0,  9.5, 4.5, 2.2, 0.5, 0.5, 0.450, 0.360, 0.780, 14.5),
    ("Haywood Highsmith",   208, 24.0,  7.0, 4.0, 1.2, 0.8, 0.6, 0.430, 0.340, 0.750, 10.0),
    ("Kevin Love",          209, 18.0,  7.5, 5.5, 1.8, 0.4, 0.3, 0.440, 0.370, 0.850, 12.5),
    ("Thomas Bryant",       210, 16.0,  6.0, 4.5, 0.8, 0.3, 0.5, 0.550, 0.200, 0.700, 11.0),
    ("Josh Richardson",     211, 20.0,  5.5, 2.8, 1.5, 0.7, 0.3, 0.410, 0.330, 0.800, 10.5),
    ("Caleb Martin",        212, 22.0,  6.5, 3.5, 1.5, 0.9, 0.4, 0.420, 0.330, 0.790, 11.5),
    ("Pelle Larsson",       213, 14.0,  4.0, 2.0, 1.5, 0.5, 0.1, 0.420, 0.350, 0.800,  8.0),
    ("Kel'el Ware",         214, 12.0,  4.5, 3.5, 0.5, 0.2, 0.8, 0.540, 0.280, 0.680, 10.0),
]

NBA_TEAMS = [
    ("Boston Celtics", "BOS"), ("New York Knicks", "NYK"), ("Milwaukee Bucks", "MIL"),
    ("Cleveland Cavaliers", "CLE"), ("Orlando Magic", "ORL"), ("Indiana Pacers", "IND"),
    ("Philadelphia 76ers", "PHI"), ("Brooklyn Nets", "BKN"), ("Chicago Bulls", "CHI"),
    ("Atlanta Hawks", "ATL"), ("Toronto Raptors", "TOR"), ("Detroit Pistons", "DET"),
    ("Charlotte Hornets", "CHA"), ("Washington Wizards", "WAS"),
    ("Oklahoma City Thunder", "OKC"), ("Denver Nuggets", "DEN"),
    ("Minnesota Timberwolves", "MIN"), ("LA Clippers", "LAC"),
    ("Dallas Mavericks", "DAL"), ("Phoenix Suns", "PHX"), ("Sacramento Kings", "SAC"),
    ("New Orleans Pelicans", "NOP"), ("Los Angeles Lakers", "LAL"),
    ("Golden State Warriors", "GSW"), ("Houston Rockets", "HOU"),
    ("Memphis Grizzlies", "MEM"), ("Utah Jazz", "UTA"), ("San Antonio Spurs", "SAS"),
    ("Portland Trail Blazers", "POR"),
]

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def gen_game_date(idx, start_date):
    """Generate game dates ~every 1.5 days with some gaps."""
    gap = random.choice([1, 1, 2, 2, 2, 3])
    return start_date + timedelta(days=idx * 2 + random.randint(-1, 1))

def generate():
    start_date = datetime(2024, 10, 23)
    num_games = 58

    # Build game schedule
    games = []
    current_date = start_date
    for i in range(num_games):
        gap = random.choice([1, 2, 2, 2, 3, 3])
        current_date += timedelta(days=gap)
        opponent = random.choice(NBA_TEAMS)
        home_away = random.choice(["Home", "Away"])
        games.append({
            "game_id": 22400100 + i,
            "game_date": current_date.strftime("%Y-%m-%d"),
            "home_away": home_away,
            "opponent": opponent[0],
            "opponent_abbr": opponent[1],
        })

    # Determine W/L with streaks built in
    # Create a pattern: some winning stretches, some losing
    win_probs = []
    for i in range(num_games):
        # Base ~55% win rate, with hot/cold stretches
        base = 0.55
        # Hot streak around games 10-18
        if 10 <= i <= 18:
            base = 0.75
        # Cold stretch around games 30-38
        elif 30 <= i <= 38:
            base = 0.35
        # Strong finish
        elif i >= 48:
            base = 0.70
        win_probs.append(base)

    team_game_log = []
    player_game_log = []
    total_wins = 0
    total_losses = 0

    for gi, game in enumerate(games):
        is_win = random.random() < win_probs[gi]
        result = "W" if is_win else "L"
        if is_win:
            total_wins += 1
        else:
            total_losses += 1

        # Generate team stats
        team_score = random.randint(98, 125)
        if is_win:
            margin = random.randint(1, 22)
            opponent_score = team_score - margin
        else:
            margin = random.randint(1, 18)
            opponent_score = team_score + margin

        # Advanced team stats
        pace = round(random.gauss(99.5, 3.0), 1)
        ortg = round(team_score / pace * 100 + random.gauss(0, 2), 1)
        drtg = round(opponent_score / pace * 100 + random.gauss(0, 2), 1)
        fg_pct = round(random.gauss(0.465, 0.035), 3)
        fg3_pct = round(random.gauss(0.360, 0.050), 3)
        ft_pct = round(random.gauss(0.790, 0.040), 3)
        oreb = random.randint(6, 14)
        dreb = random.randint(28, 40)
        reb = oreb + dreb
        ast = random.randint(20, 32)
        stl = random.randint(4, 12)
        blk = random.randint(2, 8)
        tov = random.randint(10, 20)
        pf = random.randint(15, 26)
        ts_pct = round(clamp(fg_pct + random.gauss(0.10, 0.02), 0.48, 0.64), 3)
        efg_pct = round(clamp(fg_pct + random.gauss(0.04, 0.02), 0.44, 0.60), 3)
        tov_pct = round(random.gauss(13.5, 2.0), 1)
        oreb_pct = round(random.gauss(26.0, 4.0), 1)
        ft_rate = round(random.gauss(0.250, 0.050), 3)
        opp_efg_pct = round(random.gauss(0.52, 0.03), 3)
        opp_tov_pct = round(random.gauss(13.0, 2.0), 1)
        opp_oreb_pct = round(random.gauss(25.0, 4.0), 1)
        opp_ft_rate = round(random.gauss(0.240, 0.050), 3)

        team_game_log.append({
            "game_id": game["game_id"],
            "game_date": game["game_date"],
            "home_away": game["home_away"],
            "opponent": game["opponent"],
            "opponent_abbr": game["opponent_abbr"],
            "result": result,
            "team_score": team_score,
            "opponent_score": opponent_score,
            "fg_pct": clamp(fg_pct, 0.350, 0.580),
            "fg3_pct": clamp(fg3_pct, 0.200, 0.500),
            "ft_pct": clamp(ft_pct, 0.650, 0.920),
            "oreb": oreb,
            "dreb": dreb,
            "reb": reb,
            "ast": ast,
            "stl": stl,
            "blk": blk,
            "tov": tov,
            "pf": pf,
            "plus_minus": team_score - opponent_score,
            "ortg": clamp(ortg, 95.0, 130.0),
            "drtg": clamp(drtg, 95.0, 125.0),
            "pace": pace,
            "ts_pct": clamp(ts_pct, 0.480, 0.640),
            "efg_pct": clamp(efg_pct, 0.420, 0.600),
            "tov_pct": clamp(tov_pct, 8.0, 20.0),
            "oreb_pct": clamp(oreb_pct, 15.0, 38.0),
            "ft_rate": clamp(ft_rate, 0.140, 0.400),
            "opp_efg_pct": clamp(opp_efg_pct, 0.400, 0.600),
            "opp_tov_pct": clamp(opp_tov_pct, 8.0, 20.0),
            "opp_oreb_pct": clamp(opp_oreb_pct, 15.0, 38.0),
            "opp_ft_rate": clamp(opp_ft_rate, 0.140, 0.400),
        })

        # Generate player stats for this game
        # Jimmy Butler only plays first ~35 games (before trade deadline)
        active_roster = []
        for p in ROSTER:
            if p[0] == "Jimmy Butler" and gi >= 35:
                continue
            active_roster.append(p)

        total_team_pts = 0
        game_players = []
        for pi, (name, pid, avg_min, ppg, rpg, apg, spg, bpg, fg_p, fg3_p, ft_p, usg) in enumerate(active_roster):
            # Random variation per game
            min_var = random.gauss(0, 4)
            minutes = round(clamp(avg_min + min_var, 5 if pi < 8 else 0, 42))
            if pi >= 10 and random.random() < 0.3:
                # DNP for deep bench sometimes
                continue

            min_factor = minutes / avg_min if avg_min > 0 else 0.5
            hot_cold = random.gauss(1.0, 0.25)  # performance variance

            pts_raw = ppg * min_factor * hot_cold
            pts = round(clamp(pts_raw + random.gauss(0, 3), 0, 50))
            total_team_pts += pts

            # Shooting: work backwards from points
            ft = random.randint(0, max(1, round(pts * 0.15)))
            fta = ft + random.randint(0, 3)
            remaining_pts = max(0, pts - ft)
            fg3 = random.randint(0, min(round(remaining_pts / 3), round(minutes * 0.25)))
            fg3a = fg3 + random.randint(0, max(1, round(fg3 * 0.8)))
            fg2_pts = max(0, remaining_pts - fg3 * 3)
            fg2 = round(fg2_pts / 2)
            fg = fg2 + fg3
            fga = fg + random.randint(0, max(1, round(fg * 0.6)))
            if fga == 0:
                fga = random.randint(1, 4)
            fg_pct_g = round(fg / fga, 3) if fga > 0 else 0.0
            fg3_pct_g = round(fg3 / fg3a, 3) if fg3a > 0 else 0.0
            ft_pct_g = round(ft / fta, 3) if fta > 0 else 0.0

            reb_var = random.gauss(0, 1.5)
            r_oreb = random.randint(0, 3)
            r_dreb = round(clamp(rpg * min_factor + reb_var - r_oreb, 0, 18))
            r_reb = r_oreb + r_dreb
            r_ast = round(clamp(apg * min_factor * hot_cold + random.gauss(0, 1), 0, 16))
            r_stl = round(clamp(spg * min_factor + random.gauss(0, 0.5), 0, 5))
            r_blk = round(clamp(bpg * min_factor + random.gauss(0, 0.4), 0, 5))
            r_tov = random.randint(0, max(1, round(minutes / 8)))
            r_pf = random.randint(0, 5)
            r_pm = team_game_log[-1]["plus_minus"] + random.randint(-10, 10)
            r_pm = clamp(r_pm, -30, 30)

            usage_g = round(clamp(usg + random.gauss(0, 3), 5, 40), 1)
            ts_g = round(clamp(pts / (2 * (fga + 0.44 * fta)) if (fga + 0.44 * fta) > 0 else 0.5, 0.30, 0.80), 3)
            ortg_g = round(clamp(random.gauss(110, 10), 80, 140), 1)
            drtg_g = round(clamp(random.gauss(112, 10), 85, 135), 1)
            game_score = round(pts + 0.4*fg - 0.7*fga - 0.4*(fta-ft) + 0.7*r_oreb + 0.3*r_dreb + r_stl + 0.7*r_ast + 0.7*r_blk - 0.4*r_pf - r_tov, 1)

            game_players.append({
                "game_id": game["game_id"],
                "game_date": game["game_date"],
                "player_name": name,
                "player_id": pid,
                "minutes": minutes,
                "pts": pts,
                "fg": fg,
                "fga": fga,
                "fg_pct": fg_pct_g,
                "fg3": fg3,
                "fg3a": fg3a,
                "fg3_pct": fg3_pct_g,
                "ft": ft,
                "fta": fta,
                "ft_pct": ft_pct_g,
                "oreb": r_oreb,
                "dreb": r_dreb,
                "reb": r_reb,
                "ast": r_ast,
                "stl": r_stl,
                "blk": r_blk,
                "tov": r_tov,
                "pf": r_pf,
                "plus_minus": r_pm,
                "usage_pct": usage_g,
                "ts_pct": ts_g,
                "ortg": ortg_g,
                "drtg": drtg_g,
                "game_score": game_score,
            })
        player_game_log.extend(game_players)

    # ── Write team_game_log.csv ───────────────────────────────────────────────
    with open("data/team_game_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(team_game_log[0].keys()))
        writer.writeheader()
        writer.writerows(team_game_log)

    # ── Write player_game_log.csv ─────────────────────────────────────────────
    with open("data/player_game_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(player_game_log[0].keys()))
        writer.writeheader()
        writer.writerows(player_game_log)

    # ── Generate player_season_stats.csv ──────────────────────────────────────
    import collections
    player_accum = collections.defaultdict(lambda: {"gp": 0, "minutes": [], "pts": [], "reb": [], "ast": [],
                                                      "stl": [], "blk": [], "tov": [], "fg_pct": [], "fg3_pct": [],
                                                      "ft_pct": [], "ts_pct": [], "usage_pct": [], "ortg": [],
                                                      "drtg": [], "plus_minus": [], "game_score": []})
    for pg in player_game_log:
        name = pg["player_name"]
        pid = pg["player_id"]
        acc = player_accum[(name, pid)]
        acc["gp"] += 1
        for k in ["minutes", "pts", "reb", "ast", "stl", "blk", "tov", "fg_pct", "fg3_pct",
                   "ft_pct", "ts_pct", "usage_pct", "ortg", "drtg", "plus_minus", "game_score"]:
            acc[k].append(pg[k])

    season_stats = []
    for (name, pid), acc in player_accum.items():
        gp = acc["gp"]
        avg = lambda lst: round(sum(lst) / len(lst), 1) if lst else 0
        avg3 = lambda lst: round(sum(lst) / len(lst), 3) if lst else 0
        mpg = avg(acc["minutes"])
        ppg = avg(acc["pts"])
        rpg = avg(acc["reb"])
        apg = avg(acc["ast"])
        spg = avg(acc["stl"])
        bpg = avg(acc["blk"])
        topg = avg(acc["tov"])
        fg_pct = avg3(acc["fg_pct"])
        fg3_pct = avg3(acc["fg3_pct"])
        ft_pct = avg3(acc["ft_pct"])
        ts_pct = avg3(acc["ts_pct"])
        usage_pct = avg(acc["usage_pct"])
        ortg = avg(acc["ortg"])
        drtg = avg(acc["drtg"])
        net_rtg = round(ortg - drtg, 1)

        # Approximate advanced stats
        efg_pct = round(clamp(fg_pct + random.gauss(0.04, 0.02), 0.40, 0.62), 3)
        per_val = round(clamp(ppg * 0.8 + rpg * 0.3 + apg * 0.5 + spg * 1.5 + bpg * 1.5 - topg * 0.8, 5, 30), 1)
        bpm = round(clamp(random.gauss((ppg - 12) * 0.3, 2), -5, 8), 1)
        vorp = round(clamp(bpm * gp / 58 * 0.06, -0.5, 4.0), 1)
        ws = round(clamp(random.gauss(ppg * 0.15 * gp / 58, 1.5), 0, 8), 1)
        ws_48 = round(clamp(ws / (mpg * gp / 48) if mpg * gp > 0 else 0, -0.05, 0.25), 3)
        on_off = round(random.gauss(net_rtg * 0.5, 3), 1)

        season_stats.append({
            "player_id": pid,
            "player_name": name,
            "gp": gp,
            "mpg": mpg,
            "ppg": ppg,
            "rpg": rpg,
            "apg": apg,
            "spg": spg,
            "bpg": bpg,
            "topg": topg,
            "fg_pct": fg_pct,
            "fg3_pct": fg3_pct,
            "ft_pct": ft_pct,
            "ts_pct": ts_pct,
            "efg_pct": efg_pct,
            "usage_pct": usage_pct,
            "per": per_val,
            "bpm": bpm,
            "vorp": vorp,
            "ws": ws,
            "ws_48": ws_48,
            "ortg": ortg,
            "drtg": drtg,
            "net_rtg": net_rtg,
            "on_off_net": on_off,
        })

    season_stats.sort(key=lambda x: x["ppg"], reverse=True)
    with open("data/player_season_stats.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(season_stats[0].keys()))
        writer.writeheader()
        writer.writerows(season_stats)

    # ── team_info.json ────────────────────────────────────────────────────────
    with open("data/team_info.json", "w") as f:
        json.dump({
            "team_name": "Miami Heat",
            "team_abbreviation": "MIA",
            "conference": "Eastern",
            "division": "Southeast",
            "season": "2024-25",
            "arena": "Kaseya Center",
            "head_coach": "Erik Spoelstra",
        }, f, indent=2)

    # ── league_averages.json ──────────────────────────────────────────────────
    with open("data/league_averages.json", "w") as f:
        json.dump({
            "league": {
                "ortg": 114.2, "drtg": 114.2, "pace": 99.8, "ts_pct": 0.578,
                "efg_pct": 0.534, "tov_pct": 13.2, "oreb_pct": 25.5,
                "ft_rate": 0.245, "ppg": 112.5, "rpg": 43.8, "apg": 25.8,
                "fg_pct": 0.467, "fg3_pct": 0.365, "ft_pct": 0.782,
            },
            "eastern_conference": {
                "ortg": 113.8, "drtg": 114.5, "pace": 99.2, "ts_pct": 0.575,
                "efg_pct": 0.530, "tov_pct": 13.4, "oreb_pct": 25.8,
                "ft_rate": 0.248, "ppg": 111.8, "rpg": 43.5, "apg": 25.5,
                "fg_pct": 0.464, "fg3_pct": 0.361, "ft_pct": 0.779,
            },
        }, f, indent=2)

    # ── schedule.csv (upcoming games) ─────────────────────────────────────────
    last_game_date = datetime.strptime(games[-1]["game_date"], "%Y-%m-%d")
    upcoming = []
    d = last_game_date
    for i in range(15):
        d += timedelta(days=random.choice([1, 2, 2, 3]))
        opp = random.choice(NBA_TEAMS)
        ha = random.choice(["Home", "Away"])
        hour = random.choice([19, 19, 20, 20, 15])
        minute = random.choice([0, 30])
        upcoming.append({
            "game_date": d.strftime("%Y-%m-%d"),
            "home_away": ha,
            "opponent": opp[0],
            "opponent_abbr": opp[1],
            "game_time": f"{hour}:{minute:02d} ET",
        })

    with open("data/schedule.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(upcoming[0].keys()))
        writer.writeheader()
        writer.writerows(upcoming)

    print(f"Generated {num_games} games ({total_wins}W-{total_losses}L)")
    print(f"Generated {len(player_game_log)} player game entries")
    print(f"Generated {len(season_stats)} player season stat lines")
    print(f"Generated {len(upcoming)} upcoming games")


if __name__ == "__main__":
    generate()
