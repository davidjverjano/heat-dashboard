"""Shared page setup — call at the top of every page to load fonts, CSS, and nav."""
import pathlib
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Google Fonts @import for Orbitron — must be first line inside <style>
_ORBITRON_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Orbitron:wght@400;500;600;700;800;900&display=swap');"
)


def setup_page():
    """Inject fonts, custom CSS, and render top nav bar.

    Call this once at the very top of every page file, right after any
    st.set_page_config() if present (or Streamlit will error).
    """
    from components.nav import render_top_nav

    css_file = ROOT / "assets" / "style.css"
    main_css = css_file.read_text() if css_file.exists() else ""
    # Critical nav fixes — override Streamlit emotion CSS
    nav_fix = (
        '[data-testid="stHeader"]{background:transparent!important;'
        'backdrop-filter:none!important;-webkit-backdrop-filter:none!important}'
        '.cc-topbar{z-index:999995!important}'
        '.cc-hamburger{display:flex!important}'
        '.cc-page-links{display:none!important}'
        'body.cc-menu-open .cc-page-links{display:flex!important;flex-direction:column!important}'
    )
    # @import MUST be first inside <style> for browser compliance
    st.markdown(
        f"<style>{_ORBITRON_IMPORT}\n{main_css}\n{nav_fix}</style>",
        unsafe_allow_html=True,
    )

    render_top_nav()
