"""Cut a manuscript page into per-line crops for reading.

usage: py -3.13 make_lines.py <image> <outdir> [--scale 4] [--block x0,y0,x1,y1]

Writes: <outdir>/lNN_R.png, lNN_L.png (right/left halves, overlapping), bands.json,
        lemmas.json (rows that carry red underlining), overview.png (block with band numbers).
"""
import argparse, json, os
import numpy as np
from PIL import Image, ImageDraw

def find_block(gray):
    """Main text block = longest contiguous run of ink-dense columns, then rows within it."""
    a = np.asarray(gray).astype(float)
    # thin dark strokes on bright ground: dark pixel whose 25px neighbourhood is bright.
    from PIL import ImageFilter
    bg = np.asarray(gray.filter(ImageFilter.BoxBlur(12))).astype(float)
    ink = (a < 120) & (bg > 140)
    def longest_run(v, frac, k=31):
        s = np.convolve(v.astype(float), np.ones(k) / k, mode="same")
        m = s > s.max() * frac
        best, cur, start = (0, 0, 0), 0, 0
        for i, f in enumerate(m):
            if f:
                if cur == 0: start = i
                cur += 1
                if cur > best[0]: best = (cur, start, i)
            else:
                cur = 0
        return best[1], best[2]
    x0, x1 = longest_run(ink.sum(0), 0.35)
    # rows: use only the block columns; allow small gaps (blank lines) by dilating
    rows = ink[:, x0:x1].sum(1)
    y0, y1 = longest_run(rows, 0.12, k=61)
    return int(x0), int(y0), int(x1), int(y1)

def find_bands(gray, block, min_h=6):
    x0, y0, x1, y1 = block
    a = np.asarray(gray.crop(block))
    dark = (a < 120).sum(1).astype(float)
    ds = np.convolve(dark, np.ones(3) / 3, mode="same")
    thr = ds.max() * 0.15
    bands, start = [], None
    for i, v in enumerate(ds > thr):
        if v and start is None: start = i
        if not v and start is not None:
            if i - start > min_h: bands.append([start, i])
            start = None
    if start is not None: bands.append([start, len(ds)])
    # split bands that are ~2x the median height at their internal minimum
    med = np.median([b - a for a, b in bands])
    out = []
    for a_, b_ in bands:
        h = b_ - a_
        n = int(round(h / med))
        if n >= 2 and h > 1.6 * med:
            seg = ds[a_:b_]
            cuts = [a_]
            for k in range(1, n):
                lo = a_ + int(h * (k - 0.35) / n); hi = a_ + int(h * (k + 0.35) / n)
                cuts.append(lo + int(np.argmin(ds[lo:hi])))
            cuts.append(b_)
            out += [[cuts[k], cuts[k + 1]] for k in range(n)]
        else:
            out.append([a_, b_])
    return [[y0 + a_, y0 + b_] for a_, b_ in out]

def red_rows(img, block):
    """Rows in the block containing red ink (rubrication / lemma underlines)."""
    a = np.asarray(img.crop(block).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 120) & (r - g > 50) & (r - b > 40)
    return red.sum(1), red

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("outdir")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--block", default=None)
    ap.add_argument("--overlap", type=int, default=60)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    img = Image.open(a.image).convert("RGB")
    gray = img.convert("L")
    block = tuple(map(int, a.block.split(","))) if a.block else find_block(gray)
    x0, y0, x1, y1 = block
    bands = find_bands(gray, block)
    redcount, _ = red_rows(img, block)
    mid = (x0 + x1) // 2
    meta = []
    for i, (t, b) in enumerate(bands, 1):
        top, bot = max(0, t - 10), min(img.height, b + 8)
        has_red = bool(redcount[max(0, t - y0 - 4): b - y0 + 12].sum() > 15)
        for tag, (xa, xb) in (("R", (mid - a.overlap, x1 + 20)), ("L", (x0 - 20, mid + a.overlap))):
            c = img.crop((max(0, xa), top, min(img.width, xb), bot))
            c = c.resize((c.width * a.scale, c.height * a.scale), Image.LANCZOS)
            c.save(os.path.join(a.outdir, f"l{i:02d}_{tag}.png"))
        meta.append({"line": i, "top": int(t), "bottom": int(b), "red": has_red})
    json.dump({"block": block, "bands": meta}, open(os.path.join(a.outdir, "bands.json"), "w"), indent=1)
    # overview with band numbers
    ov = img.crop((max(0, x0 - 40), max(0, y0 - 40), min(img.width, x1 + 40), min(img.height, y1 + 40))).copy()
    d = ImageDraw.Draw(ov)
    for m in meta:
        yy = m["top"] - (y0 - 40)
        d.line([(0, yy), (ov.width, yy)], fill=(0, 160, 255), width=1)
        d.text((4, yy + 2), str(m["line"]) + ("*" if m["red"] else ""), fill=(255, 0, 0))
    ov.save(os.path.join(a.outdir, "overview.png"))
    print(a.image, "block", block, "lines", len(bands), "red-lines", sum(m["red"] for m in meta))

if __name__ == "__main__":
    main()
