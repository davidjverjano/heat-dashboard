"""Statistical calculation helpers."""

import pandas as pd
import numpy as np


def rolling_average(series: pd.Series, window: int = 7) -> pd.Series:
    """Calculate rolling average with minimum 1 period."""
    return series.rolling(window, min_periods=1).mean()


def net_rating(ortg: float, drtg: float) -> float:
    return round(ortg - drtg, 1)


def win_pct(wins: int, losses: int) -> float:
    total = wins + losses
    return round(wins / total, 3) if total > 0 else 0.0


def last_n_record(game_log: pd.DataFrame, n: int = 10) -> tuple[int, int]:
    """Return (wins, losses) for the last n games."""
    recent = game_log.sort_values("game_date").tail(n)
    wins = (recent["result"] == "W").sum()
    losses = (recent["result"] == "L").sum()
    return int(wins), int(losses)


def current_streak(game_log: pd.DataFrame) -> tuple[str, int]:
    """Return (streak_type, count) e.g. ('W', 4)."""
    results = game_log.sort_values("game_date")["result"].tolist()
    if not results:
        return "—", 0
    last = results[-1]
    count = 0
    for r in reversed(results):
        if r == last:
            count += 1
        else:
            break
    return last, count


def four_factors(game_log: pd.DataFrame) -> dict:
    """Calculate team four factors from game log."""
    return {
        "eFG%": round(game_log["efg_pct"].mean() * 100, 1),
        "TOV%": round(game_log["tov_pct"].mean(), 1),
        "OREB%": round(game_log["oreb_pct"].mean(), 1),
        "FT Rate": round(game_log["ft_rate"].mean(), 3),
    }


def opponent_four_factors(game_log: pd.DataFrame) -> dict:
    """Calculate opponent four factors."""
    return {
        "eFG%": round(game_log["opp_efg_pct"].mean() * 100, 1),
        "TOV%": round(game_log["opp_tov_pct"].mean(), 1),
        "OREB%": round(game_log["opp_oreb_pct"].mean(), 1),
        "FT Rate": round(game_log["opp_ft_rate"].mean(), 3),
    }


def season_splits(game_log: pd.DataFrame) -> dict:
    """Calculate home vs away and monthly splits."""
    home = game_log[game_log["home_away"] == "Home"]
    away = game_log[game_log["home_away"] == "Away"]
    home_w = int((home["result"] == "W").sum())
    home_l = int((home["result"] == "L").sum())
    away_w = int((away["result"] == "W").sum())
    away_l = int((away["result"] == "L").sum())

    monthly = {}
    game_log = game_log.copy()
    game_log["month"] = game_log["game_date"].dt.strftime("%Y-%m")
    for month, grp in game_log.groupby("month"):
        w = int((grp["result"] == "W").sum())
        l = int((grp["result"] == "L").sum())
        monthly[month] = {"wins": w, "losses": l, "ortg": round(grp["ortg"].mean(), 1), "drtg": round(grp["drtg"].mean(), 1)}

    return {
        "home": {"wins": home_w, "losses": home_l},
        "away": {"wins": away_w, "losses": away_l},
        "monthly": monthly,
    }
