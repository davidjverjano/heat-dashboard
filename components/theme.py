"""Brand colors, fonts, and styling constants — Courtside Cre8ives."""

# ── Brand Colors ──────────────────────────────────────────────────────────────
COLORS = {
    # Core brand
    "asphalt_black": "#252422",
    "off_white": "#FFFCF2",
    "rich_red": "#C75146",
    "dark_red": "#81171B",
    "yellow_flame": "#F7B267",
    "warm_coral": "#F4845F",
    "mamey": "#F25C54",
    "warm_grey": "#CCC5B9",
    # Asphalt Black variations (dark theme)
    "bg_deepest": "#1a1917",
    "bg_secondary": "#201f1d",
    "bg_tertiary": "#252422",
    "bg_card": "#2a2926",
    "bg_card_hover": "#31302d",
    "bg_elevated": "#353432",
    # Text hierarchy
    "text_primary": "#FFFCF2",
    "text_secondary": "#b0ada6",
    "text_muted": "#6e6b64",
    "text_faint": "#484541",
    # Accent
    "accent_primary": "#F7B267",
    "accent_hover": "#f9c48a",
    # Semantic
    "win_green": "#3fb950",
    "loss_red": "#F25C54",
    "positive": "#3fb950",
    "negative": "#F25C54",
}

# Chart color sequence
CHART_COLORS = [
    "#F7B267",  # Yellow Flame (primary accent)
    "#C75146",  # Rich Red
    "#F4845F",  # Warm Coral
    "#3fb950",  # Win Green
    "#F25C54",  # Mamey
    "#81171B",  # Dark Red
    "#CCC5B9",  # Warm Grey
    "#b0ada6",  # Text secondary
]

# ── Plotly Layout Defaults ────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#1a1917",
    plot_bgcolor="#1a1917",
    font=dict(
        family="-apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif",
        color="#FFFCF2",
        size=13,
    ),
    xaxis=dict(
        gridcolor="rgba(255,252,242,0.06)",
        zerolinecolor="rgba(247,178,103,0.2)",
        tickfont=dict(color="#b0ada6"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,252,242,0.06)",
        zerolinecolor="rgba(247,178,103,0.2)",
        tickfont=dict(color="#b0ada6"),
    ),
    margin=dict(l=50, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor="#2a2926",
        font_size=13,
        font_family="-apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif",
        font_color="#FFFCF2",
        bordercolor="#F7B267",
    ),
    legend=dict(
        font=dict(color="#b0ada6"),
        bgcolor="rgba(0,0,0,0)",
    ),
    colorway=CHART_COLORS,
)


def apply_plotly_theme(fig):
    """Apply the Courtside Cre8ives brand theme to a Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
