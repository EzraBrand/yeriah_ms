"""Build and validate annotated folio translations from reviewable Markdown.

The Hebrew column is always read from transcription/NNNx.md. Translation source
files contain only English, section metadata, optional Oxford parallels, an
apparatus, and notes. This keeps the corrected transcription authoritative.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, NavigableString


ROOT = Path(__file__).resolve().parent
TRANSCRIPTIONS = ROOT / "transcription"
TRANSLATIONS = ROOT / "translations"
MANIFEST_PATH = ROOT / "translation_manifest.json"
TEMPLATE_CSS = TRANSLATIONS / "template.css"

SECTION_RE = re.compile(
    r"^## Lines\s+(\d+)[-–](\d+)\s+\|\s+([a-z0-9-]+)\s+\|\s+(.+)$",
    flags=re.IGNORECASE,
)
NUMBERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")
NOTE_RE = re.compile(r"^\[\^(\d+)\]:\s*(.*?)(?:\s+\{source:\s*(.+)\})?$")
UNCERTAINTY_RE = re.compile(r"\S*\[\?\]")


class TranslationError(ValueError):
    """Raised for an invalid translation source or generated page."""


@dataclass
class OxfordBlock:
    hebrew: str
    meta: str
    url: str = ""


@dataclass
class Section:
    start: int
    end: int
    section_id: str
    title: str
    translations: dict[int, str] = field(default_factory=dict)
    oxford: list[OxfordBlock] = field(default_factory=list)


@dataclass
class Note:
    number: int
    text: str
    source: str = ""


@dataclass
class TranslationDocument:
    metadata: dict[str, str]
    sections: list[Section]
    apparatus_title: str = ""
    apparatus_markdown: str = ""
    notes: dict[int, Note] = field(default_factory=dict)

    @property
    def folio(self) -> str:
        return self.metadata["folio"].lower()

    @property
    def translations(self) -> dict[int, str]:
        merged: dict[int, str] = {}
        for section in self.sections:
            overlap = set(merged).intersection(section.translations)
            if overlap:
                raise TranslationError(f"duplicate translated lines: {sorted(overlap)}")
            merged.update(section.translations)
        return merged


def parse_front_matter(text: str, path: Path) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise TranslationError(f"{path}: expected opening --- front matter")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise TranslationError(f"{path}: missing closing --- front matter") from exc
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise TranslationError(f"{path}: invalid front matter line: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    if "folio" not in metadata:
        raise TranslationError(f"{path}: front matter requires folio")
    return metadata, lines[end + 1 :]


def parse_oxford(lines: list[str], start: int, path: Path) -> tuple[OxfordBlock, int]:
    fields: dict[str, str] = {}
    i = start + 1
    while i < len(lines) and lines[i].strip() != ":::":
        line = lines[i]
        if ":" not in line:
            raise TranslationError(f"{path}:{i + 1}: Oxford fields use key: value")
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()
        i += 1
    if i >= len(lines):
        raise TranslationError(f"{path}:{start + 1}: unclosed Oxford block")
    if not fields.get("hebrew") or not fields.get("meta"):
        raise TranslationError(f"{path}:{start + 1}: Oxford block needs hebrew and meta")
    return OxfordBlock(fields["hebrew"], fields["meta"], fields.get("url", "")), i


def parse_translation(path: Path) -> TranslationDocument:
    metadata, lines = parse_front_matter(path.read_text(encoding="utf-8-sig"), path)
    sections: list[Section] = []
    notes: dict[int, Note] = {}
    apparatus_title = ""
    apparatus_lines: list[str] = []
    mode = ""
    current: Section | None = None
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        section_match = SECTION_RE.match(line)
        if section_match:
            current = Section(
                start=int(section_match.group(1)),
                end=int(section_match.group(2)),
                section_id=section_match.group(3),
                title=section_match.group(4).strip(),
            )
            if current.start > current.end:
                raise TranslationError(f"{path}:{i + 1}: section range is reversed")
            sections.append(current)
            mode = "section"
        elif line.lower().startswith("## apparatus |"):
            apparatus_title = line.split("|", 1)[1].strip()
            mode = "apparatus"
            current = None
        elif line.lower() == "## notes":
            mode = "notes"
            current = None
        elif line == "::: oxford":
            if mode != "section" or current is None:
                raise TranslationError(f"{path}:{i + 1}: Oxford block must be inside a section")
            block, i = parse_oxford(lines, i, path)
            current.oxford.append(block)
        elif mode == "section" and line:
            numbered = NUMBERED_RE.match(raw)
            if not numbered:
                raise TranslationError(f"{path}:{i + 1}: expected a numbered translation line")
            number = int(numbered.group(1))
            if not current.start <= number <= current.end:
                raise TranslationError(
                    f"{path}:{i + 1}: line {number} is outside section "
                    f"{current.start}-{current.end}"
                )
            if number in current.translations:
                raise TranslationError(f"{path}:{i + 1}: duplicate line {number}")
            current.translations[number] = numbered.group(2).strip()
        elif mode == "apparatus":
            apparatus_lines.append(raw)
        elif mode == "notes" and line:
            note_match = NOTE_RE.match(line)
            if not note_match:
                raise TranslationError(f"{path}:{i + 1}: invalid note; use [^N]: text")
            number = int(note_match.group(1))
            notes[number] = Note(number, note_match.group(2).strip(), (note_match.group(3) or "").strip())
        elif line and not line.startswith("#"):
            raise TranslationError(f"{path}:{i + 1}: content appears before a recognized section")
        i += 1

    if not sections:
        raise TranslationError(f"{path}: no translation sections found")
    return TranslationDocument(
        metadata=metadata,
        sections=sections,
        apparatus_title=apparatus_title,
        apparatus_markdown="\n".join(apparatus_lines).strip(),
        notes=notes,
    )


def parse_transcription(path: Path) -> dict[int, str]:
    lines: dict[int, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        match = NUMBERED_RE.match(raw)
        if not match:
            continue
        number = int(match.group(1))
        if number in lines:
            raise TranslationError(f"{path}: duplicate transcription line {number}")
        lines[number] = match.group(2)
    if not lines:
        raise TranslationError(f"{path}: no numbered transcription lines found")
    expected = list(range(1, max(lines) + 1))
    if sorted(lines) != expected:
        raise TranslationError(f"{path}: transcription lines are not consecutive")
    return lines


def load_manifest() -> dict:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    folios = data.get("folios")
    if not isinstance(folios, list):
        raise TranslationError(f"{MANIFEST_PATH}: folios must be a list")
    seen: set[str] = set()
    for entry in folios:
        folio = str(entry.get("folio", "")).lower()
        if not re.fullmatch(r"\d+[ab]", folio):
            raise TranslationError(f"{MANIFEST_PATH}: invalid folio {folio!r}")
        if folio in seen:
            raise TranslationError(f"{MANIFEST_PATH}: duplicate folio {folio}")
        if entry.get("status") not in {"draft", "published"}:
            raise TranslationError(f"{MANIFEST_PATH}: {folio} needs draft or published status")
        entry["folio"] = folio
        entry.setdefault("page", f"translation_{folio}.html")
        seen.add(folio)
    return data


def save_manifest(data: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def render_markdown_inline(text: str, *, note_refs: bool = True) -> str:
    text = text.replace("??", "@@UNC@@")
    parts = text.split("@@UNC@@")
    if len(parts) % 2 == 0:
        raise TranslationError(f"unbalanced ?? uncertainty markers in: {text!r}")
    text = "".join(
        part if index % 2 == 0 else f'<span class="uncertain">{part}</span>'
        for index, part in enumerate(parts)
    )
    if note_refs:
        text = re.sub(
            r"\[\^(\d+)\]",
            lambda m: f'<sup id="r{m.group(1)}"><a href="#n{m.group(1)}">{m.group(1)}</a></sup>',
            text,
        )
    else:
        text = re.sub(r"\[\^(\d+)\]", "", text)
    rendered = markdown.markdown(text, extensions=["extra"], output_format="html5").strip()
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        rendered = rendered[3:-4]
    soup = BeautifulSoup(rendered, "html.parser")
    for strong in soup.find_all("strong"):
        strong["class"] = [*strong.get("class", []), "lemma"]
    for code in list(soup.find_all("code")):
        if re.search(r"[\u0590-\u05FF]", code.get_text()):
            span = soup.new_tag("span", attrs={"lang": "he", "dir": "rtl"})
            span.string = code.get_text()
            code.replace_with(span)
    return str(soup)


def render_hebrew(source: str) -> str:
    rendered = markdown.markdown(source, output_format="html5").strip()
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        rendered = rendered[3:-4]
    soup = BeautifulSoup(rendered, "html.parser")
    for strong in soup.find_all("strong"):
        strong["class"] = [*strong.get("class", []), "lemma"]
    for text_node in list(soup.find_all(string=UNCERTAINTY_RE)):
        pieces = UNCERTAINTY_RE.split(str(text_node))
        matches = UNCERTAINTY_RE.findall(str(text_node))
        replacement: list[object] = []
        for index, piece in enumerate(pieces):
            if piece:
                replacement.append(NavigableString(piece))
            if index < len(matches):
                span = soup.new_tag("span", attrs={"class": "uncertain"})
                span.string = matches[index]
                replacement.append(span)
        text_node.replace_with(*replacement)
    return str(soup)


def navigation_for(folio: str, manifest: dict) -> tuple[dict | None, dict | None]:
    entries = manifest["folios"]
    index = next((i for i, entry in enumerate(entries) if entry["folio"] == folio), None)
    if index is None:
        raise TranslationError(f"{folio} is not registered in {MANIFEST_PATH.name}")
    previous = next(
        (entry for entry in reversed(entries[:index]) if entry["status"] == "published"),
        None,
    )
    following = next(
        (entry for entry in entries[index + 1 :] if entry["status"] == "published"),
        None,
    )
    return previous, following


def nav_html(folio: str, manifest: dict) -> str:
    previous, following = navigation_for(folio, manifest)
    links: list[str] = []
    if previous:
        links.append(
            f'<a href="{html.escape(previous["page"])}">← Previous: fol. '
            f'{html.escape(previous["folio"])}</a>'
        )
    links.append('<a href="index.html">Transcription home</a>')
    if following:
        links.append(
            f'<a href="{html.escape(following["page"])}">Next: fol. '
            f'{html.escape(following["folio"])} →</a>'
        )
    return "".join(links)


def render_oxford(block: OxfordBlock) -> str:
    meta = render_markdown_inline(block.meta)
    if block.url:
        meta += f' <a href="{html.escape(block.url, quote=True)}">View region</a>'
    return (
        '      <div class="oxford-lemma"><strong>Oxford Great Parchment:</strong>'
        f'<p class="oxford-hebrew" lang="he" dir="rtl">{render_hebrew(block.hebrew)}</p>'
        f'<p class="oxford-meta">{meta}</p></div>'
    )


def render_section(
    section: Section,
    translations: dict[int, str],
    hebrew: dict[int, str],
    through: int,
    final: bool,
) -> str:
    numbers = [number for number in range(section.start, section.end + 1) if number <= through]
    if not numbers:
        return ""
    parts = [
        f'    <section class="section" id="{html.escape(section.section_id)}"><h2>'
        f'{html.escape(section.title)} · Lines {section.start}–{section.end}</h2>'
    ]
    parts.extend(render_oxford(block) for block in section.oxford)
    parts.append(
        '      <div class="parallel-header"><span>Translation</span><span>Line</span>'
        '<span>Hebrew transcription</span></div>'
    )
    for number in numbers:
        if number not in translations:
            raise TranslationError(f"missing English translation for line {number}")
        parts.append(
            '      <div class="line"><div class="translation">'
            f'{render_markdown_inline(translations[number], note_refs=final)}</div>'
            f'<div class="number">{number}</div><div class="source">'
            f'{render_hebrew(hebrew[number])}</div></div>'
        )
    parts.append("    </section>")
    return "\n".join(parts)


def render_notes(document: TranslationDocument) -> str:
    if not document.notes:
        return ""
    items: list[str] = []
    for number in sorted(document.notes):
        note = document.notes[number]
        rendered = render_markdown_inline(note.text, note_refs=False)
        source = f' <span class="source-note">{html.escape(note.source)}</span>' if note.source else ""
        items.append(
            f'      <li id="n{number}">{rendered}{source} '
            f'<a href="#r{number}">↩</a></li>'
        )
    return (
        '    <section class="footnotes"><h2>Notes</h2><ol>\n'
        + "\n".join(items)
        + "\n    </ol></section>"
    )


def render_apparatus(document: TranslationDocument) -> str:
    if not document.apparatus_markdown:
        return ""
    rendered = markdown.markdown(
        document.apparatus_markdown,
        extensions=["extra"],
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")
    for table in soup.find_all("table"):
        wrapper = soup.new_tag("div", attrs={"class": "table-wrap"})
        table.wrap(wrapper)
    return (
        f'    <section class="apparatus"><h2>{html.escape(document.apparatus_title or "Apparatus")}</h2>\n'
        f'      {soup}\n    </section>'
    )


def render_page(
    document: TranslationDocument,
    hebrew: dict[int, str],
    manifest: dict,
    through: int,
    final: bool,
) -> str:
    maximum = max(hebrew)
    if through < 1 or through > maximum:
        raise TranslationError(f"--through must be between 1 and {maximum}")
    translated = document.translations
    required = set(range(1, maximum + 1 if final else through + 1))
    missing = sorted(required.difference(translated))
    if missing:
        raise TranslationError(f"missing translated lines: {missing}")
    pending = sorted(number for number in required if translated[number].strip() == "[TODO]")
    if pending:
        raise TranslationError(f"translation still pending on lines: {pending}")
    extra = sorted(set(translated).difference(hebrew))
    if extra:
        raise TranslationError(f"translated lines absent from transcription: {extra}")
    note_refs = {int(value) for text in translated.values() for value in re.findall(r"\[\^(\d+)\]", text)}
    if final:
        undefined = sorted(note_refs.difference(document.notes))
        unreferenced = sorted(set(document.notes).difference(note_refs))
        if undefined:
            raise TranslationError(f"undefined notes: {undefined}")
        if unreferenced:
            raise TranslationError(f"unreferenced notes: {unreferenced}")

    sections = [
        render_section(section, translated, hebrew, through, final)
        for section in document.sections
    ]
    body_parts = [part for part in sections if part]
    if final:
        apparatus = render_apparatus(document)
        notes = render_notes(document)
        if apparatus:
            body_parts.append(apparatus)
        if notes:
            body_parts.append(notes)
    body = "\n\n".join(body_parts)
    folio = document.folio
    description = document.metadata.get(
        "description",
        f"Parallel Hebrew-English working edition of JTS MS 2367, folio {folio}.",
    )
    editorial = document.metadata.get(
        "editorial",
        "This provisional translation follows the JTS manuscript transcription line by line.",
    )
    footer_stage = "" if final else f" · Lines 1–{through} drafted"
    css = TEMPLATE_CSS.read_text(encoding="utf-8").strip()
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <title>JTS 2367, fol. {folio} — Hebrew–English Edition</title>
  <style>
    {css}
  </style>
</head>
<body>
  <header class="masthead"><div class="masthead-inner"><p class="eyebrow">Parallel Hebrew–English working edition</p><h1>JTS MS 2367, fol. {folio}</h1><p class="subtitle" dir="auto">פרוש היריעה הגדולה — Perush Ha-Yeri‘ah Ha-Gedolah</p><nav class="page-nav" aria-label="Translation navigation">{nav_html(folio, manifest)}</nav></div></header>
  <aside class="edition-note"><p><strong>Editorial statement.</strong> {html.escape(editorial)}</p><p class="key"><span class="uncertain">Dotted underline</span> marks uncertain readings or renderings; bold maroon marks lemma text. The Hebrew is generated directly from the corrected transcription and retains its lineation and editorial uncertainty.</p></aside>
  <main>
{body}
  </main>
  <footer>Provisional translation for scholarly review · Folio {folio}{footer_stage}<br>Courtesy of the Library of the Jewish Theological Seminary, The National Library of Israel. “Ktiv” Project, The National Library of Israel.</footer>
</body></html>
'''


class TextOnlyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fragments: list[str] = []

    def handle_data(self, data: str) -> None:
        self.fragments.append(data)


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.sources: list[str] = []
        self.numbers: list[int] = []
        self.oxford: list[dict[str, str]] = []
        self._capture_source = False
        self._capture_number = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        classes = values.get("class", "").split()
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if "source" in classes:
            self._capture_source = True
            self._buffer = []
        if "number" in classes:
            self._capture_number = True
            self._buffer = []
        if "oxford-hebrew" in classes:
            self.oxford.append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._capture_source:
            self.sources.append("".join(self._buffer))
            self._capture_source = False
            self._buffer = []
        elif tag == "div" and self._capture_number:
            value = "".join(self._buffer).strip()
            if value:
                self.numbers.append(int(value))
            self._capture_number = False
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture_source or self._capture_number:
            self._buffer.append(data)


def plain_source(source: str) -> str:
    parser = TextOnlyParser()
    parser.feed(render_hebrew(source))
    parser.close()
    return "".join(parser.fragments)


def validate_html(content: str, hebrew: dict[int, str], through: int, final: bool) -> list[str]:
    errors: list[str] = []
    parser = PageAudit()
    parser.feed(content)
    parser.close()
    expected_numbers = list(range(1, through + 1))
    if parser.numbers != expected_numbers:
        errors.append(f"line numbers are {parser.numbers}, expected {expected_numbers}")
    expected_sources = [plain_source(hebrew[number]) for number in expected_numbers]
    if parser.sources != expected_sources:
        mismatch = [
            number
            for number, (actual, expected) in enumerate(zip(parser.sources, expected_sources), 1)
            if actual != expected
        ]
        errors.append(f"Hebrew differs from transcription on lines {mismatch}")
    if len(parser.ids) != len(set(parser.ids)):
        errors.append("HTML IDs are not unique")
    known_ids = set(parser.ids)
    for href in parser.hrefs:
        if href.startswith("#") and href[1:] not in known_ids:
            errors.append(f"broken fragment link: {href}")
    for attrs in parser.oxford:
        if attrs.get("lang") != "he" or attrs.get("dir") != "rtl":
            errors.append("Oxford Hebrew block lacks lang=he dir=rtl")
    for href in parser.hrefs:
        if href.startswith(("#", "http://", "https://")):
            continue
        target = ROOT / href.split("#", 1)[0]
        if not target.exists():
            errors.append(f"missing local link target: {href}")
    if final and through != max(hebrew):
        errors.append("final page does not contain every transcription line")
    return errors


def validate_page(page: Path, hebrew: dict[int, str], through: int, final: bool) -> list[str]:
    return validate_html(page.read_text(encoding="utf-8"), hebrew, through, final)


def resolve_transcription(folio: str) -> Path:
    candidates = [TRANSCRIPTIONS / f"{folio}.md", TRANSCRIPTIONS / f"0{folio}.md"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise TranslationError(f"no transcription found for folio {folio}")


def build_folio(folio: str, *, through: int | None, final: bool) -> Path:
    source_path = TRANSLATIONS / f"{folio}.md"
    page_path = ROOT / f"translation_{folio}.html"
    document = parse_translation(source_path)
    if document.folio != folio:
        raise TranslationError(f"{source_path}: folio metadata is {document.folio}, expected {folio}")
    hebrew = parse_transcription(resolve_transcription(folio))
    limit = max(hebrew) if final else through
    if limit is None:
        raise TranslationError("choose --through N or --final")
    manifest = load_manifest()
    rendered = render_page(document, hebrew, manifest, limit, final)
    page_path.write_text(rendered, encoding="utf-8", newline="\n")
    errors = validate_page(page_path, hebrew, limit, final)
    if errors:
        raise TranslationError("; ".join(errors))
    print(f"Built {page_path.name}: lines 1-{limit}{' (final)' if final else ''}")
    return page_path


def initialize_folio(folio: str) -> None:
    source_path = TRANSLATIONS / f"{folio}.md"
    if source_path.exists():
        raise TranslationError(f"{source_path} already exists")
    hebrew = parse_transcription(resolve_transcription(folio))
    TRANSLATIONS.mkdir(exist_ok=True)
    placeholders = "\n".join(f"{number}. [TODO]" for number in hebrew)
    source_path.write_text(
        f"""---
folio: {folio}
description: Parallel Hebrew-English working edition of JTS MS 2367, folio {folio}.
editorial: This provisional translation follows the JTS manuscript transcription line by line.
---

## Lines 1–{max(hebrew)} | working-section | Working section
{placeholders}

## Notes
""",
        encoding="utf-8",
        newline="\n",
    )
    manifest = load_manifest()
    if not any(entry["folio"] == folio for entry in manifest["folios"]):
        manifest["folios"].append(
            {"folio": folio, "page": f"translation_{folio}.html", "status": "draft"}
        )
        save_manifest(manifest)
    print(f"Initialized {source_path.relative_to(ROOT)} and registered {folio} as draft")


def publish_folio(folio: str) -> None:
    build_folio(folio, through=None, final=True)
    manifest = load_manifest()
    entry = next((item for item in manifest["folios"] if item["folio"] == folio), None)
    if entry is None:
        raise TranslationError(f"{folio} is not registered")
    entry["status"] = "published"
    save_manifest(manifest)
    # Rebuild generator-managed pages so neighboring navigation stays current.
    for item in manifest["folios"]:
        source = TRANSLATIONS / f'{item["folio"]}.md'
        if source.exists() and item["status"] == "published" and item["folio"] != folio:
            build_folio(item["folio"], through=None, final=True)
    subprocess.run([sys.executable, str(ROOT / "build_site.py")], cwd=ROOT, check=True)
    print(f"Published {folio} in the manifest and rebuilt navigation/index")


def check_all() -> None:
    manifest = load_manifest()
    checked = 0
    drafts = 0
    for entry in manifest["folios"]:
        folio = entry["folio"]
        source = TRANSLATIONS / f"{folio}.md"
        page = ROOT / entry["page"]
        if not source.exists():
            continue
        document = parse_translation(source)
        hebrew = parse_transcription(resolve_transcription(folio))
        if entry["status"] == "draft":
            extra = sorted(set(document.translations).difference(hebrew))
            if extra:
                raise TranslationError(f"{source}: lines absent from transcription: {extra}")
            drafts += 1
            continue
        maximum = max(hebrew)
        if set(document.translations) != set(hebrew):
            raise TranslationError(f"{source}: translation coverage does not match transcription")
        expected = render_page(document, hebrew, manifest, maximum, True)
        actual = page.read_text(encoding="utf-8")
        if actual != expected:
            raise TranslationError(f"{page}: generated HTML is stale; rebuild with --final")
        errors = validate_page(page, hebrew, maximum, True)
        if errors:
            raise TranslationError(f"{page}: {'; '.join(errors)}")
        checked += 1
    if checked == 0:
        raise TranslationError("no generator-managed translations found")
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    print(f"Validated {checked} published page(s) and parsed {drafts} draft source(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folio", nargs="?", help="folio such as 080a or 80a")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--init", action="store_true", help="create a draft translation source")
    action.add_argument("--through", type=int, metavar="LINE", help="build a valid partial page")
    action.add_argument("--final", action="store_true", help="build and strictly validate the complete page")
    action.add_argument("--publish", action="store_true", help="finalize, publish in manifest, and rebuild navigation")
    action.add_argument("--check", action="store_true", help="validate all generator-managed pages")
    args = parser.parse_args()
    try:
        if args.check:
            check_all()
            return 0
        if not args.folio:
            parser.error("folio is required unless --check is used")
        folio = args.folio.lower().lstrip("0")
        if not re.fullmatch(r"\d+[ab]", folio):
            parser.error("folio must look like 080a or 80a")
        if args.init:
            initialize_folio(folio)
        elif args.publish:
            publish_folio(folio)
        else:
            build_folio(folio, through=args.through, final=args.final)
        return 0
    except (OSError, TranslationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
