"""Print-ready SHIRÁ wrap-around labels for the 500 ml glass longneck.

Label: 190 x 95 mm trim (fits a ~66 mm diameter bottle, leaving a ~17 mm gap
at the back), 3 mm bleed on every side, 3 mm safe zone inside the trim.
Front panel 0-95 mm, back panel 95-190 mm (trim coordinates).

Layers: artwork, plus a separate magenta "dieline" group (cut line, safe zone,
panel fold guide) that the printer removes / sets to non-printing.

Run:  python3 label.py  ->  shira-<flavor>-label.svg (print), *-label-texture.svg (no dieline, for 3D)
"""

import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "composite"))
sys.path.insert(0, str(HERE.parent / "photo"))
from hero import HERO  # noqa: E402
from photo import embedded_fonts, emblem, az_flag  # noqa: E402

TRIM_W, TRIM_H, BLEED, SAFE = 190, 95, 3, 3
FRONT_W = 95
SPLIT = 55  # cream / colour band boundary on the front (mm from top)
SERIF = "'Cormorant Garamond', Georgia, serif"
SANS = "'Montserrat', Arial, sans-serif"
CREAM = "#F6EFE3"
INK = "#3A2A22"
BODY = "#4A3B32"
GOLD = "#B8934A"

FLAVORS = [
    dict(key="apricot", name="Apricot", ru_name="Абрикос", band="#E8892E", accent="#D96A12",
         title="Apricot juice", ru_title="Абрикосовый сок",
         story="Sun-ripened apricots from Azerbaijan's orchards. Nothing added.",
         ru_story="Спелые абрикосы из садов Азербайджана. Ничего лишнего.",
         ingredients="Apricot juice (100%).", ru_ingredients="Абрикосовый сок (100%)."),
    dict(key="pomegranate", name="Pomegranate", ru_name="Гранат", band="#A82334", accent="#A8172C",
         title="Pomegranate juice", ru_title="Гранатовый сок",
         story="Ruby pomegranates from Azerbaijan, gently pressed. Nothing added.",
         ru_story="Спелые гранаты из Азербайджана, бережный отжим. Ничего лишнего.",
         ingredients="Pomegranate juice (100%).", ru_ingredients="Гранатовый сок (100%)."),
    dict(key="grape", name="Grape", ru_name="Виноград", band="#573259", accent="#5B2453",
         title="Grape juice", ru_title="Виноградный сок",
         story="Dark grapes from Azerbaijan's sunlit vineyards. Nothing added.",
         ru_story="Тёмный виноград с солнечных виноградников Азербайджана.",
         ingredients="Grape juice (100%).", ru_ingredients="Виноградный сок (100%)."),
]


def wrap(text, width_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return lines + [cur]


def text_lines(lines, x, y, size, lead, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return "".join(f'<text x="{x}" y="{y + i * lead:.2f}" font-size="{size}" {a}>{ln}</text>' for i, ln in enumerate(lines))


def front(f):
    cx = FRONT_W / 2
    band_h = TRIM_H - SPLIT
    hero = HERO[f["key"]](FRONT_W * 0.66, SPLIT + band_h * 0.5, band_h * 0.6, random.Random(f["key"]))
    return f"""
<rect x="{-BLEED}" y="{-BLEED}" width="{FRONT_W + BLEED}" height="{SPLIT + BLEED}" fill="{CREAM}"/>
<rect x="{-BLEED}" y="{SPLIT}" width="{FRONT_W + BLEED}" height="{band_h + BLEED}" fill="{f['band']}"/>
<clipPath id="band-{f['key']}"><rect x="{-BLEED}" y="{SPLIT}" width="{FRONT_W + BLEED}" height="{band_h + BLEED}"/></clipPath>
<g clip-path="url(#band-{f['key']})">{hero}</g>
<g transform="translate({cx} 12.5)">{emblem(f['accent'], 5.2)}</g>
<text x="{cx}" y="30" text-anchor="middle" font-family="{SERIF}" font-weight="500" font-size="13.5" letter-spacing="2.9" fill="{INK}">SHIRÁ</text>
<line x1="{cx - 7}" y1="34" x2="{cx + 7}" y2="34" stroke="{GOLD}" stroke-width="0.35"/>
<text x="{cx}" y="42" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="{9 if len(f['name']) < 9 else 8}" fill="{f['accent']}">{f['name']}</text>
<text x="{cx}" y="47.6" text-anchor="middle" font-family="{SANS}" font-size="2.0" letter-spacing="0.5" fill="#6B5A4E">100% NATURAL JUICE · NOT FROM CONCENTRATE</text>
<text x="{cx}" y="51.2" text-anchor="middle" font-family="{SANS}" font-size="2.0" letter-spacing="0.5" fill="#6B5A4E">100% НАТУРАЛЬНЫЙ СОК · ПРЯМОГО ОТЖИМА</text>
<text x="9" y="66" font-family="{SERIF}" font-style="italic" font-size="6.5" fill="{CREAM}">{f['ru_name']}</text>
<g transform="translate(9 84.1)">{az_flag(7)}</g>
<text x="18.4" y="86.1" font-family="{SANS}" font-size="2.0" letter-spacing="0.55" fill="{CREAM}">PRODUCT OF AZERBAIJAN</text>
<text x="18.4" y="89.1" font-family="{SANS}" font-size="2.0" letter-spacing="0.12" fill="{CREAM}">ПРОИЗВЕДЕНО В АЗЕРБАЙДЖАНЕ</text>
<text x="{FRONT_W - 7}" y="88.6" text-anchor="end" font-family="{SANS}" font-weight="500" font-size="5.8" fill="{CREAM}">500 ml</text>"""


def back(f):
    x0 = FRONT_W + 7
    bx = x0 + 45
    sans = f'font-family="{SANS}" fill="{BODY}"'
    ru_col = "#6E5D51"

    def head(x, y, t):
        return f'<text x="{x}" y="{y:.2f}" font-size="2.0" letter-spacing="0.45" font-weight="500" {sans}>{t}</text>'

    def body(lines, x, y, fill=BODY):
        return text_lines(lines, x, y, 2.35, 2.9, font_family=SANS, fill=fill)

    out = [
        f'<rect x="{FRONT_W}" y="{-BLEED}" width="{TRIM_W - FRONT_W + BLEED}" height="{TRIM_H + 2 * BLEED}" fill="{CREAM}"/>',
        f'<rect x="{FRONT_W}" y="{-BLEED}" width="{TRIM_W - FRONT_W + BLEED}" height="{BLEED + 2.2}" fill="{f["band"]}"/>',
        f'<rect x="{FRONT_W}" y="{TRIM_H - 2.2}" width="{TRIM_W - FRONT_W + BLEED}" height="{BLEED + 2.2}" fill="{f["band"]}"/>',
        f'<g transform="translate({x0 + 3} 11.5)">{emblem(f["accent"], 2.7)}</g>',
        f'<text x="{x0 + 8}" y="13.4" font-family="{SERIF}" font-size="5.8" letter-spacing="1.3" fill="{INK}">SHIRÁ</text>',
        f'<text x="{x0 + 8}" y="19" font-family="{SERIF}" font-style="italic" font-size="4.0" fill="{f["accent"]}">{f["title"]} · {f["ru_title"]}</text>',
        text_lines(wrap(f["story"], 68), x0, 25, 2.8, 3.3, font_family=SERIF, font_style="italic", fill=BODY),
        text_lines(wrap(f["ru_story"], 70), x0, 28.6, 2.8, 3.3, font_family=SERIF, font_style="italic", fill=ru_col),
        f'<line x1="{x0}" y1="31.4" x2="{TRIM_W - 7}" y2="31.4" stroke="#D8C9B6" stroke-width="0.2"/>',
    ]

    # left column: ingredients, storage, recycling (English, then Russian)
    y = 35
    out.append(head(x0, y, "INGREDIENTS · СОСТАВ"))
    for lines, fill in ((wrap(f["ingredients"] + " No added sugar, water, colours or preservatives.", 30), BODY),
                        (wrap(f["ru_ingredients"] + " Без сахара, воды, красителей и консервантов.", 30), ru_col)):
        out.append(body(lines, x0, y + 3))
        y += len(lines) * 2.9
    y += 4
    out.append(head(x0, y, "STORAGE · ХРАНЕНИЕ"))
    for lines, fill in ((wrap("Shake well. Once opened, refrigerate and drink within 3 days.", 30), BODY),
                        (wrap("Взболтать. После вскрытия хранить в холодильнике до 3 суток.", 30), ru_col)):
        out.append(body(lines, x0, y + 3))
        y += len(lines) * 2.9
    y += 4.2
    out.append(f'<g transform="translate({x0 + 0.2} {y - 3.4:.2f}) scale(0.4)" fill="none" stroke="{BODY}" stroke-width="0.4">'
               '<path d="M 2.5 0 L 4.7 0 L 4.7 1.8 Q 6 2.8 6 5 L 6 10.5 Q 6 11.2 5.3 11.2 L 1.9 11.2 '
               'Q 1.2 11.2 1.2 10.5 L 1.2 5 Q 1.2 2.8 2.5 1.8 Z"/></g>')
    out.append(body(["Glass. Please recycle.", "Стекло. Сдайте в переработку."], x0 + 4.2, y))

    # right column: nutrition + barcode + dates/producer
    y = 35
    out.append(f'<text x="{bx}" y="{y:.2f}" font-size="2.0" letter-spacing="0.12" font-weight="500" {sans}>NUTRITION · ПИЩ. ЦЕННОСТЬ</text>')
    out.append(f'<text x="{bx + 35}" y="{y + 2.8:.2f}" font-size="1.8" text-anchor="end" {sans}>per 100 ml · на 100 мл</text>')
    out.append(f'<line x1="{bx}" y1="{y + 3.7:.2f}" x2="{bx + 35}" y2="{y + 3.7:.2f}" stroke="{BODY}" stroke-width="0.3"/>')
    rows = [("Energy", "Энергия"), ("Fat", "Жиры"), ("-saturates", "насыщ."), ("Carbohydrate", "Углеводы"),
            ("-sugars", "сахара"), ("Protein", "Белки"), ("Salt", "Соль")]
    for i, (en, ru) in enumerate(rows):
        yy = y + 6.6 + i * 2.75
        sub = en.startswith("-")
        name = f"{'– ' + en[1:] if sub else en} · {ru}"
        out.append(f'<text x="{bx + (1.6 if sub else 0)}" y="{yy:.2f}" font-size="2.15" {sans}>{name}</text>'
                   f'<text x="{bx + 35}" y="{yy:.2f}" font-size="2.15" text-anchor="end" {sans}>TBC</text>'
                   f'<line x1="{bx}" y1="{yy + 0.7:.2f}" x2="{bx + 35}" y2="{yy + 0.7:.2f}" stroke="#C9B9A6" stroke-width="0.15"/>')
    by = y + 6.6 + 6 * 2.75 + 2.4
    out.append(f'<rect x="{bx + 2}" y="{by:.2f}" width="31" height="21" fill="#fff" stroke="#9C8B7C" stroke-width="0.2"/>'
               f'<text x="{bx + 17.5}" y="{by + 9.5:.2f}" text-anchor="middle" font-size="2.1" {sans}>EAN-13 barcode</text>'
               f'<text x="{bx + 17.5}" y="{by + 12.6:.2f}" text-anchor="middle" font-size="1.7" fill="#9C8B7C" font-family="{SANS}">31 x 21 mm area</text>')

    # full-width footer
    out.append(text_lines(["Best before / Lot: see cap · Годен до / партия: см. крышку · 500 ml / 500 мл",
                           "Producer / Изготовитель: [ name, address ], Azerbaijan / Азербайджан"],
                          x0, 87.6, 2.15, 2.75, font_family=SANS, fill=BODY))
    return "".join(out)


def dieline():
    m = "#EC008C"
    return f"""
<g id="dieline" fill="none" stroke="{m}" stroke-width="0.25">
  <rect x="0" y="0" width="{TRIM_W}" height="{TRIM_H}"/>
  <rect x="{SAFE}" y="{SAFE}" width="{TRIM_W - 2 * SAFE}" height="{TRIM_H - 2 * SAFE}" stroke-dasharray="1.2 1"/>
  <line x1="{FRONT_W}" y1="0" x2="{FRONT_W}" y2="{TRIM_H}" stroke-dasharray="3 2"/>
  <text x="2" y="{TRIM_H + 2.4}" font-family="{SANS}" font-size="1.8" fill="{m}" stroke="none">SHIRÁ 500 ml wrap label · trim 190 x 95 mm · bleed 3 mm · safe zone 3 mm (dashed) · front | back fold guide</text>
</g>"""


def svg(f, with_dieline, scale):
    w, h = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
    body = (f'<g transform="translate({BLEED} {BLEED})">{back(f)}{front(f)}'
            + (dieline() if with_dieline else "") + "</g>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}mm" height="{h}mm" data-px-scale="{scale}">{embedded_fonts()}{body}</svg>\n')


def main():
    for f in FLAVORS:
        (HERE / f"shira-{f['key']}-label.svg").write_text(svg(f, True, 1), encoding="utf-8")
        tex = svg(f, False, 1).replace(f'width="{TRIM_W + 2 * BLEED}mm" height="{TRIM_H + 2 * BLEED}mm"',
                                       f'width="{(TRIM_W + 2 * BLEED) * 12}" height="{(TRIM_H + 2 * BLEED) * 12}"')
        (HERE / f"shira-{f['key']}-label-texture.svg").write_text(tex, encoding="utf-8")


if __name__ == "__main__":
    main()
