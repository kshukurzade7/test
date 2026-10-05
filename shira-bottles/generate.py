"""Generate SHIRÁ juice bottle mockups as SVG.

Each bottle is a clear glass bottle with juice inside, a gold cap and a
wrap-around label whose illustrations are specific to the fruit.

Run:  python3 generate.py   ->  writes shira-lineup.svg and one SVG per flavor.
"""

import math
import random
from pathlib import Path

OUT = Path(__file__).parent

SERIF = "'Cormorant Garamond', 'Playfair Display', Georgia, serif"
SANS = "'Montserrat', 'Helvetica Neue', Arial, sans-serif"
CREAM = "#F6EFE3"

FLAVORS = [
    dict(key="apricot", name="Apricot", local="Ərik",
         juice="#EC7E14", dark="#A3470A", light="#FFB24F",
         band="#E27A1E", accent="#E0701A", art_light="#F4A24E"),
    dict(key="pomegranate", name="Pomegranate", local="Nar",
         juice="#93102A", dark="#470511", light="#D23248",
         band="#A5162E", accent="#B0192F", art_light="#C93A4E"),
    dict(key="grape", name="Grape", local="Üzüm",
         juice="#46163F", dark="#1F0619", light="#7A3270",
         band="#4E1C48", accent="#5B2453", art_light="#73386B"),
    dict(key="apple", name="Apple", local="Alma",
         juice="#DDA43C", dark="#9A6110", light="#F6D07A",
         band="#6E9530", accent="#5F8A26", art_light="#8DB24E"),
]

# Bottle geometry (local coordinates, bottle is 220 wide x ~560 tall)
OUTER = ("M 88 62 L 88 150 C 88 205 20 232 20 302 L 20 522 "
         "Q 20 548 110 551 Q 200 548 200 522 L 200 302 "
         "C 200 232 132 205 132 150 L 132 62 Z")
INNER = ("M 93 62 L 93 151 C 93 209 26 236 26 304 L 26 516 "
         "Q 26 536 110 539 Q 194 536 194 516 L 194 304 "
         "C 194 236 127 209 127 151 L 127 62 Z")
LIQUID_Y = 122
LABEL_TOP, LABEL_SPLIT, LABEL_BOTTOM = 312, 402, 482


def label_path(top, bottom, bulge=7):
    return (f"M 18 {top} Q 110 {top + bulge * 2} 202 {top} L 202 {bottom} "
            f"Q 110 {bottom + bulge * 2} 18 {bottom} Z")


# ---------------------------------------------------------------- fruit icons
# Small monoline-ish icons for the top of the label, centred on (0, 0), ~24px.

def icon(key, c):
    if key == "pomegranate":
        return f"""
<circle cx="0" cy="2" r="9.5" fill="{c}"/>
<path d="M -4.2 -6 L -5.6 -12 L -2.2 -8.6 L 0 -13 L 2.2 -8.6 L 5.6 -12 L 4.2 -6 Z" fill="{c}"/>
<g fill="{CREAM}">
  <circle cx="-3" cy="0" r="1.6"/><circle cx="1" cy="-1.5" r="1.6"/>
  <circle cx="4" cy="2" r="1.6"/><circle cx="-1.5" cy="4" r="1.6"/>
  <circle cx="2" cy="6" r="1.6"/><circle cx="-5" cy="4.5" r="1.4"/>
</g>"""
    if key == "apricot":
        return f"""
<circle cx="0" cy="2" r="10" fill="{c}"/>
<path d="M 0 -7.5 C -3 -2 -3 6 0 11.5" fill="none" stroke="{CREAM}" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>
<path d="M 0 -7.5 Q 0.5 -11 2 -12.5" fill="none" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>
<path d="M 1 -10 Q 6 -15.5 11 -12 Q 6 -7.5 1 -10 Z" fill="{c}"/>"""
    if key == "grape":
        pts = [(-6, -3), (0, -3), (6, -3), (-3, 2.5), (3, 2.5), (0, 8), (-9, -3)]
        pts = [(-6, -3), (0, -3), (6, -3), (-3, 2.5), (3, 2.5), (0, 8)]
        grapes = "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{c}"/>' for x, y in pts)
        return f"""
<path d="M 0 -6 Q 0 -10 2 -13" fill="none" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>
<path d="M 1 -10 Q 7 -15 12 -10 Q 7 -6 1 -10 Z" fill="{c}"/>
{grapes}"""
    if key == "apple":
        return f"""
<path d="M 0 -5 C 4 -9 11 -7 11 1 C 11 8 6 12 3 12 C 1 12 1 11 0 11 C -1 11 -1 12 -3 12 C -6 12 -11 8 -11 1 C -11 -7 -4 -9 0 -5 Z" fill="{c}"/>
<path d="M 0 -5 Q 0.5 -10 2.5 -12.5" fill="none" stroke="{c}" stroke-width="1.4" stroke-linecap="round"/>
<path d="M 1.5 -8.5 Q 6.5 -14 11 -10.5 Q 6.5 -6.5 1.5 -8.5 Z" fill="{c}"/>
<path d="M -6 -1 Q -7 3 -5 6" fill="none" stroke="{CREAM}" stroke-width="1.2" stroke-linecap="round" opacity="0.7"/>"""
    raise ValueError(key)


# ----------------------------------------------------- large band illustrations
# Tonal illustrations drawn in the coloured band; centred on (0, 0), ~r=60.

def art(key, light, base, dark):
    rnd = random.Random(key)
    if key == "pomegranate":
        # Cut pomegranate: rind, white membranes, clusters of jewel-like arils.
        arils = []
        for ring, count in ((0, 1), (11, 7), (22, 13), (33, 19), (43, 25)):
            for i in range(count):
                a = i / count * 2 * math.pi + ring * 0.07
                x = ring * math.cos(a) + rnd.uniform(-1.5, 1.5)
                y = ring * math.sin(a) + rnd.uniform(-1.5, 1.5)
                rot = math.degrees(a)
                arils.append(
                    f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f})">'
                    f'<ellipse rx="5.2" ry="4.2" fill="{light}"/>'
                    f'<ellipse cx="-1.4" cy="-1.3" rx="1.6" ry="1.1" fill="#fff" opacity="0.35"/></g>')
        membranes = "".join(
            f'<path d="M 0 0 Q {30*math.cos(a)+8:.1f} {30*math.sin(a):.1f} '
            f'{52*math.cos(a):.1f} {52*math.sin(a):.1f}" stroke="{CREAM}" stroke-width="1.6" '
            f'fill="none" opacity="0.35"/>'
            for a in [k * 2 * math.pi / 6 + 0.3 for k in range(6)])
        return f"""
<path d="M -14 -54 L -20 -76 L -7 -64 L 0 -82 L 7 -64 L 20 -76 L 14 -54 Z" fill="{dark}" opacity="0.55"/>
<circle r="58" fill="{dark}" opacity="0.55"/>
<circle r="51" fill="{CREAM}" opacity="0.22"/>
{membranes}
{''.join(arils)}"""
    if key == "apricot":
        # Halved apricot with its stone, and a whole apricot with a leaf behind.
        stone_lines = "".join(
            f'<path d="M {-6+3*i} -14 Q {-9+3*i+ (i-2)} 0 {-6+3*i} 14" fill="none" '
            f'stroke="{dark}" stroke-width="0.9" opacity="0.5"/>' for i in range(5))
        return f"""
<g transform="translate(36 -30)">
  <circle r="34" fill="{light}" opacity="0.5"/>
  <path d="M -4 -32 C -16 -10 -14 14 -2 33" fill="none" stroke="{dark}" stroke-width="2" opacity="0.35"/>
  <path d="M -2 -32 Q 6 -58 34 -56 Q 22 -30 -2 -32 Z" fill="{dark}" opacity="0.4"/>
  <path d="M 0 -33 Q 14 -48 30 -54" fill="none" stroke="{dark}" stroke-width="1.2" opacity="0.4"/>
</g>
<circle r="52" fill="{light}" opacity="0.8"/>
<circle r="43" fill="#FFD08A" opacity="0.6"/>
<circle r="24" fill="{dark}" opacity="0.18"/>
<ellipse rx="13" ry="20" fill="{dark}" opacity="0.6" transform="rotate(-12)"/>
<g transform="rotate(-12)">{stone_lines}</g>"""
    if key == "grape":
        rows = [(-36, [-30, -10, 10, 30]), (-17, [-40, -20, 0, 20, 40]),
                (2, [-30, -10, 10, 30]), (21, [-20, 0, 20]), (40, [-10, 10]), (58, [0])]
        grapes = []
        for y, xs in rows:
            for x in xs:
                x += rnd.uniform(-1.5, 1.5)
                grapes.append(
                    f'<circle cx="{x:.1f}" cy="{y}" r="11" fill="{light}" stroke="{dark}" stroke-width="1.5"/>'
                    f'<ellipse cx="{x-3.5:.1f}" cy="{y-4}" rx="3" ry="2" fill="#fff" opacity="0.3"/>')
        return f"""
<path d="M -4 -48 C -60 -70 -86 -52 -78 -24 C -70 -32 -60 -34 -52 -28 C -58 -46 -38 -56 -26 -50 C -24 -60 -12 -60 -4 -48 Z" fill="{light}" opacity="0.6"/>
<path d="M -4 -48 L -56 -38" stroke="{dark}" stroke-width="1.2" opacity="0.5"/>
<path d="M 0 -48 Q 2 -66 12 -74" fill="none" stroke="{light}" stroke-width="4" stroke-linecap="round"/>
<path d="M 6 -62 C 20 -66 28 -56 22 -50 C 18 -46 14 -52 18 -54" fill="none" stroke="{light}" stroke-width="1.5" opacity="0.8"/>
{''.join(grapes)}"""
    if key == "apple":
        # Horizontally cut apple showing the five-pointed seed star.
        seeds = []
        for i in range(5):
            a = -90 + i * 72
            seeds.append(
                f'<g transform="rotate({a})"><path d="M 9 0 Q 18 -7 28 0 Q 18 7 9 0 Z" '
                f'fill="{CREAM}" opacity="0.35"/><path d="M 16 0 Q 20 -3.5 25 0 Q 20 3.5 16 0 Z" '
                f'fill="{dark}" opacity="0.85"/></g>')
        return f"""
<path d="M 0 -50 Q 4 -66 14 -72" fill="none" stroke="{dark}" stroke-width="4" stroke-linecap="round" opacity="0.6"/>
<path d="M 8 -60 Q 34 -84 54 -64 Q 30 -48 8 -60 Z" fill="{light}" opacity="0.8"/>
<path d="M 0 -42 C 22 -60 58 -48 58 -4 C 58 36 32 58 16 58 C 6 58 6 54 0 54 C -6 54 -6 58 -16 58 C -32 58 -58 36 -58 -4 C -58 -48 -22 -60 0 -42 Z" fill="{dark}" opacity="0.45"/>
<path d="M 0 -36 C 18 -52 50 -42 50 -4 C 50 30 28 50 14 50 C 5 50 5 47 0 47 C -5 47 -5 50 -14 50 C -28 50 -50 30 -50 -4 C -50 -42 -18 -52 0 -36 Z" fill="#F4E7B8" opacity="0.55"/>
<g transform="translate(0 2)">
  <circle r="31" fill="none" stroke="{light}" stroke-width="1.2" opacity="0.6" stroke-dasharray="2 3"/>
  {''.join(seeds)}
</g>"""
    raise ValueError(key)


# ------------------------------------------------------------------- bottle

def bottle(f, uid):
    k = f["key"]
    j, d, l = f["juice"], f["dark"], f["light"]
    lp = label_path(LABEL_TOP, LABEL_BOTTOM)
    band = (f"M 18 {LABEL_SPLIT} Q 110 {LABEL_SPLIT + 14} 202 {LABEL_SPLIT} "
            f"L 202 {LABEL_BOTTOM + 20} L 18 {LABEL_BOTTOM + 20} Z")
    return f"""
<defs>
  <clipPath id="inner-{uid}"><path d="{INNER}"/></clipPath>
  <clipPath id="outer-{uid}"><path d="{OUTER}"/></clipPath>
  <clipPath id="label-{uid}"><path d="{lp}"/></clipPath>
  <clipPath id="band-{uid}"><path d="{band}"/></clipPath>
  <linearGradient id="juiceH-{uid}" x1="0" x2="1">
    <stop offset="0" stop-color="{d}"/>
    <stop offset="0.12" stop-color="{j}"/>
    <stop offset="0.38" stop-color="{l}"/>
    <stop offset="0.55" stop-color="{j}"/>
    <stop offset="0.8" stop-color="{j}"/>
    <stop offset="0.93" stop-color="{d}"/>
    <stop offset="1" stop-color="{d}"/>
  </linearGradient>
  <linearGradient id="juiceV-{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{d}" stop-opacity="0.55"/>
    <stop offset="0.35" stop-color="{d}" stop-opacity="0"/>
    <stop offset="0.85" stop-color="{d}" stop-opacity="0"/>
    <stop offset="1" stop-color="{d}" stop-opacity="0.5"/>
  </linearGradient>
  <radialGradient id="glow-{uid}" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="{l}" stop-opacity="0.9"/>
    <stop offset="1" stop-color="{l}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="labelShade-{uid}" x1="0" x2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.28"/>
    <stop offset="0.18" stop-color="#000" stop-opacity="0.04"/>
    <stop offset="0.36" stop-color="#fff" stop-opacity="0.18"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.82" stop-color="#000" stop-opacity="0.08"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.38"/>
  </linearGradient>
</defs>

<!-- floor shadow and coloured light passing through the juice -->
<ellipse cx="118" cy="551" rx="104" ry="11" fill="#3b2a1a" opacity="0.38" filter="url(#blur6)"/>
<ellipse cx="170" cy="556" rx="80" ry="9" fill="{l}" opacity="0.55" filter="url(#blur8)"/>
<ellipse cx="110" cy="549" rx="80" ry="4" fill="#2a1b10" opacity="0.4" filter="url(#blur2)"/>

<!-- empty glass (air gap in the neck) -->
<path d="{OUTER}" fill="#ffffff" fill-opacity="0.16"/>

<!-- juice -->
<g clip-path="url(#inner-{uid})">
  <rect x="0" y="{LIQUID_Y}" width="220" height="440" fill="url(#juiceH-{uid})"/>
  <rect x="0" y="{LIQUID_Y}" width="220" height="440" fill="url(#juiceV-{uid})"/>
  <ellipse cx="128" cy="500" rx="58" ry="32" fill="url(#glow-{uid})" opacity="0.7"/>
  <rect x="150" y="{LIQUID_Y}" width="18" height="440" fill="#fff" opacity="0.06"/>
  <ellipse cx="110" cy="{LIQUID_Y}" rx="18" ry="2.6" fill="{l}" opacity="0.9"/>
  <ellipse cx="110" cy="{LIQUID_Y + 1}" rx="17" ry="1.6" fill="#fff" opacity="0.25"/>
</g>

<!-- thick glass base -->
<g clip-path="url(#outer-{uid})">
  <path d="M 20 516 Q 110 541 200 516 L 200 560 L 20 560 Z" fill="{l}" opacity="0.35"/>
  <path d="M 30 524 Q 110 546 190 524" fill="none" stroke="#fff" stroke-width="1.5" opacity="0.55"/>
  <path d="M 40 534 Q 110 551 180 534" fill="none" stroke="#fff" stroke-width="0.8" opacity="0.35"/>
</g>

<!-- glass walls -->
<path d="{OUTER}" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="6"/>
<path d="{OUTER}" fill="none" stroke="#2b1a10" stroke-opacity="0.45" stroke-width="1.1"/>
<path d="{INNER}" fill="none" stroke="#fff" stroke-opacity="0.25" stroke-width="0.8" clip-path="url(#neckOnly)"/>

<!-- highlights / reflections -->
<g clip-path="url(#outer-{uid})">
  <path d="M 36 300 C 36 262 70 238 92 214" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="0.55" filter="url(#blur2)"/>
  <rect x="33" y="300" width="9" height="215" rx="4.5" fill="url(#streak)" opacity="0.9"/>
  <rect x="47" y="310" width="3" height="190" rx="1.5" fill="#fff" opacity="0.25"/>
  <rect x="96" y="70" width="5" height="140" rx="2.5" fill="url(#streak)" opacity="0.9"/>
  <rect x="121" y="70" width="2.5" height="130" rx="1.2" fill="#fff" opacity="0.35"/>
  <path d="M 186 300 C 186 262 152 240 132 222" fill="none" stroke="#fff" stroke-width="3" opacity="0.35" filter="url(#blur2)"/>
  <rect x="188" y="300" width="4" height="215" rx="2" fill="#fff" opacity="0.4" filter="url(#blur1)"/>
  <rect x="140" y="250" width="22" height="40" rx="6" fill="#fff" opacity="0.1" transform="skewY(20) translate(0 -55)"/>
</g>

<!-- neck band -->
<path d="M 88 82 L 132 82 L 132 104 L 88 104 Z" fill="{CREAM}"/>
<path d="M 88 82 L 132 82 L 132 104 L 88 104 Z" fill="url(#labelShade-{uid})"/>
<g transform="translate(110 93) scale(0.45)">{icon(k, f["accent"])}</g>

<!-- glass collar under the cap -->
<rect x="84" y="56" width="52" height="12" rx="4" fill="#fff" opacity="0.22" stroke="#2b1a10" stroke-opacity="0.35" stroke-width="0.8"/>
<rect x="88" y="58" width="6" height="8" rx="2" fill="#fff" opacity="0.55"/>

<!-- gold cap -->
<rect x="81" y="4" width="58" height="56" rx="4" fill="url(#gold)"/>
<rect x="81" y="4" width="58" height="56" rx="4" fill="url(#knurl)" opacity="0.35"/>
<rect x="81" y="4" width="58" height="56" rx="4" fill="url(#goldV)"/>
<rect x="81" y="50" width="58" height="10" rx="3" fill="#5a3d0c" opacity="0.28"/>
<ellipse cx="110" cy="5" rx="28" ry="2.5" fill="#fff3c4" opacity="0.6"/>

<!-- label -->
<g clip-path="url(#outer-{uid})">
  <g clip-path="url(#label-{uid})">
    <rect x="0" y="{LABEL_TOP - 10}" width="220" height="200" fill="{CREAM}"/>
    <path d="{band}" fill="{f["band"]}"/>
    <g clip-path="url(#band-{uid})">
      <g transform="translate(158 452) scale(0.95)" opacity="0.55">{art(k, f["art_light"], f["band"], f["dark"])}</g>
    </g>
    <g transform="translate(110 334)">{icon(k, f["accent"])}</g>
    <text x="110" y="370" text-anchor="middle" font-family="{SERIF}" font-size="23" letter-spacing="5" fill="#3a2a22">SHIRÁ</text>
    <text x="110" y="390" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16" fill="{f["accent"]}">{f["name"]}</text>
    <text x="110" y="400" text-anchor="middle" font-family="{SANS}" font-size="5" letter-spacing="1.6" fill="#6b5a4e">100% NATURAL JUICE</text>
    <text x="34" y="430" font-family="{SERIF}" font-style="italic" font-size="12" fill="{CREAM}">{f["local"]}</text>
    <text x="34" y="472" font-family="{SANS}" font-size="4.6" letter-spacing="1.2" fill="{CREAM}" opacity="0.9">PRODUCT OF AZERBAIJAN</text>
    <text x="188" y="472" text-anchor="end" font-family="{SANS}" font-size="6" fill="{CREAM}">500 ml</text>
    <path d="{lp}" fill="url(#labelShade-{uid})"/>
  </g>
</g>
"""


SHARED_DEFS = """
<defs>
  <filter id="blur1" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1"/></filter>
  <filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <clipPath id="neckOnly"><rect x="0" y="60" width="220" height="150"/></clipPath>
  <linearGradient id="streak" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.15" stop-color="#fff" stop-opacity="0.85"/>
    <stop offset="0.7" stop-color="#fff" stop-opacity="0.6"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" x2="1">
    <stop offset="0" stop-color="#6a4a12"/>
    <stop offset="0.18" stop-color="#b98a2e"/>
    <stop offset="0.32" stop-color="#f6dd8e"/>
    <stop offset="0.42" stop-color="#d6ad4d"/>
    <stop offset="0.7" stop-color="#a77b25"/>
    <stop offset="0.86" stop-color="#d9b155"/>
    <stop offset="1" stop-color="#5b3f0e"/>
  </linearGradient>
  <linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0.25"/>
    <stop offset="0.12" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.15"/>
  </linearGradient>
  <pattern id="knurl" width="3" height="10" patternUnits="userSpaceOnUse">
    <rect width="1.2" height="10" fill="#3a2706"/>
  </pattern>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F7EDE1"/>
    <stop offset="0.72" stop-color="#F1E2D0"/>
    <stop offset="1" stop-color="#E8D5BE"/>
  </linearGradient>
</defs>"""

FONTS = ('<style>@import url("https://fonts.googleapis.com/css2?'
         'family=Cormorant+Garamond:ital,wght@0,500;1,500&amp;family=Montserrat:wght@500&amp;display=swap");</style>')


def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">\n{FONTS}{SHARED_DEFS}\n'
            f'<rect width="{width}" height="{height}" fill="url(#bg)"/>\n{body}</svg>\n')


def main():
    gap = 250
    width = 80 + gap * len(FLAVORS)
    parts = []
    for i, f in enumerate(FLAVORS):
        x = 55 + i * gap
        parts.append(f'<g transform="translate({x} 90)">{bottle(f, f["key"])}</g>')
        single = svg(340, 720, f'<g transform="translate(60 80)">{bottle(f, f["key"])}</g>')
        (OUT / f"shira-{f['key']}.svg").write_text(single, encoding="utf-8")
    (OUT / "shira-lineup.svg").write_text(svg(width, 720, "\n".join(parts)), encoding="utf-8")


if __name__ == "__main__":
    main()
