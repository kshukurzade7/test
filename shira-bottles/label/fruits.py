"""Tone-on-tone fruit illustrations for the SHIRÁ colour band.

Same visual language as composite/hero.py: flat shapes in translucent white
(LIGHT) and black (DARK) laid over the band colour, so every flavour takes on
its own band colour automatically. Each function draws around (cx, cy) with
overall radius r and returns SVG markup.
"""

import math

L, D = "#ffffff", "#000000"


def _p(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def leaf(x, y, length, width, rot, op=0.12, vein=True):
    """Simple pointed leaf, base at (x, y), pointing along rot degrees."""
    s = (f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.1f})">'
         f'<path d="M 0 0 C {length*0.25:.2f} {-width:.2f} {length*0.75:.2f} {-width:.2f} {length:.2f} 0 '
         f'C {length*0.75:.2f} {width:.2f} {length*0.25:.2f} {width:.2f} 0 0 Z" fill="{L}" fill-opacity="{op}"/>')
    if vein:
        s += f'<path d="M 0 0 L {length*0.95:.2f} 0" stroke="{D}" stroke-opacity="0.12" stroke-width="{width*0.08:.2f}"/>'
    return s + "</g>"


def berry(x, y, r, op=0.2, calyx=False, glossy=True):
    s = f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{L}" fill-opacity="{op}"/>'
    if glossy:
        s += (f'<path d="M {x - r*0.6:.2f} {y - r*0.1:.2f} A {r*0.62:.2f} {r*0.62:.2f} 0 0 1 {x - r*0.1:.2f} {y - r*0.62:.2f}" '
              f'stroke="{L}" stroke-opacity="0.38" stroke-width="{r*0.16:.2f}" fill="none" stroke-linecap="round"/>'
              f'<path d="M {x + r*0.92:.2f} {y + r*0.15:.2f} A {r*0.92:.2f} {r*0.92:.2f} 0 0 1 {x + r*0.15:.2f} {y + r*0.92:.2f}" '
              f'stroke="{D}" stroke-opacity="0.14" stroke-width="{r*0.2:.2f}" fill="none"/>')
    if calyx:
        pts = [(x + r * 0.28 * math.cos(a) * (1 if k % 2 == 0 else 0.4), y + r * 0.55 + r * 0.28 * math.sin(a) * (1 if k % 2 == 0 else 0.4))
               for k, a in enumerate([i * math.pi / 5 for i in range(10)])]
        s += f'<polygon points="{_p(pts)}" fill="{D}" fill-opacity="0.22"/>'
    return s


def stem(points, w, op=0.22):
    d = f"M {points[0][0]:.2f} {points[0][1]:.2f} " + " ".join(
        f"Q {points[i][0]:.2f} {points[i][1]:.2f} {points[i+1][0]:.2f} {points[i+1][1]:.2f}" for i in range(1, len(points) - 1, 2))
    return f'<path d="{d}" stroke="{L}" stroke-opacity="{op}" stroke-width="{w:.2f}" fill="none" stroke-linecap="round"/>'


# ---------------------------------------------------------------- berries

def _raceme(cx, cy, r, rnd, count, br, op, translucent=False):
    """A drooping string of berries hanging from a curved stalk."""
    out = [stem([(cx - r * 0.55, cy - r * 0.95), (cx - r * 0.1, cy - r * 0.9), (cx + r * 0.15, cy - r * 0.55),
                 (cx + r * 0.35, cy - r * 0.2), (cx + r * 0.3, cy + r * 0.75)], r * 0.035)]
    for i in range(count):
        t = i / (count - 1)
        x = cx + r * (0.18 + 0.2 * math.sin(t * 2.6)) + (rnd.uniform(-1, 1) * r * 0.06) + (-1) ** i * r * 0.17
        y = cy - r * 0.55 + t * r * 1.35
        rr = br * (1.15 - 0.4 * t) * rnd.uniform(0.92, 1.05)
        out.append(f'<line x1="{cx + r*0.3:.2f}" y1="{y - rr*0.6:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{L}" stroke-opacity="0.18" stroke-width="{r*0.015:.2f}"/>')
        out.append(berry(x, y, rr, op, calyx=True))
        if translucent:
            out.append("".join(
                f'<path d="M {x:.2f} {y - rr*0.85:.2f} Q {x + rr*0.55*math.cos(a):.2f} {y:.2f} {x:.2f} {y + rr*0.85:.2f}" '
                f'stroke="{L}" stroke-opacity="0.22" stroke-width="{rr*0.06:.2f}" fill="none"/>' for a in (-0.9, 0, 0.9)))
    return "".join(out)


def blackcurrant(cx, cy, r, rnd):
    lobe = (f'<g transform="translate({cx - r*0.45:.2f} {cy - r*0.2:.2f}) scale({r/30:.3f}) rotate(-15)">'
            f'<path d="M 0 22 C -10 20 -26 14 -28 0 C -26 -4 -20 -4 -18 -8 C -24 -18 -14 -30 -4 -22 C 0 -32 12 -30 12 -22 '
            f'C 22 -28 32 -16 24 -8 C 30 -4 30 4 26 6 C 22 18 10 20 0 22 Z" fill="{L}" fill-opacity="0.11"/>'
            f'<path d="M 0 20 L -2 -24 M 0 12 L -22 -6 M 0 12 L 22 -10 M 0 16 L -24 6 M 0 16 L 24 4" stroke="{D}" stroke-opacity="0.12" stroke-width="0.9" fill="none"/></g>')
    return lobe + _raceme(cx, cy, r, rnd, 9, r * 0.17, 0.2)


def redcurrant(cx, cy, r, rnd):
    return (leaf(cx - r * 0.2, cy - r * 0.75, r * 0.9, r * 0.32, 200, 0.12)
            + leaf(cx - r * 0.1, cy - r * 0.7, r * 0.75, r * 0.26, 150, 0.1)
            + _raceme(cx, cy, r, rnd, 10, r * 0.15, 0.24, translucent=True))


def cranberry(cx, cy, r, rnd):
    out = []
    for (dx, dy, s) in ((-0.62, -0.52, 0.2), (0.62, -0.58, 0.18), (0.75, 0.35, 0.21), (-0.72, 0.45, 0.19), (0.05, -0.95, 0.17), (-0.15, 0.95, 0.18)):
        x, y, rr = cx + dx * r, cy + dy * r, s * r
        out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rr:.2f}" ry="{rr*0.88:.2f}" fill="{L}" fill-opacity="0.2" '
                   f'transform="rotate({rnd.uniform(-30, 30):.0f} {x:.2f} {y:.2f})"/>'
                   f'<circle cx="{x - rr*0.35:.2f}" cy="{y - rr*0.35:.2f}" r="{rr*0.18:.2f}" fill="{L}" fill-opacity="0.35"/>')
    # halved cranberry: four air chambers
    R = r * 0.5
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R:.2f}" fill="{L}" fill-opacity="0.2"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{R*0.86:.2f}" fill="{L}" fill-opacity="0.12"/>')
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        x, y = cx + math.cos(a) * R * 0.42, cy + math.sin(a) * R * 0.42
        out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{R*0.26:.2f}" ry="{R*0.16:.2f}" fill="{D}" fill-opacity="0.16" '
                   f'transform="rotate({math.degrees(a):.0f} {x:.2f} {y:.2f})"/>'
                   f'<circle cx="{cx + math.cos(a) * R * 0.3:.2f}" cy="{cy + math.sin(a) * R * 0.3:.2f}" r="{R*0.05:.2f}" fill="{L}" fill-opacity="0.45"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R*0.08:.2f}" fill="{L}" fill-opacity="0.3"/>')
    return "".join(out)


def hawthorn(cx, cy, r, rnd):
    # deeply lobed leaf
    lf = (f'<g transform="translate({cx - r*0.15:.2f} {cy - r*0.55:.2f}) rotate(-140) scale({r/30:.3f})">'
          f'<path d="M 0 0 C 6 -6 10 -10 14 -8 C 12 -14 18 -18 22 -14 C 22 -20 30 -20 32 -14 C 36 -10 34 -4 30 0 '
          f'C 34 4 36 10 32 14 C 30 20 22 20 22 14 C 18 18 12 14 14 8 C 10 10 6 6 0 0 Z" fill="{L}" fill-opacity="0.12"/>'
          f'<path d="M 0 0 L 31 0 M 12 0 L 22 -12 M 12 0 L 22 12 M 20 0 L 30 -12 M 20 0 L 30 12" stroke="{D}" stroke-opacity="0.12" stroke-width="0.8"/></g>')
    out = [lf, stem([(cx - r * 0.1, cy - r * 0.6), (cx + r * 0.1, cy - r * 0.45), (cx + r * 0.2, cy - r * 0.2)], r * 0.03)]
    pos = [(0.0, 0.0), (0.42, 0.05), (0.2, 0.38), (-0.25, 0.32), (0.62, 0.42), (0.05, 0.75), (-0.45, 0.68), (0.45, 0.8), (-0.05, -0.38)]
    for dx, dy in pos:
        x, y, rr = cx + r * (0.2 + dx), cy + r * (dy - 0.05), r * 0.17 * rnd.uniform(0.9, 1.05)
        out.append(f'<line x1="{cx + r*0.2:.2f}" y1="{cy - r*0.2:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{L}" stroke-opacity="0.16" stroke-width="{r*0.014:.2f}"/>')
    for dx, dy in pos:
        x, y, rr = cx + r * (0.2 + dx), cy + r * (dy - 0.05), r * 0.17 * rnd.uniform(0.9, 1.05)
        out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rr:.2f}" ry="{rr*1.08:.2f}" fill="{L}" fill-opacity="0.22"/>'
                   f'<circle cx="{x:.2f}" cy="{y + rr*0.72:.2f}" r="{rr*0.22:.2f}" fill="{D}" fill-opacity="0.22"/>'
                   f'<circle cx="{x - rr*0.35:.2f}" cy="{y - rr*0.38:.2f}" r="{rr*0.16:.2f}" fill="{L}" fill-opacity="0.35"/>')
    return "".join(out)


def rosehip(cx, cy, r, rnd):
    out = [stem([(cx - r * 0.9, cy - r * 0.9), (cx - r * 0.3, cy - r * 0.8), (cx, cy - r * 0.45)], r * 0.04),
           stem([(cx - r * 0.3, cy - r * 0.8), (cx + r * 0.3, cy - r * 0.95), (cx + r * 0.65, cy - r * 0.6)], r * 0.03),
           leaf(cx - r * 0.55, cy - r * 0.85, r * 0.55, r * 0.2, 150, 0.12),
           leaf(cx - r * 0.2, cy - r * 0.85, r * 0.5, r * 0.18, 250, 0.1)]

    def hip(x, y, rx, ry, rot, halved=False):
        g = [f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.0f})">',
             f'<ellipse rx="{rx:.2f}" ry="{ry:.2f}" fill="{L}" fill-opacity="0.2"/>']
        if halved:
            g.append(f'<ellipse rx="{rx*0.72:.2f}" ry="{ry*0.78:.2f}" fill="{L}" fill-opacity="0.14"/>')
            for i in range(9):
                sx, sy = rnd.uniform(-0.4, 0.4) * rx, rnd.uniform(-0.55, 0.55) * ry
                g.append(f'<ellipse cx="{sx:.2f}" cy="{sy:.2f}" rx="{rx*0.14:.2f}" ry="{rx*0.2:.2f}" fill="{D}" fill-opacity="0.18"/>')
        else:
            g.append(f'<path d="M {-rx*0.55:.2f} {-ry*0.2:.2f} A {rx*0.6:.2f} {ry*0.6:.2f} 0 0 1 {-rx*0.1:.2f} {-ry*0.72:.2f}" '
                     f'stroke="{L}" stroke-opacity="0.38" stroke-width="{rx*0.14:.2f}" fill="none" stroke-linecap="round"/>')
        # sepal crown at the tip
        for k in range(5):
            a = math.radians(-90 + (k - 2) * 28)
            g.append(f'<path d="M 0 {ry*0.95:.2f} q {math.cos(a + math.pi)*rx*0.2:.2f} {ry*0.35:.2f} {math.cos(a + math.pi)*rx*0.55:.2f} {ry*0.45:.2f}" '
                     f'stroke="{L}" stroke-opacity="0.25" stroke-width="{rx*0.07:.2f}" fill="none" stroke-linecap="round"/>')
        g.append("</g>")
        return "".join(g)

    out.append(hip(cx, cy - r * 0.05, r * 0.24, r * 0.38, -8))
    out.append(hip(cx + r * 0.62, cy - r * 0.2, r * 0.21, r * 0.33, 18))
    out.append(hip(cx + r * 0.25, cy + r * 0.62, r * 0.27, r * 0.4, -20, halved=True))
    return "".join(out)


# ---------------------------------------------------------------- tree fruit

def _stone_halved(cx, cy, r, rnd, stone_rx, stone_ry, cleft=True, leaves=2):
    out = []
    for i in range(leaves):
        out.append(leaf(cx + r * (0.1 + 0.25 * i), cy - r * 0.95, r * (0.75 - 0.15 * i), r * 0.22, -25 - 35 * i, 0.13))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r*0.92:.2f}" fill="{L}" fill-opacity="0.13"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{r*0.84:.2f}" fill="{L}" fill-opacity="0.12"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{r*0.42:.2f}" fill="{D}" fill-opacity="0.06"/>')
    if cleft:
        out.append(f'<path d="M {cx - r*0.1:.2f} {cy - r*0.92:.2f} Q {cx - r*0.02:.2f} {cy - r*0.75:.2f} {cx + r*0.05:.2f} {cy - r*0.6:.2f}" '
                   f'stroke="{D}" stroke-opacity="0.14" stroke-width="{r*0.03:.2f}" fill="none"/>')
    out.append(f'<g transform="translate({cx} {cy}) rotate(-12)">'
               f'<path d="M 0 {-stone_ry:.2f} C {stone_rx*1.35:.2f} {-stone_ry*0.8:.2f} {stone_rx*1.35:.2f} {stone_ry*0.8:.2f} 0 {stone_ry:.2f} '
               f'C {-stone_rx*1.35:.2f} {stone_ry*0.8:.2f} {-stone_rx*1.35:.2f} {-stone_ry*0.8:.2f} 0 {-stone_ry:.2f} Z" fill="{D}" fill-opacity="0.18"/>')
    for i in range(9):  # wrinkled stone
        y0 = rnd.uniform(-0.75, 0.75) * stone_ry
        x0 = rnd.uniform(-0.6, 0.2) * stone_rx
        out.append(f'<path d="M {x0:.2f} {y0:.2f} q {stone_rx*0.25:.2f} {rnd.uniform(-1, 1)*stone_ry*0.15:.2f} {stone_rx*0.55:.2f} {rnd.uniform(-1, 1)*stone_ry*0.1:.2f}" '
                   f'stroke="{D}" stroke-opacity="0.2" stroke-width="{stone_rx*0.06:.2f}" fill="none" stroke-linecap="round"/>')
    out.append("</g>")
    out.append(f'<path d="M {cx - r*0.62:.2f} {cy - r*0.5:.2f} A {r*0.8:.2f} {r*0.8:.2f} 0 0 1 {cx - r*0.1:.2f} {cy - r*0.8:.2f}" '
               f'stroke="{L}" stroke-opacity="0.25" stroke-width="{r*0.04:.2f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def peach(cx, cy, r, rnd):
    return _stone_halved(cx, cy, r, rnd, r * 0.24, r * 0.36, cleft=True, leaves=2)


def _pome(cx, cy, r, outline, seeds_star=False, core_pear=False, quince_bumps=False):
    """Halved pome fruit (apple / pear / quince) with core and seeds."""
    out = [f'<path d="{outline}" fill="{L}" fill-opacity="0.13"/>',
           f'<path d="{outline}" fill="{L}" fill-opacity="0.12" transform="translate({cx*0.06:.2f} {cy*0.06:.2f}) scale(0.94)"/>']
    if seeds_star:
        out.append(f'<g transform="translate({cx} {cy})">')
        star = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r * (0.36 if k % 2 == 0 else 0.13)
            star.append((rr * math.cos(a), rr * math.sin(a)))
        out.append(f'<polygon points="{_p(star)}" fill="{D}" fill-opacity="0.08" stroke="{L}" stroke-opacity="0.25" stroke-width="{r*0.015:.2f}" stroke-linejoin="round"/>')
        for k in range(5):
            a = -90 + k * 72
            out.append(f'<g transform="rotate({a})"><path d="M {r*0.1:.2f} 0 Q {r*0.2:.2f} {-r*0.07:.2f} {r*0.3:.2f} 0 Q {r*0.2:.2f} {r*0.07:.2f} {r*0.1:.2f} 0 Z" '
                       f'fill="{D}" fill-opacity="0.3"/></g>')
        out.append("</g>")
    if core_pear:
        out.append(f'<path d="M {cx:.2f} {cy - r*0.55:.2f} C {cx + r*0.22:.2f} {cy - r*0.1:.2f} {cx + r*0.25:.2f} {cy + r*0.35:.2f} {cx:.2f} {cy + r*0.48:.2f} '
                   f'C {cx - r*0.25:.2f} {cy + r*0.35:.2f} {cx - r*0.22:.2f} {cy - r*0.1:.2f} {cx:.2f} {cy - r*0.55:.2f} Z" fill="{D}" fill-opacity="0.08"/>'
                   f'<path d="M {cx:.2f} {cy - r*0.88:.2f} L {cx:.2f} {cy - r*0.5:.2f}" stroke="{D}" stroke-opacity="0.1" stroke-width="{r*0.02:.2f}"/>')
        for sx in (-1, 1):
            out.append(f'<path d="M {cx + sx*r*0.03:.2f} {cy + r*0.08:.2f} q {sx*r*0.1:.2f} {-r*0.08:.2f} {sx*r*0.06:.2f} {-r*0.22:.2f} q {-sx*r*0.08:.2f} {r*0.06:.2f} {-sx*r*0.06:.2f} {r*0.22:.2f} Z" '
                       f'fill="{D}" fill-opacity="0.3"/>')
    return "".join(out)


def apple(cx, cy, r, rnd):
    o = (f"M {cx:.2f} {cy - r*0.62:.2f} C {cx + r*0.35:.2f} {cy - r*0.95:.2f} {cx + r*0.98:.2f} {cy - r*0.8:.2f} {cx + r*0.98:.2f} {cy - r*0.05:.2f} "
         f"C {cx + r*0.98:.2f} {cy + r*0.6:.2f} {cx + r*0.55:.2f} {cy + r*0.95:.2f} {cx + r*0.25:.2f} {cy + r*0.95:.2f} "
         f"C {cx + r*0.1:.2f} {cy + r*0.95:.2f} {cx + r*0.08:.2f} {cy + r*0.88:.2f} {cx:.2f} {cy + r*0.88:.2f} "
         f"C {cx - r*0.08:.2f} {cy + r*0.88:.2f} {cx - r*0.1:.2f} {cy + r*0.95:.2f} {cx - r*0.25:.2f} {cy + r*0.95:.2f} "
         f"C {cx - r*0.55:.2f} {cy + r*0.95:.2f} {cx - r*0.98:.2f} {cy + r*0.6:.2f} {cx - r*0.98:.2f} {cy - r*0.05:.2f} "
         f"C {cx - r*0.98:.2f} {cy - r*0.8:.2f} {cx - r*0.35:.2f} {cy - r*0.95:.2f} {cx:.2f} {cy - r*0.62:.2f} Z")
    return (stem([(cx, cy - r * 0.62), (cx + r * 0.02, cy - r * 0.85), (cx + r * 0.12, cy - r * 1.05)], r * 0.05)
            + leaf(cx + r * 0.08, cy - r * 0.92, r * 0.6, r * 0.2, -28, 0.14)
            + _pome(cx, cy, r, o, seeds_star=True))


def pear(cx, cy, r, rnd):
    o = (f"M {cx:.2f} {cy - r*0.95:.2f} C {cx + r*0.22:.2f} {cy - r*0.95:.2f} {cx + r*0.28:.2f} {cy - r*0.55:.2f} {cx + r*0.38:.2f} {cy - r*0.25:.2f} "
         f"C {cx + r*0.5:.2f} {cy + r*0.05:.2f} {cx + r*0.72:.2f} {cy + r*0.2:.2f} {cx + r*0.72:.2f} {cy + r*0.55:.2f} "
         f"C {cx + r*0.72:.2f} {cy + r*0.92:.2f} {cx + r*0.38:.2f} {cy + r*1.05:.2f} {cx:.2f} {cy + r*1.05:.2f} "
         f"C {cx - r*0.38:.2f} {cy + r*1.05:.2f} {cx - r*0.72:.2f} {cy + r*0.92:.2f} {cx - r*0.72:.2f} {cy + r*0.55:.2f} "
         f"C {cx - r*0.72:.2f} {cy + r*0.2:.2f} {cx - r*0.5:.2f} {cy + r*0.05:.2f} {cx - r*0.38:.2f} {cy - r*0.25:.2f} "
         f"C {cx - r*0.28:.2f} {cy - r*0.55:.2f} {cx - r*0.22:.2f} {cy - r*0.95:.2f} {cx:.2f} {cy - r*0.95:.2f} Z")
    return (stem([(cx, cy - r * 0.95), (cx + r * 0.02, cy - r * 1.12), (cx + r * 0.14, cy - r * 1.25)], r * 0.05)
            + leaf(cx + r * 0.08, cy - r * 1.12, r * 0.6, r * 0.2, -20, 0.14)
            + _pome(cx, cy + r * 0.12, r * 0.95, o, core_pear=True))


def quince(cx, cy, r, rnd):
    # lumpy, slightly irregular round outline
    pts = []
    for k in range(48):
        a = k / 48 * 2 * math.pi
        rr = r * (0.9 + 0.05 * math.sin(5 * a + 0.6) + 0.03 * math.sin(3 * a))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.96))
    o = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    fuzz = "".join(
        f'<circle cx="{cx + r*0.95*math.cos(a):.2f}" cy="{cy + r*0.92*math.sin(a):.2f}" r="{r*0.012:.2f}" fill="{L}" fill-opacity="0.3"/>'
        for a in [i * 0.21 for i in range(30)])
    return (leaf(cx + r * 0.15, cy - r * 0.92, r * 0.7, r * 0.3, -35, 0.13)
            + leaf(cx - r * 0.05, cy - r * 0.9, r * 0.55, r * 0.24, 205, 0.11)
            + _pome(cx, cy, r, o, seeds_star=True) + fuzz)


def feijoa(cx, cy, r, rnd):
    rx, ry = r * 0.62, r * 0.95
    out = [f'<g transform="rotate(-18 {cx} {cy})">',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{L}" fill-opacity="0.13"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*0.88:.2f}" ry="{ry*0.9:.2f}" fill="{L}" fill-opacity="0.12"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*0.5:.2f}" ry="{ry*0.58:.2f}" fill="{L}" fill-opacity="0.16"/>']
    for k in range(4):  # four jelly seed chambers in a cross
        a = k * math.pi / 2 + math.pi / 4
        x, y = cx + math.cos(a) * rx * 0.22, cy + math.sin(a) * ry * 0.26
        out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx*0.16:.2f}" ry="{ry*0.2:.2f}" fill="{D}" fill-opacity="0.1" '
                   f'transform="rotate({math.degrees(a):.0f} {x:.2f} {y:.2f})"/>')
        for j in range(4):
            out.append(f'<circle cx="{x + rnd.uniform(-0.5, 0.5)*rx*0.12:.2f}" cy="{y + rnd.uniform(-0.5, 0.5)*ry*0.14:.2f}" r="{r*0.018:.2f}" fill="{D}" fill-opacity="0.3"/>')
    out.append(f'<path d="M {cx:.2f} {cy - ry:.2f} l {-r*0.06:.2f} {-r*0.1:.2f} M {cx:.2f} {cy - ry:.2f} l {r*0.06:.2f} {-r*0.1:.2f} M {cx:.2f} {cy - ry:.2f} l 0 {-r*0.12:.2f}" '
               f'stroke="{L}" stroke-opacity="0.3" stroke-width="{r*0.025:.2f}" stroke-linecap="round"/>')
    out.append("</g>")
    out.insert(0, leaf(cx - r * 0.75, cy - r * 0.55, r * 0.75, r * 0.28, -60, 0.11))
    return "".join(out)


def pumpkin(cx, cy, r, rnd):
    out = [leaf(cx - r * 0.25, cy - r * 0.8, r * 0.8, r * 0.38, 200, 0.11),
           f'<path d="M {cx + r*0.05:.2f} {cy - r*0.62:.2f} C {cx + r*0.1:.2f} {cy - r*0.85:.2f} {cx + r*0.2:.2f} {cy - r*0.98:.2f} {cx + r*0.32:.2f} {cy - r*1.02:.2f}" '
           f'stroke="{L}" stroke-opacity="0.28" stroke-width="{r*0.11:.2f}" fill="none" stroke-linecap="round"/>',
           f'<path d="M {cx + r*0.25:.2f} {cy - r*0.95:.2f} c {r*0.25:.2f} {-r*0.05:.2f} {r*0.35:.2f} {r*0.15:.2f} {r*0.25:.2f} {r*0.25:.2f} '
           f'c {-r*0.08:.2f} {r*0.08:.2f} {-r*0.18:.2f} {-r*0.02:.2f} {-r*0.1:.2f} {-r*0.08:.2f}" stroke="{L}" stroke-opacity="0.25" stroke-width="{r*0.02:.2f}" fill="none"/>']
    ribs = [(-0.62, 0.42), (0.62, 0.42), (-0.32, 0.52), (0.32, 0.52), (0, 0.55)]
    for dx, w in ribs:
        out.append(f'<ellipse cx="{cx + dx*r:.2f}" cy="{cy:.2f}" rx="{w*r:.2f}" ry="{r*0.66:.2f}" fill="{L}" fill-opacity="0.12" '
                   f'stroke="{D}" stroke-opacity="0.1" stroke-width="{r*0.02:.2f}"/>')
    out.append(f'<path d="M {cx - r*0.75:.2f} {cy - r*0.25:.2f} Q {cx - r*0.62:.2f} {cy - r*0.55:.2f} {cx - r*0.35:.2f} {cy - r*0.6:.2f}" '
               f'stroke="{L}" stroke-opacity="0.3" stroke-width="{r*0.04:.2f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


FRUITS = {
    "blackcurrant": blackcurrant, "redcurrant": redcurrant, "cranberry": cranberry, "hawthorn": hawthorn,
    "rosehip": rosehip, "peach": peach, "apple": apple, "pear": pear, "quince": quince,
    "feijoa": feijoa, "pumpkin": pumpkin,
}
