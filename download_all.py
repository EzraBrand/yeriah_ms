import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iiif_tiles import download
rows = [l.split("\t") for l in open("folio_fl_map.tsv").read().strip().split("\n")]
for fol, fl, dims in rows:
    out = f"hires_{fol}.jpg"
    if os.path.exists(out):
        continue
    try:
        download(fl, out)
    except Exception as e:
        print("FAIL", fol, fl, e, flush=True)
        time.sleep(5)
print("all done")
