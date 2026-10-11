"""SHIRÁ logo kit.

The mark is a juicy orange slice: orange rind, pale pith, eight rounded pulp
segments and a small green leaf. The wordmark is "shirá" in lowercase Nunito
ExtraBold. Everything is drawn as outlines (the wordmark is converted from the
font with fontTools), so the SVG/PDF files need no fonts installed.

Run:  python3 logo.py && node export.mjs
      -> final/svg/*.svg (written here), final/png/*.png + final/pdf/*.pdf (export.mjs)
"""

import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONT = HERE.parent / "fonts" / "nunito-latin-800-normal.woff2"

INK = "#2A1A12"
LIGHT = "#FFF6EC"      # wordmark on dark backgrounds
PITH = "#FFF3DC"
LEAF, LEAF_VEIN = "#5DAE3B", "#3E8A2A"
PULP = ("#FFB53F", "#FF5A1F")   # top -> bottom
RIND = ("#FF9A2E", "#F0461A")
BG_LIGHT, BG_DARK = "#FFFBF5", "#1D1714"

_font = TTFont(FONT)
_glyphs = _font.getGlyphSet()
_cmap = _font.getBestCmap()
_scale_unit = 1 / _font["head"].unitsPerEm
X_HEIGHT = _font["OS/2"].sxHeight * _scale_unit


def wordmark(size, tracking=-0.2):
    """'shirá' as one SVG path, baseline at y=0, starting at x=0. Returns (d, width)."""
    s = size * _scale_unit
    pen = SVGPathPen(_glyphs)
    x = 0.0
    text = "shirá"
    for i, ch in enumerate(text):
        g = _glyphs[_cmap[ord(ch)]]
        g.draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        x += g.width * s + (tracking if i < len(text) - 1 else 0)
    return pen.getCommands(), x


def _segments(cx, cy, R):
    """Eight pulp segments with rounded corners: (path d, stroke width) pairs drawn fill + round-join stroke."""
    r, ri, rad = R * 0.82, R * 0.13, R * 0.07
    d = R * 0.035 + rad
    ro, rin = r - rad, ri + rad
    out = []
    for k in range(8):
        a0 = k * math.pi / 4
        a1 = a0 + math.pi / 4

        def pt(a, rho, side):
            u = (math.sin(a), -math.cos(a))
            n = (math.cos(a), math.sin(a)) if side == 0 else (-math.cos(a), -math.sin(a))
            t = math.sqrt(rho * rho - d * d)
            return cx + n[0] * d + u[0] * t, cy + n[1] * d + u[1] * t

        p0o, p1o, p1i, p0i = pt(a0, ro, 0), pt(a1, ro, 1), pt(a1, rin, 1), pt(a0, rin, 0)
        out.append(f"M{p0o[0]:.3f} {p0o[1]:.3f} A{ro:.3f} {ro:.3f} 0 0 1 {p1o[0]:.3f} {p1o[1]:.3f} "
                   f"L{p1i[0]:.3f} {p1i[1]:.3f} A{rin:.3f} {rin:.3f} 0 0 0 {p0i[0]:.3f} {p0i[1]:.3f}Z")
    return out, 2 * rad


def _leaf(cx, cy, R, fill, vein):
    L = R * 0.62
    blade = (f"M0 0 C{L*0.3:.3f} {-L*0.38:.3f} {L*0.75:.3f} {-L*0.38:.3f} {L:.3f} 0 "
             f"C{L*0.75:.3f} {L*0.38:.3f} {L*0.3:.3f} {L*0.38:.3f} 0 0Z")
    vein_line = (f'<path d="M{L*0.12:.3f} 0 L{L*0.8:.3f} 0" stroke="{vein}" stroke-width="{R*0.035:.3f}" '
                 f'stroke-linecap="round"/>' if vein else "")
    return (f'<g transform="translate({cx + R*0.42:.3f} {cy - R*0.9:.3f}) rotate(-40)">'
            f'<path fill="{fill}" d="{blade}"/>{vein_line}</g>')


def mark(cx, cy, R, uid, mono=None):
    """The orange slice. mono = one colour for single-colour use (the pith becomes transparent)."""
    segs, sw = _segments(cx, cy, R)
    if mono:
        # Rind as a ring (even-odd), segments and leaf in one flat colour.
        ring = (f'<path fill="{mono}" fill-rule="evenodd" d="M{cx - R:.3f} {cy:.3f} a{R} {R} 0 1 0 {2*R:.3f} 0 '
                f'a{R} {R} 0 1 0 {-2*R:.3f} 0Z M{cx - R*0.89:.3f} {cy:.3f} a{R*0.89:.3f} {R*0.89:.3f} 0 1 0 '
                f'{2*R*0.89:.3f} 0 a{R*0.89:.3f} {R*0.89:.3f} 0 1 0 {-2*R*0.89:.3f} 0Z"/>')
        pulp = "".join(f'<path fill="{mono}" stroke="{mono}" stroke-width="{sw:.3f}" stroke-linejoin="round" d="{d}"/>'
                       for d in segs)
        return ring + pulp + _leaf(cx, cy, R, mono, None)
    grad = (f'<defs><linearGradient id="pulp{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="{cy-R:.3f}" x2="0" y2="{cy+R:.3f}">'
            f'<stop offset="0" stop-color="{PULP[0]}"/><stop offset="1" stop-color="{PULP[1]}"/></linearGradient>'
            f'<linearGradient id="rind{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="{cy-R:.3f}" x2="0" y2="{cy+R:.3f}">'
            f'<stop offset="0" stop-color="{RIND[0]}"/><stop offset="1" stop-color="{RIND[1]}"/></linearGradient></defs>')
    pulp = "".join(f'<path fill="url(#pulp{uid})" stroke="url(#pulp{uid})" stroke-width="{sw:.3f}" '
                   f'stroke-linejoin="round" d="{d}"/>' for d in segs)
    return (grad + f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{R}" fill="url(#rind{uid})"/>'
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{R*0.89:.3f}" fill="{PITH}"/>' + pulp
            + _leaf(cx, cy, R, LEAF, LEAF_VEIN))


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w * 10:.0f}" height="{h * 10:.0f}">{rect}{body}</svg>\n')


# Geometry shared by the lockups. The leaf reaches about 0.25 R above the rind.
R = 12.5
LEAF_TOP = R * 1.25
PAD = 4


def horizontal(ink, mono=None, uid="h"):
    """Main logo: slice on the left, wordmark on the right, centred on the x-height."""
    d, tw = wordmark(26)
    cy = PAD + LEAF_TOP
    base = cy + X_HEIGHT * 26 / 2
    gap = 7
    w = PAD + 2 * R + gap + tw + PAD
    h = cy + R + PAD
    body = mark(PAD + R, cy, R, uid, mono) + f'<path fill="{ink}" transform="translate({PAD + 2*R + gap:.3f} {base:.3f})" d="{d}"/>'
    return svg(w, h, body)


def stacked(ink, mono=None, uid="s"):
    """Slice above the wordmark, for square spaces."""
    size = 26
    d, tw = wordmark(size)
    w = max(tw, 2 * R) + 2 * PAD
    cy = PAD + LEAF_TOP
    base = cy + R + 6 + X_HEIGHT * size + size * 0.25  # room for the accent on á
    h = base + size * 0.25 + PAD  # descender-free word, small bottom margin
    body = mark(w / 2, cy, R, uid, mono) + f'<path fill="{ink}" transform="translate({w/2 - tw/2:.3f} {base:.3f})" d="{d}"/>'
    return svg(w, h, body)


def mark_only(mono=None, bg=None, pad=PAD, uid="m"):
    w = 2 * (R + pad)
    cy = (w - (LEAF_TOP + R)) / 2 + LEAF_TOP  # centre slice + leaf as one shape
    return svg(w, w, mark(w / 2, cy, R, uid, mono), bg)


VERSIONS = {
    "shira-logo": horizontal(INK),
    "shira-logo-on-dark": horizontal(LIGHT, uid="hd"),
    "shira-logo-stacked": stacked(INK),
    "shira-logo-stacked-on-dark": stacked(LIGHT, uid="sd"),
    "shira-logo-black": horizontal(INK, mono=INK),
    "shira-logo-white": horizontal("#FFFFFF", mono="#FFFFFF"),
    "shira-mark": mark_only(),
    "shira-mark-black": mark_only(mono=INK),
    "shira-mark-white": mark_only(mono="#FFFFFF"),
    "shira-avatar": mark_only(bg=BG_LIGHT, pad=10, uid="a"),
}


def main():
    out = HERE / "final" / "svg"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for name, data in VERSIONS.items():
        (out / f"{name}.svg").write_text(data, encoding="utf-8")


if __name__ == "__main__":
    main()
