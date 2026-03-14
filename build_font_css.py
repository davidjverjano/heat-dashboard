"""Load @font-face CSS with base64-embedded font data.

Uses a pre-built CSS file (assets/fonts_base64.css) for deployment.
Falls back to generating from font files at runtime if the pre-built
file is missing (local development with font files present).
"""
import base64, pathlib

_ROOT = pathlib.Path(__file__).resolve().parent
_PREBUILT = _ROOT / "assets" / "fonts_base64.css"
FONT_DIR = _ROOT / "assets" / "fonts"

FONTS = [
    {
        "family": "Hyperspace",
        "file": "hyperspaceracecapsule-variablevf-14.ttf",
        "fmt": "truetype",
        "weight": "100 900",
    },
    {
        "family": "Hyperspace",
        "file": "hyperspaceracecapsule-bold-27.otf",
        "fmt": "opentype",
        "weight": "700",
    },
    {
        "family": "Hyperspace",
        "file": "hyperspaceracecapsule-heavy-28.otf",
        "fmt": "opentype",
        "weight": "900",
    },
    {
        "family": "Hyperspace",
        "file": "hyperspaceracecapsule-regular-30.otf",
        "fmt": "opentype",
        "weight": "400",
    },
    {
        "family": "Hyperspace Wide",
        "file": "hyperspaceracecapsule-widebold-15.otf",
        "fmt": "opentype",
        "weight": "700",
    },
]


def build_font_css() -> str:
    """Return CSS with @font-face rules.

    1. Try pre-built file (works on Streamlit Cloud where font binaries
       are not present).
    2. Fall back to generating from raw font files (local dev).
    """
    # \u2500\u2500 1. Pre-built file (preferred for deployment) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    if _PREBUILT.exists():
        return _PREBUILT.read_text()

    # \u2500\u2500 2. Generate from font binaries (local development) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    blocks = []
    for f in FONTS:
        path = FONT_DIR / f["file"]
        if not path.exists():
            continue
        b64 = base64.b64encode(path.read_bytes()).decode()
        mime = "font/ttf" if f["fmt"] == "truetype" else "font/otf"
        blocks.append(
            f"@font-face {{\n"
            f"  font-family: '{f['family']}';\n"
            f"  src: url('data:{mime};base64,{b64}') format('{f['fmt']}');\n"
            f"  font-weight: {f['weight']};\n"
            f"  font-style: normal;\n"
            f"  font-display: swap;\n"
            f"}}"
        )
    return "\n\n".join(blocks)


if __name__ == "__main__":
    css = build_font_css()
    print(css[:500], "...")
    print(f"\nTotal length: {len(css)} chars")
    print(f"Source: {'pre-built file' if _PREBUILT.exists() else 'generated from font files'}")
