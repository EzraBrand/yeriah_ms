from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_translation as bt
import build_site


class TranslationGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = bt.parse_translation(bt.TRANSLATIONS / "79b.md")
        cls.hebrew = bt.parse_transcription(bt.resolve_transcription("79b"))
        cls.manifest = bt.load_manifest()

    def validate_rendered(self, rendered: str, through: int, final: bool) -> list[str]:
        return bt.validate_html(rendered, self.hebrew, through, final)

    def test_79b_source_has_complete_line_coverage(self) -> None:
        self.assertEqual(sorted(self.document.translations), list(range(1, 46)))
        self.assertEqual(sorted(self.hebrew), list(range(1, 46)))

    def test_partial_stage_is_valid_and_omits_final_matter(self) -> None:
        rendered = bt.render_page(self.document, self.hebrew, self.manifest, 16, False)
        self.assertEqual(self.validate_rendered(rendered, 16, False), [])
        self.assertNotIn('class="apparatus"', rendered)
        self.assertNotIn('class="footnotes"', rendered)
        self.assertIn("Lines 1–16 drafted", rendered)

    def test_final_page_is_valid_and_preserves_all_hebrew(self) -> None:
        rendered = bt.render_page(self.document, self.hebrew, self.manifest, 45, True)
        self.assertEqual(self.validate_rendered(rendered, 45, True), [])
        self.assertIn('class="apparatus"', rendered)
        self.assertIn('class="footnotes"', rendered)

    def test_missing_translation_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        del document.sections[0].translations[1]
        with self.assertRaisesRegex(bt.TranslationError, "missing translated lines"):
            bt.render_page(document, self.hebrew, self.manifest, 16, False)

    def test_oxford_block_has_required_rtl_attributes(self) -> None:
        block = bt.OxfordBlock("ועל כן", "A short comparison.", "https://example.org/region")
        rendered = bt.render_oxford(block)
        self.assertIn('class="oxford-hebrew" lang="he" dir="rtl"', rendered)

    def test_draft_is_excluded_from_reader_navigation(self) -> None:
        data = {
            "folios": [
                {"folio": "79b", "page": "translation_79b.html", "status": "published"},
                {"folio": "80a", "page": "translation_80a.html", "status": "draft"},
            ]
        }
        rendered = build_site.build_translation_navigation(data)
        self.assertIn("translation_79b.html", rendered)
        self.assertNotIn("translation_80a.html", rendered)


if __name__ == "__main__":
    unittest.main()
