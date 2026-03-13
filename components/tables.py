"""Styled dataframe display components for the Heat dashboard."""

import streamlit as st
import pandas as pd
from components.theme import COLORS


def styled_table(df: pd.DataFrame, height: int | None = None):
    """Render a styled dataframe using Streamlit's dataframe with custom styling."""
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True,
        column_config={
            col: st.column_config.NumberColumn(format="%.1f")
            for col in df.select_dtypes(include=["float64", "float32"]).columns
        },
    )


def box_score_table(df: pd.DataFrame):
    """Render a box-score style table for a single game."""
    display_cols = [
        "player_name", "minutes", "pts", "fg", "fga", "fg_pct",
        "fg3", "fg3a", "fg3_pct", "ft", "fta", "ft_pct",
        "reb", "ast", "stl", "blk", "tov", "pf", "plus_minus",
    ]
    available = [c for c in display_cols if c in df.columns]
    display = df[available].copy()

    rename_map = {
        "player_name": "Player", "minutes": "MIN", "pts": "PTS",
        "fg": "FG", "fga": "FGA", "fg_pct": "FG%",
        "fg3": "3P", "fg3a": "3PA", "fg3_pct": "3P%",
        "ft": "FT", "fta": "FTA", "ft_pct": "FT%",
        "reb": "REB", "ast": "AST", "stl": "STL",
        "blk": "BLK", "tov": "TO", "pf": "PF", "plus_minus": "+/-",
    }
    display.rename(columns={k: v for k, v in rename_map.items() if k in display.columns}, inplace=True)
    display = display.sort_values("MIN", ascending=False)

    pct_cols = [c for c in ["FG%", "3P%", "FT%"] if c in display.columns]
    col_config = {}
    for c in pct_cols:
        col_config[c] = st.column_config.NumberColumn(format="%.1f")
    if "+/-" in display.columns:
        col_config["+/-"] = st.column_config.NumberColumn(format="%+d")

    st.dataframe(display, use_container_width=True, hide_index=True, column_config=col_config)


def comparison_table(heat_vals: dict, league_vals: dict, east_vals: dict, metrics: list[str]):
    """Comparison table: Heat vs League Avg vs East Avg."""
    rows = []
    for m in metrics:
        rows.append({
            "Metric": m,
            "Heat": heat_vals.get(m, "—"),
            "League Avg": league_vals.get(m, "—"),
            "East Avg": east_vals.get(m, "—"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
