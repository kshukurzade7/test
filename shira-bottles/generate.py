"""Generate SHIRÁ juice bottle mockups as SVG.

Each bottle is a tall, slim clear-glass bottle (long tapered neck, silver
twist-off cap) with juice inside. The label keeps the SHIRÁ sun emblem and
wordmark and adds a full-colour illustration of the flavour's fruit.

Run:  python3 generate.py   ->  writes shira-lineup.svg and one SVG per flavor.
"""

import math
import random
from pathlib import Path

OUT = Path(__file__).parent

SERIF = "'Cormorant Garamond', 'Playfair Display', Georgia, serif"
SANS = "'Montserrat', 'Helvetica Neue', Arial, sans-serif"
CREAM = "#F7F1E6"
INK = "#3a2a22"
LEAF = "#5E8C2F"
LEAF_DARK = "#3E6A1C"

FLAVORS = [
    dict(key="apricot", name="Apricot", local="Ərik",
         juice="#EC7E14", dark="#A3470A", light="#FFB24F", band="#E27A1E", accent="#E0701A"),
    dict(key="pomegranate", name="Pomegranate", local="Nar",
         juice="#8E0F28", dark="#430410", light="#D02E45", band="#A5162E", accent="#B0192F"),
    dict(key="grape", name="Grape", local="Üzüm",
         juice="#43143D", dark="#1C0517", light="#7A3270", band="#4E1C48", accent="#5B2453"),
    dict(key="apple", name="Apple", local="Alma",
         juice="#DDA43C", dark="#93600F", light="#F6D07A", band="#6E9530", accent="#5F8A26"),
]

# Bottle geometry (local coordinates: 220 wide x ~640 tall, centre x = 110).
# Straight cylindrical body, long gently tapering shoulder/neck like a
# classic juice / lemonade longneck.
OUTER = ("M 93 66 L 93 128 C 93 205 40 262 40 338 L 40 598 "
         "Q 40 620 110 622 Q 180 620 180 598 L 180 338 "
         "C 180 262 127 205 127 128 L 127 66 Z")
INNER = ("M 98 66 L 98 130 C 98 209 46 266 46 340 L 46 592 "
         "Q 46 609 110 611 Q 174 609 174 592 L 174 340 "
         "C 174 266 122 209 122 130 L 122 66 Z")
LIQUID_Y = 104
LABEL_TOP, LABEL_SPLIT, LABEL_BOTTOM = 400, 520, 572


def curved(top, bottom, x0=38, x1=182, bulge=6):
    mid = (x0 + x1) / 2
    return (f"M {x0} {top} Q {mid} {top + bulge * 2} {x1} {top} L {x1} {bottom} "
            f"Q {mid} {bottom + bulge * 2} {x0} {bottom} Z")


# ------------------------------------------------------------- SHIRÁ emblem
# The brand mark: a sun / fruit-slice disc with an eight-point star.

def emblem(c, r=11):
    spokes = "".join(
        f'<line x1="0" y1="0" x2="{(r-2.2)*math.cos(a):.2f}" y2="{(r-2.2)*math.sin(a):.2f}" '
        f'stroke="{CREAM}" stroke-width="{r*0.09:.2f}"/>'
        for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)])
    star = []
    for k in range(16):
        a = k * math.pi / 8 - math.pi / 2
        rr = r * (0.42 if k % 2 == 0 else 0.2)
        star.append(f"{rr*math.cos(a):.2f},{rr*math.sin(a):.2f}")
    return (f'<circle r="{r}" fill="{c}"/>{spokes}'
            f'<circle r="{r*0.3:.2f}" fill="{c}"/>'
            f'<polygon points="{" ".join(star)}" fill="{CREAM}"/>'
            f'<circle r="{r*0.09:.2f}" fill="{c}"/>')


# ------------------------------------------------------- fruit illustrations
# Full-colour fruit drawn around (0, 0), roughly 90 x 70 units.

def leaf(x, y, rot, s=1.0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M 0 0 Q 12 -11 28 0 Q 12 11 0 0 Z" fill="url(#g-leaf)"/>'
            f'<path d="M 1 0 Q 14 -1 26 0" stroke="{LEAF_DARK}" stroke-width="0.8" fill="none"/></g>')


def fruit_art(key):
    rnd = random.Random(key)
    if key == "apricot":
        stone_lines = "".join(
            f'<path d="M {-3+1.6*i} -8 Q {-4.5+1.6*i} 0 {-3+1.6*i} 8" fill="none" '
            f'stroke="#6b3410" stroke-width="0.5" opacity="0.6"/>' for i in range(5))
        return f"""
{leaf(-6, -26, -150, 0.9)}{leaf(4, -27, -30, 1.0)}
<path d="M 0 -24 Q 1 -30 3 -33" stroke="#6b4a1e" stroke-width="1.5" fill="none" stroke-linecap="round"/>
<circle cx="-12" cy="-2" r="22" fill="url(#g-apricot)"/>
<path d="M -14 -23 C -22 -8 -20 8 -12 20" fill="none" stroke="#c4560f" stroke-width="1" opacity="0.6"/>
<ellipse cx="-20" cy="-10" rx="6" ry="4" fill="#fff" opacity="0.25" transform="rotate(-30 -20 -10)"/>
<g transform="translate(18 10)">
  <circle r="19" fill="#E9821F"/>
  <circle r="16.5" fill="url(#g-apricot-flesh)"/>
  <ellipse rx="6.5" ry="10" fill="url(#g-stone)" transform="rotate(-15)"/>
  <g transform="rotate(-15)">{stone_lines}</g>
</g>"""
    if key == "pomegranate":
        arils = []
        for ring, count in ((0, 1), (5, 6), (10, 11), (15, 16)):
            for i in range(count):
                a = i / count * 2 * math.pi + ring * 0.11
                x = ring * math.cos(a) + rnd.uniform(-0.6, 0.6)
                y = ring * math.sin(a) + rnd.uniform(-0.6, 0.6)
                arils.append(
                    f'<g transform="translate({x:.1f} {y:.1f}) rotate({math.degrees(a):.0f})">'
                    f'<ellipse rx="2.6" ry="2.1" fill="url(#g-aril)"/>'
                    f'<circle cx="-0.8" cy="-0.7" r="0.6" fill="#fff" opacity="0.7"/></g>')
        loose = "".join(
            f'<g transform="translate({x} {y}) rotate({r})"><ellipse rx="2.6" ry="2.1" fill="url(#g-aril)"/>'
            f'<circle cx="-0.8" cy="-0.7" r="0.6" fill="#fff" opacity="0.7"/></g>'
            for x, y, r in ((36, 24, 20), (42, 20, 70), (30, 27, -30)))
        return f"""
{leaf(-30, -20, -160, 0.8)}
<g transform="translate(-12 -2)">
  <path d="M -6 -21 L -9 -31 L -3 -26 L 0 -33 L 3 -26 L 9 -31 L 6 -21 Z" fill="#8a1424"/>
  <circle r="23" fill="url(#g-pom)"/>
  <ellipse cx="-8" cy="-9" rx="6" ry="4" fill="#fff" opacity="0.28" transform="rotate(-35 -8 -9)"/>
</g>
<g transform="translate(19 12)">
  <circle r="20" fill="#9c1428"/>
  <circle r="18" fill="#f3d9c4"/>
  <path d="M 0 0 L 0 -18 M 0 0 L 16 9 M 0 0 L -16 9" stroke="#f8e6d6" stroke-width="1.2"/>
  {''.join(arils)}
</g>
{loose}"""
    if key == "grape":
        rows = [(-14, [-15, -5, 5, 15]), (-5, [-20, -10, 0, 10, 20]), (4, [-15, -5, 5, 15]),
                (13, [-10, 0, 10]), (22, [-5, 5]), (30, [0])]
        grapes = []
        for y, xs in rows:
            for x in xs:
                x += rnd.uniform(-0.8, 0.8)
                grapes.append(
                    f'<circle cx="{x:.1f}" cy="{y}" r="5.6" fill="url(#g-grape)"/>'
                    f'<ellipse cx="{x-1.8:.1f}" cy="{y-2}" rx="1.5" ry="1" fill="#fff" opacity="0.45"/>')
        return f"""
<path d="M 2 -30 C -14 -44 -36 -40 -38 -24 C -32 -27 -28 -26 -26 -22 C -32 -18 -30 -10 -24 -10 C -20 -16 -12 -20 2 -20 Z" fill="url(#g-leaf)"/>
<path d="M 2 -25 L -30 -24" stroke="{LEAF_DARK}" stroke-width="0.8"/>
<path d="M 0 -18 Q 1 -28 6 -34" stroke="#6b4a1e" stroke-width="2" fill="none" stroke-linecap="round"/>
<path d="M 4 -30 C 14 -36 20 -30 16 -26 C 13 -24 11 -28 14 -29" stroke="{LEAF}" stroke-width="0.9" fill="none"/>
<g transform="translate(-2 -2)">{''.join(grapes)}</g>"""
    if key == "apple":
        seeds = "".join(
            f'<g transform="rotate({-90 + i * 72})"><path d="M 3 0 Q 6.5 -2.6 10 0 Q 6.5 2.6 3 0 Z" '
            f'fill="#5a3412"/></g>' for i in range(5))
        return f"""
<g transform="translate(-12 0)">
  <path d="M 0 -15 C 9 -24 24 -20 24 -2 C 24 14 14 24 6 24 C 2 24 2 22 0 22 C -2 22 -2 24 -6 24 C -14 24 -24 14 -24 -2 C -24 -20 -9 -24 0 -15 Z" fill="url(#g-apple)"/>
  <path d="M 0 -15 Q 1 -24 4 -28" stroke="#6b4a1e" stroke-width="1.6" fill="none" stroke-linecap="round"/>
  {leaf(2, -23, -35, 0.75)}
  <ellipse cx="-11" cy="-8" rx="4.5" ry="7" fill="#fff" opacity="0.25" transform="rotate(20 -11 -8)"/>
</g>
<g transform="translate(20 12)">
  <circle r="17" fill="#8DB33A"/>
  <circle r="15.5" fill="#F6EFC8"/>
  <path d="M 0 -8 L 7.6 -2.5 L 4.7 6.5 L -4.7 6.5 L -7.6 -2.5 Z" fill="none" stroke="#d9cf9a" stroke-width="1"/>
  {seeds}
</g>"""
    raise ValueError(key)


FRUIT_DEFS = f"""
<radialGradient id="g-leaf" cx="0.35" cy="0.35" r="0.8"><stop offset="0" stop-color="#8DBE4A"/><stop offset="1" stop-color="{LEAF}"/></radialGradient>
<radialGradient id="g-apricot" cx="0.35" cy="0.3" r="0.75"><stop offset="0" stop-color="#FFC562"/><stop offset="0.55" stop-color="#F28A1E"/><stop offset="1" stop-color="#C9431A"/></radialGradient>
<radialGradient id="g-apricot-flesh" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FFC060"/><stop offset="1" stop-color="#F7A13A"/></radialGradient>
<radialGradient id="g-stone" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#C77A3A"/><stop offset="1" stop-color="#7A3E14"/></radialGradient>
<radialGradient id="g-pom" cx="0.35" cy="0.3" r="0.75"><stop offset="0" stop-color="#E84A55"/><stop offset="0.6" stop-color="#B3162C"/><stop offset="1" stop-color="#6E0A18"/></radialGradient>
<radialGradient id="g-aril" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#FF5A6E"/><stop offset="1" stop-color="#A50E2A"/></radialGradient>
<radialGradient id="g-grape" cx="0.35" cy="0.3" r="0.75"><stop offset="0" stop-color="#8E4A8A"/><stop offset="0.6" stop-color="#4E1C4A"/><stop offset="1" stop-color="#2A0A28"/></radialGradient>
<radialGradient id="g-apple" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#F3594A"/><stop offset="0.6" stop-color="#C41E2A"/><stop offset="1" stop-color="#7E0E18"/></radialGradient>
"""


# ------------------------------------------------------------------- bottle

def bottle(f, uid):
    k = f["key"]
    j, d, l = f["juice"], f["dark"], f["light"]
    lp = curved(LABEL_TOP, LABEL_BOTTOM)
    band = curved(LABEL_SPLIT, LABEL_BOTTOM + 30)
    return f"""
<defs>
  <clipPath id="inner-{uid}"><path d="{INNER}"/></clipPath>
  <clipPath id="outer-{uid}"><path d="{OUTER}"/></clipPath>
  <clipPath id="label-{uid}"><path d="{lp}"/></clipPath>
  <linearGradient id="juiceH-{uid}" x1="0" x2="1">
    <stop offset="0" stop-color="{d}"/>
    <stop offset="0.12" stop-color="{j}"/>
    <stop offset="0.36" stop-color="{l}"/>
    <stop offset="0.55" stop-color="{j}"/>
    <stop offset="0.8" stop-color="{j}"/>
    <stop offset="0.94" stop-color="{d}"/>
    <stop offset="1" stop-color="{d}"/>
  </linearGradient>
  <linearGradient id="juiceV-{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{d}" stop-opacity="0.5"/>
    <stop offset="0.3" stop-color="{d}" stop-opacity="0"/>
    <stop offset="0.85" stop-color="{d}" stop-opacity="0"/>
    <stop offset="1" stop-color="{d}" stop-opacity="0.5"/>
  </linearGradient>
  <radialGradient id="glow-{uid}" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{l}" stop-opacity="0.9"/>
    <stop offset="1" stop-color="{l}" stop-opacity="0"/>
  </radialGradient>
</defs>

<!-- floor shadow and coloured light passing through the juice -->
<ellipse cx="116" cy="622" rx="84" ry="10" fill="#3b2a1a" opacity="0.38" filter="url(#blur6)"/>
<ellipse cx="160" cy="628" rx="70" ry="8" fill="{l}" opacity="0.55" filter="url(#blur8)"/>
<ellipse cx="110" cy="620" rx="64" ry="3.5" fill="#2a1b10" opacity="0.45" filter="url(#blur2)"/>

<!-- empty glass at the top of the neck -->
<path d="{OUTER}" fill="#ffffff" fill-opacity="0.18"/>

<!-- juice -->
<g clip-path="url(#inner-{uid})">
  <rect x="0" y="{LIQUID_Y}" width="220" height="540" fill="url(#juiceH-{uid})"/>
  <rect x="0" y="{LIQUID_Y}" width="220" height="540" fill="url(#juiceV-{uid})"/>
  <ellipse cx="124" cy="585" rx="48" ry="30" fill="url(#glow-{uid})" opacity="0.7"/>
  <rect x="140" y="{LIQUID_Y}" width="14" height="540" fill="#fff" opacity="0.06"/>
  <ellipse cx="110" cy="{LIQUID_Y}" rx="12" ry="1.8" fill="{l}" opacity="0.9"/>
</g>

<!-- thick glass base -->
<g clip-path="url(#outer-{uid})">
  <path d="M 40 592 Q 110 613 180 592 L 180 640 L 40 640 Z" fill="{l}" opacity="0.35"/>
  <path d="M 48 600 Q 110 618 172 600" fill="none" stroke="#fff" stroke-width="1.4" opacity="0.55"/>
  <path d="M 56 609 Q 110 622 164 609" fill="none" stroke="#fff" stroke-width="0.8" opacity="0.35"/>
</g>

<!-- glass walls -->
<path d="{OUTER}" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="5"/>
<path d="{OUTER}" fill="none" stroke="#2b1a10" stroke-opacity="0.45" stroke-width="1"/>

<!-- highlights / reflections -->
<g clip-path="url(#outer-{uid})">
  <path d="M 52 336 C 54 286 82 248 99 205" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity="0.5" filter="url(#blur2)"/>
  <rect x="50" y="336" width="8" height="255" rx="4" fill="url(#streak)" opacity="0.9"/>
  <rect x="63" y="344" width="2.5" height="230" rx="1.2" fill="#fff" opacity="0.22"/>
  <rect x="101" y="72" width="4" height="130" rx="2" fill="url(#streak)" opacity="0.9"/>
  <rect x="117" y="72" width="2" height="120" rx="1" fill="#fff" opacity="0.35"/>
  <path d="M 168 336 C 166 290 140 254 124 214" fill="none" stroke="#fff" stroke-width="2.5" opacity="0.35" filter="url(#blur2)"/>
  <rect x="169" y="336" width="3.5" height="255" rx="1.7" fill="#fff" opacity="0.4" filter="url(#blur1)"/>
</g>

<!-- glass lip under the cap -->
<rect x="90" y="60" width="40" height="11" rx="4" fill="#fff" opacity="0.25" stroke="#2b1a10" stroke-opacity="0.35" stroke-width="0.8"/>
<rect x="93" y="62" width="5" height="7" rx="2" fill="#fff" opacity="0.55"/>

<!-- silver twist-off cap -->
<rect x="89" y="28" width="42" height="36" rx="3" fill="url(#silver)"/>
<rect x="89" y="28" width="42" height="36" rx="3" fill="url(#knurl)" opacity="0.22"/>
<rect x="89" y="28" width="42" height="36" rx="3" fill="url(#capV)"/>
<rect x="89" y="56" width="42" height="8" rx="2" fill="#000" opacity="0.12"/>
<line x1="89" y1="56" x2="131" y2="56" stroke="#fff" stroke-opacity="0.5" stroke-width="0.6"/>
<ellipse cx="110" cy="29" rx="20" ry="2" fill="#fff" opacity="0.7"/>

<!-- label -->
<g clip-path="url(#outer-{uid})">
  <g clip-path="url(#label-{uid})">
    <rect x="0" y="{LABEL_TOP - 10}" width="220" height="200" fill="{CREAM}"/>
    <path d="{band}" fill="{f["band"]}"/>
    <g transform="translate(110 420)">{emblem(f["accent"], 10)}</g>
    <text x="110" y="451" text-anchor="middle" font-family="{SERIF}" font-size="21" letter-spacing="4.5" fill="{INK}">SHIRÁ</text>
    <text x="110" y="470" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="14.5" fill="{f["accent"]}">{f["name"]}</text>
    <text x="110" y="480" text-anchor="middle" font-family="{SANS}" font-size="4.4" letter-spacing="1.4" fill="#6b5a4e">100% NATURAL JUICE</text>
    <g transform="translate(138 524) scale(0.8)">{fruit_art(k)}</g>
    <text x="52" y="540" font-family="{SERIF}" font-style="italic" font-size="12" fill="{CREAM}">{f["local"]}</text>
    <text x="52" y="551" font-family="{SANS}" font-size="5" fill="{CREAM}" opacity="0.9">500 ml</text>
    <text x="52" y="563" font-family="{SANS}" font-size="3.8" letter-spacing="1" fill="{CREAM}" opacity="0.85">PRODUCT OF AZERBAIJAN</text>
    <path d="{lp}" fill="url(#labelShade)"/>
  </g>
</g>
"""


SHARED_DEFS = f"""
<defs>
  <filter id="blur1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1"/></filter>
  <filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <linearGradient id="streak" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.15" stop-color="#fff" stop-opacity="0.85"/>
    <stop offset="0.7" stop-color="#fff" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="silver" x1="0" x2="1">
    <stop offset="0" stop-color="#8d877c"/>
    <stop offset="0.2" stop-color="#cfc9bd"/>
    <stop offset="0.34" stop-color="#fbf8f0"/>
    <stop offset="0.48" stop-color="#ddd7ca"/>
    <stop offset="0.75" stop-color="#b9b2a4"/>
    <stop offset="0.88" stop-color="#e2ddd1"/>
    <stop offset="1" stop-color="#7c766b"/>
  </linearGradient>
  <linearGradient id="capV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0.3"/>
    <stop offset="0.15" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.12"/>
  </linearGradient>
  <pattern id="knurl" width="2.4" height="10" patternUnits="userSpaceOnUse">
    <rect width="0.9" height="10" fill="#3a352c"/>
  </pattern>
  <linearGradient id="labelShade" x1="0" x2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.3"/>
    <stop offset="0.2" stop-color="#000" stop-opacity="0.04"/>
    <stop offset="0.36" stop-color="#fff" stop-opacity="0.18"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.82" stop-color="#000" stop-opacity="0.08"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.38"/>
  </linearGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F7EDE1"/>
    <stop offset="0.72" stop-color="#F1E2D0"/>
    <stop offset="1" stop-color="#E8D5BE"/>
  </linearGradient>
  {FRUIT_DEFS}
</defs>"""

FONTS = ('<style>@import url("https://fonts.googleapis.com/css2?'
         'family=Cormorant+Garamond:ital,wght@0,500;1,500&amp;family=Montserrat:wght@500&amp;display=swap");</style>')


def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">\n{FONTS}{SHARED_DEFS}\n'
            f'<rect width="{width}" height="{height}" fill="url(#bg)"/>\n{body}</svg>\n')


def main():
    gap = 200
    width = 100 + gap * len(FLAVORS)
    parts = []
    for i, f in enumerate(FLAVORS):
        x = 50 + i * gap
        parts.append(f'<g transform="translate({x} 50)">{bottle(f, f["key"])}</g>')
        single = svg(320, 740, f'<g transform="translate(50 50)">{bottle(f, f["key"])}</g>')
        (OUT / f"shira-{f['key']}.svg").write_text(single, encoding="utf-8")
    (OUT / "shira-lineup.svg").write_text(svg(width, 740, "\n".join(parts)), encoding="utf-8")


if __name__ == "__main__":
    main()
