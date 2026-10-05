"""SHIRÁ labels and neck collars on the real shelf photo (base.png).

Covers the existing labels with the SHIRÁ front label (same artwork as the
other mockups) and adds a cream neck collar with the SHIRÁ mark under the cap.
Each piece is wrapped onto its bottle cylinder per pixel by warp.mjs and relit
with the lighting measured from the original white labels.

Inputs:  base.png, labels_raw.json (per-column label edges + shading)
Outputs: params.json, flat/*.svg  ->  node warp.mjs  ->  shira-shelf.png
"""

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "photo"))
sys.path.insert(0, str(HERE.parent / "composite"))
from photo import flat_label, embedded_fonts, emblem, CREAM  # noqa: E402

GOLD = "#B8934A"
FLAVOURS = {
    "apricot": dict(key="apricot", name="Apricot", ru_name="Абрикос", band="#E8892E", accent="#E0701A"),
    "pomegranate": dict(key="pomegranate", name="Pomegranate", ru_name="Гранат", band="#A82334", accent="#B0192F"),
    "grape": dict(key="grape", name="Grape", ru_name="Виноград", band="#573259", accent="#5B2453"),
}
# photo label id -> flavour, bottle axis (cx) and radius in photo pixels.
# C runs off the right edge of the photo, so its right label edge is mirrored.
LABELS = {
    "A": dict(flavour="pomegranate", cx=111, R=71),
    "B": dict(flavour="grape", cx=262, R=70, extend=8),
    "C": dict(flavour="apricot", cx=416, R=80, mirror=True, x0=335),
}
# neck collars: cx, R, top and bottom y of the band (just under the cap)
COLLARS = {
    "A": dict(flavour="pomegranate", cx=107, R=25, top=70.5, bot=88),
    "B": dict(flavour="grape", cx=269, R=27, top=72.5, bot=90),
}


def fit(xs, ys, cx):
    """Robust fit y = a + b*(x - cx) + c*(x - cx)^2 (label edges on a cylinder)."""
    pts = [(x - cx, y) for x, y in zip(xs, ys) if y is not None]
    med = sorted(y for _, y in pts)[len(pts) // 2]
    pts = [(u, y) for u, y in pts if abs(y - med) <= 4]
    s = [sum(u ** k for u, _ in pts) for k in range(5)]
    t = [sum(y * u ** k for u, y in pts) for k in range(3)]
    m = [[s[i + j] for j in range(3)] + [t[i]] for i in range(3)]
    for i in range(3):
        for r in range(i + 1, 3):
            f = m[r][i] / m[i][i]
            m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    c = [0.0, 0.0, 0.0]
    for i in (2, 1, 0):
        c[i] = (m[i][3] - sum(m[i][j] * c[j] for j in range(i + 1, 3))) / m[i][i]
    return lambda x: c[0] + c[1] * (x - cx) + c[2] * (x - cx) ** 2


def smooth(v, k):
    return [sum(v[max(0, i - k): i + k + 1]) / len(v[max(0, i - k): i + k + 1]) for i in range(len(v))]


def collar_svg(f, fw, fh):
    cx = fw / 2
    return f"""
<rect x="-1" y="-1" width="{fw + 2:.2f}" height="{fh + 2}" fill="{CREAM}"/>
<rect x="-1" y="{fh * 0.12:.2f}" width="{fw + 2:.2f}" height="{fh * 0.035:.2f}" fill="{GOLD}"/>
<rect x="-1" y="{fh * 0.845:.2f}" width="{fw + 2:.2f}" height="{fh * 0.035:.2f}" fill="{GOLD}"/>
<g transform="translate({cx:.2f} {fh / 2:.2f})">{emblem(f['accent'], fh * 0.27)}</g>"""


def main():
    raw = json.loads((HERE / "labels_raw.json").read_text())
    (HERE / "flat").mkdir(exist_ok=True)
    params = []
    for lid, L in LABELS.items():
        cols = raw[lid]
        xs = [c[0] for c in cols]
        cx, R = L["cx"], L["R"]
        top, bot = fit(xs, [c[1] for c in cols], cx), fit(xs, [c[2] for c in cols], cx)
        x0 = L.get("x0", xs[0] - 0.8)
        x1 = (2 * cx - x0) if L.get("mirror") else xs[-1] + 1.2 + L.get("extend", 0)
        ta = math.asin(max(-0.995, (x0 - cx) / R))
        tb = math.asin(min(0.995, (x1 - cx) / R))
        fw_px = R * (tb - ta)
        fh_px = bot(cx) - top(cx)
        fh = 88.0
        fw = fh * fw_px / fh_px
        f = FLAVOURS[L["flavour"]]
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fw:.3f} {fh}" '
               f'width="{fw * 12:.0f}" height="{fh * 12:.0f}">{embedded_fonts()}{flat_label(f, fw, fh)}</svg>\n')
        (HERE / "flat" / f"{lid}-{f['key']}-label.svg").write_text(svg, encoding="utf-8")
        lum = smooth([sum(c[3]) / 3 for c in cols], 3)
        tint = [0.5 + 0.5 * sum(c[3][ch] for c in cols) / sum(sum(c[3]) / 3 for c in cols) for ch in range(3)]
        span = range(int(x0 * 4) - 4, int(min(x1, 420) * 4) + 5)
        params.append(dict(
            svg=f"flat/{lid}-{f['key']}-label.svg", cx=cx, R=R, ta=ta, tb=tb, x0=x0, x1=min(x1, 420.5),
            top=[top(x / 4) - 1.2 for x in span], bot=[bot(x / 4) + 1.0 for x in span], qx0=span.start,
            lum_x0=xs[0], lum=lum, lum_max=max(lum), tint=tint))

    for lid, C in COLLARS.items():
        f = FLAVOURS[C["flavour"]]
        cx, R = C["cx"], C["R"]
        ta, tb = -math.radians(82), math.radians(82)
        fw_px, fh_px = R * (tb - ta), C["bot"] - C["top"]
        fh = 20.0
        fw = fh * fw_px / fh_px
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fw:.3f} {fh}" '
               f'width="{fw * 16:.0f}" height="{fh * 16:.0f}">{collar_svg(f, fw, fh)}</svg>\n')
        (HERE / "flat" / f"{lid}-collar.svg").write_text(svg, encoding="utf-8")
        x0, x1 = cx + R * math.sin(ta), cx + R * math.sin(tb)
        span = range(int(x0 * 4) - 4, int(x1 * 4) + 5)
        # front of the ring sits slightly lower than its sides (seen from below eye level)
        curve = lambda x, y: y + 1.2 * (1 - ((x - cx) / R) ** 2)
        lum = [222 * (0.62 + 0.38 * math.cos(math.asin(max(-1, min(1, (x - cx) / R))))) for x in range(int(x0), int(x1) + 1)]
        params.append(dict(
            svg=f"flat/{lid}-collar.svg", cx=cx, R=R, ta=ta, tb=tb, x0=x0, x1=x1,
            top=[curve(x / 4, C["top"]) for x in span], bot=[curve(x / 4, C["bot"]) for x in span], qx0=span.start,
            lum_x0=int(x0), lum=lum, lum_max=240, tint=[0.97, 0.99, 1.04]))
    (HERE / "params.json").write_text(json.dumps(params), encoding="utf-8")


if __name__ == "__main__":
    main()
