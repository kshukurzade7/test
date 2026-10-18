"""'Arch' label design on the real shelf photo (base.png): Redcurrant and
Blackcurrant labels (plus Peach on the cropped third bottle), cream neck
collars. Reuses the wrapping/lighting pipeline of shelf.py.

Run:  python3 shelf_arch.py && PARAMS=params-arch.json OUT=shira-shelf-arch.png node warp.mjs
"""

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "label"))
import shelf  # noqa: E402
import collection as c  # noqa: E402
import collection_arch as arch  # noqa: E402

FLAV = {f["key"]: f for f in c.FLAVOURS}
CREAM, SERIF, SANS = c.CREAM, c.SERIF, c.SANS


def flat_label(f, fw, fh):
    cx, k = fw / 2, f["key"]
    aw, top = min(fw * 0.62, 62), fh * 0.34
    r = aw / 2
    x0, x1 = cx - r, cx + r
    path = f"M {x0:.2f} {fh + 2} V {top + r:.2f} A {r:.2f} {r:.2f} 0 0 1 {x1:.2f} {top + r:.2f} V {fh + 2} Z"
    art = c.ART[k](cx, fh * 0.62, fh * 0.25, random.Random(k))
    return f"""
<clipPath id="lab-{k}"><rect width="{fw:.2f}" height="{fh}" rx="2.2"/></clipPath>
<clipPath id="arch-{k}"><path d="{path}"/></clipPath>
<g clip-path="url(#lab-{k})">
  <rect x="-1" y="-1" width="{fw + 2:.2f}" height="{fh + 2}" fill="{f['band']}"/>
  <path d="{path}" fill="{arch.shade(f['band'], -0.28)}"/>
  <path d="{path}" fill="none" stroke="{CREAM}" stroke-width="0.35" transform="translate(0 -1.6)" opacity="0.7"/>
  <g clip-path="url(#arch-{k})">{art}</g>
  <text x="{cx}" y="{fh*0.13:.2f}" text-anchor="middle" font-family="{SERIF}" font-weight="500" font-size="10.5" letter-spacing="2.2" fill="{CREAM}">SHIRÁ</text>
  <text x="{cx}" y="{fh*0.235:.2f}" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="{8.5 if len(f['name']) < 9 else 7.5}" fill="{CREAM}">{f['name']}</text>
  <text x="{cx}" y="{fh*0.29:.2f}" text-anchor="middle" font-family="{SANS}" font-size="2.0" letter-spacing="0.45" fill="{CREAM}" opacity="0.85">100% NATURAL JUICE</text>
  <text x="{cx}" y="{fh*0.925:.2f}" text-anchor="middle" font-family="{SANS}" font-weight="500" font-size="4.2" fill="{CREAM}">500 ml</text>
  <text x="{cx}" y="{fh*0.965:.2f}" text-anchor="middle" font-family="{SANS}" font-size="1.9" letter-spacing="0.45" fill="{CREAM}" opacity="0.85">PRODUCT OF AZERBAIJAN</text>
</g>"""


shelf.flat_label = flat_label
shelf.FLAVOURS = FLAV
shelf.LABELS = {
    "A": dict(shelf.LABELS["A"], flavour="redcurrant"),
    "B": dict(shelf.LABELS["B"], flavour="blackcurrant"),
    "C": dict(shelf.LABELS["C"], flavour="peach"),
}
shelf.COLLARS = {
    "A": dict(shelf.COLLARS["A"], flavour="redcurrant"),
    "B": dict(shelf.COLLARS["B"], flavour="blackcurrant"),
}

if __name__ == "__main__":
    shelf.main()
    # keep the arch run apart from shelf.py's outputs (params.json, collar SVGs)
    p = HERE / "params.json"
    txt = p.read_text().replace("-collar.svg", "-collar-arch.svg")
    (HERE / "params-arch.json").write_text(txt)
    for lid in "AB":
        (HERE / "flat" / f"{lid}-collar.svg").rename(HERE / "flat" / f"{lid}-collar-arch.svg")
    p.unlink()
