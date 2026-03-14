"""
Courtside Cre8ives — Components Package.

This package provides reusable UI components for the Streamlit dashboard:
- charts.py   : Plotly chart factory functions
- metrics.py  : KPI card / metric row components
- tables.py   : Styled DataFrame display helpers
- theme.py    : Brand colours and Plotly theme defaults
"""

from components.theme import COLORS, apply_plotly_theme

__all__ = ["COLORS", "apply_plotly_theme"]
