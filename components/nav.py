"""Top navigation bar — unified hamburger menu on all screen sizes.

Layout:  [Hamburger ☰]  [Logo COURTSIDE CRE8IVES]  (spacer)  [Social Icons]  [Season Badge]
Menu:    Slide-down panel with page links — same on desktop and mobile.
"""
import base64, pathlib, streamlit as st
import streamlit.components.v1 as components

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = [
    ("Overview", "pages/1_Overview.py"),
    ("Last Game", "pages/2_Last_Game.py"),
    ("Trends", "pages/3_Weekly_Trends.py"),
    ("Season", "pages/4_Season_View.py"),
    ("Players", "pages/5_Players.py"),
    ("Narratives", "pages/6_Narratives.py"),
]

SOCIALS = [
    ("X", "https://x.com/courtcre8ives",
     '<svg width="14" height="14" viewBox="0 0 24 24" fill="#b0ada6"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'),
    ("Instagram", "https://www.instagram.com/courtsidecre8ives",
     '<svg width="14" height="14" viewBox="0 0 24 24" fill="#b0ada6"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>'),
    ("TikTok", "https://www.tiktok.com/@courtsidecre8ives",
     '<svg width="14" height="14" viewBox="0 0 24 24" fill="#b0ada6"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 0010.86 4.46V13a8.28 8.28 0 005.58 2.16V11.7a4.83 4.83 0 01-3.77-1.79V6.69z"/></svg>'),
]


def _cc_icon_b64() -> str | None:
    icon = ROOT / "assets" / "cc-icon.svg"
    if not icon.exists():
        return None
    svg = icon.read_text().replace('<svg ', '<svg fill="#FFFCF2" ', 1)
    return base64.b64encode(svg.encode()).decode()


def render_top_nav():
    """Render the navigation bar with hamburger menu on all screen sizes."""
    icon_b64 = _cc_icon_b64()
    icon_html = (
        f'<img src="data:image/svg+xml;base64,{icon_b64}" '
        f'class="cc-nav-logo"/>'
        if icon_b64 else ""
    )

    # Build social icons HTML
    social_html = ""
    for name, url, svg in SOCIALS:
        social_html += (
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'class="cc-nav-social" title="{name}">{svg}</a>'
        )

    # Single topbar with hamburger always visible
    st.markdown(
f'<div class="cc-topbar">'
f'<div class="cc-topbar-inner">'
f'<button class="cc-hamburger" id="ccHamburger" aria-label="Menu">'
f'<svg width="18" height="18" viewBox="0 0 20 20" fill="none">'
f'<rect class="cc-ham-line cc-ham-1" y="3" width="20" height="2" rx="1" fill="#FFFCF2"/>'
f'<rect class="cc-ham-line cc-ham-2" y="9" width="20" height="2" rx="1" fill="#FFFCF2"/>'
f'<rect class="cc-ham-line cc-ham-3" y="15" width="20" height="2" rx="1" fill="#FFFCF2"/>'
f'</svg>'
f'</button>'
f'<a class="cc-topbar-brand" href="/" target="_self">'
f'{icon_html}'
f'<span class="cc-topbar-brand-text">'
f'COURTSIDE<span class="cc-topbar-accent">CRE8IVES</span>'
f'</span>'
f'</a>'
f'<div class="cc-topbar-right">'
f'{social_html}'
f'<span class="cc-topbar-season">2025-26</span>'
f'</div>'
f'</div>'
f'</div>',
        unsafe_allow_html=True,
    )

    # Inject JS for hamburger toggle via components.html
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
    // Close menu when a page link is clicked
    var links = doc.querySelectorAll('[data-testid="stPageLink"] a');
    links.forEach(function(a){
      a.addEventListener('click', function(){
        doc.body.classList.remove('cc-menu-open');
      });
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

    # Page links — rendered by Streamlit for routing, hidden by default, shown on menu open
    cols = st.columns(len(PAGES))
    for i, (label, path) in enumerate(PAGES):
        with cols[i]:
            st.page_link(path, label=label)
