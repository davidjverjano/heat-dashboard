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
    """Render a branded box-score table for a single game."""
    display_cols = [
        "player_name", "minutes", "pts", "fg", "fga", "fg_pct",
        "fg3", "fg3a", "fg3_pct", "ft", "fta", "ft_pct",
        "reb", "ast", "stl", "blk", "tov", "pf", "plus_minus",
    ]
    available = [c for c in display_cols if c in df.columns]
    display = df[available].copy()
    display = display.sort_values("minutes", ascending=False)

    # ── Column display config ────────────────────────────────────────────────
    col_map = {
        "player_name": "PLAYER", "minutes": "MIN", "pts": "PTS",
        "fg": "FG", "fga": "FGA", "fg_pct": "FG%",
        "fg3": "3P", "fg3a": "3PA", "fg3_pct": "3P%",
        "ft": "FT", "fta": "FTA", "ft_pct": "FT%",
        "reb": "REB", "ast": "AST", "stl": "STL",
        "blk": "BLK", "tov": "TO", "pf": "PF", "plus_minus": "+/-",
    }

    # ── Build HTML rows ──────────────────────────────────────────────────────
    header_cells = ""
    for col in available:
        label = col_map.get(col, col)
        align = "left" if col == "player_name" else "center"
        header_cells += f'<th style="text-align:{align}">{label}</th>'

    body_rows = ""
    for i, (_, row) in enumerate(display.iterrows()):
        row_class = "even" if i % 2 == 0 else "odd"
        cells = ""
        for col in available:
            val = row[col]
            align = "left" if col == "player_name" else "center"

            if col == "player_name":
                cell_html = f'<span class="cc-box-player">{val}</span>'
            elif col in ("fg_pct", "fg3_pct", "ft_pct"):
                # Convert decimal to percentage
                if pd.notna(val) and val > 0:
                    pct_val = val * 100 if val <= 1 else val
                    cell_html = f'<span class="cc-box-num">{pct_val:.0f}%</span>'
                else:
                    cell_html = '<span class="cc-box-num cc-box-zero">—</span>'
            elif col == "plus_minus":
                pm = int(val) if pd.notna(val) else 0
                if pm > 0:
                    cell_html = f'<span class="cc-box-num cc-box-plus">+{pm}</span>'
                elif pm < 0:
                    cell_html = f'<span class="cc-box-num cc-box-minus">{pm}</span>'
                else:
                    cell_html = '<span class="cc-box-num">0</span>'
            elif col == "pts":
                cell_html = f'<span class="cc-box-num cc-box-pts">{int(val)}</span>'
            else:
                int_val = int(val) if pd.notna(val) else 0
                cell_html = f'<span class="cc-box-num">{int_val}</span>'

            cells += f'<td style="text-align:{align}">{cell_html}</td>'

        body_rows += f'<tr class="cc-box-row {row_class}">{cells}</tr>'

    html = f"""
    <div class="cc-box-score-wrap">
        <table class="cc-box-score">
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{body_rows}</tbody>
        </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


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
