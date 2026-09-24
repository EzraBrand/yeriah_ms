# Yeriah Gedolah — Tzarfati commentary transcription (JTS 2367, fols. 76b–97b)

## Layout
- `folio_fl_map.tsv` — folio → NLI IIIF file id (from the manifest at
  `https://iiif.nli.org.il/IIIFv21/DOCID/PNX_MANUSCRIPTS990001050100205171-1/manifest`).
- `iiif_tiles.py FLxxxx out.jpg` — full-resolution download by 333px tiles (server caps single requests at 526px).
- `download_all.py` — runs the above for every folio → `hires_NNNx.jpg` (~4000x5400 px, 2x the PDF export).
- `make_lines.py hires_076b.jpg hl_076b --scale 2` — detects the text block and line bands, writes one image per
  line split right/left (`lNN_R.png`, `lNN_L.png`), `bands.json` with red-underline flags, and `overview.png`.
- `models/` — kraken models (gitignored): `BiblIA_01` (general medieval Hebrew), `Italian_01`, layout models
  `BiblIAlong02_se3_2_tl` (main block only) and `SoferMahirCleanFL06Eb_83_tl` (main/margin/paratext).
- `htr/` — kraken outputs. Lines are stored visually reversed; `*_logical.txt` has them flipped back.
- `transcription/NNNx.md` — human/LLM transcription, one file per folio.

## Commands
```
py -3.13 download_all.py
py -3.13 make_lines.py hires_077a.jpg hl_077a --scale 2
set PYTHONUTF8=1
C:\Users\ezrab\kraken-venv\Scripts\kraken.exe -i hires_077a.jpg htr\077a.txt segment -bl -i models\SoferMahirCleanFL06Eb_83_tl.mlmodel ocr -m models\Italian_01.mlmodel
```

## Reading protocol (what actually worked)
1. Run kraken first; read its logical-order output alongside the line crops.
2. Send at most 8 line images per model call; transcribe immediately into `transcription/NNNx.md`.
3. Mark uncertain words `[?]`, bold the lemmas, and add `(k)` where kraken supports the reading.
4. Second pass only on `[?]` words, with Busi's base text open for the lemmas.

## Preferred line source: kraken ALTO (added 25-Sep-2026)
`make_lines.py` (projection bands) fails on skewed pages and on red-underline rows. Use instead:
```
kraken -a -i hires_077a.jpg htr\077a_seg.xml segment -bl -i models\SoferMahirCleanFL06Eb_83_tl.mlmodel
py -3.13 alto_lines.py hires_077a.jpg htr\077a_seg.xml al_077a --scale 2
```
This gives deskewed per-line crops (`Main_NN_R/L.png`, `Margin_NN_F.png`) whose numbering matches the
kraken text output line-for-line. Margin text in the gutter is out of focus in the NLI photographs.
