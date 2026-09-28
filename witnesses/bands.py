"""Cut a witness page into overlapping horizontal bands, each split into right and left halves, enlarged.

usage: py -3.13 witnesses/bands.py munich311 019v [020r ...] [--h 260] [--scale 2]
Writes witnesses/<name>/bd_<page>/B<k>R.png and B<k>L.png (k = 1.. from the top; about 6 text lines each).
A band overlaps the next by 50 px, so no line is cut in every band. Line numbers in collation notes are
counted by eye from the top of the text block.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("pages", nargs="+")
ap.add_argument("--h", type=int, default=260); ap.add_argument("--scale", type=float, default=2)
a = ap.parse_args()
wd = ROOT / "witnesses" / a.name
for pg in a.pages:
    im = ImageOps.autocontrast(Image.open(wd / "img" / f"{pg}.jpg").convert("L"), cutoff=1)
    od = wd / f"bd_{pg}"; od.mkdir(exist_ok=True)
    W, H = im.size
    y, k = 90, 1
    while y < H - 120:
        band = im.crop((0, y, W, min(H, y + a.h)))
        for side, box in (("R", (W // 2 - 60, 0, W, band.height)), ("L", (0, 0, W // 2 + 60, band.height))):
            c = band.crop(box)
            c.resize((int(c.width * a.scale), int(c.height * a.scale)), Image.LANCZOS).save(od / f"B{k}{side}.png")
        y += a.h - 50; k += 1
    print(pg, k - 1, "bands")
