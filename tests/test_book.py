from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lint_book import EDITIONS, compile_edition, compile_sample, validate_source  # noqa: E402


class BookSourceTests(unittest.TestCase):
    def test_both_editions_have_required_book_structures(self):
        for language, config in EDITIONS.items():
            with self.subTest(language=language):
                self.assertEqual(validate_source(language, config), [])

    def test_shared_style_defines_requested_typography_and_art(self):
        style = (ROOT / "styles" / "pulp-book.sty").read_text(encoding="utf-8")
        for marker in (
            r"\RequirePackage{fontspec}",
            r"\RequirePackage{fancyhdr}",
            r"\RequirePackage{lettrine}",
            r"\RequirePackage{multicol}",
            r"\RequirePackage[most]{tcolorbox}",
            r"\addcontentsline{toc}{chapter}{#2}",
            r"\newcommand{\PulpCoverArt}[1]",
            r"\newcommand{\PulpBarcode}",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, style)

    def test_both_full_editions_compile_with_xelatex(self):
        for language, config in EDITIONS.items():
            with self.subTest(language=language):
                self.assertEqual(compile_edition(language, config, "xelatex"), [])

    def test_two_chapter_layout_samples_compile_in_both_languages(self):
        for language in EDITIONS:
            with self.subTest(language=language):
                self.assertEqual(compile_sample(language, "xelatex"), [])


if __name__ == "__main__":
    unittest.main()
