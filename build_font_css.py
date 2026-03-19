"""Load @font-face / @import CSS for hybrid font stack.

Hyperspace Race Capsule — primary headlines, brand text (base64 embedded).
Orbitron — subheaders, labels, UI text (Google Fonts CDN).
System font stack — all numeric data (no DEMO glyph issues).
"""
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent
_PREBUILT = _ROOT / "assets" / "fonts_base64.css"


def build_font_css() -> str:
    """Return CSS that loads both Hyperspace (base64) and Orbitron (CDN).

    1. Try pre-built file first (has both @font-face and @import).
    2. Fall back to Orbitron-only @import rule.
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
