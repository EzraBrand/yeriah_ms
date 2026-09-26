# Translation page workflow

The corrected file in `transcription/` is the only source for the Hebrew column. A file here contains the English translation, section boundaries, optional Oxford parallels, apparatus, and notes. `build_translation.py` joins the two sources and writes the public HTML page.

## Start a folio

```powershell
py -3.13 build_translation.py 080a --init
```

This creates `translations/80a.md` and registers it as `draft` in `translation_manifest.json`. Drafts do not appear in the public index.

Section headings use this exact form:

```markdown
## Lines 1–16 | short-section-id | Reader-facing section title
```

Write one numbered English line for every manuscript line. Use ordinary Markdown plus these conventions:

- `**lemma text**` for a lemma;
- `??uncertain rendering [?]??` for a dotted uncertainty marker;
- `*Tiferet*` for a transliterated technical term;
- `[^1]` for a note reference.

Notes are single paragraphs:

```markdown
## Notes
[^1]: The note text. {source: Biblical and textual note.}
```

An optional Oxford block goes immediately below its section heading:

```markdown
::: oxford
hebrew: ועל כן ...
meta: The witnesses differ at **this phrase**.
url: https://www.ilanot.org/detail?...
:::
```

An optional apparatus uses ordinary Markdown, including tables:

```markdown
## Apparatus | Interpretive sequence
| Image | Function | Reference |
|---|---|---|
| ... | ... | ... |
```

## Build in visible stages

```powershell
py -3.13 build_translation.py 080a --through 16
py -3.13 build_translation.py 080a --through 32
py -3.13 build_translation.py 080a --final
py -3.13 build_translation.py 080a --publish
```

The first two commands create valid partial pages. `--final` is the third editorial stage: it adds the remaining lines, apparatus, and notes, and requires full consecutive English coverage, defined and referenced notes, exact Hebrew agreement with the transcription, valid navigation targets, unique IDs, and correct Oxford RTL attributes. `--publish` is the fourth assembly stage: it exposes the folio in navigation and rebuilds the reader index.

After review, publish explicitly:

```powershell
py -3.13 build_translation.py 080a --publish
```

Publishing changes the manifest status, refreshes navigation on generator-managed pages, and rebuilds `index.html`. Validate the managed corpus at any time with:

```powershell
py -3.13 build_translation.py --check
```
