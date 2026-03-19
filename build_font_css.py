"""Load @font-face / @import CSS for Orbitron (Google Fonts).

Previously loaded Hyperspace Race Capsule DEMO via base64 data URIs.
Replaced with Orbitron — a free, full-glyph geometric display font.
"""
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent
_PREBUILT = _ROOT / "assets" / "fonts_base64.css"


def build_font_css() -> str:
    """Return CSS that loads Orbitron from Google Fonts CDN.

    1. Try pre-built file first (for consistency).
    2. Fall back to inline @import rule.
    """
    if _PREBUILT.exists():
        return _PREBUILT.read_text()

    return _orbitron_import()


def _orbitron_import() -> str:
    return (
        "@import url('https://fonts.googleapis.com/css2?"
        "family=Orbitron:wght@400;500;600;700;800;900&display=swap');\n"
    )


if __name__ == "__main__":
    css = build_font_css()
    print(css[:500], "...")
    print(f"\nTotal length: {len(css)} chars")
