"""Brand colors, fonts, and styling constants for the Miami Heat dashboard."""

# ── Brand Colors ────────────────────────────────────────────────────────────────────
COLORS = {
    "asphalt_black": "#252422",
    "off_white": "#FFFCF2",
    "rich_red": "#C75146",
    "dark_red": "#81171B",
    "yellow_flame": "#F7B267",
    "warm_coral": "#F4845F",
    "mamey": "#F25C54",
    "warm_grey": "#CCC5B9",
    "bg_secondary": "#1a1816",
    "win_green": "#4CAF50",
    "loss_red": "#F25C54",
}

# Chart color sequence
CHART_COLORS = [
    "#C75146",  # Rich Red
    "#F7B267",  # Yellow Flame
    "#F4845F",  # Warm Coral
    "#F25C54",  # Mamey
    "#81171B",  # Dark Red
    "#CCC5B9",  # Warm Grey
]

# ── Plotly Layout Defaults ───────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#252422",
    plot_bgcolor="#252422",
    font=dict(family="Barlow Condensed, Oswald, sans-serif", color="#FFFCF2", size=13),
    xaxis=dict(
        gridcolor="rgba(204,197,185,0.15)",
        zerolinecolor="rgba(204,197,185,0.25)",
        tickfont=dict(color="#CCC5B9"),
    ),
    yaxis=dict(
        gridcolor="rgba(204,197,185,0.15)",
        zerolinecolor="rgba(204,197,185,0.25)",
        tickfont=dict(color="#CCC5B9"),
    ),
    margin=dict(l=50, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#1a1816",
        font_size=13,
        font_family="Barlow Condensed, Oswald, sans-serif",
        font_color="#FFFCF2",
        bordercolor="#C75146",
    ),
    legend=dict(
        font=dict(color="#CCC5B9"),
        bgcolor="rgba(0,0,0,0)",
    ),
    colorway=CHART_COLORS,
)


def apply_plotly_theme(fig):
    """Apply the Heat brand theme to a Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# Alias for backwards compatibility
apply_heat_theme = apply_plotly_theme
