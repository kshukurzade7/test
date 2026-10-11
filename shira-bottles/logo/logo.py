"""Colourful SHIRÁ logo: the citrus-slice mark with each of its eight segments in a
flavour colour from the range (no pomegranate), plus the SHIRÁ wordmark.

Variants:
  A  colourful mark, wordmark in ink (calm, premium)
  B  colourful mark, each wordmark letter in a flavour colour (playful)
  C  mark with a smooth colour flow around the slice, wordmark in ink

Run:  python3 logo.py  ->  preview/variant-<a|b|c>-<light|dark>.svg and preview/compare.html
"""

import colorsys
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "photo"))
from photo import embedded_fonts  # noqa: E402

CREAM = "#F6EFE3"
INK = "#3A2A22"
GOLD = "#B8934A"
DARK_BG = "#2B201B"
SERIF = "'Cormorant Garamond', Georgia, serif"

# Segment colours, clockwise from the top, in colour-wheel order (flavour band colours).
SEGMENTS = [
    ("blackcurrant", "#5A2D63"),
    ("redcurrant", "#C21F3A"),
    ("rosehip", "#D9502F"),
    ("pumpkin", "#E67722"),
    ("peach", "#F2A06E"),
    ("quince", "#D9A22F"),
    ("pear", "#9AA13A"),
    ("feijoa", "#4F7A3A"),
]
# Variant B letter colours (S H I R Á).
LETTERS = ["#5A2D63", "#C21F3A", "#E67722", "#D9A22F", "#4F7A3A"]


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def mix(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#" + "".join(f"{round((x + (y - x) * t) * 255):02X}" for x, y in zip(ra, rb))


def wedge(r, a0, a1, fill):
    """Pie slice from angle a0 to a1 (radians, 0 = up, clockwise)."""
    x0, y0 = r * math.sin(a0), -r * math.cos(a0)
    x1, y1 = r * math.sin(a1), -r * math.cos(a1)
    large = 1 if a1 - a0 > math.pi else 0
    return f'<path d="M0 0 L{x0:.3f} {y0:.3f} A{r} {r} 0 {large} 1 {x1:.3f} {y1:.3f} Z" fill="{fill}"/>'


def mark(r, smooth=False, gap_colour=CREAM):
    """Citrus slice: eight segments split by four thin straight cuts, light centre."""
    step = math.pi / 4
    if smooth:
        # Many thin wedges blending each segment colour into the next.
        # Each wedge overlaps the next one so no hairline seams show between them.
        n = 32
        parts = []
        for k, (_, c) in enumerate(SEGMENTS):
            nxt = SEGMENTS[(k + 1) % len(SEGMENTS)][1]
            for j in range(n):
                a0 = k * step + j * step / n
                parts.append(wedge(r, a0, a0 + 3 * step / n, mix(c, nxt, j / n)))
        body = "".join(parts)
    else:
        body = "".join(wedge(r, k * step, (k + 1) * step, c) for k, (_, c) in enumerate(SEGMENTS))
    gap = r * 0.075
    cuts = "".join(
        f'<line x1="{-r*1.05*math.sin(a):.3f}" y1="{r*1.05*math.cos(a):.3f}" '
        f'x2="{r*1.05*math.sin(a):.3f}" y2="{-r*1.05*math.cos(a):.3f}" stroke="{gap_colour}" stroke-width="{gap:.3f}"/>'
        for a in [k * step for k in range(4)])
    return f'{body}{cuts}<circle r="{r*0.3:.3f}" fill="{gap_colour}"/>'


def wordmark(x, y, size, variant, ink, dark=False):
    spacing = size * 0.215
    if variant == "b":
        # Lift the darkest letter colours on a dark background so every letter stays readable.
        colours = [mix(c, "#FFFFFF", 0.3) if dark else c for c in LETTERS]
        spans = "".join(f'<tspan fill="{c}">{ch}</tspan>' for ch, c in zip("SHIRÁ", colours))
        return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{SERIF}" font-weight="500" '
                f'font-size="{size}" letter-spacing="{spacing:.2f}">{spans}</text>')
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{SERIF}" font-weight="500" '
            f'font-size="{size}" letter-spacing="{spacing:.2f}" fill="{ink}">SHIRÁ</text>')


def stacked(variant, dark=False):
    """Full logo: mark above the wordmark, gold rule below (same proportions as the label)."""
    bg = DARK_BG if dark else CREAM
    ink = CREAM if dark else INK
    w, h = 120, 100
    cx = w / 2
    content = (f'<g transform="translate({cx} 26)">{mark(15, smooth=variant == "c", gap_colour=bg)}</g>'
               + wordmark(cx + 2.9, 72, 27, variant, ink, dark)
               + f'<line x1="{cx - 14}" y1="80" x2="{cx + 14}" y2="80" stroke="{GOLD}" stroke-width="0.7"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 4}" height="{h * 4}">'
            f'{embedded_fonts()}<rect width="{w}" height="{h}" fill="{bg}"/>{content}</svg>\n')


def main():
    out = HERE / "preview"
    out.mkdir(exist_ok=True)
    rows = []  # compare sheet: one row per variant (light, dark), caption underneath
    for v, title in [("a", "A — rəngbərəng nişan, tünd yazı"),
                     ("b", "B — rəngbərəng nişan, rəngli hərflər"),
                     ("c", "C — nişanda yumşaq rəng keçidi")]:
        pair = []
        for dark in (False, True):
            svg = stacked(v, dark)
            (out / f"variant-{v}-{'dark' if dark else 'light'}.svg").write_text(svg, encoding="utf-8")
            pair.append(svg)
        rows.append(f'<div class="row">{"".join(pair)}</div><p>{title}</p>')
    html = ('<!doctype html><meta charset="utf-8"><body style="margin:0;padding:24px;background:#E9DDCB;'
            "font:600 22px Montserrat,Arial,sans-serif;color:#3A2A22\">"
            '<style>.row{display:flex;gap:16px}.row svg{width:420px;height:350px;border-radius:12px}'
            "p{margin:8px 0 28px}</style>" + "".join(rows) + "</body>")
    (out / "compare.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
