"""SHIRÁ "buta" label design: warm cream paper with a tonal field of Azerbaijani
buta (paisley) motifs, a gold double frame, and the fruit set in one large
flavour-coloured buta. Back panel unchanged from the collection layout.

Run:  python3 collection_buta.py
      -> collection-buta/shira-<flavour>-label.svg (print, with dieline)
         collection-buta/shira-<flavour>-label-texture.svg (no dieline)
"""

import random
from pathlib import Path

import collection as c
from collection_arch import shade

HERE = Path(__file__).parent
OUT = HERE / "collection-buta"
c.STYLE = "citrus"

FRONT_W, TRIM_H, BLEED, SERIF, SANS, CREAM, INK, GOLD = (
    c.FRONT_W, c.TRIM_H, c.BLEED, c.SERIF, c.SANS, c.CREAM, c.INK, c.GOLD)
PAPER = "#FBF4E6"
# buta in a unit box (tip up, belly down, tip curling right)
BUTA = ("M 0.42 -1.02 C 0.58 -0.62 0.98 -0.16 0.86 0.46 C 0.74 1.02 0.05 1.12 -0.42 0.9 "
        "C -0.95 0.64 -0.98 -0.08 -0.5 -0.42 C -0.18 -0.64 0.1 -0.62 0.2 -0.84 C 0.28 -0.98 0.3 -1.04 0.42 -1.02 Z")


def buta(x, y, s, rot=0, extra=""):
    return f'<path d="{BUTA}" transform="translate({x:.2f} {y:.2f}) rotate({rot}) scale({s:.2f})" {extra}/>'


def ring(x, y, s, width):
    return buta(x, y, s, 0, f'fill="none" stroke="{GOLD}" stroke-width="{width / s:.4f}"')


def pattern(colour):
    out = []
    step = 9.5
    for row in range(-1, 11):
        for col in range(-1, 11):
            x = col * step + (step / 2 if row % 2 else 0)
            y = row * step * 0.9
            out.append(buta(x, y, 1.9, 28 if (row + col) % 2 else -28))
    return f'<g fill="{colour}" opacity="0.07">{"".join(out)}</g>'


def front(f):
    cx = FRONT_W / 2
    accent, band = f["accent"], f["band"]
    art = c.ART[f["key"]](cx, 62, 20, random.Random(f["key"]))
    clip = f"buta-{f['key']}"
    bx, by, bs = cx, 62.5, 23.5
    ns = 9.5 if len(f["name"]) <= 9 else 8.4
    return f"""
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" fill="{PAPER}"/>
{pattern(accent)}
<rect x="4.2" y="4.2" width="{FRONT_W - 8.4}" height="{TRIM_H - 8.4}" fill="none" stroke="{GOLD}" stroke-width="0.35"/>
<rect x="5.4" y="5.4" width="{FRONT_W - 10.8}" height="{TRIM_H - 10.8}" fill="none" stroke="{GOLD}" stroke-width="0.15"/>
<rect x="14" y="8" width="{FRONT_W - 28}" height="26" fill="{PAPER}"/>
<text x="{cx}" y="17" text-anchor="middle" font-family="{SERIF}" font-weight="600" font-size="11.5" letter-spacing="2.6" fill="{INK}">SHIRÁ</text>
<text x="{cx}" y="27.5" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-weight="500" font-size="{ns}" fill="{accent}">{f['name']}</text>
<text x="{cx}" y="32.2" text-anchor="middle" font-family="{SANS}" font-size="1.8" letter-spacing="0.5" fill="#6B5A4E">100% NATURAL JUICE · NOT FROM CONCENTRATE</text>
{buta(bx, by, bs + 2.2, 0, f'fill="{PAPER}"')}
{ring(bx, by, bs + 1.4, 0.45)}
<clipPath id="{clip}"><path d="{BUTA}" transform="translate({bx} {by}) scale({bs})"/></clipPath>
{buta(bx, by, bs, 0, f'fill="{band}"')}
<g clip-path="url(#{clip})">{art}</g>
<text x="9.5" y="85.4" font-family="{SANS}" font-weight="600" font-size="4.6" fill="{INK}">500</text>
<text x="9.5" y="88.6" font-family="{SANS}" font-size="2.2" letter-spacing="0.4" fill="{INK}">ml</text>
<text x="{FRONT_W - 9.5}" y="84.6" text-anchor="end" font-family="{SANS}" font-size="1.8" letter-spacing="0.45" fill="#6B5A4E">PRODUCT OF</text>
<text x="{FRONT_W - 9.5}" y="87.4" text-anchor="end" font-family="{SANS}" font-weight="500" font-size="1.8" letter-spacing="0.45" fill="#6B5A4E">AZERBAIJAN</text>"""


def main():
    c.front = front
    OUT.mkdir(exist_ok=True)
    for f in c.FLAVOURS:
        (OUT / f"shira-{f['key']}-label.svg").write_text(c.svg(f, True), encoding="utf-8")
        (OUT / f"shira-{f['key']}-label-texture.svg").write_text(c.svg(f, False), encoding="utf-8")


if __name__ == "__main__":
    main()
