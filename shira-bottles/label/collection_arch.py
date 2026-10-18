"""SHIRÁ "arch" label design: full-colour front with the fruit framed in a
deeper-toned arched window, cream wordmark and flavour name on the colour.
The back panel is unchanged from the collection layout.

Run:  python3 collection_arch.py
      -> collection-arch/shira-<flavour>-label.svg (print, with dieline)
         collection-arch/shira-<flavour>-label-texture.svg (no dieline)
"""

import random
from pathlib import Path

import collection as c

HERE = Path(__file__).parent
OUT = HERE / "collection-arch"
c.STYLE = "citrus"

FRONT_W, TRIM_H, BLEED, SERIF, SANS, CREAM = c.FRONT_W, c.TRIM_H, c.BLEED, c.SERIF, c.SANS, c.CREAM


def shade(hex_colour, k):
    """Mix a #RRGGBB colour towards black (k < 0) or white (k > 0)."""
    rgb = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    t = 255 if k > 0 else 0
    return "#" + "".join(f"{round(v + (t - v) * abs(k)):02X}" for v in rgb)


def front(f):
    cx = FRONT_W / 2
    aw, top = 62, 33
    x0, x1 = cx - aw / 2, cx + aw / 2
    arch = (f"M {x0} {TRIM_H + BLEED} V {top + aw / 2} A {aw / 2} {aw / 2} 0 0 1 {x1} {top + aw / 2} "
            f"V {TRIM_H + BLEED} Z")
    art = c.ART[f["key"]](cx, 58, 24, random.Random(f["key"]))
    name_size = 9.5 if len(f["name"]) <= 9 else 8.5
    return f"""
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" fill="{f['band']}"/>
<path d="{arch}" fill="{shade(f['band'], -0.28)}"/>
<path d="{arch}" fill="none" stroke="{CREAM}" stroke-width="0.35" transform="translate(0 -1.6)" opacity="0.7"/>
<clipPath id="arch-{f['key']}"><path d="{arch}"/></clipPath>
<g clip-path="url(#arch-{f['key']})">{art}</g>
<text x="{cx}" y="12" text-anchor="middle" font-family="{SERIF}" font-weight="500" font-size="11" letter-spacing="2.4" fill="{CREAM}">SHIRÁ</text>
<text x="{cx}" y="23.4" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="{name_size}" fill="{CREAM}">{f['name']}</text>
<text x="{cx}" y="29" text-anchor="middle" font-family="{SANS}" font-size="1.9" letter-spacing="0.5" fill="{CREAM}" opacity="0.85">100% NATURAL JUICE · NOT FROM CONCENTRATE</text>
<text x="{cx}" y="85.6" text-anchor="middle" font-family="{SANS}" font-weight="500" font-size="5" fill="{CREAM}">500 ml</text>
<text x="{cx}" y="89.6" text-anchor="middle" font-family="{SANS}" font-size="1.9" letter-spacing="0.5" fill="{CREAM}" opacity="0.85">PRODUCT OF AZERBAIJAN</text>"""


def main():
    c.front = front
    OUT.mkdir(exist_ok=True)
    for f in c.FLAVOURS:
        (OUT / f"shira-{f['key']}-label.svg").write_text(c.svg(f, True), encoding="utf-8")
        (OUT / f"shira-{f['key']}-label-texture.svg").write_text(c.svg(f, False), encoding="utf-8")


if __name__ == "__main__":
    main()
