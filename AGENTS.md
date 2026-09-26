# AGENTS.md

## Project purpose

This repository is an experimental scholarly transcription, translation, and presentation of Reuven Tzarfati’s *Perush ha-Yeri‘ah ha-Gedolah* from JTS MS 2367. Work in this repository should remain suitable for expert review: preserve manuscript evidence, distinguish witnesses, expose uncertainty, and avoid silently repairing difficult text.

## Active workspace and concurrent work

- The active shared clone is `C:\Users\ezrab\Ezra Brandt\Claude\yeriah_ms`.
- The former clone at `C:\Users\ezrab\Downloads\yeriah_ms` is reference-only. Do not make new edits or commits there.
- Claude may be downloading manuscript tiles or correcting transcriptions in this clone. Before editing, building, pulling, merging, rebasing, or committing, inspect `git status`, recent file modification times, and any active download/transcription logs or processes.
- Preserve all concurrent uncommitted work. Do not clean generated folders, remove logs, restart downloads, or modify a transcription folio another process is actively writing.
- Before publishing, fetch the remote and reconcile any divergent commits only after the active downloader or transcription job has finished. Never rewrite another agent’s commit.

## Source hierarchy and witness discipline

- The JTS 2367 transcription is the source text translated in the folio HTML editions.
- Treat *Iggeret Sippurim* as the underlying Great Parchment text expounded by Tzarfati. Oxford, Bodleian Library MS Hunt. Add. E is a visual manuscript witness to that text, not the commentary itself.
- Keep Busi’s edited witnesses, the Oxford parchment, and the JTS copy of Tzarfati’s commentary distinct as documentary layers. Establish local wording through comparison rather than assuming that any one witness reproduces the exact recension or layout available to Tzarfati.
- Never replace a JTS reading silently with Oxford, Busi, a biblical source, or a conjecture. Show consequential variants explicitly and explain the reason for preferring any reading.
- Preserve the existing transcription notation: `[?]` for uncertainty, `<..>` for illegible text, strikethrough for deleted text, and explicit labels for interlinear or marginal material.
- When a manuscript image must be rechecked, say so. Do not convert a plausible reading into a certainty merely because it makes better sense.

## Academic translation style

- Translate line by line and retain the manuscript line numbers.
- Use clear academic English while preserving the argument’s syntax, repetitions, and abrupt transitions when they are meaningful.
- Do not paraphrase away technical or mythic language. Translate the claim in the main text and explain it in a note where needed.
- Italicize transliterated sefirotic and technical terms such as *Chokhmah*, *Binah*, *Chesed*, *Pachad*, *Gevurah*, *Tiferet*, *Netzach*, *Hod*, *Yesod*, *Malkhut*, *sefirah*, and *ilan*.
- Use “hypostasis” for `הויה` only where the word denotes an emanated divine grade; do not apply that rendering mechanically.
- Retain unresolved readings with a visible dotted-underline uncertainty marker in HTML. Use bracketed explanations sparingly and label supplied syntax or conjectural meaning.
- Translate biblical lemmata recognizably, but do not force them to match a standard English Bible when the medieval Hebrew adapts or combines verses.
- When the commentary depends on wordplay, give the literal forms or transliteration in a note.

## Annotation style

- Notes should do identifiable scholarly work: cite a biblical or rabbinic source, explain terminology, register a textual variant, identify a parallel, or state why a reading remains uncertain.
- Separate source identification from interpretation. Use wording such as “the commentary maps,” “apparently,” “probably,” or “provisionally” when the text does not justify certainty.
- Cite tractate and folio for Talmudic passages and work/section or chapter/verse for other primary sources when known.
- Do not inflate the notes with generic introductions to Kabbalah. Explain only what materially helps the reader understand this passage.
- Flag internal contradictions rather than harmonizing them. A contradiction may reflect textual corruption, recensional difference, diagrammatic logic, or the present transcription.
- Use the comparative apparatus for variants that affect meaning; minor orthographic differences need not be tabulated unless they bear on interpretation.

## Oxford Great Parchment presentation

- Place every Oxford quotation immediately before the corresponding JTS lemma or section.
- The label, Hebrew quotation, editorial comparison, and region link must not run together in one paragraph.
- Put the Hebrew quotation in its own semantic paragraph:

  ```html
  <div class="oxford-lemma">
    <strong>Oxford Great Parchment:</strong>
    <p class="oxford-hebrew" lang="he" dir="rtl">...</p>
    <p class="oxford-meta">Variant note, if needed. <a href="...">View region</a></p>
  </div>
  ```

- Every `.oxford-hebrew` paragraph must have `lang="he"`, `dir="rtl"`, right alignment, and a Hebrew-capable font stack.
- Quote enough Oxford text to establish the correspondence. Do not abbreviate merely to save vertical space; readable paragraphing is preferred.
- Link to the exact Ilanot Portal shape/region supplied for the passage whenever available.
- Keep English variant discussion in a separate LTR `.oxford-meta` paragraph.

## HTML edition structure

- Produce one self-contained HTML page per translated folio, named `translation_NNNx.html`.
- For generator-managed folios, edit `translations/Nx.md`; do not hand-edit the generated `translation_Nx.html`. The corrected `transcription/NNNx.md` remains the sole source for the Hebrew column.
- Build visible checkpoints with `build_translation.py --through N`; use `--final` for the complete page and `--publish` only after review. Draft manifest entries must not appear in public navigation.
- Match the established visual system: warm paper background, maroon lemma headings, green Oxford panels, side-by-side English/Hebrew lines, and responsive mobile stacking.
- The main parallel grid uses English translation on the left, line number in the center, and JTS Hebrew on the right.
- JTS Hebrew must be `dir="rtl"`, right-aligned, and visually distinct from the English translation.
- Retain previous/home/next navigation so the folios form a continuous reading sequence.
- Add visualizations or tables only when they clarify a real relationship: sefirotic mapping, narrative analogy, witness variants, or a sequence spanning several lemmata.
- Mark reconstructions and inferred mappings as provisional in captions or table cells.
- Keep footnote backlinks functional and IDs unique within each page.
- Use semantic headings in order and provide meaningful `aria-label` text for navigation and diagrams.

## GitHub Pages and project navigation

- `index.html` is generated by `build_site.py` from `transcription/combined_transcriptions.md`. Change the generator rather than hand-editing generated navigation.
- Translation navigation is generated from `translation_manifest.json`. Register new work as `draft`; `build_translation.py --publish` changes it to `published`, refreshes generator-managed neighboring pages, and regenerates `index.html`.
- Preserve the prominent translation heading and the links to the GitHub-rendered research survey and project README.
- Keep `README.md` accessible to nontechnical readers; place implementation commands after the project overview.

## Validation before committing

- Parse every changed HTML file with Python’s standard `html.parser` or an equivalent validator.
- Run `py -3.13 build_translation.py --check` for generator-managed pages and `py -3.13 -m unittest discover -s tests -v` after changing the generator.
- Confirm that each Oxford block contains exactly one standalone `.oxford-hebrew` paragraph and that it has `lang="he" dir="rtl"`.
- Run `git diff --check`.
- Rebuild `index.html` after changing `build_site.py`.
- Check previous/next/home links and verify that all linked local files exist.
- When publishing, wait for the GitHub Pages deployment and verify the live URLs return HTTP 200.
