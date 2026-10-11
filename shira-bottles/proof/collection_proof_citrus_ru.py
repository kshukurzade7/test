"""Print-at-home A4 proof for the extended SHIRÁ range, Russian labels (ШИРА́): two wrap labels per page.

Run:  python3 collection_proof_citrus_ru.py && node collection_pdf_citrus.mjs collection-citrus-ru
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "label"))
import proof  # noqa: E402
from collection_proof_citrus import KEYS  # noqa: E402
from collection import RU  # noqa: E402

proof.LABEL_DIR = HERE.parent / "label" / "collection-citrus-ru"
OUT = HERE / "collection-citrus-ru"


def main():
    OUT.mkdir(exist_ok=True)
    pages = [KEYS[i:i + 2] for i in range(0, len(KEYS), 2)]
    for n, keys in enumerate(pages, 1):
        names = " и ".join(RU[k]["name"] for k in keys)
        content = proof.note(10, 12, [f"Пробная печать этикеток ШИРА́ · страница {n} из {len(pages)} · "
                                      "печатать в масштабе 100% (фактический размер) на A4"], 3, weight=600)
        for i, k in enumerate(keys):
            content += proof.label(k, 10, 24 + i * 126)
        content += proof.note(10, 287, [f"{names} · этикетки 190 × 95 мм · вырезать по меткам обреза"], 2.8)
        (OUT / f"page{n}.svg").write_text(proof.page(content), encoding="utf-8")


if __name__ == "__main__":
    main()
