"""Download a full-resolution NLI IIIF image by tiles and stitch it.
usage: py -3.13 iiif_tiles.py FL27544706 out.jpg
"""
import io, json, os, sys, time, urllib.request
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-scraper/0.1",
      "Referer": "https://www.nli.org.il/"}
BASE = "https://iiif.nli.org.il/IIIFv21/"

def get(url, tries=4):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            if t == tries - 1:
                raise
            time.sleep(1.5 * (t + 1))

def info(fl):
    return json.loads(get(f"{BASE}{fl}/info.json"))

def download(fl, out, tile=333, cache_dir=None):
    inf = info(fl)
    W, H = inf["width"], inf["height"]
    cache_dir = cache_dir or f"tiles_{fl}"
    os.makedirs(cache_dir, exist_ok=True)
    canvas = Image.new("RGB", (W, H))
    n = 0
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            w = min(tile, W - x); h = min(tile, H - y)
            p = os.path.join(cache_dir, f"{x}_{y}.jpg")
            if not os.path.exists(p):
                data = get(f"{BASE}{fl}/{x},{y},{w},{h}/full/0/default.jpg")
                open(p, "wb").write(data)
                n += 1
                time.sleep(0.05)
            canvas.paste(Image.open(p).convert("RGB"), (x, y))
    canvas.save(out, quality=95)
    print(fl, W, H, "fetched", n, "->", out)
    return W, H

if __name__ == "__main__":
    fl, out = sys.argv[1], sys.argv[2]
    download(fl, out)
