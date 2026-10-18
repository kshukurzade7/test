"""Three label concepts for the clear 500 ml juice bottle (gold twist cap), with the
"shirá" orange-slice logo:

  v1  small front label: arch-topped cream label, flavour-colour foot
  v2  clear label: logo and text printed straight on clear film (white on dark
      juices, ink on light ones), so the juice is the label
  v3  band: a 45 mm cream band round the middle with flavour-colour edges

Flat front artwork only (mm units); mockup.mjs wraps it onto the bottle photos.
All text is converted to outlines, so the SVGs need no fonts.

Run:  python3 labels.py  ->  svg/v<1|2|3>-<flavour>.svg
"""

import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
sys.path.insert(0, str(HERE.parent / "logo"))
from logo import mark, wordmark  # noqa: E402

PAPER = "#FFFBF5"
INK = "#2A1A12"
GOLD = "#C9A04E"

# Which flavour is in which photo (bottle-1 ... bottle-5), with the label colours.
BOTTLES = [
    dict(photo="bottle-1", key="rosehip", name="Rosehip", colour="#C2452E", juice="dark"),
    dict(photo="bottle-2", key="apple", name="Apple", colour="#4E842E", juice="light"),
    dict(photo="bottle-3", key="blackcurrant", name="Blackcurrant", colour="#4A2752", juice="dark"),
    dict(photo="bottle-4", key="cranberry", name="Cranberry", colour="#8E1638", juice="dark"),
    dict(photo="bottle-5", key="redcurrant", name="Redcurrant", colour="#B81C36", juice="dark"),
]


class Face:
    """A font whose text is drawn as SVG outlines."""

    def __init__(self, file):
        self.font = TTFont(FONTS / file)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm

    def width(self, text, size, tracking=0.0):
        s = size / self.upm
        return sum(self.glyphs[self.cmap[ord(c)]].width * s for c in text) + tracking * (len(text) - 1)

    def text(self, text, x, y, size, fill, tracking=0.0, anchor="middle"):
        s = size / self.upm
        w = self.width(text, size, tracking)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        pen = SVGPathPen(self.glyphs)
        cx = x0
        for c in text:
            g = self.glyphs[self.cmap[ord(c)]]
            g.draw(TransformPen(pen, (s, 0, 0, -s, cx, y)))
            cx += g.width * s + tracking
        return f'<path fill="{fill}" d="{pen.getCommands()}"/>'


BOLD = Face("nunito-latin-800-normal.woff2")
SMALL = Face("montserrat-latin-500-normal.woff2")


def logo_lockup(cx, y_base, size, ink, uid, mono=None):
    """Horizontal shirá lockup centred on cx, wordmark baseline at y_base."""
    d, tw = wordmark(size)
    r = size * 0.42
    gap = size * 0.24
    total = 2 * r + gap + tw
    x0 = cx - total / 2
    xh = size * 0.49  # Nunito x-height
    return (mark(x0 + r, y_base - xh / 2, r, uid, mono)
            + f'<path fill="{ink}" transform="translate({x0 + 2 * r + gap:.3f} {y_base:.3f})" d="{d}"/>')


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w * 20:.0f}" height="{h * 20:.0f}">{body}</svg>\n')


def v1(b):
    """Arch-topped front label, 62 x 84 mm."""
    w, h = 62, 84
    cx = w / 2
    arch = f"M0 {h} L0 {cx} A{cx} {cx} 0 0 1 {w} {cx} L{w} {h} Z"
    inset = 2.2
    ri = cx - inset
    inner = f"M{inset} {h - inset} L{inset} {cx} A{ri} {ri} 0 0 1 {w - inset} {cx} L{w - inset} {h - inset} Z"
    foot = 66
    body = [f'<clipPath id="a{b["key"]}"><path d="{arch}"/></clipPath>',
            f'<g clip-path="url(#a{b["key"]})"><path fill="{PAPER}" d="{arch}"/>'
            f'<rect x="0" y="{foot}" width="{w}" height="{h - foot}" fill="{b["colour"]}"/></g>',
            f'<path d="{inner}" fill="none" stroke="{GOLD}" stroke-width="0.35"/>',
            mark(cx, 17, 7.5, f"v1{b['key']}"),
            f'<path fill="{INK}" transform="translate({cx - wordmark(13)[1] / 2:.3f} 37)" d="{wordmark(13)[0]}"/>',
            f'<rect x="{cx - 6}" y="41" width="12" height="0.45" fill="{GOLD}"/>',
            BOLD.text(b["name"], cx, 52, 8.6 if len(b["name"]) < 10 else 7.4, b["colour"]),
            SMALL.text("100% NATURAL JUICE", cx, 58.5, 2.3, INK, tracking=0.45),
            SMALL.text("NOT FROM CONCENTRATE", cx, 62, 2.0, "#7A6A5E", tracking=0.4),
            SMALL.text("500 ml", cx, 76.5, 4.6, PAPER),
            ]
    return svg(w, h, "".join(body))


def v2(b):
    """Clear label: only the print, no paper. 64 x 70 mm print area."""
    w, h = 64, 70
    cx = w / 2
    ink = "#FFFFFF" if b["juice"] == "dark" else INK
    sub = ink
    d, tw = wordmark(21)
    body = [mark(cx, 13, 8, f"v2{b['key']}", mono=ink),
            f'<path fill="{ink}" transform="translate({cx - tw / 2:.3f} 40)" d="{d}"/>',
            f'<rect x="{cx - 7}" y="45" width="14" height="0.5" fill="{ink}"/>',
            BOLD.text(b["name"].upper(), cx, 54, 5.2, ink, tracking=0.9),
            SMALL.text("100% NATURAL JUICE · NOT FROM CONCENTRATE", cx, 60.5, 1.9, sub, tracking=0.25),
            SMALL.text("500 ml", cx, 67, 3.0, sub)]
    return svg(w, h, "".join(body))


def v3(b):
    """Band round the middle, 45 mm tall; front 110 mm drawn (the rest wraps behind)."""
    w, h = 110, 45
    cx = w / 2
    edge = 2.4
    body = [f'<rect width="{w}" height="{h}" fill="{PAPER}"/>',
            f'<rect width="{w}" height="{edge}" fill="{b["colour"]}"/>',
            f'<rect y="{h - edge}" width="{w}" height="{edge}" fill="{b["colour"]}"/>',
            f'<rect y="{edge + 1}" width="{w}" height="0.3" fill="{GOLD}"/>',
            f'<rect y="{h - edge - 1.3}" width="{w}" height="0.3" fill="{GOLD}"/>',
            logo_lockup(cx, 19.5, 12, INK, f"v3{b['key']}"),
            BOLD.text(b["name"], cx, 31.5, 7.6 if len(b["name"]) < 10 else 6.6, b["colour"]),
            SMALL.text("100% NATURAL JUICE · NOT FROM CONCENTRATE", cx, 37.8, 1.9, INK, tracking=0.35),
            SMALL.text("500 ml", cx - 37, 24.5, 4.0, b["colour"]),
            SMALL.text("PRODUCT OF", cx + 37, 22.3, 1.9, INK, tracking=0.35),
            SMALL.text("AZERBAIJAN", cx + 37, 25.6, 1.9, INK, tracking=0.35)]
    return svg(w, h, "".join(body))


def main():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)
    for b in BOTTLES:
        for n, fn in (("v1", v1), ("v2", v2), ("v3", v3)):
            (out / f"{n}-{b['key']}.svg").write_text(fn(b), encoding="utf-8")


if __name__ == "__main__":
    main()
