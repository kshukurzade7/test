"""SHIRÁ modern premium labels for the clear 500 ml bottle (60 x 100 mm front label).

Three directions, same layout and type (Playfair Display + Jost), same glossy fruit:
  noir    matte black label, gold-foil SHIRÁ, juicy fruit that glows on black
  colour  label in a deep tone of the flavour colour, cream type
  clear   clear film: big SHIRÁ and the flavour name printed straight on the glass

All text is outlined (no fonts needed). Run:  python3 design.py  ->  svg/<concept>-<flavour>.svg
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "band"))
from labels import Face  # noqa: E402

DISPLAY = Face("playfair-display-latin-600-normal.woff2")
ITALIC = Face("playfair-display-latin-500-italic.woff2")
SANS = Face("jost-latin-500-normal.woff2")

CREAM = "#F3E9D6"
GOLD = ["#8A6424", "#C9A250", "#F0DA98", "#B88C3C", "#7C5A20"]

FLAVOURS = [
    dict(key="rosehip", name="Rosehip", deep="#6E1E10", juice="dark"),
    dict(key="apple", name="Apple", deep="#1F4128", juice="light"),
    dict(key="blackcurrant", name="Blackcurrant", deep="#26122F", juice="dark"),
    dict(key="cranberry", name="Cranberry", deep="#4A0A1D", juice="dark"),
    dict(key="redcurrant", name="Redcurrant", deep="#640C1B", juice="dark"),
]


def gold(uid, w):
    stops = "".join(f'<stop offset="{i / 4:.2f}" stop-color="{c}"/>' for i, c in enumerate(GOLD))
    return f'<linearGradient id="{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{w * 0.35:.1f}">{stops}</linearGradient>'


# --- glossy fruit (drawn around 0,0, about 60 units across) ------------------

class Art:
    def __init__(self, uid):
        self.uid, self.n, self.defs = uid, 0, []

    def _id(self):
        self.n += 1
        return f"{self.uid}{self.n}"

    def sphere(self, x, y, rx, ry, light, mid, dark, rot=0, calyx=None):
        gid = self._id()
        self.defs.append(f'<radialGradient id="{gid}" cx="0.38" cy="0.32" r="0.75">'
                         f'<stop offset="0" stop-color="{light}"/><stop offset="0.45" stop-color="{mid}"/>'
                         f'<stop offset="1" stop-color="{dark}"/></radialGradient>')
        star = ""
        if calyx:
            star = "".join(f'<path d="M0 0 L{math.cos(a) * rx * 0.22:.2f} {math.sin(a) * rx * 0.22:.2f}" '
                           f'stroke="{calyx}" stroke-width="{rx * 0.08:.2f}" stroke-linecap="round"/>'
                           for a in [k * 2 * math.pi / 5 for k in range(5)])
            star = f'<g transform="translate({rx * 0.42:.2f} {ry * 0.5:.2f})">{star}</g>'
        return (f'<g transform="translate({x} {y}) rotate({rot})">'
                f'<ellipse rx="{rx}" ry="{ry}" fill="url(#{gid})"/>'
                f'<ellipse cx="{-rx * 0.36:.2f}" cy="{-ry * 0.4:.2f}" rx="{rx * 0.24:.2f}" ry="{ry * 0.15:.2f}" '
                f'fill="#fff" opacity="0.55" transform="rotate(-30 {-rx * 0.36:.2f} {-ry * 0.4:.2f})"/>{star}</g>')

    def leaf(self, x, y, rot, L, w, vein):
        gid = self._id()
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
                         f'<stop offset="0" stop-color="#6E9E44"/><stop offset="1" stop-color="#1F3F1B"/></linearGradient>')
        return (f'<g transform="translate({x} {y}) rotate({rot})">'
                f'<path d="M0 0 C{L * 0.3} {-w} {L * 0.72} {-w} {L} 0 C{L * 0.72} {w} {L * 0.3} {w} 0 0Z" fill="url(#{gid})"/>'
                f'<path d="M{L * 0.05} 0 Q{L * 0.5} {-w * 0.08} {L * 0.92} 0" stroke="{vein}" stroke-width="0.6" fill="none"/></g>')


def fruit(key, uid, stem):
    a = Art(uid)
    s = f'stroke="{stem}" stroke-width="1.2" fill="none" stroke-linecap="round"'
    if key == "blackcurrant":
        pts = [(-1, -12, 5.6), (6, -4, 6), (-6, 2, 6.2), (4, 9, 6.2), (-4, 16, 5.8), (3, 22, 5.2), (-2, 27, 4.4)]
        body = (a.leaf(-4, -24, -150, 22, 9, stem) + a.leaf(-4, -24, -40, 18, 7.5, stem)
                + f'<path d="M-4 -24 C-2 -18 0 -14 -1 -12 C1 0 0 16 -2 27" {s}/>'
                + "".join(a.sphere(x, y, r, r, "#8E73B8", "#3A2158", "#12081D", calyx="#0B0612") for x, y, r in pts))
    elif key == "redcurrant":
        pts = [(-1, -12, 5.4), (5, -5, 5.8), (-5, 2, 6), (4, 9, 6), (-3, 16, 5.6), (3, 22, 5), (-1, 27, 4.2)]
        body = (a.leaf(-4, -24, -150, 22, 9, stem) + a.leaf(-4, -24, -40, 18, 7.5, stem)
                + f'<path d="M-4 -24 C-2 -18 0 -14 -1 -12 C1 0 0 16 -2 27" {s}/>'
                + "".join(a.sphere(x, y, r, r, "#FF8A80", "#E0102E", "#6E0010", calyx="#4A0008") for x, y, r in pts))
    elif key == "cranberry":
        body = (f'<path d="M-24 -20 C-10 -16 4 -15 22 -22" {s}/>'
                + a.leaf(-18, -18, -115, 11, 4.2, stem) + a.leaf(-4, -16, -70, 10, 4, stem) + a.leaf(10, -17, -110, 11, 4.2, stem)
                + f'<path d="M-12 -17 C-13 -8 -13 -2 -12 4 M3 -16 C4 -6 4 4 3 10 M15 -19 C16 -10 16 -4 14 2" {s}/>'
                + a.sphere(-12, 11, 9, 8.4, "#FF7D86", "#B5112F", "#4F0414", calyx="#3A0310")
                + a.sphere(14, 9, 8.4, 7.8, "#FF7D86", "#B5112F", "#4F0414", calyx="#3A0310")
                + a.sphere(2, 19, 9.6, 9, "#FF8A92", "#C0142F", "#550516", calyx="#3A0310"))
    elif key == "rosehip":
        def hip(x, y, rot):
            sep = "".join(f'<path d="M0 -13 Q{d * 4:.1f} -19 {d * 9:.1f} -21" stroke="#3B2614" stroke-width="1" fill="none" stroke-linecap="round"/>'
                          for d in (-1, -0.45, 0.45, 1))
            return (f'<g transform="translate({x} {y}) rotate({rot})">{sep}</g>'
                    + a.sphere(x, y, 9, 13, "#FFB073", "#E0461C", "#6E1406", rot=rot))
        body = (f'<path d="M-2 -32 C-4 -24 -9 -16 -11 -6 M-2 -32 C3 -24 9 -18 11 -10" {s}/>'
                + a.leaf(-2, -32, -150, 18, 7, stem) + a.leaf(-2, -32, -30, 16, 6.5, stem)
                + hip(-11, 9, 8) + hip(11, 4, -12))
    elif key == "apple":
        gid = a._id()
        a.defs.append(f'<radialGradient id="{gid}" cx="0.36" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFF3A6"/>'
                      f'<stop offset="0.4" stop-color="#E8C93A"/><stop offset="0.8" stop-color="#9DA92B"/><stop offset="1" stop-color="#4C6A1A"/></radialGradient>')
        blush = a._id()
        a.defs.append(f'<radialGradient id="{blush}" cx="0.75" cy="0.6" r="0.5"><stop offset="0" stop-color="#E0462A" stop-opacity="0.55"/>'
                      f'<stop offset="1" stop-color="#E0462A" stop-opacity="0"/></radialGradient>')
        shape = ("M0 -14 C7 -21 22 -20 26 -6 C30 8 22 25 9 28 C5 29 2 27 0 26 "
                 "C-2 27 -5 29 -9 28 C-22 25 -30 8 -26 -6 C-22 -20 -7 -21 0 -14 Z")
        body = (f'<path d="{shape}" fill="url(#{gid})"/><path d="{shape}" fill="url(#{blush})"/>'
                f'<ellipse cx="-12" cy="-4" rx="4" ry="7" fill="#fff" opacity="0.45" transform="rotate(20 -12 -4)"/>'
                f'<path d="M0 -14 C-1 -20 1 -26 4 -30" stroke="#5A3A1E" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
                + a.leaf(3, -27, -25, 18, 6.5, stem))
    else:
        raise ValueError(key)
    return f'<defs>{"".join(a.defs)}</defs>{body}'


# --- labels -----------------------------------------------------------------

W, H = 60, 100


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 20}" height="{H * 20}">'
            f'{body}</svg>\n')


def texture(uid, tone):
    """Faint matte paper grain."""
    return (f'<filter id="t{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.8" '
            f'numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 {tone}  0 0 0 0 {tone}  0 0 0 0 {tone}  0 0 0 0.07 0"/>'
            f'<feComposite in2="SourceGraphic" operator="in"/></filter>')


def paper_label(f, concept):
    uid = f"{concept}{f['key']}"
    cx = W / 2
    bg = "#100E0D" if concept == "noir" else f["deep"]
    word = f"url(#g{uid})" if concept == "noir" else CREAM
    accent = f"url(#g{uid})"
    name_size = 9.5 if len(f["name"]) < 10 else 7.8
    return svg(
        f'<defs>{gold("g" + uid, W)}{texture(uid, 1)}</defs>'
        f'<rect width="{W}" height="{H}" rx="1.5" fill="{bg}"/>'
        f'<rect width="{W}" height="{H}" rx="1.5" fill="{bg}" filter="url(#t{uid})"/>'
        + SANS.text("AZERBAIJAN", cx, 9.6, 1.8, accent, tracking=1.25)
        + DISPLAY.text("SHIRÁ", cx, 24, 13.5, word, tracking=1.1)
        + f'<rect x="{cx - 5}" y="28" width="10" height="0.35" fill="{accent}"/>'
        + f'<g transform="translate({cx} 53) scale(0.56)">{fruit(f["key"], uid, GOLD[1])}</g>'
        + ITALIC.text(f["name"], cx, 81.5, name_size, CREAM)
        + f'<rect x="{cx - 3}" y="85" width="6" height="0.35" fill="{accent}"/>'
        + SANS.text("COLD PRESSED JUICE", cx, 89.6, 1.7, CREAM, tracking=0.85)
        + SANS.text("500 ML", cx, 93.8, 1.7, accent, tracking=0.9))


def clear_label(f):
    uid = f"clear{f['key']}"
    cx = W / 2
    ink = "#FFFFFF" if f["juice"] == "dark" else "#1E1712"
    accent = f"url(#g{uid})" if f["juice"] == "dark" else "#5A3E12"  # gold vanishes on yellow juice
    return svg(
        f'<defs>{gold("g" + uid, W)}</defs>'
        + SANS.text("AZERBAIJAN", cx, 30, 1.9, accent, tracking=1.3)
        + DISPLAY.text("SHIRÁ", cx, 47, 16, ink, tracking=1.2)
        + f'<rect x="{cx - 6}" y="52" width="12" height="0.45" fill="{accent}"/>'
        + ITALIC.text(f["name"], cx, 64, 10 if len(f["name"]) < 10 else 8.2, ink)
        + SANS.text("COLD PRESSED JUICE", cx, 71, 1.8, ink, tracking=0.9)
        + SANS.text("500 ML", cx, 75.5, 1.8, accent, tracking=0.9))


def main():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)
    for f in FLAVOURS:
        (out / f"noir-{f['key']}.svg").write_text(paper_label(f, "noir"), encoding="utf-8")
        (out / f"colour-{f['key']}.svg").write_text(paper_label(f, "colour"), encoding="utf-8")
        (out / f"clear-{f['key']}.svg").write_text(clear_label(f), encoding="utf-8")


if __name__ == "__main__":
    main()
