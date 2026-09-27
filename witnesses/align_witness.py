"""Align a witness's kraken reading with the JTS transcription.

usage: py -3.13 witnesses/align_witness.py munich311 --jts 093b 094a 094b --pages 027v 028r 028v 029r [--model Italian_01]

For each JTS line, finds the best-matching window in the witness's machine text (character-trigram
similarity over consonants) and reports the witness page:line, the score, and the matched text.
Writes witnesses/<name>/align_<first>-<last>.tsv.
"""
import argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LET = re.compile(r"[^א-ת ]")
FINAL = str.maketrans("ךםןףץ", "כמנפצ")

def norm(s):
    s = s.replace("ﭏ", "אל")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"\[\?\]|<\.\.>|~~.*?~~", " ", s)
    return " ".join(LET.sub(" ", s).translate(FINAL).split())

def grams(s, n=3):
    s = s.replace(" ", "")
    return {s[i:i + n] for i in range(len(s) - n + 1)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--jts", nargs="+", required=True)
    ap.add_argument("--pages", nargs="+", required=True); ap.add_argument("--model", default="Italian_01")
    a = ap.parse_args()
    wd = ROOT / "witnesses" / a.name
    wl = []  # (page, lineno, text)
    for pg in a.pages:
        for l in (wd / "htr" / f"{pg}_{a.model}_logical.txt").read_text(encoding="utf-8").split("\n"):
            m = re.match(r"(\d+) (.*)", l)
            if m:
                wl.append((pg, int(m.group(1)), norm(m.group(2))))
    out = ["jts\tscore\twitness\tjts_text\twitness_text"]
    scores = []
    for f in a.jts:
        t = (ROOT / "transcription" / f"{f}.md").read_text(encoding="utf-8").split("## Notes")[0]
        for m in re.finditer(r"^(\d+)\. (.*)$", t, re.M):
            jt = norm(m.group(2))
            if len(jt) < 15:
                continue
            g = grams(jt)
            best = (0, None, "")
            for i in range(len(wl)):
                for span in (1, 2):
                    if i + span > len(wl): continue
                    txt = " ".join(x[2] for x in wl[i:i + span])
                    wg = grams(txt)
                    sc = len(g & wg) / max(1, len(g))
                    sc -= 0.15 * (span - 1)
                    if sc > best[0]:
                        best = (sc, f"{wl[i][0]}:{wl[i][1]}" + (f"-{wl[i+span-1][1]}" if span > 1 else ""), txt)
            scores.append(best[0])
            out.append(f"{f[1:]}:{m.group(1)}\t{best[0]:.2f}\t{best[1]}\t{jt}\t{best[2]}")
    p = wd / f"align_{a.jts[0]}-{a.jts[-1]}.tsv"
    p.write_text("\n".join(out), encoding="utf-8")
    import statistics
    print(f"{len(scores)} JTS lines; median trigram overlap {statistics.median(scores):.2f}; "
          f">=0.5: {sum(s>=0.5 for s in scores)}; <0.3: {sum(s<0.3 for s in scores)} -> {p.name}")

if __name__ == "__main__":
    main()
