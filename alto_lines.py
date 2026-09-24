"""Cut per-line crops from a kraken ALTO segmentation (handles skew, separates regions).

usage: py -3.13 alto_lines.py hires_077a.jpg htr/077a_seg.xml al_077a [--scale 2]

Writes al_077a/<region>_<nn>_{R,L}.png (and _F full line if short), plus lines.tsv with
region type, index, bbox, baseline y, and 'red' flag for red underline near the line.
Lines are ordered top-to-bottom within region; regions ordered Main first.
"""
import argparse, os, re, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

NS = {"a": "http://www.loc.gov/standards/alto/ns-v4#"}

def parse(alto):
    t = ET.parse(alto); root = t.getroot()
    tags = {o.get("ID"): o.get("LABEL") for o in root.iter("{%s}OtherTag" % NS["a"])}
    out = []
    for blk in root.iter("{%s}TextBlock" % NS["a"]):
        rtype = tags.get(blk.get("TAGREFS", ""), "default")
        for ln in blk.iter("{%s}TextLine" % NS["a"]):
            bl = ln.get("BASELINE", "")
            pts = [tuple(map(float, p.split(","))) for p in bl.split() if "," in p]
            if not pts:
                nums = list(map(float, re.findall(r"[\d.]+", bl)))
                pts = list(zip(nums[0::2], nums[1::2]))
            poly = None
            for sh in ln.iter("{%s}Polygon" % NS["a"]):
                nums = list(map(float, re.findall(r"[\d.]+", sh.get("POINTS", ""))))
                poly = list(zip(nums[0::2], nums[1::2]))
            if not pts:
                continue
            xs = [p[0] for p in (poly or pts)]; ys = [p[1] for p in (poly or pts)]
            out.append(dict(rtype=rtype, x0=int(min(xs)), x1=int(max(xs)), y0=int(min(ys)), y1=int(max(ys)),
                            by=float(np.mean([p[1] for p in pts])), pts=pts))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("alto"); ap.add_argument("outdir")
    ap.add_argument("--scale", type=int, default=2); ap.add_argument("--pad", type=int, default=14)
    ap.add_argument("--overlap", type=int, default=120)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    img = Image.open(a.image).convert("RGB")
    arr = np.asarray(img).astype(int)
    red = (arr[..., 0] > 120) & (arr[..., 0] - arr[..., 1] > 50) & (arr[..., 0] - arr[..., 2] > 40)
    lines = parse(a.alto)
    order = {"Main": 0, "default": 1, "Margin": 2, "Correction": 3}
    lines.sort(key=lambda l: (order.get(l["rtype"], 9), l["by"]))
    rows = []
    counters = {}
    for l in lines:
        r = l["rtype"]; counters[r] = counters.get(r, 0) + 1; n = counters[r]
        # deskew: rotate crop so baseline is horizontal
        (xa, ya), (xb, yb) = l["pts"][0], l["pts"][-1]
        if xa > xb: xa, ya, xb, yb = xb, yb, xa, ya
        ang = np.degrees(np.arctan2(yb - ya, xb - xa)) if xb != xa else 0.0
        h = max(l["y1"] - l["y0"], 30)
        box = (max(0, l["x0"] - a.pad), max(0, l["y0"] - a.pad), min(img.width, l["x1"] + a.pad), min(img.height, l["y1"] + a.pad))
        crop = img.crop(box)
        if abs(ang) > 0.4:
            crop = crop.rotate(ang, resample=Image.BICUBIC, expand=False, fillcolor=(235, 225, 205))
            # after rotation, trim to the band around the (now horizontal) baseline
            cy = (l["by"] - box[1])
            top = int(max(0, cy - 0.85 * h)); bot = int(min(crop.height, cy + 0.45 * h))
            crop = crop.crop((0, top, crop.width, bot))
        # red rubric bars sit in the interline space just ABOVE the lemma words: look 0.9*h..0.15*h above baseline
        by = int(l["by"]); ra, rb = max(0, int(by - 0.95 * h)), max(0, int(by - 0.15 * h))
        has_red = bool(red[ra:rb, box[0]:box[2]].sum() > 40)
        W = crop.width; mid = W // 2
        if W <= 1400:
            c = crop.resize((crop.width * a.scale, crop.height * a.scale), Image.LANCZOS)
            c.save(os.path.join(a.outdir, f"{r}_{n:02d}_F.png"))
        else:
            for tag, (p, q) in (("R", (mid - a.overlap, W)), ("L", (0, mid + a.overlap))):
                c = crop.crop((max(0, p), 0, min(W, q), crop.height))
                c = c.resize((c.width * a.scale, c.height * a.scale), Image.LANCZOS)
                c.save(os.path.join(a.outdir, f"{r}_{n:02d}_{tag}.png"))
        rows.append(f"{r}\t{n}\t{box[0]},{box[1]},{box[2]},{box[3]}\t{l['by']:.0f}\t{ang:.1f}\t{'red' if has_red else ''}")
    open(os.path.join(a.outdir, "lines.tsv"), "w").write("\n".join(rows))
    print(a.image, {k: v for k, v in counters.items()}, "red:", sum(1 for r in rows if r.endswith("red")))

if __name__ == "__main__":
    main()
