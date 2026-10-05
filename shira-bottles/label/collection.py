"""SHIRÁ flavour collection: print-ready wrap labels for the extended range.

English-only labels in the original layout (cream top, colour band with a
tone-on-tone fruit, full back panel), with the citrus-slice SHIRÁ mark and a
small Azerbaijan flag beside PRODUCT OF AZERBAIJAN.

Run:  python3 collection.py
      -> collection/shira-<flavour>-label.svg (print, with dieline)
         collection/shira-<flavour>-label-texture.svg (no dieline)
"""

import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "photo"))
sys.path.insert(0, str(HERE.parent / "composite"))
from photo import embedded_fonts, emblem, az_flag  # noqa: E402
from hero import HERO  # noqa: E402
from fruits import FRUITS  # noqa: E402
import label as base  # noqa: E402  (shared helpers: wrap, text_lines, dieline, constants)

TRIM_W, TRIM_H, BLEED, FRONT_W, SPLIT = base.TRIM_W, base.TRIM_H, base.BLEED, base.FRONT_W, base.SPLIT
SERIF, SANS, CREAM, INK, BODY, GOLD = base.SERIF, base.SANS, base.CREAM, base.INK, base.BODY, base.GOLD
wrap, text_lines = base.wrap, base.text_lines

ART = {**HERO, **FRUITS}
OUT = HERE / "collection"

# "original" reproduces the first proof's design exactly (original mark, no flag);
# "current" uses the redrawn citrus-slice mark and the small flag.
STYLE = "current"


def original_emblem(c, r):
    """The original SHIRÁ mark from the first proof: disc with eight rounded spokes."""
    import math
    spokes = "".join(
        f'<line x1="0" y1="0" x2="{r*0.86*math.cos(a):.3f}" y2="{r*0.86*math.sin(a):.3f}" '
        f'stroke="{CREAM}" stroke-width="{r*0.17:.3f}" stroke-linecap="round"/>'
        for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)])
    return f'<circle r="{r}" fill="{c}"/>{spokes}<circle r="{r*0.26:.3f}" fill="{CREAM}"/>'


def mark(c, r):
    return original_emblem(c, r) if STYLE == "original" else emblem(c, r)


def origin_line():
    if STYLE in ("original", "citrus"):
        return f'<text x="9" y="88.2" font-family="{SANS}" font-size="2.0" letter-spacing="0.55" fill="{CREAM}">PRODUCT OF AZERBAIJAN</text>'
    return (f'<g transform="translate(9 84.9)">{az_flag(7)}</g>'
            f'<text x="18.4" y="88.2" font-family="{SANS}" font-size="2.0" letter-spacing="0.55" fill="{CREAM}">PRODUCT OF AZERBAIJAN</text>')

# band = colour block, accent = flavour name + mark, juice = liquid colour for mockups
FLAVOURS = [
    dict(key="blackcurrant", name="Blackcurrant", band="#3B2240", accent="#4A2752", juice="#2A0E2C",
         story="Dark, fragrant blackcurrants from Azerbaijan's hills, pressed for a deep, bold juice. Nothing added."),
    dict(key="redcurrant", name="Redcurrant", band="#C21F3A", accent="#B81C36", juice="#C0182E",
         story="Bright redcurrants, hand-picked in Azerbaijan and pressed for a crisp, lively juice. Nothing added."),
    dict(key="peach", name="Peach", band="#EE9468", accent="#D9663F", juice="#F0A86A",
         story="Soft, sun-ripened peaches from Azerbaijan's orchards, pressed into a smooth, golden juice. Nothing added."),
    dict(key="cranberry", name="Cranberry", band="#8E1638", accent="#8E1638", juice="#9A1230",
         story="Tart cranberries, gently pressed for a clean, refreshing juice. Nothing added, nothing taken away."),
    dict(key="pear", name="Pear", band="#9AA13A", accent="#7A8226", juice="#E3D27A",
         story="Juicy late-summer pears from Azerbaijan, pressed for a mellow, delicate juice. Nothing added."),
    dict(key="quince", name="Quince", band="#C8952C", accent="#A9741A", juice="#E6B54A",
         story="Fragrant golden quinces, an Azerbaijani autumn favourite, pressed into an aromatic juice. Nothing added."),
    dict(key="pumpkin", name="Pumpkin", band="#D9631F", accent="#C4541A", juice="#E8782A",
         story="Sweet autumn pumpkins from Azerbaijan's fields, pressed into a velvety, warming juice. Nothing added."),
    dict(key="feijoa", name="Feijoa", band="#4F7A3A", accent="#3F6630", juice="#D8DDA0",
         story="Aromatic feijoa from Azerbaijan's subtropical south, pressed for a fresh, exotic juice. Nothing added."),
    dict(key="rosehip", name="Rosehip", band="#C2452E", accent="#B03A26", juice="#C8461E",
         story="Wild rosehips, naturally rich in vitamin C, pressed into a bright, tangy juice. Nothing added."),
    dict(key="hawthorn", name="Hawthorn", band="#8A3A2F", accent="#7E3128", juice="#A8452A",
         story="Wild hawthorn berries from Azerbaijan's mountains, pressed for a gentle, fruity juice. Nothing added."),
    dict(key="pomegranate", name="Pomegranate", band="#A82334", accent="#A8172C", juice="#B00E2C",
         story="Ruby pomegranates from Azerbaijan, gently pressed for a deep, tart juice. Nothing added, nothing taken away."),
    dict(key="apple", name="Apple", band="#5F9A3A", accent="#4E842E", juice="#E2B24A",
         story="Crisp apples from Azerbaijan's orchards, pressed and bottled for a pure, clear juice. Nothing added."),
]
for f in FLAVOURS:
    f["ingredients"] = f"{f['name']} juice (100%)."


def front(f):
    cx = FRONT_W / 2
    band_h = TRIM_H - SPLIT
    art = ART[f["key"]](FRONT_W * 0.66, SPLIT + band_h * 0.5, band_h * 0.6, random.Random(f["key"]))
    name_size = 9 if len(f["name"]) <= 9 else 8
    return f"""
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{SPLIT + BLEED}" fill="{CREAM}"/>
<rect x="{-BLEED}" y="{SPLIT}" width="{FRONT_W + BLEED}" height="{band_h + BLEED}" fill="{f['band']}"/>
<clipPath id="band-{f['key']}"><rect x="{-BLEED}" y="{SPLIT}" width="{FRONT_W + BLEED}" height="{band_h + BLEED}"/></clipPath>
<g clip-path="url(#band-{f['key']})">{art}</g>
<g transform="translate({cx} 12.5)">{mark(f['accent'], 5.2)}</g>
<text x="{cx}" y="30" text-anchor="middle" font-family="{SERIF}" font-weight="500" font-size="13.5" letter-spacing="2.9" fill="{INK}">SHIRÁ</text>
<line x1="{cx - 7}" y1="34" x2="{cx + 7}" y2="34" stroke="{GOLD}" stroke-width="0.35"/>
<text x="{cx}" y="43" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="{name_size}" fill="{f['accent']}">{f['name']}</text>
<text x="{cx}" y="49.3" text-anchor="middle" font-family="{SANS}" font-size="2.0" letter-spacing="0.5" fill="#6B5A4E">100% NATURAL JUICE · NOT FROM CONCENTRATE</text>
{origin_line()}
<text x="{FRONT_W - 8}" y="88.6" text-anchor="end" font-family="{SANS}" font-weight="500" font-size="6" fill="{CREAM}">500 ml</text>"""


def back(f):
    x0 = FRONT_W + 7
    bx = x0 + 45
    sans = f'font-family="{SANS}" fill="{BODY}"'

    def head(x, y, t):
        return f'<text x="{x}" y="{y:.2f}" font-size="2.0" letter-spacing="0.5" font-weight="500" {sans}>{t}</text>'

    def body(lines, x, y):
        return text_lines(lines, x, y, 2.4, 3.05, font_family=SANS, fill=BODY)

    out = [
        f'<rect x="{FRONT_W}" y="{-BLEED}" width="{TRIM_W - FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" fill="{CREAM}"/>',
        f'<rect x="{FRONT_W}" y="{-BLEED}" width="{TRIM_W - FRONT_W + BLEED}" height="{BLEED + 2.2}" fill="{f["band"]}"/>',
        f'<rect x="{FRONT_W}" y="{TRIM_H - 2.2}" width="{TRIM_W - FRONT_W + BLEED}" height="{BLEED + 2.2}" fill="{f["band"]}"/>',
        f'<g transform="translate({x0 + 3} 12)">{mark(f["accent"], 2.7)}</g>',
        f'<text x="{x0 + 8}" y="13.9" font-family="{SERIF}" font-size="5.8" letter-spacing="1.3" fill="{INK}">SHIRÁ</text>',
        f'<text x="{x0 + 8}" y="19.6" font-family="{SERIF}" font-style="italic" font-size="4.2" fill="{f["accent"]}">{f["name"]} juice</text>',
    ]
    story = wrap(f["story"], 66)
    out.append(text_lines(story, x0, 26.5, 2.9, 3.6, font_family=SERIF, font_style="italic", fill=BODY))
    top = 26.5 + len(story) * 3.6 + 3.2
    out.append(f'<line x1="{x0}" y1="{top - 2.6:.2f}" x2="{TRIM_W - 7}" y2="{top - 2.6:.2f}" stroke="#D8C9B6" stroke-width="0.2"/>')

    y = top + 1
    out.append(head(x0, y, "INGREDIENTS"))
    ing = wrap(f["ingredients"] + " No added sugar, water, colours or preservatives. Pasteurised.", 28)
    out.append(body(ing, x0, y + 3.2))
    y += 3.2 + len(ing) * 3.05 + 1.6
    out.append(head(x0, y, "STORAGE"))
    st = wrap("Shake well. Store cool and dry, away from sunlight. Once opened, refrigerate and drink within 3 days.", 28)
    out.append(body(st, x0, y + 3.2))
    y += 3.2 + len(st) * 3.05 + 1.6
    out.append(f'<g transform="translate({x0 + 0.2} {y - 3.4:.2f}) scale(0.4)" fill="none" stroke="{BODY}" stroke-width="0.4">'
               '<path d="M 2.5 0 L 4.7 0 L 4.7 1.8 Q 6 2.8 6 5 L 6 10.5 Q 6 11.2 5.3 11.2 L 1.9 11.2 '
               'Q 1.2 11.2 1.2 10.5 L 1.2 5 Q 1.2 2.8 2.5 1.8 Z"/></g>')
    out.append(body(["Glass bottle. Please recycle."], x0 + 4.2, y))
    y += 4.2
    out.append(body(["Best before / Lot: see cap."], x0, y))
    out.append(body(["Producer: [ name, address ],", "Azerbaijan · [ website ]"], x0, y + 3.6))

    y = top + 1
    out.append(head(bx, y, "NUTRITION"))
    out.append(f'<text x="{bx + 35}" y="{y:.2f}" font-size="1.8" text-anchor="end" {sans}>per 100 ml</text>')
    out.append(f'<line x1="{bx}" y1="{y + 1:.2f}" x2="{bx + 35}" y2="{y + 1:.2f}" stroke="{BODY}" stroke-width="0.3"/>')
    for i, r in enumerate(["Energy", "Fat", "-saturates", "Carbohydrate", "-sugars", "Protein", "Salt"]):
        yy = y + 3.9 + i * 2.85
        sub = r.startswith("-")
        name = ("of which " + r[1:]) if sub else r
        out.append(f'<text x="{bx + (1.8 if sub else 0)}" y="{yy:.2f}" font-size="2.35" {sans}>{name}</text>'
                   f'<text x="{bx + 35}" y="{yy:.2f}" font-size="2.35" text-anchor="end" {sans}>TBC</text>'
                   f'<line x1="{bx}" y1="{yy + 0.75:.2f}" x2="{bx + 35}" y2="{yy + 0.75:.2f}" stroke="#C9B9A6" stroke-width="0.15"/>')
    by = y + 3.9 + 6 * 2.85 + 2.6
    out.append(f'<rect x="{bx + 2}" y="{by:.2f}" width="31" height="21" fill="#fff" stroke="#9C8B7C" stroke-width="0.2"/>'
               f'<text x="{bx + 17.5}" y="{by + 9.5:.2f}" text-anchor="middle" font-size="2.1" {sans}>EAN-13 barcode</text>'
               f'<text x="{bx + 17.5}" y="{by + 12.6:.2f}" text-anchor="middle" font-size="1.7" fill="#9C8B7C" font-family="{SANS}">31 x 21 mm area</text>')
    return "".join(out)


def svg(f, with_dieline):
    w, h = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
    body = (f'<g transform="translate({BLEED} {BLEED})">{back(f)}{front(f)}'
            + (base.dieline() if with_dieline else "") + "</g>")
    size = f'width="{w}mm" height="{h}mm"' if with_dieline else f'width="{w * 12}" height="{h * 12}"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" {size}>{embedded_fonts()}{body}</svg>\n'


def main():
    global STYLE, OUT
    if "--original" in sys.argv:
        STYLE, OUT = "original", HERE / "collection-original"
    if "--citrus" in sys.argv:
        STYLE, OUT = "citrus", HERE / "collection-citrus"
    OUT.mkdir(exist_ok=True)
    for f in FLAVOURS:
        (OUT / f"shira-{f['key']}-label.svg").write_text(svg(f, True), encoding="utf-8")
        (OUT / f"shira-{f['key']}-label-texture.svg").write_text(svg(f, False), encoding="utf-8")


if __name__ == "__main__":
    main()
