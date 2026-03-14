"""Horizontal top navigation bar — replaces default Streamlit sidebar nav."""
import base64, pathlib, streamlit as st
import streamlit.components.v1 as components

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

    # Brand bar with hamburger button (no onclick — Streamlit strips it).
    # JS is injected via components.html() below to wire the click handler.
    st.markdown(
        f'<div class="cc-top-nav">'
        f'<div class="cc-nav-inner">'
        f'<button class="cc-hamburger-btn" id="ccHamburger" aria-label="Menu">'
        f'<svg width="20" height="20" viewBox="0 0 20 20" fill="none">'
        f'<rect class="cc-ham-line cc-ham-1" y="3" width="20" height="2" rx="1" fill="#FFFCF2"/>'
        f'<rect class="cc-ham-line cc-ham-2" y="9" width="20" height="2" rx="1" fill="#FFFCF2"/>'
        f'<rect class="cc-ham-line cc-ham-3" y="15" width="20" height="2" rx="1" fill="#FFFCF2"/>'
        f'</svg>'
        f'</button>'
        f'<div class="cc-nav-brand">'
        f'{icon_html}'
        f'<span class="cc-nav-brand-text">'
        f'COURTSIDE<span class="cc-nav-brand-accent">CRE8IVES</span>'
        f'</span>'
        f'</div>'
        f'<div class="cc-nav-spacer"></div>'
        f'<div class="cc-nav-season">2025-26</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Inject JS via components.html (renders in iframe, reaches parent doc).
    # This wires the hamburger button click to toggle body.cc-menu-open
    # which controls nav visibility via CSS media queries in style.css.
    components.html(
        """<script>
(function(){
  var doc = window.parent.document;
  function wire(){
    var btn = doc.getElementById('ccHamburger');
    if(!btn || btn.dataset.wired) return;
    btn.dataset.wired = '1';
    btn.addEventListener('click', function(){
      doc.body.classList.toggle('cc-menu-open');
    });
  }
  wire();
  var n=0, iv=setInterval(function(){
    wire(); n++;
    if(n>30 || (doc.getElementById('ccHamburger') && doc.getElementById('ccHamburger').dataset.wired)) clearInterval(iv);
  }, 150);
})();
</script>""",
        height=0,
        scrolling=False,
    )

    # Page links row using Streamlit's native page_link (ensures routing works)
    cols = st.columns(len(PAGES))
    for i, (label, path) in enumerate(PAGES):
        with cols[i]:
            st.page_link(path, label=label)
