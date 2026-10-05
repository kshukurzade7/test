"""Print-at-home A4 proof for the extended SHIRÁ range: two wrap labels per page."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import proof  # noqa: E402

proof.LABEL_DIR = HERE.parent / "label" / "collection-citrus"
KEYS = ["blackcurrant", "redcurrant", "peach", "cranberry", "pear", "quince",
        "pumpkin", "feijoa", "rosehip", "hawthorn", "pomegranate", "apple"]
OUT = HERE / "collection-citrus"


def main():
    OUT.mkdir(exist_ok=True)
    pages = [KEYS[i:i + 2] for i in range(0, len(KEYS), 2)]
    for n, keys in enumerate(pages, 1):
        names = " and ".join(k.capitalize() for k in keys)
        content = proof.note(10, 12, [f"SHIRÁ label proof · page {n} of {len(pages)} · print at 100% (Actual size) on A4"], 3, weight=600)
        for i, k in enumerate(keys):
            content += proof.label(k, 10, 24 + i * 126)
        content += proof.note(10, 287, [f"{names} · 190 × 95 mm wrap labels · cut on the crop marks"], 2.8)
        (OUT / f"page{n}.svg").write_text(proof.page(content), encoding="utf-8")


if __name__ == "__main__":
    main()
