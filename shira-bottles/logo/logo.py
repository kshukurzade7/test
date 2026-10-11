"""SHIRÁ logo kit.

Master logo: the eight-segment citrus slice in a warm "sun" palette (gold at the
top deepening to red at the bottom, as if lit from above) with the SHIRÁ
wordmark. The colour story of the range lives in the flavour marks: one mark per
flavour in that flavour's label colour (no pomegranate).

Everything is drawn as outlines (the wordmark is converted from Cormorant
Garamond 500 with fontTools), so the SVG/PDF files need no fonts installed.

Run:  python3 logo.py && node export.mjs
      -> final/svg/*.svg (written here), final/png/*.png + final/pdf/*.pdf (export.mjs)
"""

import math
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
FONT = HERE.parent / "fonts" / "cormorant-garamond-latin-500-normal.woff2"
sys.path.insert(0, str(HERE.parent / "label"))
sys.path.insert(0, str(HERE.parent / "photo"))
sys.path.insert(0, str(HERE.parent / "composite"))
from collection import FLAVOURS  # noqa: E402

INK = "#3A2A22"
CREAM = "#F6EFE3"
GOLD = "#B8934A"
DARK_BG = "#2B201B"

# Sun palette by distance from the top of the slice: top pair, upper sides, lower sides, bottom pair.
SUN = ["#F2B33D", "#EF8E3A", "#E0612B", "#C9372C"]
SUN_SEGMENTS = [SUN[0], SUN[1], SUN[2], SUN[3], SUN[3], SUN[2], SUN[1], SUN[0]]  # clockwise from 12 o'clock

RANGE = [f for f in FLAVOURS if f["key"] != "pomegranate"]

_font = TTFont(FONT)
_glyphs = _font.getGlyphSet()
_cmap = _font.getBestCmap()
UPM = _font["head"].unitsPerEm


def text_outline(text, size, tracking):
    """Wordmark as one SVG path (baseline at y=0, starting at x=0). Returns (d, width, cap_height)."""
    scale = size / UPM
    pen = SVGPathPen(_glyphs)
    x = 0.0
    for i, ch in enumerate(text):
        name = _cmap[ord(ch)]
        _glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += _glyphs[name].width * scale + (tracking if i < len(text) - 1 else 0)
    cap = _font["OS/2"].sCapHeight * scale
    return pen.getCommands(), x, cap


def mark(r, colours, cx=0.0, cy=0.0):
    """Citrus slice as eight separate segment shapes: real gaps between them and a hole in the
    middle, so the mark works on any background."""
    d, ri = r * 0.0375, r * 0.3  # half the cut width, centre hole radius
    step = math.pi / 4
    out = []
    for k, colour in enumerate(colours):
        a0, a1 = k * step, (k + 1) * step

        def pt(a, rho, side):
            u = (math.sin(a), -math.cos(a))
            n = (math.cos(a), math.sin(a)) if side == 0 else (-math.cos(a), -math.sin(a))
            t = math.sqrt(rho * rho - d * d)
            return cx + n[0] * d + u[0] * t, cy + n[1] * d + u[1] * t

        p0o, p1o = pt(a0, r, 0), pt(a1, r, 1)
        p1i, p0i = pt(a1, ri, 1), pt(a0, ri, 0)
        out.append(f'<path fill="{colour}" d="M{p0o[0]:.3f} {p0o[1]:.3f} A{r} {r} 0 0 1 {p1o[0]:.3f} {p1o[1]:.3f} '
                   f'L{p1i[0]:.3f} {p1i[1]:.3f} A{ri} {ri} 0 0 0 {p0i[0]:.3f} {p0i[1]:.3f}Z"/>')
    return "".join(out)


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" '
            f'width="{w * 10:.0f}" height="{h * 10:.0f}">{rect}{body}</svg>\n')


def stacked(colours, ink, rule=GOLD, bg=None):
    r, size = 20, 30
    d, tw, cap = text_outline("SHIRÁ", size, size * 0.14)
    pad = 8
    w = max(tw, 2 * r) + 2 * pad
    cx = w / 2
    mark_y = pad + r
    base = mark_y + r + 12 + cap
    rule_y = base + 7
    h = rule_y + pad
    body = (mark(r, colours, cx, mark_y)
            + f'<path fill="{ink}" transform="translate({cx - tw / 2:.3f} {base:.3f})" d="{d}"/>'
            + (f'<rect x="{cx - 14:.2f}" y="{rule_y - 0.4:.2f}" width="28" height="0.8" fill="{rule}"/>' if rule else ""))
    return svg(w, h, body, bg)


def horizontal(colours, ink, bg=None):
    r, size = 13, 30
    d, tw, cap = text_outline("SHIRÁ", size, size * 0.14)
    pad = 6
    gap = 9
    h = 2 * r + 2 * pad
    cy = h / 2
    base = cy + cap / 2
    w = pad + 2 * r + gap + tw + pad
    body = (mark(r, colours, pad + r, cy)
            + f'<path fill="{ink}" transform="translate({pad + 2 * r + gap:.3f} {base:.3f})" d="{d}"/>')
    return svg(w, h, body, bg)


def mark_only(colours, bg=None, pad=4):
    r = 20
    w = 2 * (r + pad)
    return svg(w, w, mark(r, colours, w / 2, w / 2), bg)


def collection_sheet():
    """Flavour marks: one per flavour in its label colour, with the name underneath."""
    cols, cell_w, cell_h, r = 4, 46, 52, 13
    rows = math.ceil(len(RANGE) / cols)
    hd, hw, hcap = text_outline("SHIRÁ", 16, 16 * 0.14)
    top = 34
    w, h = cols * cell_w + 16, top + rows * cell_h + 8
    left = (w - (22 + 6 + hw)) / 2  # header: mark (r=11) + gap + wordmark, centred as one group
    body = [mark(11, SUN_SEGMENTS, left + 11, 17),
            f'<path fill="{INK}" transform="translate({left + 28:.2f} {17 + hcap / 2:.2f})" d="{hd}"/>']
    for i, f in enumerate(RANGE):
        in_row = min(cols, len(RANGE) - (i // cols) * cols)  # centre a short last row
        cx = w / 2 + ((i % cols) - (in_row - 1) / 2) * cell_w
        cy = top + (i // cols) * cell_h + r + 4
        nd, nw, _ = text_outline(f["name"], 7, 0.2)
        body.append(mark(r, [f["accent"]] * 8, cx, cy))
        body.append(f'<path fill="{f["accent"]}" transform="translate({cx - nw / 2:.2f} {cy + r + 11:.2f})" d="{nd}"/>')
    return svg(w, h, "".join(body), CREAM)


# name -> svg. Colour versions for light backgrounds, "on-dark" versions for dark ones,
# one-colour versions for stamps, embossing and single-colour print.
VERSIONS = {
    "shira-logo": stacked(SUN_SEGMENTS, INK),
    "shira-logo-on-dark": stacked(SUN_SEGMENTS, CREAM),
    "shira-logo-black": stacked([INK] * 8, INK, rule=INK),
    "shira-logo-white": stacked([CREAM] * 8, CREAM, rule=CREAM),
    "shira-logo-horizontal": horizontal(SUN_SEGMENTS, INK),
    "shira-logo-horizontal-on-dark": horizontal(SUN_SEGMENTS, CREAM),
    "shira-mark": mark_only(SUN_SEGMENTS),
    "shira-mark-black": mark_only([INK] * 8),
    "shira-mark-white": mark_only([CREAM] * 8),
    "shira-avatar": mark_only(SUN_SEGMENTS, bg=CREAM, pad=12),
    "shira-flavour-marks": collection_sheet(),
}


def main():
    out = HERE / "final" / "svg"
    out.mkdir(parents=True, exist_ok=True)
    for name, data in VERSIONS.items():
        (out / f"{name}.svg").write_text(data, encoding="utf-8")


if __name__ == "__main__":
    main()
