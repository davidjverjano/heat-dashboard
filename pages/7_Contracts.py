"""Page 7 — Contracts: Salary table, cap breakdown, draft capital."""

import json
import pathlib
import streamlit as st
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
from components.page_setup import setup_page
setup_page()

from components.theme import COLORS
import plotly.graph_objects as go

st.markdown("# CONTRACTS & CAP")

# ── Load Data ─────────────────────────────────────────────────────────────────
DATA_DIR = ROOT / "data"
with open(DATA_DIR / "contracts.json") as f:
    contracts = json.load(f)


# ── Helper: _html (matches Narratives pattern — strips indentation) ──────────
def _html(html_str: str):
    """Render HTML with unsafe_allow_html, stripping leading indentation."""
    import textwrap
    st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)


# ── Helper: format currency ──────────────────────────────────────────────────
def _fmt(val, short=False):
    """Format a dollar amount."""
    if val is None or val == 0:
        return "—"
    if short:
        if abs(val) >= 1_000_000:
            return f"${val / 1_000_000:,.1f}M"
        elif abs(val) >= 1_000:
            return f"${val / 1_000:,.0f}K"
    return f"${val:,.0f}"


def _fmt_signed(val):
    """Format dollar amount with +/- sign."""
    if val is None:
        return "—"
    prefix = "+" if val > 0 else ""
    if abs(val) >= 1_000_000:
        return f"{prefix}${val / 1_000_000:,.1f}M"
    return f"{prefix}${val:,.0f}"


# ── Status badge colors ──────────────────────────────────────────────────────
STATUS_COLORS = {
    "guaranteed": ("#3fb950", "Guaranteed"),
    "player_option": ("#F7B267", "Player Opt"),
    "club_option": ("#4da6ff", "Club Opt"),
    "extension_eligible": ("#bb86fc", "Ext Elig"),
    "ufa": ("#6e6b64", "UFA"),
    "rfa": ("#3fb950", "RFA"),
    "two_way": ("#9c7cba", "Two-Way"),
    "waived": ("#F25C54", "Waived"),
}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CAP SUMMARY CARDS
# ══════════════════════════════════════════════════════════════════════════════
cap = contracts["cap_summary"]
cap_space_color = COLORS["loss_red"] if cap["cap_space"] < 0 else COLORS["win_green"]
tax_color = COLORS["win_green"] if cap["tax_space"] > 0 else COLORS["loss_red"]

_html(f"""
<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-bottom:24px;">
  <div style="background:{COLORS['bg_card']}; border:1px solid rgba(247,178,103,0.10); border-radius:12px; padding:16px 18px;">
    <div style="font-family:'Orbitron',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1.5px; color:{COLORS['text_muted']}; text-transform:uppercase; margin-bottom:6px;">Cap Space</div>
    <div style="font-family:var(--font-data); font-size:1.4rem; font-weight:800; color:{cap_space_color}; font-variant-numeric:tabular-nums;">{_fmt_signed(cap['cap_space'])}</div>
  </div>
  <div style="background:{COLORS['bg_card']}; border:1px solid rgba(247,178,103,0.10); border-radius:12px; padding:16px 18px;">
    <div style="font-family:'Orbitron',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1.5px; color:{COLORS['text_muted']}; text-transform:uppercase; margin-bottom:6px;">1st Apron Space</div>
    <div style="font-family:var(--font-data); font-size:1.4rem; font-weight:800; color:{COLORS['win_green']}; font-variant-numeric:tabular-nums;">{_fmt(cap['first_apron_space'], short=True)}</div>
  </div>
  <div style="background:{COLORS['bg_card']}; border:1px solid rgba(247,178,103,0.10); border-radius:12px; padding:16px 18px;">
    <div style="font-family:'Orbitron',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1.5px; color:{COLORS['text_muted']}; text-transform:uppercase; margin-bottom:6px;">Tax Space</div>
    <div style="font-family:var(--font-data); font-size:1.4rem; font-weight:800; color:{tax_color}; font-variant-numeric:tabular-nums;">{_fmt(cap['tax_space'], short=True)}</div>
  </div>
  <div style="background:{COLORS['bg_card']}; border:1px solid rgba(247,178,103,0.10); border-radius:12px; padding:16px 18px;">
    <div style="font-family:'Orbitron',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1.5px; color:{COLORS['text_muted']}; text-transform:uppercase; margin-bottom:6px;">Est. Tax Bill</div>
    <div style="font-family:var(--font-data); font-size:1.4rem; font-weight:800; color:{COLORS['win_green']}; font-variant-numeric:tabular-nums;">{_fmt(cap['est_tax_bill'])}</div>
  </div>
</div>
""")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ACTIVE ROSTER SALARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Active Roster")

roster = contracts["active_roster"]
seasons_display = ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30"]


def _salary_cell(player_salaries, season):
    """Build HTML for a salary cell with status badge."""
    if season not in player_salaries:
        return '<td style="padding:8px 10px; text-align:center; color:#484541;">—</td>'

    s = player_salaries[season]
    amount = s["amount"]
    status = s.get("status", "guaranteed")
    color, label = STATUS_COLORS.get(status, ("#6e6b64", ""))
    pct = s.get("pct_cap", 0)

    if status == "two_way":
        val_html = '<span style="font-family:var(--font-data); font-size:0.85rem; color:#9c7cba; font-weight:600;">Two-Way</span>'
    elif status in ("ufa", "rfa"):
        val_html = f'<span style="font-family:var(--font-data); font-size:0.85rem; color:{color}; font-weight:600; font-variant-numeric:tabular-nums;">{_fmt(amount, short=True)}</span>'
    else:
        val_html = f'<span style="font-family:var(--font-data); font-size:0.85rem; color:{COLORS["text_primary"]}; font-weight:600; font-variant-numeric:tabular-nums;">{_fmt(amount, short=True)}</span>'

    badge = ""
    if status not in ("guaranteed",):
        badge = f'<span style="display:inline-block; font-family:\'Orbitron\',var(--font-data); font-size:8px; font-weight:700; letter-spacing:0.5px; padding:1px 5px; border-radius:3px; background:rgba({_hex_to_rgb(color)},0.15); color:{color}; margin-left:4px; vertical-align:middle;">{label}</span>'

    pct_html = f'<div style="font-family:var(--font-data); font-size:10px; color:{COLORS["text_muted"]}; font-variant-numeric:tabular-nums;">{pct:.1f}%</div>' if pct > 0 else ""

    return f'<td style="padding:8px 10px; text-align:right;">{val_html}{badge}{pct_html}</td>'


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB string for rgba()."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"


# Build table header
header_cells = '<th style="padding:10px 10px; text-align:left; font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:700; letter-spacing:1px; color:#F7B267; text-transform:uppercase; border-bottom:2px solid rgba(247,178,103,0.2);">Player</th>'
header_cells += '<th style="padding:10px 6px; text-align:center; font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1px; color:#b0ada6; text-transform:uppercase; border-bottom:2px solid rgba(247,178,103,0.2);">Pos</th>'
header_cells += '<th style="padding:10px 6px; text-align:center; font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:400; letter-spacing:1px; color:#b0ada6; text-transform:uppercase; border-bottom:2px solid rgba(247,178,103,0.2);">Age</th>'
for s in seasons_display:
    header_cells += f'<th style="padding:10px 10px; text-align:right; font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:700; letter-spacing:1px; color:#F7B267; text-transform:uppercase; border-bottom:2px solid rgba(247,178,103,0.2);">{s}</th>'

# Build table rows
rows_html = ""
for i, p in enumerate(roster):
    bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_tertiary"]
    name = p["player"]
    pos = p["pos"]
    age = p["age"]

    # Highlight top earners
    salary_25 = p["salaries"].get("2025-26", {}).get("amount", 0)
    name_color = COLORS["accent_primary"] if salary_25 >= 20000000 else COLORS["text_primary"]
    name_weight = "700" if salary_25 >= 20000000 else "500"

    row = f'<tr style="background:{bg}; transition:background 0.15s;">'
    row += f'<td style="padding:8px 10px; white-space:nowrap;"><span style="font-family:var(--font-data); font-size:0.85rem; color:{name_color}; font-weight:{name_weight};">{name}</span></td>'
    row += f'<td style="padding:8px 6px; text-align:center; font-family:var(--font-data); font-size:0.8rem; color:{COLORS["text_secondary"]};">{pos}</td>'
    row += f'<td style="padding:8px 6px; text-align:center; font-family:var(--font-data); font-size:0.8rem; color:{COLORS["text_secondary"]}; font-variant-numeric:tabular-nums;">{age}</td>'
    for s in seasons_display:
        row += _salary_cell(p["salaries"], s)
    row += "</tr>"
    rows_html += row

# Dead money row
for dm in contracts["dead_money"]:
    rows_html += f'<tr style="background:rgba(242,92,84,0.05);">'
    rows_html += f'<td style="padding:8px 10px; white-space:nowrap;"><span style="font-family:var(--font-data); font-size:0.85rem; color:{COLORS["loss_red"]}; font-weight:500; text-decoration:line-through;">{dm["player"]}</span> <span style="font-family:\'Orbitron\',var(--font-data); font-size:8px; font-weight:700; letter-spacing:0.5px; padding:1px 5px; border-radius:3px; background:rgba(242,92,84,0.15); color:{COLORS["loss_red"]};">WAIVED</span></td>'
    rows_html += f'<td style="padding:8px 6px; text-align:center; color:{COLORS["text_muted"]};">—</td>'
    rows_html += f'<td style="padding:8px 6px; text-align:center; color:{COLORS["text_muted"]};">—</td>'
    for s in seasons_display:
        if s in dm["salaries"]:
            sal = dm["salaries"][s]
            rows_html += f'<td style="padding:8px 10px; text-align:right;"><span style="font-family:var(--font-data); font-size:0.85rem; color:{COLORS["loss_red"]}; font-weight:600; font-variant-numeric:tabular-nums;">{_fmt(sal["amount"], short=True)}</span><div style="font-family:var(--font-data); font-size:10px; color:{COLORS["text_muted"]}; font-variant-numeric:tabular-nums;">{sal["pct_cap"]:.1f}%</div></td>'
        else:
            rows_html += f'<td style="padding:8px 10px; text-align:center; color:#484541;">—</td>'
    rows_html += "</tr>"

# Total row
total_html = '<tr style="background:rgba(247,178,103,0.08); border-top:2px solid rgba(247,178,103,0.3);">'
total_html += f'<td colspan="3" style="padding:10px 10px; font-family:\'Orbitron\',var(--font-data); font-size:11px; font-weight:700; letter-spacing:1px; color:{COLORS["accent_primary"]}; text-transform:uppercase;">Total Active</td>'
for s in seasons_display:
    ct = contracts["cap_table"].get(s, {})
    active = ct.get("active_cap", 0)
    total_html += f'<td style="padding:10px 10px; text-align:right; font-family:var(--font-data); font-size:0.9rem; font-weight:800; color:{COLORS["text_primary"]}; font-variant-numeric:tabular-nums;">{_fmt(active, short=True)}</td>'
total_html += "</tr>"

_html(f"""
<div style="overflow-x:auto; border-radius:12px; border:1px solid rgba(247,178,103,0.10); background:{COLORS['bg_secondary']};">
  <table style="width:100%; border-collapse:collapse; min-width:800px;">
    <thead><tr>{header_cells}</tr></thead>
    <tbody>{rows_html}{total_html}</tbody>
  </table>
</div>
""")

# Legend
_html(f"""
<div style="display:flex; flex-wrap:wrap; gap:12px; margin:12px 0 28px; padding:0 4px;">
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(63,185,80,0.15); color:#3fb950;">RFA</span>
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(110,107,100,0.15); color:#6e6b64;">UFA</span>
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(247,178,103,0.15); color:#F7B267;">PLAYER OPT</span>
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(77,166,255,0.15); color:#4da6ff;">CLUB OPT</span>
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(187,134,252,0.15); color:#bb86fc;">EXT ELIG</span>
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:700; letter-spacing:0.5px; padding:2px 8px; border-radius:3px; background:rgba(156,124,186,0.15); color:#9c7cba;">TWO-WAY</span>
</div>
""")

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CAP BREAKDOWN VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Cap Breakdown")

col_chart, col_detail = st.columns([3, 2])

with col_chart:
    # Stacked bar: Active Cap + Dead Cap + Cap Holds vs Cap Max line
    ct = contracts["cap_table"]
    seasons = list(ct.keys())
    active_vals = [ct[s]["active_cap"] / 1_000_000 for s in seasons]
    dead_vals = [0 for _ in seasons]  # dead cap only in 2025-26 but already in active
    holds_vals = [ct[s]["cap_holds"] / 1_000_000 for s in seasons]
    cap_max_vals = [ct[s]["cap_max"] / 1_000_000 for s in seasons]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Active Cap", x=seasons, y=active_vals,
        marker_color=COLORS["accent_primary"],
        marker_line_width=0,
        text=[f"${v:.0f}M" for v in active_vals],
        textposition="inside",
        textfont=dict(size=11, color="#252422", family="-apple-system, system-ui, sans-serif"),
    ))
    fig.add_trace(go.Bar(
        name="Cap Holds", x=seasons, y=holds_vals,
        marker_color="rgba(199,81,70,0.7)",
        marker_line_width=0,
        text=[f"${v:.0f}M" if v > 10 else "" for v in holds_vals],
        textposition="inside",
        textfont=dict(size=10, color="#FFFCF2", family="-apple-system, system-ui, sans-serif"),
    ))
    fig.add_trace(go.Scatter(
        name="Cap Maximum", x=seasons, y=cap_max_vals,
        mode="lines+markers",
        line=dict(color="#FFFCF2", width=2, dash="dash"),
        marker=dict(size=6, color="#FFFCF2"),
    ))

    # 1st Apron line
    apron_vals = [contracts["apron_table"]["first_apron"][s]["threshold"] / 1_000_000 for s in seasons]
    fig.add_trace(go.Scatter(
        name="1st Apron", x=seasons, y=apron_vals,
        mode="lines+markers",
        line=dict(color=COLORS["loss_red"], width=2, dash="dot"),
        marker=dict(size=5, color=COLORS["loss_red"]),
    ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor=COLORS["bg_deepest"],
        plot_bgcolor=COLORS["bg_deepest"],
        font=dict(
            family="-apple-system, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif",
            color=COLORS["text_primary"], size=12,
        ),
        xaxis=dict(gridcolor="rgba(255,252,242,0.04)", tickfont=dict(color=COLORS["text_secondary"])),
        yaxis=dict(
            gridcolor="rgba(255,252,242,0.06)",
            tickfont=dict(color=COLORS["text_secondary"]),
            tickprefix="$", ticksuffix="M",
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(color=COLORS["text_secondary"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=60, r=20, t=40, b=40),
        height=400,
        hoverlabel=dict(
            bgcolor=COLORS["bg_card"], font_size=12,
            font_family="-apple-system, system-ui, sans-serif",
            font_color=COLORS["text_primary"], bordercolor=COLORS["accent_primary"],
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_detail:
    # Cap / Tax / Apron detail cards per season
    st.markdown(
        f'<div style="font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:400; '
        f'letter-spacing:1.5px; color:{COLORS["text_muted"]}; text-transform:uppercase; margin-bottom:12px;">'
        f'2025-26 Cap Details</div>',
        unsafe_allow_html=True,
    )
    current = contracts["cap_table"]["2025-26"]
    tax_current = contracts["tax_table"]["2025-26"]
    apron_1 = contracts["apron_table"]["first_apron"]["2025-26"]
    apron_2 = contracts["apron_table"]["second_apron"]["2025-26"]

    details = [
        ("Cap Maximum", current["cap_max"], COLORS["text_primary"], False),
        ("Total Allocations", current["total_allocations"], COLORS["warm_coral"], False),
        ("Cap Space", current["cap_space"], COLORS["loss_red"] if current["cap_space"] < 0 else COLORS["win_green"], False),
        ("Tax Threshold", apron_1["threshold"] - apron_1["space"] + tax_current["tax_space"], COLORS["text_primary"], True),
        ("Tax Space", tax_current["tax_space"], COLORS["win_green"] if tax_current["tax_space"] > 0 else COLORS["loss_red"], False),
        ("1st Apron", apron_1["threshold"], COLORS["text_primary"], True),
        ("1st Apron Space", apron_1["space"], COLORS["win_green"], False),
        ("2nd Apron", apron_2["threshold"], COLORS["text_primary"], True),
        ("2nd Apron Space", apron_2["space"], COLORS["win_green"], False),
    ]

    for label, val, color, has_border in details:
        is_space = "Space" in label
        val_str = _fmt_signed(val) if is_space or label == "Cap Space" else _fmt(val)
        border = "border-top:1px solid rgba(247,178,103,0.12); margin-top:4px; padding-top:8px;" if has_border else ""
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; align-items:center; padding:4px 0; {border}">'
            f'<span style="font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:400; letter-spacing:0.5px; color:{COLORS["text_secondary"]};">{label}</span>'
            f'<span style="font-family:var(--font-data); font-size:0.85rem; font-weight:700; color:{color}; font-variant-numeric:tabular-nums;">{val_str}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — CONTRACT DEADLINES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Key Deadlines")

deadlines = contracts["contract_deadlines"]

# Group by date
from collections import OrderedDict
deadline_groups = OrderedDict()
for d in deadlines:
    date_str = d["date"]
    if date_str not in deadline_groups:
        deadline_groups[date_str] = []
    deadline_groups[date_str].append(d)

TYPE_COLORS = {
    "guaranteed": ("#3fb950", "GUARANTEED"),
    "player_option": ("#F7B267", "PLAYER OPTION"),
    "club_option": ("#4da6ff", "CLUB OPTION"),
    "extension_eligible": ("#bb86fc", "EXTENSION ELIGIBLE"),
    "qualifying_offer": ("#CCC5B9", "QUALIFYING OFFER"),
}

# Render each deadline date group as its own self-contained card
for date_str, items in deadline_groups.items():
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    date_display = dt.strftime("%b %d, %Y")

    group_html = f'<div style="background:{COLORS["bg_card"]}; border:1px solid rgba(247,178,103,0.08); border-radius:10px; padding:12px 16px; margin-bottom:8px;">'
    group_html += f'<div style="font-family:\'Orbitron\',var(--font-data); font-size:10px; font-weight:700; letter-spacing:1px; color:{COLORS["accent_primary"]}; text-transform:uppercase; margin-bottom:6px; padding-bottom:4px; border-bottom:1px solid rgba(247,178,103,0.12);">{date_display}</div>'

    for item in items:
        tc, tl = TYPE_COLORS.get(item["type"], ("#6e6b64", item["type"].upper()))
        val_str = f' <span style="font-family:var(--font-data); font-variant-numeric:tabular-nums; font-weight:600; color:{COLORS["text_primary"]};">{_fmt(item["value"], short=True)}</span>' if item.get("value") else ""

        group_html += f'<div style="display:flex; align-items:center; gap:8px; padding:5px 0;">'
        group_html += f'<span style="font-family:\'Orbitron\',var(--font-data); font-size:8px; font-weight:700; letter-spacing:0.5px; padding:2px 6px; border-radius:3px; background:rgba({_hex_to_rgb(tc)},0.15); color:{tc}; white-space:nowrap;">{tl}</span>'
        group_html += f'<span style="font-family:var(--font-data); font-size:0.85rem; color:{COLORS["text_primary"]}; font-weight:500;">{item["player"]}</span>'
        group_html += f'<span style="font-family:var(--font-data); font-size:0.8rem; color:{COLORS["text_muted"]};">{item["detail"]}</span>'
        group_html += val_str
        group_html += '</div>'
    group_html += '</div>'
    _html(group_html)


st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — DRAFT CAPITAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### Draft Capital")

col_r1, col_r2 = st.columns(2)

with col_r1:
    _html(f"""
    <div style="font-family:'Orbitron',var(--font-data); font-size:11px; font-weight:700; letter-spacing:1px; color:{COLORS['accent_primary']}; text-transform:uppercase; margin-bottom:10px;">Round 1</div>
    """)

    for pick in contracts["draft_picks"]["round_1"]:
        year = pick["year"]
        holder = pick["holder"]
        note = pick.get("note", "")

        if holder == "MIA" and "owe" not in note.lower():
            badge_bg = "rgba(63,185,80,0.12)"
            badge_color = "#3fb950"
            icon = "&#10003;"
        elif "MIA" in holder and ("/" in holder or "if" in holder.lower()):
            badge_bg = "rgba(247,178,103,0.12)"
            badge_color = "#F7B267"
            icon = "&#9888;"
        else:
            badge_bg = "rgba(110,107,100,0.12)"
            badge_color = "#6e6b64"
            icon = "&#10005;"

        note_html = f'<div style="font-family:var(--font-data); font-size:11px; color:{COLORS["text_muted"]}; margin-top:2px;">{note}</div>' if note else ""
        pick_html = f'<div style="display:flex; align-items:flex-start; gap:10px; padding:8px 12px; margin-bottom:4px; background:{badge_bg}; border-radius:8px;">'
        pick_html += f'<span style="font-family:var(--font-data); font-size:1.1rem; min-width:20px; text-align:center; color:{badge_color};">{icon}</span>'
        pick_html += f'<div style="flex:1;"><div style="display:flex; justify-content:space-between; align-items:center;">'
        pick_html += f'<span style="font-family:\'Orbitron\',var(--font-data); font-size:12px; font-weight:700; color:{COLORS["text_primary"]}; font-variant-numeric:tabular-nums;">{year}</span>'
        pick_html += f'<span style="font-family:var(--font-data); font-size:0.8rem; color:{badge_color}; font-weight:600;">{holder}</span>'
        pick_html += f'</div>{note_html}</div></div>'
        _html(pick_html)

with col_r2:
    _html(f"""
    <div style="font-family:'Orbitron',var(--font-data); font-size:11px; font-weight:700; letter-spacing:1px; color:{COLORS['accent_primary']}; text-transform:uppercase; margin-bottom:10px;">Round 2</div>
    """)

    for pick in contracts["draft_picks"]["round_2"]:
        year = pick["year"]
        holder = pick["holder"]
        note = pick.get("note", "")

        if "MIA" in holder and "/" not in holder:
            badge_bg = "rgba(63,185,80,0.12)"
            badge_color = "#3fb950"
            icon = "&#10003;"
        elif "MIA" in holder:
            badge_bg = "rgba(247,178,103,0.12)"
            badge_color = "#F7B267"
            icon = "&#9888;"
        else:
            badge_bg = "rgba(110,107,100,0.12)"
            badge_color = "#6e6b64"
            icon = "&#10005;"

        note_html = f'<div style="font-family:var(--font-data); font-size:11px; color:{COLORS["text_muted"]}; margin-top:2px;">{note}</div>' if note else ""
        pick_html = f'<div style="display:flex; align-items:flex-start; gap:10px; padding:8px 12px; margin-bottom:4px; background:{badge_bg}; border-radius:8px;">'
        pick_html += f'<span style="font-family:var(--font-data); font-size:1.1rem; min-width:20px; text-align:center; color:{badge_color};">{icon}</span>'
        pick_html += f'<div style="flex:1;"><div style="display:flex; justify-content:space-between; align-items:center;">'
        pick_html += f'<span style="font-family:\'Orbitron\',var(--font-data); font-size:12px; font-weight:700; color:{COLORS["text_primary"]}; font-variant-numeric:tabular-nums;">{year}</span>'
        pick_html += f'<span style="font-family:var(--font-data); font-size:0.8rem; color:{badge_color}; font-weight:600;">{holder}</span>'
        pick_html += f'</div>{note_html}</div></div>'
        _html(pick_html)


# ── Source attribution ────────────────────────────────────────────────────────
_html(f"""
<div style="text-align:center; margin-top:24px; padding:12px 0;">
  <span style="font-family:'Orbitron',var(--font-data); font-size:9px; font-weight:400; letter-spacing:1px; color:{COLORS['text_muted']}; text-transform:uppercase;">
    Data via <a href="https://www.spotrac.com/nba/miami-heat/yearly" target="_blank" style="color:{COLORS['accent_primary']}; text-decoration:none;">Spotrac.com</a> &nbsp;|&nbsp; Updated {contracts['last_updated']}
  </span>
</div>
""")
