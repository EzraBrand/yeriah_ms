"""Build the GitHub Pages reader from the combined transcription Markdown."""

from __future__ import annotations

import html
import re
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription" / "combined_transcriptions.md"
OUTPUT = ROOT / "index.html"


def slug_for(title: str) -> str:
    match = re.search(r"fol\.\s*(\d+[ab])", title, flags=re.IGNORECASE)
    return f"folio-{match.group(1).lower()}" if match else "transcription"


def apply_text_direction(soup: BeautifulSoup) -> None:
    """Mark Hebrew-dominant prose RTL without reversing English apparatus."""
    for node in soup.find_all(["p", "li", "blockquote", "h1", "h2", "h3"]):
        text = node.get_text(" ", strip=True)
        hebrew = len(re.findall(r"[\u0590-\u05FF]", text))
        latin = len(re.findall(r"[A-Za-z]", text))
        if hebrew > latin:
            node["dir"] = "rtl"
            node["lang"] = "he"
            node["class"] = [*node.get("class", []), "hebrew-text"]
        else:
            node["dir"] = "ltr"


def collapse_notes(soup: BeautifulSoup) -> None:
    notes_heading = next(
        (h for h in soup.find_all("h2") if h.get_text(" ", strip=True).lower() == "notes"),
        None,
    )
    if notes_heading is None:
        return
    details = soup.new_tag("details", attrs={"class": "notes"})
    summary = soup.new_tag("summary")
    summary.string = "Editorial notes"
    details.append(summary)
    sibling = notes_heading.next_sibling
    notes_heading.replace_with(details)
    while sibling is not None:
        following = sibling.next_sibling
        details.append(sibling.extract())
        sibling = following


def build() -> None:
    source = SOURCE.read_text(encoding="utf-8-sig")
    chunks = [chunk.strip() for chunk in re.split(r"(?m)^---\s*$", source) if chunk.strip()]
    if chunks and chunks[0].startswith("# Combined Transcriptions"):
        chunks[0] = re.sub(r"^# Combined Transcriptions\s*", "", chunks[0], count=1).strip()

    sections: list[str] = []
    navigation: list[tuple[str, str]] = []
    for chunk in chunks:
        heading = re.search(r"(?m)^#\s+(.+)$", chunk)
        if not heading:
            continue
        title = heading.group(1).strip()
        section_id = slug_for(title)
        label_match = re.search(r"fol\.\s*(\d+[ab])", title, flags=re.IGNORECASE)
        label = label_match.group(1) if label_match else title
        navigation.append((section_id, label))

        rendered = markdown.markdown(
            chunk,
            extensions=["extra", "sane_lists", "smarty"],
            output_format="html5",
        )
        soup = BeautifulSoup(rendered, "html.parser")
        apply_text_direction(soup)
        collapse_notes(soup)
        sections.append(f'<section class="folio" id="{section_id}">{soup}</section>')

    nav_html = "\n".join(
        f'<a href="#{section_id}">{html.escape(label)}</a>' for section_id, label in navigation
    )
    sections_html = "\n".join(sections)
    OUTPUT.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="A working transcription of JTS MS 2367, Perush Ha-Yeriah Ha-Gedolah.">
  <title>JTS 2367 — Combined Transcription</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div>
        <p class="eyebrow">JTS MS 2367</p>
        <h1>Combined Transcription</h1>
        <p class="subtitle" dir="auto">פרוש היריעה הגדולה — working transcription</p>
      </div>
      <a class="repo-link" href="https://github.com/EzraBrand/yeriah_ms">View source on GitHub</a>
    </div>
  </header>

  <nav class="project-nav" aria-label="Project pages">
    <strong>Read the annotated translation:</strong>
    <a href="translation_76b.html">Folio 76b</a>
    <a href="translation_77a.html">Folio 77a</a>
    <a href="translation_77b.html">Folio 77b</a>
    <a href="research_state_of_the_field.md">Research survey</a>
    <a href="https://github.com/EzraBrand/yeriah_ms#reading-reuven-tzarfatis-commentary-on-the-great-parchment">About the project</a>
  </nav>

  <div class="reader-tools">
    <nav class="folio-nav" aria-label="Folio navigation">
      {nav_html}
    </nav>
    <label class="search-label" for="folio-search">
      <span>Search this transcription</span>
      <input id="folio-search" type="search" placeholder="Hebrew or English…" autocomplete="off">
    </label>
    <p id="search-status" class="search-status" aria-live="polite"></p>
  </div>

  <main id="transcription" class="transcription">
    {sections_html}
    <p id="no-results" class="no-results" hidden>No matching folios found.</p>
  </main>

  <footer>
    <p>Draft scholarly transcription. Brackets and question marks preserve editorial uncertainty.</p>
  </footer>

  <script>
    const search = document.querySelector('#folio-search');
    const folios = [...document.querySelectorAll('.folio')];
    const status = document.querySelector('#search-status');
    const noResults = document.querySelector('#no-results');
    search.addEventListener('input', () => {{
      const query = search.value.trim().toLocaleLowerCase();
      let visible = 0;
      for (const folio of folios) {{
        const match = !query || folio.textContent.toLocaleLowerCase().includes(query);
        folio.hidden = !match;
        if (match) visible += 1;
      }}
      noResults.hidden = visible !== 0;
      status.textContent = query ? `${{visible}} of ${{folios.length}} folios shown` : '';
    }});
  </script>
</body>
</html>
""",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Built {OUTPUT} with {len(sections)} folios")


if __name__ == "__main__":
    build()
