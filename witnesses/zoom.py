"""Enlarge one region of a witness page.  usage: py -3.13 witnesses/zoom.py munich311 019v y0 y1 [--x0 0 --x1 W --scale 3 --out z.png]
Writes witnesses/<name>/zoom_<page>_<y0>.png (full width split into right/left halves stacked, unless --x0/--x1 given)."""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("page"); ap.add_argument("y0", type=int); ap.add_argument("y1", type=int)
ap.add_argument("--x0", type=int); ap.add_argument("--x1", type=int); ap.add_argument("--scale", type=float, default=3)
a = ap.parse_args()
wd = ROOT / "witnesses" / a.name
im = ImageOps.autocontrast(Image.open(wd / "img" / f"{a.page}.jpg").convert("L"), cutoff=1)
W = im.width
if a.x0 is not None:
    parts = [im.crop((a.x0, a.y0, a.x1, a.y1))]
else:
    parts = [im.crop((W // 2 - 60, a.y0, W - 40, a.y1)), im.crop((40, a.y0, W // 2 + 60, a.y1))]
parts = [p.resize((int(p.width * a.scale), int(p.height * a.scale)), Image.LANCZOS) for p in parts]
out = Image.new("L", (max(p.width for p in parts), sum(p.height + 8 for p in parts)), 0)
y = 0
for p in parts:
    out.paste(p, (0, y)); y += p.height + 8
p = wd / f"zoom_{a.page}_{a.y0}.png"; out.save(p); print(p.name)
