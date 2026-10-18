"""SHIRÁ premium direction: a quiet, wine-label look for the clear juice bottle.

  logo     SHIRÁ in Bodoni Moda capitals (gold foil) with a buta emblem, the
           Azerbaijani paisley, which also reads as a drop of juice
  label    narrow ivory front label (55 x 95 mm): fine gold frame, blind-embossed
           buta, gold-foil name, an engraved fruit drawing, the flavour in italic
  collar   gold-foil neck band under the cap

The juice gives each bottle its colour; the label stays ivory, black and gold,
with the flavour colour only as a short rule. All text is drawn as outlines.

Run:  python3 label.py  ->  svg/front-<flavour>.svg, svg/collar.svg, svg/logo*.svg
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "band"))
from labels import Face  # noqa: E402  (font -> SVG outlines)

SERIF = Face("bodoni-moda-latin-500-normal.woff2")
ITALIC = Face("cormorant-garamond-latin-500-italic.woff2")
SANS = Face("jost-latin-400-normal.woff2")

IVORY = "#F7F2E8"
INK = "#231E1A"
GOLD_STOPS = ["#7E5A1F", "#B4893A", "#DCC07A", "#A87D32", "#74521C"]  # foil sheen, left to right

FLAVOURS = [
    dict(key="rosehip", name="Rosehip", colour="#B03A26"),
    dict(key="apple", name="Apple", colour="#4E842E"),
    dict(key="blackcurrant", name="Blackcurrant", colour="#4A2752"),
    dict(key="cranberry", name="Cranberry", colour="#8E1638"),
    dict(key="redcurrant", name="Redcurrant", colour="#B81C36"),
]


def foil(uid, x0, x1):
    stops = "".join(f'<stop offset="{i / (len(GOLD_STOPS) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(GOLD_STOPS))
    return (f'<linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0" '
            f'gradientTransform="rotate(12)">{stops}</linearGradient>')


# --- buta -------------------------------------------------------------------

BUTA = ("M2 22 C-10 22 -16 12 -14 2 C-12 -8 -4 -14 2 -20 C6 -24 10 -28 15 -28 "
        "C20 -28 22 -22 18 -19 C15 -17 12 -19 13 -22 C17 -14 18 -4 16 6 C14 16 9 22 2 22 Z")


def buta(cx, cy, scale, fill):
    """The brand emblem: a buta outline with a second buta drawn inside it."""
    return (f'<g transform="translate({cx} {cy}) scale({scale})">'
            f'<path d="{BUTA}" fill="none" stroke="{fill}" stroke-width="1.7" stroke-linejoin="round"/>'
            f'<g transform="translate(0.9 4.2) scale(0.66)"><path d="{BUTA}" fill="none" stroke="{fill}" stroke-width="1.5"/></g></g>')


def embossed_buta(cx, cy, scale):
    """Blind emboss: paper colour only, shown by a light edge and a soft shadow edge."""
    return (buta(cx + 0.18, cy + 0.22, scale, "#D9CFBE") + buta(cx - 0.12, cy - 0.15, scale, "#FFFDF8")
            + buta(cx, cy, scale, "#EFE7D8"))


# --- engraved fruit (ink line drawings, centred on 0,0, about 60 units across) --

def _hatch(uid, cx, cy, rx, ry, angle=-35, spacing=2.2, side=(0.5, 0.45)):
    """Diagonal hatching in the lower-right shadow of an ellipse."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    r = max(rx, ry)
    n = int(2 * r / spacing) + 2
    lines = " ".join(f"M{cx + nx * i * spacing - dx * r * 1.6:.2f} {cy + ny * i * spacing - dy * r * 1.6:.2f} "
                     f"L{cx + nx * i * spacing + dx * r * 1.6:.2f} {cy + ny * i * spacing + dy * r * 1.6:.2f}"
                     for i in range(-n, n + 1))
    ox, oy = -rx * side[0], -ry * side[1]
    return (f'<clipPath id="h{uid}"><ellipse cx="{cx}" cy="{cy}" rx="{rx - 0.6}" ry="{ry - 0.6}"/></clipPath>'
            f'<mask id="m{uid}"><rect x="-200" y="-200" width="400" height="400" fill="#fff"/>'
            f'<ellipse cx="{cx + ox}" cy="{cy + oy}" rx="{rx * 1.05}" ry="{ry * 1.05}" fill="#000"/></mask>'
            f'<g clip-path="url(#h{uid})" mask="url(#m{uid})"><path d="{lines}" stroke-width="0.35"/></g>')


def _leaf(x, y, rot, L=22, w=7, veins=4):
    v = " ".join(f"M{L*t:.1f} 0 Q{L*t+3:.1f} {-w*0.45:.1f} {L*t+5.5:.1f} {-w*0.6:.1f} "
                 f"M{L*t:.1f} 0 Q{L*t+3:.1f} {w*0.45:.1f} {L*t+5.5:.1f} {w*0.6:.1f}"
                 for t in [0.15 + i * 0.6 / veins for i in range(veins)])
    return (f'<g transform="translate({x} {y}) rotate({rot})">'
            f'<path d="M0 0 C{L*0.3} {-w} {L*0.7} {-w} {L} 0 C{L*0.7} {w} {L*0.3} {w} 0 0Z" stroke-width="0.8"/>'
            f'<path d="M0 0 Q{L*0.5} -0.6 {L*0.95} 0" stroke-width="0.55"/><path d="{v}" stroke-width="0.35"/></g>')


def _berry(uid, x, y, r, calyx=True):
    star = ""
    if calyx:  # dried flower at the tip, as on currants and cranberries
        star = "".join(f'<path d="M{x + r*0.62:.2f} {y + r*0.62:.2f} l{math.cos(a)*r*0.28:.2f} {math.sin(a)*r*0.28:.2f}" stroke-width="0.35"/>'
                       for a in [k * math.pi / 2.5 for k in range(5)])
    return (f'<circle cx="{x}" cy="{y}" r="{r}" stroke-width="0.75"/>'
            f'<path d="M{x - r*0.55:.2f} {y - r*0.15:.2f} A{r*0.6:.2f} {r*0.6:.2f} 0 0 1 {x - r*0.1:.2f} {y - r*0.6:.2f}" stroke-width="0.4"/>'
            + _hatch(uid, x, y, r, r, spacing=1.35) + star)


def engraving(key):
    if key == "apple":
        body = ("M0 -14 C6 -20 20 -19 24 -6 C28 7 21 24 9 27 C5 28 2 26 0 25 "
                "C-2 26 -5 28 -9 27 C-21 24 -28 7 -24 -6 C-20 -19 -6 -20 0 -14 Z")
        return (f'<path d="{body}" stroke-width="0.9"/>'
                f'<path d="M0 -14 C-1 -20 1 -25 4 -29" stroke-width="1.1"/>'
                + _leaf(3, -26, -20, 20, 7)
                + '<path d="M-17 -6 C-20 2 -19 12 -14 19" stroke-width="0.45"/>'
                + '<path d="M-3 -11 C-2 -8 2 -8 3 -11" stroke-width="0.45"/>'
                + _hatch("ap", 0, 5, 25, 22, side=(0.55, 0.55)))
    if key == "rosehip":
        def hip(uid, x, y, rot):
            return (f'<g transform="translate({x} {y}) rotate({rot})">'
                    f'<ellipse cx="0" cy="0" rx="8.5" ry="12" stroke-width="0.85"/>'
                    + "".join(f'<path d="M0 -11.5 Q{s*3:.1f} -16 {s*7:.1f} -19" stroke-width="0.5"/>' for s in (-1, -0.4, 0.4, 1))
                    + '<path d="M-4 -6 C-6 -2 -6 4 -4 8" stroke-width="0.4"/>'
                    + _hatch(uid, 0, 0, 8.5, 12, spacing=1.4) + '</g>')
        return ('<path d="M-6 -30 C-6 -18 -10 -8 -11 2 M-6 -30 C0 -22 8 -14 10 -4" stroke-width="0.9"/>'
                + _leaf(-6, -30, -150, 20, 7) + _leaf(-6, -30, -35, 18, 6.5)
                + hip("rh1", -11, 14, 10) + hip("rh2", 11, 9, -14))
    if key in ("blackcurrant", "redcurrant"):
        # A hanging string of berries on a curved stalk, with a lobed currant leaf behind.
        pts = [(-2, -14, 4.6), (4, -6, 4.8), (-4, 1, 5), (3, 9, 5), (-3, 16, 4.8), (2, 23, 4.4), (-1, 29, 3.8)]
        stalk = "M-10 -30 C-4 -24 0 -18 -2 -14 M-2 -14 C1 -2 1 14 -1 29"
        leaf = ('<g transform="translate(-14 -24) rotate(-25) scale(0.72)">'
                '<path d="M0 22 C-6 18 -20 20 -26 10 L-22 8 C-30 2 -32 -10 -24 -16 L-20 -12 C-20 -22 -10 -28 -4 -24 '
                'L0 -30 L4 -24 C10 -28 20 -22 20 -12 L24 -16 C32 -10 30 2 22 8 L26 10 C20 20 6 18 0 22 Z" '
                'stroke-width="1.1" stroke-linejoin="round"/>'
                '<path d="M0 18 L0 -26 M0 12 L-21 -11 M0 12 L21 -11 M0 16 L-21 8 M0 16 L21 8" stroke-width="0.6"/></g>')
        berries = "".join(_berry(f"{key[0]}{i}", x, y, r) for i, (x, y, r) in enumerate(pts))
        return leaf + f'<path d="{stalk}" stroke-width="0.8"/>' + berries
    if key == "cranberry":
        twig = "M-26 -18 C-12 -14 2 -12 24 -20"
        leaves = "".join(f'<g transform="translate({x} {y}) rotate({r})"><ellipse cx="4.5" cy="0" rx="4.5" ry="1.9" stroke-width="0.6"/>'
                         f'<path d="M0.5 0 L8 0" stroke-width="0.35"/></g>'
                         for x, y, r in ((-20, -16, -60), (-12, -14, 50), (-2, -13, -55), (8, -14, 45), (16, -17, -50)))
        stems = "M-12 -14 C-14 -6 -15 0 -14 6 M2 -13 C3 -6 3 4 2 12 M14 -16 C15 -8 16 -2 14 4"
        return (f'<path d="{twig}" stroke-width="0.9"/>' + leaves + f'<path d="{stems}" stroke-width="0.6"/>'
                + _berry("c1", -14, 13, 7.2) + _berry("c2", 2, 19, 7.5) + _berry("c3", 14, 11, 6.8))
    raise ValueError(key)


# --- artwork ----------------------------------------------------------------

def svg(w, h, body, px_per_mm=20):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w * px_per_mm:.0f}" height="{h * px_per_mm:.0f}">{body}</svg>\n')


def front(f):
    w, h = 55, 95
    cx = w / 2
    gid = f"gold-{f['key']}"
    out = [f'<defs>{foil(gid, 0, w)}<filter id="paper{f["key"]}" x="0" y="0" width="100%" height="100%">'
           f'<feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="2" seed="7"/>'
           f'<feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.38  0 0 0 0 0.28  0 0 0 0.06 0"/>'
           f'<feComposite in2="SourceGraphic" operator="in"/></filter></defs>',
           f'<rect width="{w}" height="{h}" rx="1.2" fill="{IVORY}"/>',
           f'<rect width="{w}" height="{h}" rx="1.2" fill="{IVORY}" filter="url(#paper{f["key"]})"/>',
           # double gold frame
           f'<rect x="2.6" y="2.6" width="{w - 5.2}" height="{h - 5.2}" fill="none" stroke="url(#{gid})" stroke-width="0.32"/>',
           f'<rect x="3.5" y="3.5" width="{w - 7}" height="{h - 7}" fill="none" stroke="url(#{gid})" stroke-width="0.12"/>',
           embossed_buta(cx, 13.2, 0.27),
           SERIF.text("SHIRÁ", cx, 27.8, 8.4, f"url(#{gid})", tracking=1.9),
           SANS.text("AZERBAIJAN", cx, 32.6, 1.75, INK, tracking=0.95),
           f'<rect x="{cx - 4}" y="35.4" width="8" height="0.18" fill="url(#{gid})"/>',
           f'<g transform="translate({cx} 53) scale(0.42)" fill="none" stroke="{INK}" stroke-linecap="round">{engraving(f["key"])}</g>',
           ITALIC.text(f["name"], cx, 75.5, 7.2 if len(f["name"]) < 10 else 6.2, INK),
           f'<rect x="{cx - 2.6}" y="78.6" width="5.2" height="0.55" fill="{f["colour"]}"/>',
           SANS.text("COLD PRESSED · 100% NATURAL", cx, 83.6, 1.55, INK, tracking=0.55),
           SANS.text("500 ML", cx, 88.2, 1.75, INK, tracking=0.9)]
    return svg(w, h, "".join(out))


def collar():
    """Gold-foil neck band, 70 x 9 mm (wraps the neck; front 40 mm carries the text)."""
    w, h = 70, 9
    out = [f'<defs>{foil("gc", 0, w)}</defs>', f'<rect width="{w}" height="{h}" fill="url(#gc)"/>',
           f'<rect y="1" width="{w}" height="0.15" fill="{INK}" opacity="0.5"/>',
           f'<rect y="{h - 1.15}" width="{w}" height="0.15" fill="{INK}" opacity="0.5"/>',
           SANS.text("HARVEST 2026 · SHIRÁ · AZERBAIJAN", w / 2, 5.3, 1.45, INK, tracking=0.55)]
    return svg(w, h, "".join(out))


def logo(dark=False):
    """Stand-alone logo: buta above SHIRÁ, gold on ivory or on near-black."""
    w, h = 80, 60
    bg = "#14110F" if dark else IVORY
    out = [f'<defs>{foil("gl", 0, w)}</defs>', f'<rect width="{w}" height="{h}" fill="{bg}"/>',
           buta(w / 2, 17, 0.55, "url(#gl)"),
           SERIF.text("SHIRÁ", w / 2, 44, 13, "url(#gl)", tracking=3.2),
           SANS.text("AZERBAIJAN", w / 2, 51, 2.4, "#CDBB98" if dark else INK, tracking=1.4)]
    return svg(w, h, "".join(out), px_per_mm=12)


def main():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)
    for f in FLAVOURS:
        (out / f"front-{f['key']}.svg").write_text(front(f), encoding="utf-8")
    (out / "collar.svg").write_text(collar(), encoding="utf-8")
    (out / "logo.svg").write_text(logo(), encoding="utf-8")
    (out / "logo-dark.svg").write_text(logo(dark=True), encoding="utf-8")


if __name__ == "__main__":
    main()
