"""Shared page setup — call at the top of every page to load fonts, CSS, and nav."""
import pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent.parent


def setup_page():
    """Inject fonts (base64), custom CSS, and render top nav bar.
    
    Call this once at the very top of every page file, right after any
    st.set_page_config() if present (or Streamlit will error).
    """
    from build_font_css import build_font_css
    from components.nav import render_top_nav

    font_css = build_font_css()
    css_file = ROOT / "assets" / "style.css"
    main_css = css_file.read_text() if css_file.exists() else ""
    st.markdown(f"<style>{font_css}\n{main_css}</style>", unsafe_allow_html=True)

    render_top_nav()
