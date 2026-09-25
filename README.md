# Reading Reuven Tzarfati’s *Commentary on the Great Parchment*

This project is an experimental digital edition of a difficult and little-studied medieval Hebrew kabbalistic commentary: Reuven Tzarfati’s *Perush ha-Yeri‘ah ha-Gedolah* (Commentary on the Great Parchment), preserved here from Jewish Theological Seminary MS 2367, fols. 76b–97b.

The manuscript is challenging in several ways. Its script is difficult, its prose assumes an esoteric vocabulary, and its explanations move among biblical verses, rabbinic traditions, sefirotic symbolism, and the spatial logic of kabbalistic diagrams. The project therefore combines manuscript transcription, academic translation, textual comparison, annotation, and experimental visualization.

## Read the project

- [Combined Hebrew transcription](https://ezrabrand.github.io/yeriah_ms/)
- [Folio 76b: translation and annotations](https://ezrabrand.github.io/yeriah_ms/translation_76b.html)
- [Folio 77a: translation and annotations](https://ezrabrand.github.io/yeriah_ms/translation_77a.html)
- [Folio 77b: translation and annotations](https://ezrabrand.github.io/yeriah_ms/translation_77b.html)
- [State-of-research and bibliography](https://github.com/EzraBrand/yeriah_ms/blob/master/research_state_of_the_field.md)

Each translated folio places the Hebrew transcription and English translation side by side. Comparative excerpts from Oxford, Bodleian Library MS Hunt. Add. E—the Great Parchment presented by the [Ilanot Portal](https://www.ilanot.org/detail?id=https://ilanot.org/resource/item/manuscript40rgm)—are inserted beside the corresponding lemmata. Notes distinguish secure readings, conjectures, source identifications, and differences between witnesses.

## An experiment with AI and the humanities

This is explicitly an experiment in using generative AI for manuscript research. It was inspired in part by Benjamin Breen’s Res Obscura essay [“AI makes the humanities more important, but also a lot weirder”](https://resobscura.substack.com/p/ai-makes-the-humanities-more-important), especially its argument that AI can extend paleography, translation, classification, and tool-building while making humanistic judgment—not merely automated output—more important. Other examples of this emerging experimental approach include the [Hacker News discussion of using LLMs to trace alchemical knowledge and decode seventeenth-century letters](https://news.ycombinator.com/item?id=49835531) and [Source Library](https://sourcelibrary.org/).

Claude Fable performed the initial technical work: assembling the image and OCR pipeline, segmenting manuscript pages, and establishing the first transcription workflow. Codex GPT-5.6-Sol subsequently developed the academic translations, annotations, comparative apparatus, visualizations, HTML reading editions, research survey, and public site.

## What the project may contribute

The working translations already suggest that the commentary reads its “parchment” spatially: rivers, trees, limbs, directions, and biblical figures become coordinates in a sefirotic diagram. Comparison with the Oxford Great Parchment can clarify corrupt or abbreviated lemmata, but it also reveals meaningful differences. Recent work by J. H. Chajes cautions that the text published by Giulio Busi as *The Great Parchment* may be distinct from the parchment on which Tzarfati commented. The project therefore treats every proposed alignment as evidence to be tested, not as a settled identity.

See the [state-of-research report](https://github.com/EzraBrand/yeriah_ms/blob/master/research_state_of_the_field.md) for the bibliography, RAMBI search results, manuscript map, and current research questions.

## Technical workflow

The remainder of this README documents the reproducible transcription and site-building workflow.

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
