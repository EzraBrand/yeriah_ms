"""Global character alignment of a JTS section with a witness's machine reading, then report
what the witness has at each uncertain ([?]) JTS word and each lemma.

usage: py -3.13 witnesses/collate_uncertain.py munich311 --jts 093b:18 094b:40 --wit 026r:16 028v:21
Outputs witnesses/<name>/collate_<start>.tsv with columns:
  jts_line  jts_word  witness_page:line  witness_chars(machine)  kind
and prints an overall character-match rate (a rough HTR quality measure for the witness hand).
"""
import argparse, difflib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINAL = str.maketrans("ךםןףץ", "כמנפצ")

def clean_words(s):
    s = s.replace("ﭏ", "אל")
    s = re.sub(r"\((?:[^()]*)\)", " ", s)
    s = re.sub(r"~~.*?~~", " ", s)
    toks = []
    for w in s.split():
        unc = "[?]" in w
        lem = "**" in w
        c = re.sub(r"[^א-ת]", "", w).translate(FINAL)
        if c:
            toks.append((c, unc, lem))
    return toks

def jts_lines(start, end):
    f0, l0 = start.split(":"); f1, l1 = end.split(":")
    fols = sorted(p.stem for p in (ROOT / "transcription").glob("0[0-9][0-9][ab].md"))
    fols = [f for f in fols if f"0{f0}" <= f <= f"0{f1}"] if len(f0) == 3 else [f for f in fols if f0 <= f <= f1]
    out = []
    for f in fols:
        t = (ROOT / "transcription" / f"{f}.md").read_text(encoding="utf-8").split("## Notes")[0]
        for m in re.finditer(r"^(\d+)\. (.*)$", t, re.M):
            key = (f, int(m.group(1)))
            if (f, int(m.group(1))) < (f"0{f0}" if len(f0) == 3 else f0, int(l0)): continue
            if (f, int(m.group(1))) > (f"0{f1}" if len(f1) == 3 else f1, int(l1)): continue
            out.append((f"{f[1:]}:{m.group(1)}", m.group(2)))
    return out

def wit_lines(wd, model, start, end):
    p0, l0 = start.split(":"); p1, l1 = end.split(":")
    pages = sorted(p.name.split("_")[0] for p in (wd / "htr").glob(f"*_{model}_logical.txt"))
    out = []
    for pg in pages:
        if not (p0 <= pg <= p1): continue
        for l in (wd / "htr" / f"{pg}_{model}_logical.txt").read_text(encoding="utf-8").split("\n"):
            m = re.match(r"(\d+) (.*)", l)
            if not m: continue
            n = int(m.group(1))
            if (pg, n) < (p0, int(l0)) or (pg, n) > (p1, int(l1)): continue
            out.append((f"{pg}:{n}", m.group(2)))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--jts", nargs=2, required=True)
    ap.add_argument("--wit", nargs=2, required=True); ap.add_argument("--model", default="Italian_01")
    a = ap.parse_args()
    wd = ROOT / "witnesses" / a.name
    J = jts_lines(*a.jts); W = wit_lines(wd, a.model, *a.wit)
    js, jmap = [], []          # char stream + (line, word, unc, lem, word text)
    for ln, txt in J:
        for wi, (c, unc, lem) in enumerate(clean_words(txt)):
            for ch in c:
                js.append(ch); jmap.append((ln, wi, unc, lem, c))
    ws, wmap = [], []
    for ln, txt in W:
        for w in txt.split():
            c = re.sub(r"[^א-ת]", "", w.replace("ﭏ", "אל")).translate(FINAL)
            for ch in c:
                ws.append(ch); wmap.append(ln)
            ws.append(" "); wmap.append(ln)
    wstr = "".join(ws)
    wnos = wstr.replace(" ", "")
    idx = [i for i, ch in enumerate(wstr) if ch != " "]
    sm = difflib.SequenceMatcher(None, "".join(js), wnos, autojunk=False)
    # map each JTS char to a witness char index (or None) via opcodes
    j2w = [None] * len(js)
    for tag, i1, i2, k1, k2 in sm.get_opcodes():
        if tag == "equal":
            for d in range(i2 - i1): j2w[i1 + d] = k1 + d
        elif tag == "replace":
            for d in range(i2 - i1): j2w[i1 + d] = k1 + min(d, k2 - k1 - 1) if k2 > k1 else None
    matched = sum(b.size for b in sm.get_matching_blocks())
    print(f"JTS {len(js)} letters, witness {len(wnos)} letters; matched letters {matched} "
          f"({matched/len(js):.0%} of JTS)")
    # group by JTS word
    rows = ["jts\tword\tkind\twitness\twitness_text"]
    k = 0
    while k < len(js):
        ln, wi, unc, lem, word = jmap[k]
        e = k
        while e < len(js) and jmap[e][:2] == (ln, wi): e += 1
        if unc or lem:
            ws_i = [j2w[x] for x in range(k, e) if j2w[x] is not None]
            if ws_i:
                a0, a1 = max(0, min(ws_i) - 3), max(ws_i) + 4
                seg_start = idx[a0] if a0 < len(idx) else len(wstr) - 1
                seg_end = idx[min(a1, len(idx) - 1)]
                seg = wstr[seg_start:seg_end + 1].strip()
                wl = wmap[idx[min(ws_i)]]
            else:
                seg, wl = "—", "—"
            rows.append(f"{ln}\t{word}\t{'uncertain' if unc else 'lemma'}\t{wl}\t{seg}")
        k = e
    p = wd / f"collate_{a.jts[0].replace(':','-')}.tsv"
    p.write_text("\n".join(rows), encoding="utf-8")
    print("wrote", p.name, len(rows) - 1, "rows")

if __name__ == "__main__":
    main()
