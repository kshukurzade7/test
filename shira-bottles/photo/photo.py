"""Put SHIRÁ labels onto the real glass bottle photo (base.png).

Each existing label is covered by a new SHIRÁ label: cream top with the
SHIRÁ emblem and wordmark, coloured band with a tone-on-tone fruit
cross-section. The flat label is wrapped onto the bottle with a cylindrical
warp, follows the measured label edges, and is multiplied by the lighting
measured from the original label so it sits in the photo.

Inputs:  base.png, labels.json (per-column label edges and shading)
Outputs: params.json (warp parameters), flat/<flavor>-label.svg
Then:   node warp.mjs   ->  shira-real-bottles.png
"""

import base64
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "composite"))
from hero import HERO, SERIF, SANS  # noqa: E402

W, H = 256, 329
CREAM = "#F6EFE3"
INK = "#3a2a22"

LABELS = {
    # photo label id: flavour + bottle cylinder (centre x, radius) in photo px
    "1": dict(key="apricot", name="Apricot", local="Ərik", band="#E8892E", accent="#E0701A", cx=59, r=34.5),
    "2": dict(key="pomegranate", name="Pomegranate", local="Nar", band="#A82334", accent="#B0192F", cx=130, r=35),
    "3": dict(key="grape", name="Grape", local="Üzüm", band="#573259", accent="#5B2453", cx=197, r=34),
}


FONT_DIR = HERE.parent / "fonts"
LATIN = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2212"
LATIN_EXT = "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+1E00-1E9F,U+A720-A7FF"
CYRILLIC = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"


def embedded_fonts():
    """@font-face rules with the font files embedded, so the SVG is self-contained."""
    faces = []
    for fam, file, style, rng in [
        ("Cormorant Garamond", "cormorant-garamond-latin-500-normal", "normal", LATIN),
        ("Cormorant Garamond", "cormorant-garamond-latin-ext-500-normal", "normal", LATIN_EXT),
        ("Cormorant Garamond", "cormorant-garamond-latin-500-italic", "italic", LATIN),
        ("Cormorant Garamond", "cormorant-garamond-latin-ext-500-italic", "italic", LATIN_EXT),
        ("Cormorant Garamond", "cormorant-garamond-cyrillic-500-normal", "normal", CYRILLIC),
        ("Cormorant Garamond", "cormorant-garamond-cyrillic-500-italic", "italic", CYRILLIC),
        ("Montserrat", "montserrat-latin-500-normal", "normal", LATIN),
        ("Montserrat", "montserrat-cyrillic-500-normal", "normal", CYRILLIC),
    ]:
        data = base64.b64encode((FONT_DIR / f"{file}.woff2").read_bytes()).decode()
        faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:500;"
                     f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng};}}")
    return "<style>" + "".join(faces) + "</style>"


def quad_fit(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    med = sorted(y for _, y in pts)[len(pts) // 2]
    pts = [(x, y) for x, y in pts if abs(y - med) <= 4]
    sx = [sum(x ** k for x, _ in pts) for k in range(5)]
    sy = [sum(y * x ** k for x, y in pts) for k in range(3)]
    m = [[sx[i + j] for j in range(3)] + [sy[i]] for i in range(3)]
    for i in range(3):
        for r in range(i + 1, 3):
            f = m[r][i] / m[i][i]
            m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    c = [0, 0, 0]
    for i in (2, 1, 0):
        c[i] = (m[i][3] - sum(m[i][j] * c[j] for j in range(i + 1, 3))) / m[i][i]
    return lambda x: c[0] + c[1] * x + c[2] * x * x


def smooth(vals, k):
    return [sum(vals[max(0, i - k): i + k + 1]) / len(vals[max(0, i - k): i + k + 1]) for i in range(len(vals))]


def emblem(c, r):
    """SHIRÁ mark: a citrus slice. Solid disc cut into eight segments by four
    thin straight lines through the centre, with a small light centre."""
    gap = r * 0.075
    cuts = "".join(
        f'<line x1="{-r*1.05*math.cos(a):.3f}" y1="{-r*1.05*math.sin(a):.3f}" '
        f'x2="{r*1.05*math.cos(a):.3f}" y2="{r*1.05*math.sin(a):.3f}" stroke="{CREAM}" stroke-width="{gap:.3f}"/>'
        for a in [k * math.pi / 4 for k in range(4)])
    return (f'<circle r="{r}" fill="{c}"/>{cuts}'
            f'<circle r="{r*0.3:.3f}" fill="{CREAM}"/>')


def az_flag(w):
    """Minimal flag of Azerbaijan, top-left at (0, 0), w wide (2:1): three flat
    stripes, white crescent and eight-point star, softly rounded, hairline edge."""
    h = w / 2
    cx, cy = w * 0.47, h / 2
    star = " ".join(
        f"{w*0.565 + (h*0.075 if k % 2 == 0 else h*0.035) * math.cos(k * math.pi / 8 - math.pi / 2):.3f},"
        f"{cy + (h*0.075 if k % 2 == 0 else h*0.035) * math.sin(k * math.pi / 8 - math.pi / 2):.3f}"
        for k in range(16))
    uid = f"azf{int(w * 100)}"
    return (f'<clipPath id="{uid}"><rect width="{w}" height="{h:.3f}" rx="{h*0.14:.3f}"/></clipPath>'
            f'<g clip-path="url(#{uid})">'
            f'<rect width="{w}" height="{h/3:.3f}" fill="#00B5E2"/>'
            f'<rect y="{h/3:.3f}" width="{w}" height="{h/3:.3f}" fill="#EF3340"/>'
            f'<rect y="{2*h/3:.3f}" width="{w}" height="{h/3 + 0.01:.3f}" fill="#509E2F"/>'
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{h*0.15:.3f}" fill="#fff"/>'
            f'<circle cx="{cx + h*0.04:.3f}" cy="{cy:.3f}" r="{h*0.125:.3f}" fill="#EF3340"/>'
            f'<polygon points="{star}" fill="#fff"/></g>'
            f'<rect width="{w}" height="{h:.3f}" rx="{h*0.14:.3f}" fill="none" stroke="#F6EFE3" stroke-width="{h*0.05:.3f}" stroke-opacity="0.85"/>')


def flat_label(f, fw, fh):
    """Flat SHIRÁ label artwork, fw x fh units."""
    cx = fw / 2
    band_y = fh * 0.56
    bh = fh - band_y
    hero = HERO[f["key"]](fw * 0.68, band_y + bh * 0.55, bh * 0.62, random.Random(f["key"]))
    return f"""
<clipPath id="lab-{f['key']}"><rect width="{fw:.2f}" height="{fh}" rx="2.2"/></clipPath>
<clipPath id="bandc-{f['key']}"><rect x="-1" y="{band_y}" width="{fw + 2:.2f}" height="{bh + 1}"/></clipPath>
<g clip-path="url(#lab-{f['key']})">
  <rect x="-1" y="-1" width="{fw + 2:.2f}" height="{fh + 2}" fill="{CREAM}"/>
  <rect x="-1" y="{band_y}" width="{fw + 2:.2f}" height="{bh + 1}" fill="{f['band']}"/>
  <g clip-path="url(#bandc-{f['key']})">{hero}</g>
  <g transform="translate({cx} {fh*0.12:.2f})">{emblem(f['accent'], 4.6)}</g>
  <text x="{cx}" y="{fh*0.3:.2f}" text-anchor="middle" font-family="{SERIF}" font-size="11.5" letter-spacing="2.2" fill="{INK}">SHIRÁ</text>
  <line x1="{cx-6}" y1="{fh*0.335:.2f}" x2="{cx+6}" y2="{fh*0.335:.2f}" stroke="#C9A35A" stroke-width="0.35"/>
  <text x="{cx}" y="{fh*0.44:.2f}" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="{8 if len(f['name']) < 9 else 7}" fill="{f['accent']}">{f['name']}</text>
  <text x="{cx}" y="{fh*0.49:.2f}" text-anchor="middle" font-family="{SANS}" font-size="2.3" letter-spacing="0.6" fill="#6b5a4e">100% NATURAL JUICE</text>
  <text x="{cx}" y="{fh*0.525:.2f}" text-anchor="middle" font-family="{SANS}" font-size="2.3" letter-spacing="0.4" fill="#6b5a4e">100% НАТУРАЛЬНЫЙ СОК</text>
  <text x="{fw*0.12:.2f}" y="{band_y + bh*0.27:.2f}" font-family="{SERIF}" font-style="italic" font-size="5.5" fill="{CREAM}">{f.get('ru_name', '')}</text>
  <g transform="translate({fw*0.12:.2f} {fh - 7.4:.2f})">{az_flag(5.2)}</g>
  <text x="{fw*0.12 + 6.8:.2f}" y="{fh - 5.6:.2f}" font-family="{SANS}" font-size="2.0" letter-spacing="0.4" fill="{CREAM}">PRODUCT OF AZERBAIJAN</text>
  <text x="{fw*0.12 + 6.8:.2f}" y="{fh - 3.0:.2f}" font-family="{SANS}" font-size="2.0" letter-spacing="0.05" fill="{CREAM}">ПРОИЗВЕДЕНО В АЗЕРБАЙДЖАНЕ</text>
  <text x="{fw*0.88:.2f}" y="{fh - 3.6:.2f}" text-anchor="end" font-family="{SANS}" font-size="2.8" fill="{CREAM}">500 ml</text>
</g>"""


def label_params(lid, f, m):
    xs = list(range(m["x0"], m["x0"] + len(m["tops"])))
    top = quad_fit(xs, m["tops"])
    bot = quad_fit(xs, m["bots"])
    x0, x1 = xs[0] - 0.8, xs[-1] + 2.0
    cx, R = f["cx"], f["r"]
    ta = math.asin(max(-0.999, (x0 - cx) / R))
    tb = math.asin(min(0.999, (x1 - cx) / R))
    fw, fh = R * (tb - ta), 88

    # lighting: luminance of the original white label, plus its average tint
    lum = smooth([sum(c) / 3 for c in m["shade"]], 3)
    tint = [0.5 + 0.5 * sum(c[ch] for c in m["shade"]) / sum(sum(c) / 3 for c in m["shade"]) for ch in range(3)]

    flat = flat_label(f, fw, fh)
    (HERE / "flat").mkdir(exist_ok=True)
    (HERE / "flat" / f"{f['key']}-label.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fw:.3f} {fh}" '
        f'width="{fw * 10:.0f}" height="{fh * 10}">{embedded_fonts()}{flat}</svg>\n', encoding="utf-8")
    return dict(key=f["key"], cx=cx, R=R, ta=ta, tb=tb, x0=x0, x1=x1,
                top=[top(x / 4) - 1.0 for x in range(int(x0 * 4) - 4, int(x1 * 4) + 5)],
                bot=[bot(x / 4) + 0.9 for x in range(int(x0 * 4) - 4, int(x1 * 4) + 5)],
                qx0=int(x0 * 4) - 4, lum_x0=xs[0], lum=lum, tint=tint)


def main():
    labels = json.loads((HERE / "labels.json").read_text())
    params = [label_params(lid, f, labels[lid]) for lid, f in LABELS.items()]
    (HERE / "params.json").write_text(json.dumps(params), encoding="utf-8")


if __name__ == "__main__":
    main()
