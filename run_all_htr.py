"""Run kraken (SoferMahir layout + Italian_01) on every hires_*.jpg as it appears.
Skips folios that already have htr/NNNx_italian.txt. Waits for downloads to finish.
"""
import os, subprocess, time, glob
K = r"C:\Users\ezrab\kraken-venv\Scripts\kraken.exe"
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
rows = [l.split("\t")[0] for l in open("folio_fl_map.tsv").read().strip().split("\n")]
os.makedirs("htr", exist_ok=True)
pending = set(rows)
idle = 0
while pending and idle < 120:
    done_any = False
    for fol in sorted(pending):
        img = f"hires_{fol}.jpg"; out = f"htr/{fol}_italian.txt"
        if os.path.exists(out):
            pending.discard(fol); continue
        if not os.path.exists(img):
            continue
        # make sure download finished (file size stable)
        s1 = os.path.getsize(img); time.sleep(2); s2 = os.path.getsize(img)
        if s1 != s2 or s1 < 500000:
            continue
        t = time.time()
        r = subprocess.run([K, "-i", img, out, "segment", "-bl", "-i", "models/SoferMahirCleanFL06Eb_83_tl.mlmodel",
                            "ocr", "-m", "models/Italian_01.mlmodel"], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        ok = os.path.exists(out)
        if ok:
            lines = open(out, encoding="utf-8").read().split("\n")
            open(f"htr/{fol}_italian_logical.txt", "w", encoding="utf-8").write(
                "\n".join(f"{i:02d} {l[::-1]}" for i, l in enumerate(lines, 1) if l.strip()))
        print(fol, "ok" if ok else "FAIL", f"{time.time()-t:.0f}s", flush=True)
        if not ok:
            print(r.stderr[-800:], flush=True)
        pending.discard(fol); done_any = True
        # also cut line crops for the reading pass
        subprocess.run(["py", "-3.13", "make_lines.py", img, f"hl_{fol}", "--scale", "2"], capture_output=True)
    if not done_any:
        idle += 1; time.sleep(30)
    else:
        idle = 0
print("finished; pending:", sorted(pending))
