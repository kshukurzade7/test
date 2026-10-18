"""SHIRÁ "village" label design: kraft paper with a stitched border and a small
illustrated Azerbaijani village scene (Caucasus peaks, stone house with a tiled
roof, cypress, fruit tree, a basket of the flavour's fruit). Back panel keeps
the collection layout on the same kraft paper.

Run:  python3 collection_village.py
      -> collection-village/shira-<flavour>-label.svg (print, with dieline)
         collection-village/shira-<flavour>-label-texture.svg (no dieline)
"""

import random
from pathlib import Path

import collection as c
from collection_arch import shade

HERE = Path(__file__).parent
OUT = HERE / "collection-village"
c.STYLE = "citrus"

FRONT_W, TRIM_H, BLEED, SERIF, SANS, CREAM, INK = (
    c.FRONT_W, c.TRIM_H, c.BLEED, c.SERIF, c.SANS, c.CREAM, c.INK)
KRAFT = "#EAD8B4"
# colours that read on a green canopy / in the basket, where the band colour doesn't
FRUIT = {"pear": "#D8D464", "apple": "#D6493B", "feijoa": "#B8D860", "blackcurrant": "#4A2752",
         "quince": "#E8BE3A", "peach": "#F29A66"}
WX, WY, WW, WH = 8, 7, 79, 45  # scene window on the front panel


def fruit_dot(x, y, r, col):
    return (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{col}" stroke="{shade(col, -0.4)}" stroke-width="0.2"/>'
            f'<circle cx="{x - r * 0.3:.2f}" cy="{y - r * 0.35:.2f}" r="{r * 0.28:.2f}" fill="#fff" opacity="0.55"/>')


def scene(f):
    rnd = random.Random(f["key"])
    fc = FRUIT.get(f["key"], f["band"])
    k = f["key"]
    # canopy fruit
    cano = "".join(fruit_dot(rnd.uniform(49, 63), rnd.uniform(15, 27), 1.25, fc) for _ in range(15))
    # basket fruit (heaped)
    heap = []
    for row, (n, y) in enumerate(((5, 37.3), (4, 35.4), (3, 33.6))):
        for i in range(n):
            heap.append(fruit_dot(33.2 + 1.3 * (5 - n) + i * 2.6 + rnd.uniform(-.2, .2), y, 1.45, fc))
    # fallen fruit on the grass
    fall = "".join(fruit_dot(x, y, 1.0, fc) for x, y in ((53, 40.5), (58.5, 41.5), (63, 39.8)))
    posts = "".join(f'<rect x="{x}" y="33.5" width="0.7" height="4" fill="#7A5836"/>' for x in range(4, 27, 4))
    smoke = ('<path d="M18.6 14 q-1.6 -2 0 -3.6 t0 -3.6" fill="none" stroke="#fff" stroke-width="0.7" opacity="0.7" stroke-linecap="round"/>')
    birds = "".join(f'<path d="M{x} {y} q1.2 -1.4 2.4 0 q1.2 -1.4 2.4 0" fill="none" stroke="{INK}" stroke-width="0.35" stroke-linecap="round"/>'
                    for x, y in ((30, 7), (37, 10), (24, 11)))
    return f"""
<defs>
  <linearGradient id="sky-{k}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FCE7C0"/><stop offset="1" stop-color="#FFF6E2"/>
  </linearGradient>
  <clipPath id="win-{k}"><rect x="0" y="0" width="{WW}" height="{WH}" rx="2.6"/></clipPath>
</defs>
<g transform="translate({WX} {WY})">
 <g clip-path="url(#win-{k})">
  <rect width="{WW}" height="{WH}" fill="url(#sky-{k})"/>
  <circle cx="63" cy="11" r="9" fill="#FFD98A" opacity="0.35"/>
  <circle cx="63" cy="11" r="5.2" fill="#F7B544"/>
  {birds}
  <path d="M0 29 L12 15 L19 22 L33 8 L48 23 L58 17 L70 25 L79 21 V45 H0Z" fill="#B7A9B8"/>
  <path d="M33 8 L29.6 11.4 L32 11 L33.4 12.6 L35 11 L36.6 11.6Z M12 15 L9.6 17.6 L11.4 17.2 L12.6 18.4 L14 17Z" fill="#FFFFFF" opacity="0.9"/>
  <path d="M0 33 Q16 22 36 30 T79 28 V45 H0Z" fill="#A9B26B"/>
  <path d="M0 38 Q22 30 44 36 T79 34 V45 H0Z" fill="#86994F"/>
  {posts}
  <!-- stone house -->
  <rect x="8" y="23.5" width="15" height="9.5" fill="#D9BC8C"/>
  <path d="M6.6 24 L15.5 17.2 L24.4 24Z" fill="#B5532F"/>
  <path d="M6.6 24 L24.4 24" stroke="#8E3E22" stroke-width="0.5"/>
  <rect x="18" y="14.5" width="2.2" height="5" fill="#B9A07A"/>
  {smoke}
  <rect x="14.2" y="27.2" width="3.2" height="5.8" rx="1.5" fill="#6B4A2F"/>
  <rect x="9.6" y="26.6" width="2.8" height="2.8" fill="#6B4A2F"/><rect x="19.4" y="26.6" width="2.8" height="2.8" fill="#6B4A2F"/>
  <path d="M8 33 H23" stroke="#B89C70" stroke-width="0.4"/>
  <!-- cypress -->
  <path d="M30.5 36 C28.6 30 29.6 21 31 15 C32.4 21 33.4 30 31.5 36Z" fill="#3E5B33"/>
  <path d="M36 37 C34.6 32 35.4 25 36.4 21 C37.4 25 38.2 32 36.8 37Z" fill="#4A6B3B"/>
  <!-- fruit tree -->
  <path d="M55.2 38 L55.4 28 L56.6 28 L56.8 38Z" fill="#6B4A2F"/>
  <circle cx="51" cy="22" r="6.6" fill="#5E8A3A"/><circle cx="62" cy="21.5" r="6.6" fill="#5E8A3A"/>
  <circle cx="56.5" cy="16.5" r="7.2" fill="#6B9A44"/><circle cx="56.5" cy="24" r="6.4" fill="#5E8A3A"/>
  {cano}
  <!-- path -->
  <path d="M26 45 Q34 40 44 40.5 Q56 41 79 45Z" fill="#D8BE8A" opacity="0.9"/>
  {fall}
  <!-- basket -->
  <ellipse cx="38.5" cy="42.4" rx="9" ry="1.1" fill="#000" opacity="0.15"/>
  {''.join(heap)}
  <path d="M31 37.6 H46 L44.4 43 Q38.5 44.2 32.6 43Z" fill="#A9773F"/>
  <path d="M31.6 39.4 H45.4 M32 41.2 H45" stroke="#7E5629" stroke-width="0.35"/>
  <path d="M34 37.6 L35 43.4 M37.2 37.6 L37.4 43.6 M40.4 37.6 L40 43.6 M43.4 37.6 L42.6 43.4" stroke="#7E5629" stroke-width="0.3"/>
 </g>
 <rect width="{WW}" height="{WH}" rx="2.6" fill="none" stroke="{INK}" stroke-width="0.5"/>
 <rect x="1" y="1" width="{WW - 2}" height="{WH - 2}" rx="1.9" fill="none" stroke="{INK}" stroke-width="0.15"/>
</g>"""


def front(f):
    cx = FRONT_W / 2
    ns = 8.8 if len(f["name"]) <= 9 else 7.8
    return f"""
<defs><filter id="grain-{f['key']}" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.25  0 0 0 0 0.12  0 0 0 0.9 -0.28"/>
</filter></defs>
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" fill="{KRAFT}"/>
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" filter="url(#grain-{f['key']})" opacity="0.5"/>
<rect x="4" y="4" width="{FRONT_W - 8}" height="{TRIM_H - 8}" rx="2" fill="none" stroke="{INK}" stroke-width="0.3" stroke-dasharray="1.4 0.9" opacity="0.7"/>
{scene(f)}
<text x="{cx}" y="64.2" text-anchor="middle" font-family="{SERIF}" font-weight="700" font-size="11.5" letter-spacing="2.4" fill="{INK}">SHIRÁ</text>
<text x="{cx}" y="73.6" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-weight="600" font-size="{ns}" fill="{shade(f['accent'], -0.15)}">{f['name']}</text>
<line x1="{cx - 9}" y1="77.3" x2="{cx + 9}" y2="77.3" stroke="{INK}" stroke-width="0.25" opacity="0.6"/>
<text x="{cx}" y="81.2" text-anchor="middle" font-family="{SANS}" font-weight="500" font-size="1.9" letter-spacing="0.5" fill="{INK}">100% NATURAL JUICE · NOT FROM CONCENTRATE</text>
<text x="{cx}" y="86.6" text-anchor="middle" font-family="{SANS}" font-weight="500" font-size="2.0" letter-spacing="0.5" fill="{INK}">PRODUCT OF AZERBAIJAN · 500 ml</text>"""


def back(f):
    return c._orig_back(f).replace(f'fill="{CREAM}"', f'fill="{KRAFT}"', 1)


def main():
    c._orig_back = c.back
    c.front, c.back = front, back
    OUT.mkdir(exist_ok=True)
    for f in c.FLAVOURS:
        (OUT / f"shira-{f['key']}-label.svg").write_text(c.svg(f, True), encoding="utf-8")
        (OUT / f"shira-{f['key']}-label-texture.svg").write_text(c.svg(f, False), encoding="utf-8")


if __name__ == "__main__":
    main()
