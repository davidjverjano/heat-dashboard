"""Reusable Plotly chart functions for the Heat dashboard."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from components.theme import COLORS, CHART_COLORS, apply_plotly_theme


def win_loss_timeline(game_log: pd.DataFrame) -> go.Figure:
    """Bar chart of wins/losses over the season."""
    df = game_log.copy().sort_values("game_date")
    colors = [COLORS["win_green"] if r == "W" else COLORS["loss_red"] for r in df["result"]]
    fig = go.Figure(
        go.Bar(
            x=df["game_date"],
            y=df["plus_minus"],
            marker_color=colors,
            hovertemplate=(
                "<b>%{x|%b %d}</b><br>"
                "vs %{customdata[0]}<br>"
                "%{customdata[1]} %{customdata[2]}-%{customdata[3]}<br>"
                "+/- : %{y:+d}<extra></extra>"
            ),
            customdata=df[["opponent", "result", "team_score", "opponent_score"]].values,
        )
    )
    fig.update_layout(
        title="Win / Loss Timeline",
        xaxis_title="",
        yaxis_title="Point Differential",
        showlegend=False,
        height=350,
    )
    apply_plotly_theme(fig)
    return fig


def point_diff_trend(game_log: pd.DataFrame, window: int = 7) -> go.Figure:
    """Rolling point differential trend line."""
    df = game_log.copy().sort_values("game_date")
    df["rolling_diff"] = df["plus_minus"].rolling(window, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["game_date"],
            y=df["rolling_diff"],
            mode="lines",
            line=dict(color=COLORS["yellow_flame"], width=3),
            name=f"{window}-Game Rolling Avg",
            hovertemplate="%{x|%b %d}: %{y:+.1f}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["warm_grey"], opacity=0.5)
    fig.update_layout(
        title=f"Point Differential ({window}-Game Rolling)",
        xaxis_title="",
        yaxis_title="Avg +/-",
        height=280,
        showlegend=False,
    )
    apply_plotly_theme(fig)
    return fig


def rolling_line_chart(
    game_log: pd.DataFrame,
    columns: list[str],
    labels: list[str] | None = None,
    title: str = "",
    window: int = 7,
    height: int = 350,
    reference_lines: dict | None = None,
) -> go.Figure:
    """Multi-line rolling average chart."""
    df = game_log.copy().sort_values("game_date")
    labels = labels or columns
    fig = go.Figure()
    for i, (col, label) in enumerate(zip(columns, labels)):
        rolling = df[col].rolling(window, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=df["game_date"],
                y=rolling,
                mode="lines",
                name=label,
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2.5),
                hovertemplate=f"{label}: " + "%{y:.1f}<extra></extra>",
            )
        )
    if reference_lines:
        for label, val in reference_lines.items():
            fig.add_hline(
                y=val,
                line_dash="dot",
                line_color=COLORS["warm_grey"],
                opacity=0.5,
                annotation_text=label,
                annotation_font_color=COLORS["warm_grey"],
            )
    fig.update_layout(title=title, xaxis_title="", yaxis_title="", height=height)
    apply_plotly_theme(fig)
    return fig


def four_factors_bar(team_vals: dict, opp_vals: dict, title: str = "Four Factors") -> go.Figure:
    """Grouped bar chart comparing team vs opponent four factors."""
    factors = ["eFG%", "TOV%", "OREB%", "FT Rate"]
    team_v = [team_vals.get(f, 0) for f in factors]
    opp_v = [opp_vals.get(f, 0) for f in factors]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Heat", x=factors, y=team_v, marker_color=COLORS["rich_red"]))
    fig.add_trace(go.Bar(name="Opponent", x=factors, y=opp_v, marker_color=COLORS["warm_grey"]))
    fig.update_layout(
        title=title, barmode="group", height=350, yaxis_title="", legend=dict(orientation="h", y=1.12)
    )
    apply_plotly_theme(fig)
    return fig


def radar_chart(categories: list, values: list, title: str = "Team Profile") -> go.Figure:
    """Radar / spider chart for team profile."""
    cats = categories + [categories[0]]
    vals = values + [values[0]]
    fig = go.Figure(
        go.Scatterpolar(
            r=vals,
            theta=cats,
            fill="toself",
            fillcolor="rgba(199,81,70,0.25)",
            line=dict(color=COLORS["rich_red"], width=2),
            marker=dict(color=COLORS["yellow_flame"], size=6),
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="#252422",
            radialaxis=dict(gridcolor="rgba(204,197,185,0.15)", tickfont=dict(color="#CCC5B9", size=10)),
            angularaxis=dict(gridcolor="rgba(204,197,185,0.15)", tickfont=dict(color="#FFFCF2", size=12)),
        ),
        title=title,
        height=420,
        showlegend=False,
    )
    apply_plotly_theme(fig)
    return fig


def scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    text_col: str | None = None,
    title: str = "",
    highlight_idx: int | None = None,
    height: int = 400,
) -> go.Figure:
    """Scatter plot with optional highlighted point."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="markers+text" if text_col else "markers",
            text=df[text_col] if text_col else None,
            textposition="top center",
            textfont=dict(size=10, color=COLORS["warm_grey"]),
            marker=dict(color=COLORS["warm_grey"], size=8, opacity=0.6),
            hovertemplate=f"{x}: " + "%{x:.1f}<br>" + f"{y}: " + "%{y:.1f}<extra></extra>",
        )
    )
    if highlight_idx is not None and highlight_idx < len(df):
        row = df.iloc[highlight_idx]
        fig.add_trace(
            go.Scatter(
                x=[row[x]],
                y=[row[y]],
                mode="markers+text",
                text=["MIA"],
                textposition="top center",
                textfont=dict(size=13, color=COLORS["yellow_flame"]),
                marker=dict(color=COLORS["rich_red"], size=14, line=dict(width=2, color=COLORS["yellow_flame"])),
                showlegend=False,
            )
        )
    fig.update_layout(title=title, xaxis_title=x, yaxis_title=y, height=height, showlegend=False)
    apply_plotly_theme(fig)
    return fig


def bar_chart(
    labels: list,
    values: list,
    title: str = "",
    highlight_label: str | None = None,
    horizontal: bool = False,
    height: int = 350,
) -> go.Figure:
    """Simple bar chart with optional highlighted bar."""
    colors = [
        COLORS["rich_red"] if l == highlight_label else COLORS["warm_grey"]
        for l in labels
    ]
    if horizontal:
        fig = go.Figure(go.Bar(y=labels, x=values, orientation="h", marker_color=colors))
    else:
        fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors))
    fig.update_layout(title=title, height=height, showlegend=False)
    apply_plotly_theme(fig)
    return fig


def sparkline(values: list | pd.Series, color: str = COLORS["yellow_flame"], height: int = 80) -> go.Figure:
    """Minimal sparkline chart."""
    fig = go.Figure(
        go.Scatter(
            y=list(values),
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=color.replace(")", ",0.1)").replace("rgb", "rgba") if "rgb" in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)",
        )
    )
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    apply_plotly_theme(fig)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def usage_ts_scatter(player_stats: pd.DataFrame) -> go.Figure:
    """Usage% vs TS% scatter for all players."""
    fig = go.Figure(
        go.Scatter(
            x=player_stats["usage_pct"],
            y=player_stats["ts_pct"],
            mode="markers+text",
            text=player_stats["player_name"].apply(lambda n: n.split()[-1]),
            textposition="top center",
            textfont=dict(size=10, color=COLORS["off_white"]),
            marker=dict(
                size=player_stats["ppg"] * 1.2 + 4,
                color=COLORS["rich_red"],
                line=dict(width=1, color=COLORS["yellow_flame"]),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "USG%: %{x:.1f}%<br>"
                "TS%: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Usage% vs True Shooting%",
        xaxis_title="Usage %",
        yaxis_title="TS %",
        height=400,
        showlegend=False,
    )
    apply_plotly_theme(fig)
    return fig


def plus_minus_distribution(player_game_log: pd.DataFrame, player_name: str) -> go.Figure:
    """Histogram of a player's +/- values."""
    df = player_game_log[player_game_log["player_name"] == player_name]
    colors = [COLORS["win_green"] if v >= 0 else COLORS["loss_red"] for v in df["plus_minus"]]
    fig = go.Figure(
        go.Histogram(
            x=df["plus_minus"],
            marker_color=COLORS["rich_red"],
            nbinsx=20,
            hovertemplate="+/-: %{x}<br>Count: %{y}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["warm_grey"])
    fig.update_layout(
        title=f"{player_name} — +/- Distribution",
        xaxis_title="+/-",
        yaxis_title="Games",
        height=300,
        showlegend=False,
    )
    apply_plotly_theme(fig)
    return fig
