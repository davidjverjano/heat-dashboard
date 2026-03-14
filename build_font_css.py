"""Generate @font-face CSS with base64-embedded font data.

Run once or at app startup to produce a <style> block that works
inside Streamlit's st.markdown() without needing static file serving.
"""
import base64, pathlib

FONT_DIR = pathlib.Path(__file__).resolve().parent / "assets" / "fonts"

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
    """Return a CSS string with all @font-face rules using data-URIs."""
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
    print(build_font_css()[:500], "...")
    print(f"\nTotal length: {len(build_font_css())} chars")
