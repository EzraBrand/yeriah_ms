"""Rebuild transcription/combined_transcriptions.md from the per-folio files (NNNx.md).

usage: py -3.13 combine_transcriptions.py [--check]
--check only reports whether the current combined file differs from the rebuilt text.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "transcription"
OUT = ROOT / "combined_transcriptions.md"

def rebuild() -> str:
    files = sorted(p for p in ROOT.glob("*.md") if re.fullmatch(r"\d{3}[ab]\.md", p.name))
    parts = [p.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip() for p in files]
    return "# Combined Transcriptions\n\n" + "\n\n---\n\n".join(parts) + "\n"

if __name__ == "__main__":
    text = rebuild()
    if "--check" in sys.argv:
        old = OUT.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        print("same" if old == text else "differs")
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {OUT.name}: {text.count(chr(10) + '---' + chr(10)) + 1} folios")
