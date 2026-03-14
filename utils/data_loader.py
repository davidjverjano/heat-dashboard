"""Load and cache data from local CSV/JSON files."""

import json
import pathlib
import pandas as pd
import streamlit as st

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


@st.cache_data(ttl=300)
def load_team_info() -> dict:
    with open(DATA_DIR / "team_info.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_game_log() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "team_game_log.csv", parse_dates=["game_date"])
    df.sort_values("game_date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data(ttl=300)
def load_player_game_log() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "player_game_log.csv", parse_dates=["game_date"])
    df.sort_values(["game_date", "player_name"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data(ttl=300)
def load_player_season_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "player_season_stats.csv")
    df.sort_values("ppg", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data(ttl=300)
def load_schedule() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "schedule.csv", parse_dates=["game_date"])
    df.sort_values("game_date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data(ttl=300)
def load_league_averages() -> dict:
    with open(DATA_DIR / "league_averages.json") as f:
        return json.load(f)


@st.cache_data(ttl=300)
def load_league_team_ratings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "league_team_ratings.csv")


@st.cache_data(ttl=300)
def load_team_rankings() -> dict:
    with open(DATA_DIR / "team_rankings.json") as f:
        return json.load(f)
