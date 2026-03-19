"""Styled dataframe display components for the Heat dashboard."""

import streamlit as st
import pandas as pd
from components.theme import COLORS


# ═════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═════════════════════════════════════════════════════════════════════════════

# Columns that represent percentages stored as 0.xxx decimals
_PCT_COLS = {
    "FG%", "3P%", "FT%", "TS%", "eFG%", "FG_PCT", "FG3_PCT", "FT_PCT",
    "TS_PCT", "EFG_PCT", "fg_pct", "fg3_pct", "ft_pct", "ts_pct", "efg_pct",
}

# Columns that should NOT be converted (already in natural scale or are rates)
_SKIP_PCT = {"TOV%", "OREB%", "FT Rate", "USG%"}


def _fmt_cell(val, col_name: str) -> str:
    """Format a cell value — convert decimals to %, apply +/- sign, etc."""
    if pd.isna(val):
        return '<span class="cc-t-num cc-t-zero">—</span>'

    # Percentage columns: convert 0.xxx → xx%
    if col_name in _PCT_COLS and isinstance(val, (int, float)):
        pct = val * 100 if abs(val) <= 1 else val
        if pct == 0:
            return '<span class="cc-t-num cc-t-zero">—</span>'
        return f'<span class="cc-t-num">{pct:.1f}%</span>'

    # +/- column
    if col_name in ("+/-", "plus_minus", "BPM", "NET", "Net"):
        v = float(val)
        if v > 0:
            return f'<span class="cc-t-num cc-t-plus">+{v:g}</span>'
        elif v < 0:
            return f'<span class="cc-t-num cc-t-minus">{v:g}</span>'
        return '<span class="cc-t-num">0</span>'

    # PTS column (highlight)
    if col_name == "PTS":
        return f'<span class="cc-t-num cc-t-pts">{int(val)}</span>'

    # Integer columns
    if isinstance(val, float) and val == int(val) and col_name not in _SKIP_PCT:
        return f'<span class="cc-t-num">{int(val)}</span>'

    # Float with 1-3 decimal places
    if isinstance(val, float):
        # Format with appropriate precision
        if abs(val) >= 10:
            return f'<span class="cc-t-num">{val:.1f}</span>'
        elif abs(val) >= 1:
            return f'<span class="cc-t-num">{val:.1f}</span>'
        else:
            return f'<span class="cc-t-num">{val:.3f}</span>'

    return f'<span class="cc-t-num">{val}</span>'


def _build_table_html(headers: list, rows_data: list[list], col_keys: list,
                      first_col_name: bool = True, row_highlight_fn=None) -> str:
    """Build a branded HTML table.

    Args:
        headers: column display names
        rows_data: list of row dicts or list of cell values
        col_keys: column keys (original names for formatting logic)
        first_col_name: if True, first column gets player/name styling
        row_highlight_fn: optional fn(row_idx, row_dict) → extra style str
    """
    # Header cells
    hdr = ""
    for i, h in enumerate(headers):
        align = "left" if i == 0 and first_col_name else "center"
        hdr += f'<th style="text-align:{align}">{h}</th>'

    # Body rows
    body = ""
    for idx, row in enumerate(rows_data):
        row_class = "even" if idx % 2 == 0 else "odd"
        extra_style = ""
        if row_highlight_fn:
            extra_style = row_highlight_fn(idx, row)

        cells = ""
        for i, (key, val) in enumerate(zip(col_keys, row)):
            align = "left" if i == 0 and first_col_name else "center"
            if i == 0 and first_col_name:
                cell_html = f'<span class="cc-t-name">{val}</span>'
            else:
                cell_html = _fmt_cell(val, headers[i])
            cells += f'<td style="text-align:{align}">{cell_html}</td>'

        body += f'<tr class="cc-t-row {row_class}" style="{extra_style}">{cells}</tr>'

    return f"""
    <div class="cc-branded-table-wrap">
        <table class="cc-branded-table">
            <thead><tr>{hdr}</tr></thead>
            <tbody>{body}</tbody>
        </table>
    </div>
    """


# ═════════════════════════════════════════════════════════════════════════════
# 1. BOX SCORE TABLE (Last Game page)
# ═════════════════════════════════════════════════════════════════════════════

def box_score_table(df: pd.DataFrame):
    """Render a branded box-score table for a single game."""
    display_cols = [
        "player_name", "minutes", "pts", "fg", "fga", "fg_pct",
        "fg3", "fg3a", "fg3_pct", "ft", "fta", "ft_pct",
        "reb", "ast", "stl", "blk", "tov", "pf", "plus_minus",
    ]
    available = [c for c in display_cols if c in df.columns]
    display = df[available].copy().sort_values("minutes", ascending=False)

    col_map = {
        "player_name": "PLAYER", "minutes": "MIN", "pts": "PTS",
        "fg": "FG", "fga": "FGA", "fg_pct": "FG%",
        "fg3": "3P", "fg3a": "3PA", "fg3_pct": "3P%",
        "ft": "FT", "fta": "FTA", "ft_pct": "FT%",
        "reb": "REB", "ast": "AST", "stl": "STL",
        "blk": "BLK", "tov": "TO", "pf": "PF", "plus_minus": "+/-",
    }

    headers = [col_map.get(c, c) for c in available]
    rows = [[row[c] for c in available] for _, row in display.iterrows()]

    html = _build_table_html(headers, rows, available, first_col_name=True)
    st.markdown(html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 2. SEASON AVERAGES TABLE (Players page)
# ═════════════════════════════════════════════════════════════════════════════

def styled_table(df: pd.DataFrame, height: int | None = None):
    """Render a branded season-stats table."""
    headers = list(df.columns)
    col_keys = list(df.columns)
    rows = [list(row) for _, row in df.iterrows()]

    html = _build_table_html(headers, rows, col_keys, first_col_name=True)

    # Wrap with optional max-height scrolling
    if height:
        html = f'<div style="max-height:{height}px;overflow-y:auto;">{html}</div>'

    st.markdown(html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 3. COMPARISON TABLE (Season View — Heat vs League vs East)
# ═════════════════════════════════════════════════════════════════════════════

def comparison_table(heat_vals: dict, league_vals: dict, east_vals: dict, metrics: list[str]):
    """Branded comparison table: Heat vs League Avg vs East Avg."""
    headers = ["METRIC", "HEAT", "LEAGUE AVG", "EAST AVG"]
    col_keys = ["metric", "heat", "league", "east"]

    rows = []
    for m in metrics:
        h_val = heat_vals.get(m, "—")
        l_val = league_vals.get(m, "—")
        e_val = east_vals.get(m, "—")

        # Format percentage metrics
        if m in ("TS%", "eFG%", "FG%", "3P%", "FT%"):
            def _pct(v):
                if isinstance(v, (int, float)):
                    return f"{v * 100:.1f}%" if abs(v) < 1 else f"{v:.1f}%"
                return str(v)
            rows.append([m, _pct(h_val), _pct(l_val), _pct(e_val)])
        else:
            rows.append([m, h_val, l_val, e_val])

    def _heat_highlight(idx, row):
        """Highlight the Heat column value — green if above league, red if below."""
        return ""

    html = _build_table_html(headers, rows, col_keys, first_col_name=True,
                             row_highlight_fn=_heat_highlight)
    st.markdown(html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 4. SCHEDULE TABLE (Overview page)
# ═════════════════════════════════════════════════════════════════════════════

def schedule_table(df: pd.DataFrame):
    """Render a branded upcoming schedule table."""
    headers = list(df.columns)
    col_keys = list(df.columns)
    rows = [list(row) for _, row in df.iterrows()]

    html = _build_table_html(headers, rows, col_keys, first_col_name=True)
    st.markdown(html, unsafe_allow_html=True)
