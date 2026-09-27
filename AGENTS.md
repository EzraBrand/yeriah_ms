# AGENTS.md

## Project purpose

This repository is an experimental scholarly transcription, translation, and presentation of Reuven Tzarfati’s *Perush ha-Yeri‘ah ha-Gedolah* from JTS MS 2367. Work in this repository should remain suitable for expert review: preserve manuscript evidence, distinguish witnesses, expose uncertainty, and avoid silently repairing difficult text.

## Active workspace and concurrent work

- The active shared clone is `C:\Users\ezrab\Ezra Brandt\Claude\yeriah_ms`.
- The former clone at `C:\Users\ezrab\Downloads\yeriah_ms` is reference-only. Do not make new edits or commits there.
- Claude and Codex work in this clone at the same time: typically Claude transcribes, rechecks images, and reviews; Codex translates and annotates. Before editing, building, pulling, merging, rebasing, or committing, inspect `git status`, recent file modification times, and any active download/transcription logs or processes.
- Stage files by explicit path. Never use `git add -A`, `git add .`, or `git commit -a`: they sweep in the other agent's uncommitted work.
- A folio whose files show uncommitted changes belongs to the agent that made them. Do not edit or rebuild its translation page until those changes are committed; if a fix is needed there, report it instead.
- Preserve all concurrent uncommitted work. Do not clean generated folders, remove logs, restart downloads, or modify a transcription folio another process is actively writing.
- Before publishing, fetch the remote and reconcile any divergent commits only after the active downloader or transcription job has finished. Never rewrite another agent’s commit.
- Commit a translation draft (`translations/Nx.md`, its generated page, and the `draft` manifest entry) as soon as a reviewable checkpoint exists. Uncommitted drafts block other agents from building or reviewing, and they can be lost.
- End a work session with a short handoff: folios done, commits, open `[?]` points, and rechecks still needed.

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

## Pre-translation check of the transcription

The transcription is a draft. A translation built on a misreading hides the error behind fluent English. Before translating a folio:

- Read the folio's transcription notes and count its `[?]` marks. Folios with many uncertain readings (at present 91a–92a) need a second transcription pass before translation.
- Compare every lemma with the Oxford Great Parchment (`oxford/oxford_zones.md`; see “Oxford text for lemma comparison”) and with the kraken text. Busi’s 2004 edition is not available to the project (no local or online copy; see `research_state_of_the_field.md`); do not claim a Busi comparison unless a copy is supplied. **Where Oxford diverges from a JTS lemma, recheck the JTS image before translating.** In 80b the draft transcription had `נהר עשירי יכלבו לבד` and `ואפלה לאברהם`; the image reads `ודור עשירי ישובו לנח` and `ומפלגא לאברהם`, as in Oxford. The same recheck turned an apparent first-person disclaimer (`לא קבלתי`) into `נתנו לנו קבלה`.
- Also compare against the kraken text (`htr/NNNx_italian_logical.txt`). When kraken agrees with Oxford against the transcription, the transcription is probably wrong.
- The hi-res images and line crops are not kept. To recheck: `py -3.13 download_from.py 080b` (it continues to later folios; stop or ignore them; on HTTP 429 rerun with `--workers 2`), then `py -3.13 alto_lines.py hires_080b.jpg htr\080b_seg.xml al_080b --scale 2`, and read only the needed `al_080b/Main_NN_R/L.png` crops, at most 8 images per call.
- Correct the transcription first (in `transcription/NNNx.md`, with a dated note of the old and new reading), then rebuild the translation. Never correct the Hebrew only in the English.

## Translation fidelity checklist

These points come from the review of the 80b draft (27 September 2026). Check each before `--final`:

- **Carry every uncertainty.** Each `[?]` in the Hebrew needs a matching `??…[?]??` in the English. Do not render an uncertain word as secure English.
- **Add no unlabelled words.** Bracketed supplements must be syntax, e.g. `[is]`, or labelled conjecture. Do not invent a clause to smooth an opening fragment.
- **Keep lemmata recognizable.** Translate a biblical lemma in its biblical sense. When the exposition rereads the same words (a pun, a revocalization, a gematria), keep the lemma recognizable and show the second sense with a transliteration, e.g. 80b:20 “for whom it is thus” (*she-kakhah*) reread as *shakhakhah*, “subsided” (Esther 7:10).
- **Keep abbreviations as written in the Hebrew column.** The page Hebrew must match the transcription exactly (`לישמעאלי'`, not an expanded `לישמעאלים`); expansions belong in the English or a note.
- **Keep JTS syntax.** Subject, object, and preposition follow JTS even where Oxford or the Bible differ; e.g. `והולידו את בני האלהים` makes "the sons of God" the object. Record the difference in a note.
- **Translate prepositions exactly.** `למעלה מ-` is "above", not "to".
- **Keep compounds apart when the commentary splits them.** If the exposition parses `שבעה עשר` into "seven" and "ten", do not translate both places as "the seventeenth".
- **One word, one rendering.** When the same Hebrew word appears in a lemma and a gloss, render it the same way, or give both senses and explain the wordplay (e.g. `כלה` "all" / "bride").
- **Name the speakers correctly.** `המחבר` is the author of the Great Parchment text; the commentator is Tzarfati. Never call either of them "the translator".
- **Verify every gematria.** Compute it in the note (e.g. `שככה` = `בשגם` = `משה` = 345). If it does not calculate as read, say so; do not assert it.
- **Anchor notes where the topic starts.** Put the reference at the first line that the note discusses. Split a note that covers two separate passages. Number notes in order of first appearance.

## Oxford text for lemma comparison

The full Oxford transcription is available locally; do not click through the portal zone by zone.

- `oxford/oxford_zones.md` has one section per zone: `## Zone <label> | <shape id>`, then the plain Hebrew. Zones 2.1–2.22 hold the running text of the narratives Tzarfati expounds (for example 2.5 = the Flood through the Sacrifice of Isaac, 80a–82a; 2.15 = levirate marriage and Ruth, 90a–91b; 2.16 = the lampstand, 91b–92b). `oxford/shapes.json` is the raw response.
- Refresh both with `py -3.13 fetch_oxford.py`. The Ilanot Portal viewer loads every zone in one request: `https://www.ilanot.org/shapesjson?id=https://ilanot.org/resource/item/manuscript40rgm`. The response is a list with one surface; `[0]["text"][<shape id>]` has `zoneName` and `text` (XHTML). If a shell fetch is blocked, open that URL in a browser, or run `fetch('/shapesjson?id=…')` in a page on ilanot.org.
- A zone link for the translation pages is `https://www.ilanot.org/detail?id=https://ilanot.org/resource/item/manuscript40rgm&shape=<shape id>`.
- Method that works: list every bold lemma of the folio, find its Oxford wording with `grep` in `oxford_zones.md`, and reread in the image each lemma where the two differ. On 27 September 2026 this found about 50 misread lemmata in 76b–92a (e.g. `שדה כובס` read as `כוכב`, `כרובים` as `כוכבים`). Oxford points to the place to recheck; the JTS image decides the reading.

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
- When a folio is published, add it to the README's “Read the project” list and to the Translations column of the contents table, and update the “Current status” section. When a transcription recheck changes a reading that matters for the argument, record it in the folio's transcription notes (dated), not in the README.

## Validation before committing

- Parse every changed HTML file with Python’s standard `html.parser` or an equivalent validator.
- Run `py -3.13 build_translation.py --check` for generator-managed pages and `py -3.13 -m unittest discover -s tests -v` after changing the generator.
- Confirm that each Oxford block contains exactly one standalone `.oxford-hebrew` paragraph and that it has `lang="he" dir="rtl"`.
- Run `git diff --check`.
- After changing any `transcription/NNNx.md`, run `py -3.13 combine_transcriptions.py` and `py -3.13 build_site.py`, and rebuild every translation page that uses that folio.
- Before `--publish`, go through the translation fidelity checklist above.
- Run `py -3.13 audit_translations.py` (all manifest folios) or `py -3.13 audit_translations.py 81a` (one folio). It must report `clean` before a publish. It compares each page's Hebrew column with the current transcription and flags uncertain Hebrew readings that are unmarked in the English.
- Folios 76b–79a are hand-written HTML pages, not generator-managed. When their transcription changes, edit the Hebrew and English columns of the page by hand; the audit shows where.
- Rebuild `index.html` after changing `build_site.py`.
- Check previous/next/home links and verify that all linked local files exist.
- When publishing, wait for the GitHub Pages deployment and verify the live URLs return HTTP 200.
