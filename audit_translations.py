"""Audit translation pages against the corrected transcriptions.

usage: py -3.13 audit_translations.py [80b 81a ...]
With no folios, audits every page in translation_manifest.json (drafts too).

Reports, per line:
- HEBREW-DIFFERS  the page's Hebrew column no longer matches transcription/NNNx.md
                  (markup, punctuation and the ﭏ ligature are ignored). Generator pages are
                  fixed by rebuilding; hand-written pages (76b-79a) must be edited by hand.
- NO-SOURCE-LINE  the page has a line number that the transcription lacks.
- UNCERTAIN       the Hebrew has a [?] reading but the English line has no uncertainty marker.
Exit status 1 if anything is reported.
"""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Lines(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cur, self.field, self.depth = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get("class") or "").split()
        if tag == "div" and "line" in cls:
            self.cur = {"num": "", "tr": "", "src": "", "tr_unc": 0}
            self.rows.append(self.cur)
            return
        if self.cur is not None and tag == "div" and cls and cls[0] in ("translation", "number", "source"):
            self.field, self.depth = {"translation": "tr", "number": "num", "source": "src"}[cls[0]], 1
            return
        if self.field and tag == "div":
            self.depth += 1
        if self.field == "tr" and "uncertain" in cls:
            self.cur["tr_unc"] += 1

    def handle_endtag(self, tag):
        if self.field and tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.field = None

    def handle_data(self, data):
        if self.field:
            self.cur[self.field] += data


def norm(text):
    text = text.replace("ﭏ", "אל")
    text = re.sub(r"\(interlinear:\s*([^)]*)\)", r" \1 ", text)  # page style: (interlinear: X)
    text = re.sub(r"\((?:[^()]*)\)", " ", text)   # labels such as (interlinear), (blot)
    text = re.sub(r"[^\u05d0-\u05ea ]", " ", text)
    return " ".join(text.split())


def transcription(folio):
    path = ROOT / "transcription" / f"0{folio}.md"
    lines = {}
    for m in re.finditer(r"^(\d+)\. (.*)$", path.read_text(encoding="utf-8"), re.M):
        lines[str(int(m.group(1)))] = m.group(2)
    return lines


def audit(folio):
    page = ROOT / f"translation_{folio}.html"
    parser = Lines()
    parser.feed(page.read_text(encoding="utf-8"))
    source = transcription(folio)
    out = []
    for row in parser.rows:
        num = row["num"].strip()
        if re.fullmatch(r"\d+[ab]", num):
            continue   # hand-written pages split one manuscript line into a/b rows
        key = str(int(num)) if num.isdigit() else num
        hebrew = " ".join(row["src"].split())
        english = " ".join(row["tr"].split())
        if key not in source:
            out.append(f"{folio}:{num} NO-SOURCE-LINE")
            continue
        if norm(source[key]) != norm(hebrew):
            out.append(f"{folio}:{num} HEBREW-DIFFERS\n    page: {hebrew}\n    text: {source[key]}")
        if "[?]" in hebrew and not ("[?]" in english or row["tr_unc"]):
            words = re.findall(r"(\S+)\[\?\]", hebrew)
            out.append(f"{folio}:{num} UNCERTAIN {words}\n    en: {english}")
    return out


def main():
    folios = sys.argv[1:]
    if not folios:
        manifest = json.loads((ROOT / "translation_manifest.json").read_text(encoding="utf-8"))
        folios = [entry["folio"] for entry in manifest["folios"]]
    report = [line for folio in folios for line in audit(folio)]
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(report) if report else f"clean: {', '.join(folios)}")
    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main())
