"""For every hires_*.jpg without al_<fol>/lines.tsv: run kraken segmentation (ALTO) and alto_lines.py."""
import os, glob, subprocess, time
K = r"C:\Users\ezrab\kraken-venv\Scripts\kraken.exe"
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
for img in sorted(glob.glob("hires_*.jpg")):
    fol = img[6:-4]
    if os.path.exists(f"al_{fol}/lines.tsv"):
        continue
    s1 = os.path.getsize(img); time.sleep(1)
    if os.path.getsize(img) != s1 or s1 < 500000:
        continue
    seg = f"htr/{fol}_seg.xml"
    t = time.time()
    if not os.path.exists(seg):
        subprocess.run([K, "-a", "-i", img, seg, "segment", "-bl", "-i", "models/SoferMahirCleanFL06Eb_83_tl.mlmodel"],
                       env=env, capture_output=True)
    r = subprocess.run(["py", "-3.13", "alto_lines.py", img, seg, f"al_{fol}", "--scale", "2"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(fol, r.stdout.strip() or r.stderr[-200:], f"{time.time()-t:.0f}s", flush=True)
print("done")
