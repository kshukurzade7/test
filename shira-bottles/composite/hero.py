"""Premium "tonal hero" band for the SHIRÁ render.

Keeps the original render (base.png), including the cream top of each label
with the SHIRÁ emblem and wordmark, and rebuilds only the coloured band:
a large, cropped, tone-on-tone fruit cross-section in the same visual language
as the SHIRÁ emblem, plus the original band text.

The flat band artwork is wrapped onto each bottle with a cylindrical warp
(thin vertical strips), and re-lit with the shading measured from the photo.

Inputs:  base.png, bands.json (per-column label measurements, see measure.py)
Outputs: shira-premium.svg, view.html, flat/<flavor>-band.svg (flat artwork)
"""

import base64
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).parent
W, H = 613, 569
CREAM = "#F6EFE3"
SERIF = "'Cormorant Garamond', Georgia, serif"
SANS = "'Montserrat', 'Helvetica Neue', Arial, sans-serif"
THETA_MAX = math.radians(78)
FONTS = ('<style>@import url("https://fonts.googleapis.com/css2?'
         'family=Cormorant+Garamond:ital,wght@0,500;1,500&amp;family=Montserrat:wght@500&amp;display=swap");</style>')

BOTTLES = {
    "apricot": dict(local="Ərik", band_h=81),
    "pomegranate": dict(local="Nar", band_h=85),
    "grape": dict(local="Üzüm", band_h=83),
}

LIGHT = "#ffffff"
DARK = "#000000"


# ------------------------------------------------------------ hero artwork
# Drawn in flat band coordinates; fw x fh is the unwrapped band.

def pomegranate(cx, cy, r, rnd):
    """Cross-section: rind, pith, six chambers of faceted arils."""
    membranes = [k * math.pi / 3 + 0.25 for k in range(6)]
    arils = []
    step = r * 0.125
    for iy in range(-9, 10):
        for ix in range(-9, 10):
            x = (ix + (iy % 2) * 0.5) * step + rnd.uniform(-0.12, 0.12) * step
            y = iy * step * 0.87 + rnd.uniform(-0.12, 0.12) * step
            d = math.hypot(x, y)
            if d > r * 0.8 or d < r * 0.15:
                continue
            a = math.atan2(y, x)
            # leave gaps along the membranes so the chambers read
            if any(abs(math.sin(a - m)) * d < step * 0.42 and math.cos(a - m) > 0 for m in membranes):
                continue
            rot = math.degrees(a) + rnd.uniform(-25, 25)
            s = step * rnd.uniform(0.44, 0.52)
            op = rnd.uniform(0.18, 0.28)
            arils.append(
                f'<g transform="translate({cx + x:.2f} {cy + y:.2f}) rotate({rot:.0f})">'
                f'<path d="M {-s} 0 Q {-s*0.9} {-s*0.95} 0 {-s*0.95} Q {s*1.2} {-s*0.7} {s*1.15} 0 '
                f'Q {s*1.2} {s*0.7} 0 {s*0.95} Q {-s*0.9} {s*0.95} {-s} 0 Z" fill="{LIGHT}" fill-opacity="{op:.2f}"/>'
                f'<ellipse cx="{-s*0.25:.2f}" cy="{-s*0.38:.2f}" rx="{s*0.32:.2f}" ry="{s*0.16:.2f}" fill="{LIGHT}" fill-opacity="0.4"/></g>')
    crown = (f'<path d="M {cx-r*0.2} {cy-r*0.93} L {cx-r*0.3} {cy-r*1.22} L {cx-r*0.12} {cy-r*1.08} '
             f'L {cx} {cy-r*1.3} L {cx+r*0.12} {cy-r*1.08} L {cx+r*0.3} {cy-r*1.22} L {cx+r*0.2} {cy-r*0.93} Z" '
             f'fill="{LIGHT}" fill-opacity="0.13"/>')
    return f"""
{crown}
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LIGHT}" fill-opacity="0.13"/>
<circle cx="{cx}" cy="{cy}" r="{r*0.88}" fill="{LIGHT}" fill-opacity="0.09"/>
<circle cx="{cx}" cy="{cy}" r="{r*0.84}" fill="{DARK}" fill-opacity="0.10"/>
{''.join(arils)}
<circle cx="{cx}" cy="{cy}" r="{r*0.1}" fill="{LIGHT}" fill-opacity="0.12"/>"""


def apricot(cx, cy, r, rnd):
    """Halved apricot: skin, flesh with fine radial fibres, ridged stone; leaf."""
    fibres = "".join(
        f'<path d="M {cx + r*0.38*math.cos(a):.2f} {cy + r*0.38*math.sin(a):.2f} '
        f'L {cx + r*0.82*math.cos(a):.2f} {cy + r*0.82*math.sin(a):.2f}" '
        f'stroke="{LIGHT}" stroke-opacity="0.12" stroke-width="0.5"/>'
        for a in [k * 2 * math.pi / 48 for k in range(48)])
    ridges = "".join(
        f'<path d="M {-r*0.13 + i*r*0.065:.2f} {-r*0.3:.2f} Q {-r*0.17 + i*r*0.065 + (i-2)*0.6:.2f} 0 '
        f'{-r*0.13 + i*r*0.065:.2f} {r*0.3:.2f}" stroke="{DARK}" stroke-opacity="0.16" stroke-width="0.6" fill="none"/>'
        for i in range(5))
    lx, ly = cx + r * 0.55, cy - r * 0.95
    return f"""
<g transform="translate({lx} {ly}) rotate(-30)">
  <path d="M 0 0 C {r*0.25} {-r*0.32} {r*0.75} {-r*0.32} {r} 0 C {r*0.75} {r*0.32} {r*0.25} {r*0.32} 0 0 Z" fill="{LIGHT}" fill-opacity="0.14"/>
  <path d="M 0 0 L {r*0.95} 0" stroke="{DARK}" stroke-opacity="0.12" stroke-width="0.7"/>
</g>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LIGHT}" fill-opacity="0.13"/>
<circle cx="{cx}" cy="{cy}" r="{r*0.92}" fill="{LIGHT}" fill-opacity="0.12"/>
<circle cx="{cx}" cy="{cy}" r="{r*0.42}" fill="{DARK}" fill-opacity="0.07"/>
<g transform="translate({cx} {cy}) rotate(-14)">
  <path d="M 0 {-r*0.36} C {r*0.24} {-r*0.3} {r*0.26} {r*0.26} 0 {r*0.36} C {-r*0.26} {r*0.26} {-r*0.24} {-r*0.3} 0 {-r*0.36} Z" fill="{DARK}" fill-opacity="0.17"/>
  {ridges}
</g>
<path d="M {cx - r*0.62} {cy - r*0.5} A {r*0.8} {r*0.8} 0 0 1 {cx - r*0.1} {cy - r*0.8}" stroke="{LIGHT}" stroke-opacity="0.25" stroke-width="1.2" fill="none" stroke-linecap="round"/>"""


def grape(cx, cy, r, rnd):
    """Bunch of berries with a vine leaf and tendril."""
    g = r * 0.17
    rows = [(-2, [-1.5, -0.5, 0.5, 1.5]), (-1, [-2, -1, 0, 1, 2]), (0, [-1.5, -0.5, 0.5, 1.5]),
            (1, [-1, 0, 1]), (2, [-1.5, -0.5, 0.5, 1.5]), (3, [-1, 0, 1]), (4, [-0.5, 0.5]), (5, [0])]
    berries = []
    for row, xs in rows:
        for xx in xs:
            x = cx + xx * g * 2.05 + rnd.uniform(-0.4, 0.4)
            y = cy + row * g * 1.8
            berries.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{g}" fill="{LIGHT}" fill-opacity="0.17"/>'
                f'<path d="M {x - g*0.62:.2f} {y - g*0.1:.2f} A {g*0.62} {g*0.62} 0 0 1 {x - g*0.1:.2f} {y - g*0.62:.2f}" '
                f'stroke="{LIGHT}" stroke-opacity="0.35" stroke-width="{g*0.16:.2f}" fill="none" stroke-linecap="round"/>'
                f'<path d="M {x + g*0.95:.2f} {y + g*0.1:.2f} A {g*0.95} {g*0.95} 0 0 1 {x + g*0.1:.2f} {y + g*0.95:.2f}" '
                f'stroke="{DARK}" stroke-opacity="0.16" stroke-width="{g*0.22:.2f}" fill="none"/>')
    s = r / 30
    leaf = (f'<g transform="translate({cx - r*0.55} {cy - r*0.62}) rotate(-24) scale({s})">'
            f'<path d="M 0 22 C -6 18 -20 20 -26 10 L -22 8 C -30 2 -32 -10 -24 -16 L -20 -12 C -20 -22 -10 -28 -4 -24 '
            f'L 0 -30 L 4 -24 C 10 -28 20 -22 20 -12 L 24 -16 C 32 -10 30 2 22 8 L 26 10 C 20 20 6 18 0 22 Z" '
            f'fill="{LIGHT}" fill-opacity="0.11"/>'
            f'<path d="M 0 18 L 0 -26 M 0 12 L -21 -11 M 0 12 L 21 -11 M 0 16 L -21 8 M 0 16 L 21 8" '
            f'stroke="{DARK}" stroke-opacity="0.12" stroke-width="0.9" fill="none"/></g>')
    stem = (f'<path d="M {cx} {cy - g*4.6} C {cx + 1} {cy - r*0.9} {cx + r*0.2} {cy - r*1.1} {cx + r*0.45} {cy - r*1.2}" '
            f'stroke="{LIGHT}" stroke-opacity="0.2" stroke-width="{g*0.35:.2f}" fill="none" stroke-linecap="round"/>'
            f'<path d="M {cx + r*0.15} {cy - r*1.0} C {cx + r*0.45} {cy - r*1.0} {cx + r*0.6} {cy - r*0.75} {cx + r*0.5} {cy - r*0.62} '
            f'C {cx + r*0.42} {cy - r*0.54} {cx + r*0.34} {cy - r*0.66} {cx + r*0.42} {cy - r*0.7}" '
            f'stroke="{LIGHT}" stroke-opacity="0.2" stroke-width="0.7" fill="none"/>')
    return leaf + stem + "".join(berries)


HERO = {"apricot": apricot, "pomegranate": pomegranate, "grape": grape}


def flat_band(key, fw, fh, local):
    """Flat (unwrapped) band artwork, transparent background."""
    rnd = random.Random(key)
    hero = HERO[key](fw * 0.66, fh * 0.52, fh * 0.56, rnd)
    return f"""
<clipPath id="flatclip-{key}"><rect width="{fw}" height="{fh}"/></clipPath>
<g clip-path="url(#flatclip-{key})">{hero}</g>
<text x="{fw*0.16:.1f}" y="{fh*0.27:.1f}" font-family="{SERIF}" font-style="italic" font-size="10" fill="{CREAM}">{local}</text>
<text x="{fw*0.16:.1f}" y="{fh*0.84:.1f}" font-family="{SANS}" font-size="4.4" letter-spacing="1.1" fill="{CREAM}">PRODUCT OF AZERBAIJAN</text>
<text x="{fw*0.82:.1f}" y="{fh*0.84:.1f}" text-anchor="end" font-family="{SANS}" font-size="5.6" fill="{CREAM}">500 ml</text>"""


# ---------------------------------------------------------- wrap onto photo

def smooth(vals, k=3):
    out = []
    for i in range(len(vals)):
        win = vals[max(0, i - k): i + k + 1]
        out.append(sum(win) / len(win))
    return out


def quad_fit(xs, ys):
    """Least-squares parabola through the measured label edge."""
    n = len(xs)
    sx = [sum(x ** k for x in xs) for k in range(5)]
    sy = [sum(y * x ** k for x, y in zip(xs, ys)) for k in range(3)]
    m = [[sx[i + j] for j in range(3)] + [sy[i]] for i in range(3)]
    for i in range(3):
        for r in range(i + 1, 3):
            f = m[r][i] / m[i][i]
            m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    c = [0, 0, 0]
    for i in (2, 1, 0):
        c[i] = (m[i][3] - sum(m[i][j] * c[j] for j in range(i + 1, 3))) / m[i][i]
    return [c[0] + c[1] * x + c[2] * x * x for x in xs]


def wrapped(key, cols, info):
    xs = [c[0] for c in cols]
    tops = quad_fit(xs, [c[1] for c in cols])
    bg = [smooth([c[3][ch] for c in cols], 7) for ch in range(3)]
    lum = [sum(bg[ch][i] for ch in range(3)) for i in range(len(xs))]
    x0, x1 = xs[0] + 0.5, xs[-1] + 0.5
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2
    R = half / math.sin(THETA_MAX)
    fw, fh = R * 2 * THETA_MAX, info["band_h"]
    top_at = lambda x: tops[min(len(xs) - 1, max(0, int(round(x - xs[0]))))]

    # band base colour = brightest measured colour; shading re-applied on top
    imax = max(range(len(xs)), key=lambda i: lum[i])
    base = "#%02x%02x%02x" % tuple(int(bg[ch][imax]) for ch in range(3))
    shade_stops = "".join(
        f'<stop offset="{(xs[i] + 0.5 - x0) / (x1 - x0):.3f}" stop-opacity="{max(0, 1 - lum[i] / lum[imax]):.3f}"/>'
        for i in range(0, len(xs), 2))

    outline_top = " ".join(f"L {x + 0.5:.1f} {t - 0.3:.2f}" for x, t in zip(xs, tops))
    outline_bot = " ".join(f"L {x + 0.5:.1f} {t + fh + 1:.2f}" for x, t in reversed(list(zip(xs, tops))))
    outline = "M" + outline_top[1:] + " " + outline_bot + " Z"

    strips = []
    n = 90
    for i in range(n):
        ta = -THETA_MAX + 2 * THETA_MAX * i / n
        tb = -THETA_MAX + 2 * THETA_MAX * (i + 1) / n
        xa, xb = cx + R * math.sin(ta), cx + R * math.sin(tb)
        fa, fb = R * (ta + THETA_MAX), R * (tb + THETA_MAX)
        sx = (xb - xa) / (fb - fa)
        ty = top_at((xa + xb) / 2)
        strips.append(
            f'<g transform="translate({xa:.3f} {ty:.3f}) scale({sx:.4f} 1) translate({-fa:.3f} 0)">'
            f'<g clip-path="url(#s-{key}-{i})"><use href="#flat-{key}"/></g></g>'
            f'<clipPath id="s-{key}-{i}"><rect x="{fa - 0.15:.3f}" y="-2" width="{fb - fa + 0.3:.3f}" height="{fh + 4}"/></clipPath>')

    flat = f'<rect x="-2" y="-3" width="{fw + 4:.1f}" height="{fh + 6}" fill="{base}"/>' + flat_band(key, fw, fh, info["local"])
    (HERE / "flat").mkdir(exist_ok=True)
    (HERE / "flat" / f"{key}-band.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fw:.1f} {fh}" width="{fw*6:.0f}" height="{fh*6}">'
        f'{FONTS}{flat}</svg>\n', encoding="utf-8")

    return f"""
<defs>
  <g id="flat-{key}">{flat}</g>
  <clipPath id="band-{key}"><path d="{outline}"/></clipPath>
  <linearGradient id="shade-{key}" gradientUnits="userSpaceOnUse" x1="{x0}" y1="0" x2="{x1}" y2="0">{shade_stops}</linearGradient>
</defs>
<g clip-path="url(#band-{key})" filter="url(#photo-soft)">
  <rect x="{x0 - 2}" y="{min(tops) - 2}" width="{x1 - x0 + 4}" height="{fh + 12}" fill="{base}"/>
  {''.join(strips)}
  <rect x="{x0 - 2}" y="{min(tops) - 2}" width="{x1 - x0 + 4}" height="{fh + 12}" fill="url(#shade-{key})"/>
</g>"""


def main():
    bands_file = HERE / "bands.json"
    bands = json.loads(bands_file.read_text())
    img = base64.b64encode((HERE / "base.png").read_bytes()).decode()
    body = "\n".join(wrapped(k, bands[k], info) for k, info in BOTTLES.items())
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">{FONTS}'
           f'<defs><filter id="photo-soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.3"/></filter></defs>'
           f'<image href="data:image/png;base64,{img}" width="{W}" height="{H}"/>\n{body}\n</svg>\n')
    (HERE / "shira-premium.svg").write_text(svg, encoding="utf-8")
    (HERE / "view.html").write_text(f'<meta charset="utf-8"><body style="margin:0">{svg}</body>', encoding="utf-8")


if __name__ == "__main__":
    main()
