"""SHIRÁ "fresh" labels: read as 100% natural juice, not syrup or liqueur.

Cues for juice rather than syrup: a white label, a large fresh fruit with leaves on
a pale flavour-tint halo, "100% JUICE" as the biggest claim after the brand, and the
no-sugar / no-water / not-from-concentrate promise spelled out. No black, no gold.

  white  pure white label
  tint   very pale flavour-tint label (same layout)

62 x 92 mm front label. Text is outlined. Run:  python3 design.py  ->  svg/<variant>-<flavour>.svg
"""

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "band"))
from labels import Face  # noqa: E402

# Glossy fruit drawings from modern/design.py (loaded by path: this file has the same name).
_spec = importlib.util.spec_from_file_location("modern_design", HERE.parent / "modern" / "design.py")
_modern = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_modern)
fruit = _modern.fruit

BRAND = Face("inter-tight-latin-500-normal.woff2")
LIGHT = Face("inter-tight-latin-300-normal.woff2")
ITALIC = Face("playfair-display-latin-500-italic.woff2")
SANS = Face("jost-latin-500-normal.woff2")

INK = "#1D2A1F"       # deep green-black: natural, not luxury-black
LEAF = "#3F7A35"

FLAVOURS = [
    dict(key="rosehip", name="Rosehip", colour="#C2401E", tint="#FCEDE6", halo="#FAD9C8"),
    dict(key="apple", name="Apple", colour="#6E8F1F", tint="#F6F7E3", halo="#EEF0C2"),
    dict(key="blackcurrant", name="Blackcurrant", colour="#4A2766", tint="#F2EDF6", halo="#E3D7EE"),
    dict(key="cranberry", name="Cranberry", colour="#A3122F", tint="#FBEAEE", halo="#F6D2DA"),
    dict(key="redcurrant", name="Redcurrant", colour="#C8102E", tint="#FDECEE", halo="#F9D3D8"),
]

W, H = 62, 92


def label(f, variant):
    cx = W / 2
    bg = "#FFFFFF" if variant == "white" else f["tint"]
    halo = f["tint"] if variant == "white" else "#FFFFFF"
    name_size = 10 if len(f["name"]) < 10 else 8.2
    badge_w = 30
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * 20}" height="{H * 20}">'
            f'<rect width="{W}" height="{H}" rx="1.2" fill="{bg}"/>'
            + BRAND.text("SHIRÁ", cx, 13.5, 9.5, INK, tracking=2.4)
            + SANS.text("FRESH FROM AZERBAIJAN", cx, 18.6, 1.65, LEAF, tracking=0.75)
            # fruit on a soft halo: the hero
            + f'<circle cx="{cx}" cy="43" r="15.5" fill="{halo}"/>'
            + f'<g transform="translate({cx} 44.5) scale(0.54)">{fruit(f["key"], variant + f["key"], LEAF)}</g>'
            + ITALIC.text(f["name"], cx, 68.2, name_size, f["colour"])
            # the claim: 100% JUICE
            + f'<rect x="{cx - badge_w / 2}" y="71.4" width="{badge_w}" height="6.2" rx="3.1" fill="{f["colour"]}"/>'
            + BRAND.text("100% JUICE", cx, 75.8, 3.6, "#FFFFFF", tracking=0.55)
            + SANS.text("NOT FROM CONCENTRATE", cx, 81.9, 1.6, INK, tracking=0.6)
            + SANS.text("NO ADDED SUGAR · NO WATER · NO PRESERVATIVES", cx, 85, 1.38, INK, tracking=0.28)
            + LIGHT.text("500 ml", cx, 89.3, 2.2, INK)
            + "</svg>\n")


def main():
    out = HERE / "svg"
    out.mkdir(exist_ok=True)
    for f in FLAVOURS:
        for v in ("white", "tint"):
            (out / f"{v}-{f['key']}.svg").write_text(label(f, v), encoding="utf-8")


if __name__ == "__main__":
    main()
