"""Arch labels wrapped onto the supplied studio bottle photos (photo-N.webp).

The wrap (190 x 95 mm trim, 3 mm bleed) is mapped onto the bottle cylinder
(66 mm diameter), front panel facing the camera, and lit from the photo's own
column brightness so the glass highlights stay over the paper.

Run:  node render-wraps.mjs <keys...> && python3 mock.py
"""
import math
import os
import numpy as np
from PIL import Image, ImageFilter

CX, R, Y0, LH = 541.5, 161.5, 745, 463      # bottle axis, radius, label top/height (px)
MM_R, PX_MM, BLEED, FRONT_C = 33.0, 12, 3, 47.5
DESIGN = os.environ.get("DESIGN", "arch")
SUF = "" if DESIGN == "arch" else f"-{DESIGN}"
JOBS = [(1, "quince"), (2, "redcurrant"), (3, "blackcurrant"), (4, "rosehip"), (5, "apple")]


def wrap_on(photo, wrap):
    base = np.asarray(photo.convert("RGB")).astype(float)
    H, W, _ = base.shape
    wp = np.asarray(wrap.convert("RGB")).astype(float)
    # highlight profile from the bottle's own body (relative column brightness)
    band = base[850:1100].mean((0, 2))
    prof = np.convolve(band, np.ones(5) / 5, "same")
    body = prof[int(CX - R * 0.9): int(CX + R * 0.9)]
    prof = prof / np.median(body)
    ys, xs = np.mgrid[0:H, 0:W]
    dx = (xs + 0.5 - CX) / R
    ok = np.abs(dx) < 0.995
    th = np.arcsin(np.clip(dx, -0.995, 0.995))
    cos = np.cos(th)
    sag = 7 * cos                                   # front of the ring sits lower (slight camera elevation)
    v = (ys + 0.5 - (Y0 + sag)) / LH
    u_mm = FRONT_C + MM_R * th
    inside = ok & (v >= 0) & (v <= 1) & (np.abs(u_mm - FRONT_C) <= 47.5 + 4.3)
    # wrap texture coords (px); texture includes bleed on all sides
    tx = (u_mm + BLEED) * PX_MM
    ty = (BLEED + v * 95) * PX_MM
    tx = np.clip(tx, 0, wp.shape[1] - 1.01)
    ty = np.clip(ty, 0, wp.shape[0] - 1.01)
    x0, y0 = tx.astype(int), ty.astype(int)
    fx, fy = (tx - x0)[..., None], (ty - y0)[..., None]
    t = (wp[y0, x0] * (1 - fx) * (1 - fy) + wp[y0, x0 + 1] * fx * (1 - fy)
         + wp[y0 + 1, x0] * (1 - fx) * fy + wp[y0 + 1, x0 + 1] * fx * fy)
    shade = (0.70 + 0.30 * cos ** 0.7)
    hi = np.clip(1 + 0.55 * (prof[None, :] - 1), 0.88, 1.28)
    lit = np.clip(t * (shade * hi)[..., None], 0, 255)
    # feathered coverage
    cov = inside.astype(float)
    cov = np.asarray(Image.fromarray((cov * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255.0
    out = base * (1 - cov[..., None]) + lit * cov[..., None]
    return Image.fromarray(out.astype(np.uint8))


def main():
    outs = []
    for i, k in JOBS:
        res = wrap_on(Image.open(f"photo-{i}.webp"), Image.open(f"wraps{SUF}/{k}.png"))
        res.save(f"shira-bottle-{k}{SUF}.png")
        outs.append(res)
    sheet = Image.new("RGB", (len(outs) * 543, 724), "white")
    for n, im in enumerate(outs):
        sheet.paste(im.resize((543, 724), Image.LANCZOS), (n * 543, 0))
    sheet.save(f"shira-bottles-lineup{SUF}.png")


if __name__ == "__main__":
    main()
