"""Run kraken (SoferMahir layout + a recognition model) on witness pages.

usage: py -3.13 witnesses/htr_witness.py munich311 [--model Italian_01] [pages...]
Writes witnesses/<name>/htr/<page>_<model>.txt and _logical.txt (lines reversed back to reading order).
With --upscale N the image is enlarged N× first (the Munich photographs are ~1200 px wide).
"""
import argparse, os, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
K = r"C:\Users\ezrab\kraken-venv\Scripts\kraken.exe"
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("pages", nargs="*")
ap.add_argument("--model", default="Italian_01"); ap.add_argument("--upscale", type=float, default=1.0)
a = ap.parse_args()
wd = ROOT / "witnesses" / a.name
(wd / "htr").mkdir(exist_ok=True)
pages = a.pages or sorted(p.stem for p in (wd / "img").glob("*.jpg"))
for pg in pages:
    img = wd / "img" / f"{pg}.jpg"
    if a.upscale != 1.0:
        up = wd / "htr" / f"{pg}_x{a.upscale:g}.png"
        if not up.exists():
            im = Image.open(img); im.resize((int(im.width * a.upscale), int(im.height * a.upscale)), Image.LANCZOS).save(up)
        img = up
    tag = f"{a.model}" + (f"_x{a.upscale:g}" if a.upscale != 1.0 else "")
    out = wd / "htr" / f"{pg}_{tag}.txt"
    r = subprocess.run([K, "-i", str(img), str(out), "segment", "-bl", "-i", str(ROOT / "models/SoferMahirCleanFL06Eb_83_tl.mlmodel"),
                        "ocr", "-m", str(ROOT / f"models/{a.model}.mlmodel")], env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if out.exists():
        lines = [l for l in out.read_text(encoding="utf-8").split("\n") if l.strip()]
        (wd / "htr" / f"{pg}_{tag}_logical.txt").write_text(
            "\n".join(f"{i:02d} {l[::-1]}" for i, l in enumerate(lines, 1)), encoding="utf-8")
        print(pg, "ok", len(lines), "lines", flush=True)
    else:
        print(pg, "FAIL", r.stderr[-400:], flush=True)
