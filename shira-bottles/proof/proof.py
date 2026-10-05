"""Print-at-home proof sheet: SHIRÁ wrap labels + neck collars at actual size.

Two A4 pages. Each label is the print artwork (190 x 95 mm trim + 3 mm bleed)
with crop marks at the trim; collars are 90 x 14 mm. Print at 100% / "Actual
size", cut on the crop marks and wrap onto a real 500 ml longneck.

Run:  python3 proof.py && node pdf.mjs  ->  shira-label-proof.pdf
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "photo"))
from photo import emblem, embedded_fonts  # noqa: E402

LABEL_DIR = HERE.parent / "label"
FLAVOURS = [("apricot", "#E0701A"), ("pomegranate", "#B0192F"), ("grape", "#5B2453")]
CREAM, GOLD = "#F6EFE3", "#B8934A"
SANS = "'Montserrat', Arial, sans-serif"


def crop_marks(x, y, w, h, gap=3, length=5):
    """Hairline crop marks just outside a trim box (mm)."""
    lines = []
    for cx, sx in ((x, -1), (x + w, 1)):
        for cy, sy in ((y, -1), (y + h, 1)):
            lines.append(f'<line x1="{cx + sx * gap}" y1="{cy}" x2="{cx + sx * (gap + length)}" y2="{cy}"/>')
            lines.append(f'<line x1="{cx}" y1="{cy + sy * gap}" x2="{cx}" y2="{cy + sy * (gap + length)}"/>')
    return f'<g stroke="#000" stroke-width="0.15">{"".join(lines)}</g>'


def label(key, x, y):
    """Place a 196 x 101 mm label (incl. bleed) with its trim box at (x, y)."""
    svg = (LABEL_DIR / f"shira-{key}-label-texture.svg").read_text(encoding="utf-8")
    svg = re.sub(r'width="\d+" height="\d+"', f'x="{x - 3}" y="{y - 3}" width="196" height="101"', svg, count=1)
    svg = svg.replace("<style>@font-face", "<style>/*fonts*/@font-face", 1)
    svg = re.sub(r"<style>/\*fonts\*/.*?</style>", "", svg, count=1, flags=re.S)  # fonts embedded once per page
    return svg + crop_marks(x, y, 190, 95)


def collar(accent, x, y, w=90, h=14):
    cx = w / 2
    body = (f'<rect x="-2" y="-2" width="{w + 4}" height="{h + 4}" fill="{CREAM}"/>'
            f'<rect x="-2" y="{h * 0.13:.2f}" width="{w + 4}" height="0.5" fill="{GOLD}"/>'
            f'<rect x="-2" y="{h * 0.83:.2f}" width="{w + 4}" height="0.5" fill="{GOLD}"/>'
            f'<g transform="translate({cx} {h / 2})">{emblem(accent, h * 0.26)}</g>')
    return (f'<svg x="{x - 2}" y="{y - 2}" width="{w + 4}" height="{h + 4}" viewBox="-2 -2 {w + 4} {h + 4}">{body}</svg>'
            + crop_marks(x, y, w, h))


def note(x, y, lines, size=3.1, lead=4.6, weight=500):
    return "".join(f'<text x="{x}" y="{y + i * lead:.1f}" font-family="{SANS}" font-size="{size}" '
                   f'font-weight="{weight}" fill="#3A2A22">{t}</text>' for i, t in enumerate(lines))


def page(content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
            f'{embedded_fonts()}<rect width="210" height="297" fill="#fff"/>{content}</svg>')


def main():
    p1 = (note(10, 12, ["SHIRÁ label proof · page 1 of 2 · print at 100% (Actual size) on A4"], 3, weight=600)
          + label("apricot", 10, 24) + label("pomegranate", 10, 150)
          + note(10, 287, ["Apricot and Pomegranate wrap labels · 190 × 95 mm · cut on the crop marks"], 2.8))
    p2 = (note(10, 12, ["SHIRÁ label proof · page 2 of 2"], 3, weight=600)
          + label("grape", 10, 24)
          + note(10, 140, ["Neck collars · 90 × 14 mm"], 3.2, weight=600)
          + collar(FLAVOURS[0][1], 10, 148) + collar(FLAVOURS[1][1], 110, 148) + collar(FLAVOURS[2][1], 10, 172)
          + note(10, 206, ["How to make a real-life sample"], 3.6, weight=600)
          + note(10, 214, [
              "1. Print both pages at 100% / \"Actual size\" (not \"Fit to page\"). Check: each label measures 190 mm wide.",
              "2. Best paper: matte or textured sticker paper (A4 label sheets). Plain thick matte paper + glue stick also works.",
              "3. Cut exactly on the crop marks. The coloured edge outside the marks is bleed and is cut off.",
              "4. Fill a clear 500 ml glass longneck with juice. Wrap the label with its bottom edge about 17 mm above the",
              "    base, front panel facing you. The ends leave a small gap at the back.",
              "5. Wrap a collar tightly just under the cap, mark centred at the front; overlap the ends at the back.",
              "6. Photograph by a window in daylight, front-on at label height, plain wall behind, no flash.",
              "    Send me the full-size photo and I can clean it up and add the other flavours.",
          ], 2.9, 5.2, 400))
    (HERE / "page1.svg").write_text(page(p1), encoding="utf-8")
    (HERE / "page2.svg").write_text(page(p2), encoding="utf-8")


if __name__ == "__main__":
    main()
