"""Add flavour-specific botanical illustrations onto the original SHIRÁ render.

The original bottle render (base.png) is kept untouched. Each label's coloured
band gets a fine-line, engraving-style botanical drawing of its fruit in the
label's cream ink, in the empty area between the local fruit name and the
"PRODUCT OF AZERBAIJAN" line.

Run:  python3 composite.py  ->  shira-with-fruit.svg and view.html
      node shot.mjs view.html shira-with-fruit.png 0 0 613 569 3
"""

import base64
import math
from pathlib import Path

HERE = Path(__file__).parent
W, H = 613, 569
INK = "#F6EFE3"
SW = 1.5  # main stroke width in drawing units

# (fruit key, centre x, centre y, scale) in base.png pixel coordinates
PLACEMENTS = [
    ("apricot", 129, 444, 0.4),
    ("pomegranate", 296, 450, 0.42),
    ("grape", 469, 441, 0.42),
]


def leaf(x, y, rot, length=30, width=8, veins=4):
    """Slender leaf with midrib and side veins, base at (x, y)."""
    L, w = length, width
    v = "".join(
        f"M {L*t:.1f} 0 Q {L*t+4:.1f} {-w*0.45:.1f} {L*t+7:.1f} {-w*0.62:.1f} "
        f"M {L*t:.1f} 0 Q {L*t+4:.1f} {w*0.45:.1f} {L*t+7:.1f} {w*0.62:.1f} "
        for t in [0.18 + i * 0.6 / veins for i in range(veins)])
    return (f'<g transform="translate({x} {y}) rotate({rot})">'
            f'<path d="M 0 0 C {L*0.3} {-w} {L*0.7} {-w} {L} 0 C {L*0.7} {w} {L*0.3} {w} 0 0 Z" '
            f'stroke-width="{SW}"/>'
            f'<path d="M 0 0 Q {L*0.5} {-1} {L*0.96} 0" stroke-width="{SW*0.7}"/>'
            f'<path d="{v}" stroke-width="{SW*0.45}"/></g>')


def hatching(uid, cx, cy, r, ox, oy, spacing=3.2, angle=-35):
    """Diagonal hatching in the shadow crescent of a sphere (cx, cy, r)."""
    lines = []
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    n = int(2 * r / spacing) + 2
    for i in range(-n, n + 1):
        px, py = cx + nx * i * spacing, cy + ny * i * spacing
        lines.append(f"M {px - dx*r*1.5:.1f} {py - dy*r*1.5:.1f} L {px + dx*r*1.5:.1f} {py + dy*r*1.5:.1f}")
    return (f'<clipPath id="ha-{uid}"><circle cx="{cx}" cy="{cy}" r="{r - 1}"/></clipPath>'
            f'<clipPath id="hb-{uid}"><path clip-rule="evenodd" d="M {cx-r*3} {cy-r*3} h {r*6} v {r*6} h {-r*6} Z '
            f'M {cx+ox+r} {cy+oy} A {r} {r} 0 1 0 {cx+ox-r} {cy+oy} A {r} {r} 0 1 0 {cx+ox+r} {cy+oy} Z"/></clipPath>'
            f'<g clip-path="url(#ha-{uid})"><g clip-path="url(#hb-{uid})">'
            f'<path d="{" ".join(lines)}" stroke-width="{SW*0.4}" opacity="0.85"/></g></g>')


def line_art(key):
    if key == "pomegranate":
        seeds = "".join(
            f'<g transform="translate({x} {y}) rotate({r})"><path d="M 0 -3.4 C 3 -1 3 2.6 0 3.4 C -3 2.6 -3 -1 0 -3.4 Z" stroke-width="{SW*0.7}"/>'
            f'<path d="M -0.8 -1 Q -1 0.5 -0.4 1.4" stroke-width="{SW*0.4}"/></g>'
            for x, y, r in ((40, 30, 20), (47, 24, -25), (46, 34, 60)))
        return f"""
<path d="M -1 -32 C -3 -38 -6 -42 -10 -45" stroke-width="{SW}"/>
{leaf(-10, -45, -165, 26, 6.5)}{leaf(-10, -45, -115, 22, 6)}{leaf(-3, -38, -25, 24, 6.5)}
<path d="M -8 -20 L -11 -31 L -5 -26 L -2 -34 L 1 -26 L 5 -33 L 7 -26 L 12 -30 L 9 -20" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M 0 -20 C 18 -22 32 -8 32 8 C 32 26 18 38 0 38 C -18 38 -32 26 -32 8 C -32 -8 -18 -22 0 -20 Z" stroke-width="{SW*1.1}"/>
<path d="M -20 -6 C -25 4 -24 16 -17 25" stroke-width="{SW*0.6}"/>
<path d="M -14 -12 C -17 -9 -19 -6 -20 -3" stroke-width="{SW*0.6}"/>
{hatching("pom", 0, 9, 32, -9, -7)}
{seeds}"""
    if key == "apricot":
        return f"""
<path d="M -16 -18 C -14 -28 -6 -36 2 -40" stroke-width="{SW}"/>
<path d="M 22 -6 C 20 -20 10 -32 2 -40" stroke-width="{SW}"/>
{leaf(2, -40, -155, 26, 9, 4)}{leaf(2, -40, -28, 26, 9, 4)}
<circle cx="-16" cy="4" r="22" stroke-width="{SW*1.1}"/>
<path d="M -16 -18 C -26 -6 -26 14 -18 26" stroke-width="{SW*0.7}"/>
{hatching("apr1", -16, 4, 22, -7, -6)}
<circle cx="22" cy="12" r="18" stroke-width="{SW*1.1}"/>
<path d="M 22 -6 C 14 4 14 20 20 30" stroke-width="{SW*0.7}"/>
{hatching("apr2", 22, 12, 18, -6, -5)}"""
    if key == "grape":
        rows = [(-8, [-18, -6, 6, 18]), (3, [-12, 0, 12]), (3, [-24, 24]), (14, [-18, -6, 6, 18]),
                (25, [-12, 0, 12]), (36, [-6, 6]), (47, [0])]
        grapes = "".join(
            f'<circle cx="{x}" cy="{y}" r="5.6" stroke-width="{SW}"/>'
            f'<path d="M {x-3.4} {y-1} A 3.6 3.6 0 0 1 {x-0.6} {y-3.8}" stroke-width="{SW*0.6}"/>'
            f'<path d="M {x+1.5} {y+5.2} A 5.6 5.6 0 0 0 {x+5.4} {y+1.2}" stroke-width="{SW*1.6}" opacity="0.7"/>'
            for y, xs in rows for x in xs)
        return f"""
<path d="M 2 -16 C 2 -24 4 -30 10 -36 C 16 -42 26 -44 34 -42" stroke-width="{SW*1.2}"/>
<g transform="translate(-26 -28) rotate(-20) scale(0.85)">
  <path d="M 0 22 C -6 18 -20 20 -26 10 L -22 8 C -30 2 -32 -10 -24 -16 L -20 -12 C -20 -22 -10 -28 -4 -24 L 0 -30 L 4 -24 C 10 -28 20 -22 20 -12 L 24 -16 C 32 -10 30 2 22 8 L 26 10 C 20 20 6 18 0 22 Z" stroke-width="{SW*1.15}" stroke-linejoin="round"/>
  <path d="M 0 18 L 0 -26 M 0 12 L -21 -11 M 0 12 L 21 -11 M 0 16 L -21 8 M 0 16 L 21 8" stroke-width="{SW*0.55}"/>
</g>
<path d="M 8 -34 C 14 -46 26 -48 30 -40 C 33 -34 26 -30 24 -35 C 23 -38 26 -39 27 -37" stroke-width="{SW*0.7}"/>
<path d="M 2 -16 L 0 -12" stroke-width="{SW}"/>
{grapes}"""
    raise ValueError(key)


def main():
    img = base64.b64encode((HERE / "base.png").read_bytes()).decode()
    art = "\n".join(
        f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{INK}" '
        f'stroke-linecap="round" opacity="0.94" filter="url(#ink)">{line_art(k)}</g>'
        for k, x, y, s in PLACEMENTS)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <!-- very slight softening so the vector lines sit in the photographic render -->
  <filter id="ink" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="0.6"/>
  </filter>
</defs>
<image href="data:image/png;base64,{img}" width="{W}" height="{H}"/>
{art}
</svg>
"""
    (HERE / "shira-with-fruit.svg").write_text(svg, encoding="utf-8")
    (HERE / "view.html").write_text(f'<body style="margin:0">{svg}</body>', encoding="utf-8")


if __name__ == "__main__":
    main()
