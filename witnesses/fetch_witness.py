"""Download pages of a witness manuscript from its saved NLI IIIF manifest.

usage: py -3.13 witnesses/fetch_witness.py munich311 "Fol. 026r" "Fol. 033v"
Downloads every canvas from the first label through the second (inclusive) into
witnesses/<name>/img/<label>.jpg at full resolution (tiled, cached per file).
"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from iiif_tiles import download

name, first, last = sys.argv[1:4]
root = Path(__file__).resolve().parent / name
canvases = json.loads((root / "manifest.json").read_text(encoding="utf-8"))["sequences"][0]["canvases"]
labels = [c.get("label") for c in canvases]
i, j = labels.index(first), labels.index(last)
(root / "img").mkdir(exist_ok=True)
for c in canvases[i:j + 1]:
    fl = c["images"][0]["resource"]["service"]["@id"].rstrip("/").split("/")[-1]
    out = root / "img" / (c["label"].replace("Fol. ", "").replace(" ", "_") + ".jpg")
    if out.exists():
        continue
    download(fl, str(out), cache_dir=str(root / "tiles" / fl))
    print("OK", c["label"], fl, flush=True)
