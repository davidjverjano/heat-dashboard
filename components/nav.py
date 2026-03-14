"""Horizontal top navigation bar — replaces default Streamlit sidebar nav."""
import base64, pathlib, streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Page definitions: (label, file_path_relative_to_pages_dir)
PAGES = [
    ("Overview", "pages/1_Overview.py"),
    ("Last Game", "pages/2_Last_Game.py"),
    ("Trends", "pages/3_Weekly_Trends.py"),
    ("Season", "pages/4_Season_View.py"),
    ("Players", "pages/5_Players.py"),
    ("Narratives", "pages/6_Narratives.py"),
]


def _cc_icon_b64() -> str | None:
    icon = ROOT / "assets" / "cc-icon.svg"
    if not icon.exists():
        return None
    svg = icon.read_text().replace('<svg ', '<svg fill="#FFFCF2" ', 1)
    return base64.b64encode(svg.encode()).decode()


def render_top_nav():
    """Render the full-width horizontal navigation bar at the top of every page."""
    icon_b64 = _cc_icon_b64()
    icon_html = (
        f'<img src="data:image/svg+xml;base64,{icon_b64}" '
        f'style="width:28px; height:auto; display:block;"/>'
        if icon_b64 else ""
    )

    # Brand bar with hamburger toggle for mobile.
    # Uses a small inline script to toggle a body class that controls
    # the visibility of the Streamlit page-link row below.
    st.markdown(
        f'''<div class="cc-top-nav">
            <div class="cc-nav-inner">
                <button class="cc-hamburger-btn" onclick="document.body.classList.toggle('cc-menu-open')" aria-label="Menu">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <rect class="cc-ham-line cc-ham-1" y="3" width="20" height="2" rx="1" fill="#FFFCF2"/>
                        <rect class="cc-ham-line cc-ham-2" y="9" width="20" height="2" rx="1" fill="#FFFCF2"/>
                        <rect class="cc-ham-line cc-ham-3" y="15" width="20" height="2" rx="1" fill="#FFFCF2"/>
                    </svg>
                </button>
                <div class="cc-nav-brand">
                    {icon_html}
                    <span class="cc-nav-brand-text">
                        COURTSIDE<span class="cc-nav-brand-accent">CRE8IVES</span>
                    </span>
                </div>
                <div class="cc-nav-spacer"></div>
                <div class="cc-nav-season">2025-26</div>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )

    # Page links row using Streamlit's native page_link (ensures routing works)
    cols = st.columns(len(PAGES))
    for i, (label, path) in enumerate(PAGES):
        with cols[i]:
            st.page_link(path, label=label)
