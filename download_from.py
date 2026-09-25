"""Download hires_NNNx.jpg for folios from a start folio onward, fetching tiles in parallel.

usage: py -3.13 download_from.py 083a [--workers 6]
Uses the same tile cache (tiles_FL.../) and URL scheme as iiif_tiles.py.
"""
import argparse, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iiif_tiles import BASE, get, info

TILE = 333

def fetch(fl, x, y, w, h, p):
    if not os.path.exists(p):
        data = get(f"{BASE}{fl}/{x},{y},{w},{h}/full/0/default.jpg")
        with open(p + ".part", "wb") as f:
            f.write(data)
        os.replace(p + ".part", p)

def download(fl, out, workers):
    inf = info(fl)
    W, H = inf["width"], inf["height"]
    cache = f"tiles_{fl}"
    os.makedirs(cache, exist_ok=True)
    jobs = [(x, y, min(TILE, W - x), min(TILE, H - y)) for y in range(0, H, TILE) for x in range(0, W, TILE)]
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda j: fetch(fl, *j, os.path.join(cache, f"{j[0]}_{j[1]}.jpg")), jobs))
    canvas = Image.new("RGB", (W, H))
    for x, y, w, h in jobs:
        canvas.paste(Image.open(os.path.join(cache, f"{x}_{y}.jpg")).convert("RGB"), (x, y))
    canvas.save(out, quality=95)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start", nargs="?", default="076b")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    rows = [l.split("\t") for l in open("folio_fl_map.tsv").read().strip().split("\n")]
    for fol, fl, dims in rows:
        out = f"hires_{fol}.jpg"
        if fol < a.start or os.path.exists(out):
            continue
        t = time.time()
        try:
            download(fl, out, a.workers)
            print("OK", fol, f"{time.time() - t:.0f}s", flush=True)
        except Exception as e:
            print("FAIL", fol, fl, e, flush=True)
            time.sleep(5)
    print("all done", flush=True)

if __name__ == "__main__":
    main()
