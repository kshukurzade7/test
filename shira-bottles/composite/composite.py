"""Add flavour-specific fruit illustrations onto the original SHIRÁ render.

The original bottle render (base.png) is kept untouched; each label's coloured
band gets a small full-colour fruit drawing in its empty left area, between
the local fruit name and the "PRODUCT OF AZERBAIJAN" line.

Run:  python3 composite.py  ->  shira-with-fruit.svg (open/render it to PNG).
"""

import base64
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from generate import FRUIT_DEFS, fruit_art  # noqa: E402

W, H = 613, 569
# (fruit key, centre x, centre y, scale) in base.png pixel coordinates
PLACEMENTS = [
    ("apricot", 131, 444, 0.48),
    ("pomegranate", 295, 448, 0.5),
    ("grape", 470, 442, 0.52),
]


def main():
    img = base64.b64encode((HERE / "base.png").read_bytes()).decode()
    fruits = "\n".join(
        f'<g transform="translate({x} {y}) scale({s})" filter="url(#soft)">{fruit_art(k)}</g>'
        for k, x, y, s in PLACEMENTS)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  {FRUIT_DEFS}
  <!-- slight softening + drop shadow so the vector art sits in the photo -->
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="0.25" result="b"/>
    <feGaussianBlur in="SourceAlpha" stdDeviation="1.2" result="s"/>
    <feOffset in="s" dx="0.6" dy="1" result="so"/>
    <feComponentTransfer in="so" result="sh"><feFuncA type="linear" slope="0.35"/></feComponentTransfer>
    <feMorphology in="SourceAlpha" operator="dilate" radius="1.4" result="d"/>
    <feGaussianBlur in="d" stdDeviation="1.6" result="dg"/>
    <feFlood flood-color="#F6EFE3" flood-opacity="0.45"/>
    <feComposite in2="dg" operator="in" result="glow"/>
    <feMerge><feMergeNode in="glow"/><feMergeNode in="sh"/><feMergeNode in="b"/></feMerge>
  </filter>
</defs>
<image href="data:image/png;base64,{img}" width="{W}" height="{H}"/>
{fruits}
</svg>
"""
    (HERE / "shira-with-fruit.svg").write_text(svg, encoding="utf-8")
    (HERE / "view.html").write_text(
        f'<body style="margin:0">{svg}</body>', encoding="utf-8")


if __name__ == "__main__":
    main()
