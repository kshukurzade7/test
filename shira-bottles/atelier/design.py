"""SHIRÁ, typographic premium directions (no illustrations): each flavour is a number.

  atelier   warm-white 60 x 90 mm label, apothecary/perfume style: Nº, light spaced
            SHIRÁ, italic flavour name, one flavour-colour dot, ruled info table
  monolith  30 x 120 mm vertical black strip, SHIRÁ running up it in gold
  sun       white 60 x 90 mm label with one large flavour-colour disc

Text is outlined (no fonts needed). Run:  python3 design.py  ->  svg/<concept>-<flavour>.svg
"""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "band"))
from labels import Face  # noqa: E402

LIGHT = Face("inter-tight-latin-300-normal.woff2")
MEDIUM = Face("inter-tight-latin-500-normal.woff2")
ITALIC = Face("playfair-display-latin-500-italic.woff2")
MONO = Face("dm-mono-latin-400-normal.woff2")

PAPER = "#FAF8F3"
INK = "#161412"
GOLD = ["#8A6424", "#C9A250", "#F0DA98", "#B88C3C", "#7C5A20"]

FLAVOURS = [
    dict(no="01", key="rosehip", name="Rosehip", dot="#C8401F", sun=("#FFB27A", "#E5532A", "#9C2410")),
    dict(no="02", key="apple", name="Apple", dot="#8FA32C", sun=("#FBF0A0", "#D9C640", "#7E9628")),
    dict(no="03", key="blackcurrant", name="Blackcurrant", dot="#3B1F52", sun=("#A88AD6", "#4E2C78", "#1E0B30")),
    dict(no="04", key="cranberry", name="Cranberry", dot="#9E0F2C", sun=("#FF8A98", "#C21838", "#6A0619")),
    dict(no="05", key="redcurrant", name="Redcurrant", dot="#C8102E", sun=("#FF9AA0", "#E01C36", "#8A0A1C")),
]


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 20}" height="{h * 20}">{body}</svg>\n'


def grain(uid, alpha=0.05):
    return (f'<filter id="n{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.6" '
            f'numOctaves="2" seed="5"/><feColorMatrix values="0 0 0 0 0.3  0 0 0 0 0.26  0 0 0 0 0.2  0 0 0 {alpha} 0"/>'
            f'<feComposite in2="SourceGraphic" operator="in"/></filter>')


def gold(uid, w):
    stops = "".join(f'<stop offset="{i / 4:.2f}" stop-color="{c}"/>' for i, c in enumerate(GOLD))
    return f'<linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{w * 0.4:.1f}">{stops}</linearGradient>'


def atelier(f):
    w, h = 60, 90
    cx, m = w / 2, 5.5
    uid = f"at{f['key']}"
    rule = lambda y: f'<rect x="{m}" y="{y:.2f}" width="{w - 2 * m}" height="0.14" fill="{INK}"/>'  # noqa: E731
    rows = [("ORIGIN", "AZERBAIJAN"), ("FRUIT", "100%"), ("PRESSING", "COLD"), ("HARVEST", "2026")]
    table = "".join(MONO.text(k, m, 71.2 + i * 4, 1.6, INK, anchor="start")
                    + MONO.text(v, w - m, 71.2 + i * 4, 1.6, INK, anchor="end") + rule(72.6 + i * 4)
                    for i, (k, v) in enumerate(rows))
    return svg(w, h,
               f'<defs>{grain(uid)}</defs><rect width="{w}" height="{h}" rx="1" fill="{PAPER}"/>'
               f'<rect width="{w}" height="{h}" rx="1" fill="{PAPER}" filter="url(#n{uid})"/>'
               + MONO.text(f"Nº {f['no']}", m, 8.6, 1.9, INK, anchor="start")
               + MONO.text("500 ML", w - m, 8.6, 1.9, INK, anchor="end") + rule(10.4)
               + LIGHT.text("SHIRÁ", cx, 29.5, 11, INK, tracking=2.8)
               + MONO.text("COLD-PRESSED FRUIT JUICE", cx, 36.4, 1.6, INK, tracking=0.35)
               + ITALIC.text(f["name"], cx, 54, 10.5 if len(f["name"]) < 10 else 8.4, INK)
               + f'<circle cx="{cx}" cy="60.5" r="1.5" fill="{f["dot"]}"/>'
               + rule(67.6) + table)


def monolith(f):
    w, h = 30, 120
    cx = w / 2
    uid = f"mo{f['key']}"
    word = MEDIUM.text("SHIRÁ", 0, 0, 13, f"url(#g{uid})", tracking=5.2)  # centred on 0, 0
    return svg(w, h,
               f'<defs>{gold("g" + uid, 60)}{grain(uid, 0.08)}</defs>'
               f'<rect width="{w}" height="{h}" rx="1" fill="#0E0D0C"/>'
               f'<rect width="{w}" height="{h}" rx="1" fill="#0E0D0C" filter="url(#n{uid})"/>'
               + MONO.text(f"Nº {f['no']}", cx, 9, 1.9, f"url(#g{uid})", tracking=0.4)
               + f'<rect x="{cx - 3}" y="11.6" width="6" height="0.2" fill="url(#g{uid})"/>'
               # SHIRÁ reads bottom-to-top up the middle of the strip
               + f'<g transform="translate({cx + 0.9} 52) rotate(-90)">{word}</g>'
               + ITALIC.text(f["name"], cx, 96, 4.9 if len(f["name"]) < 10 else 3.9, "#F1E8D8")
               + f'<circle cx="{cx}" cy="100.4" r="0.9" fill="{f["dot"]}"/>'
               + MONO.text("COLD PRESSED", cx, 106, 1.45, "#F1E8D8", tracking=0.3)
               + MONO.text("500 ML · AZ", cx, 110.4, 1.45, f"url(#g{uid})", tracking=0.3))


def sun(f):
    w, h = 60, 90
    cx = w / 2
    uid = f"su{f['key']}"
    a, b, c = f["sun"]
    return svg(w, h,
               f'<defs>{grain(uid, 0.04)}<radialGradient id="d{uid}" cx="0.38" cy="0.32" r="0.8">'
               f'<stop offset="0" stop-color="{a}"/><stop offset="0.55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient></defs>'
               f'<rect width="{w}" height="{h}" rx="1" fill="#FBFAF7"/><rect width="{w}" height="{h}" rx="1" fill="#FBFAF7" filter="url(#n{uid})"/>'
               f'<circle cx="{cx}" cy="29" r="19" fill="url(#d{uid})"/>'
               + MONO.text(f"Nº {f['no']}", cx, 7.4, 1.7, INK, tracking=0.4)
               + LIGHT.text("SHIRÁ", cx, 63, 10.5, INK, tracking=2.5)
               + ITALIC.text(f["name"], cx, 73, 7 if len(f["name"]) < 10 else 6, f["dot"])
               + MONO.text("COLD PRESSED · AZERBAIJAN · 500 ML", cx, 83.5, 1.45, INK, tracking=0.2))


def main():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)
    for f in FLAVOURS:
        for name, fn in (("atelier", atelier), ("monolith", monolith), ("sun", sun)):
            (out / f"{name}-{f['key']}.svg").write_text(fn(f), encoding="utf-8")


if __name__ == "__main__":
    main()
