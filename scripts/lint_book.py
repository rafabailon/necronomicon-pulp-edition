#!/usr/bin/env python3
"""Validate the bilingual LaTeX sources and optionally compile both editions."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_COUNTS: dict[str, int] = {}
EDITIONS = {
    "en": {
        "path": ROOT / "en" / "necronomicon-pulp.tex",
        "language": r"\setdefaultlanguage{english}",
        "chapter_count": 10,
    },
    "es": {
        "path": ROOT / "es" / "necronomicon-pulp.tex",
        "language": r"\setdefaultlanguage{spanish}",
        "chapter_count": 10,
    },
}
SAMPLES = {
    "en": ROOT / "samples" / "en-two-chapters.tex",
    "es": ROOT / "samples" / "es-two-chapters.tex",
}
MASTER_MARKERS = (
    r"\documentclass[11pt,twoside,openany]{scrbook}",
    r"\usepackage{polyglossia}",
    r"\usepackage{pulp-book}",
    r"\frontmatter",
    r"\mainmatter",
    r"\backmatter",
    r"\end{document}",
)


def validate_source(language: str, config: dict[str, object]) -> list[str]:
    path = config["path"]
    assert isinstance(path, Path)
    source = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if config["language"] not in source:
        errors.append(f"{path.relative_to(ROOT)}: wrong language configuration")
    for marker in MASTER_MARKERS:
        if marker not in source:
            errors.append(f"{path.relative_to(ROOT)}: missing required marker {marker}")
    language_root = ROOT / language
    chapter_files = sorted((language_root / "chapters").glob("*.tex"))
    if len(chapter_files) != int(config["chapter_count"]):
        errors.append(
            f"{language}/chapters: expected {config['chapter_count']} separate chapters, "
            f"found {len(chapter_files)}"
        )
    chapter_sources = [chapter.read_text(encoding="utf-8") for chapter in chapter_files]
    if any(not re.search(r"(?m)^\\ChapterPage\{", chapter) for chapter in chapter_sources):
        errors.append(f"{language}/chapters: each chapter must start with a ChapterPage heading.")
    if len(re.findall(r"\\input\{" + re.escape(language) + r"/chapters/", source)) != len(
        chapter_files
    ):
        errors.append(f"{path.relative_to(ROOT)}: master file must include every chapter exactly once.")
    required_parts = (
        language_root / "front-matter" / "cover.tex",
        language_root / "front-matter" / "credits.tex",
        language_root / "front-matter" / "contents.tex",
        language_root / "back-matter" / "back-cover.tex",
    )
    for part in required_parts:
        if not part.is_file():
            errors.append(f"{part.relative_to(ROOT)}: required book component is missing.")
        elif rf"\input{{{part.relative_to(ROOT).with_suffix('')}}}" not in source:
            errors.append(f"{path.relative_to(ROOT)}: does not include {part.relative_to(ROOT)}.")
    cover_path = language_root / "front-matter" / "cover.tex"
    if cover_path.is_file():
        cover = cover_path.read_text(encoding="utf-8")
        cover_slogan = (
            r"\PulpCoverArt{A TALE FROM THE SUNKEN COAST}"
            if language == "en"
            else r"\PulpCoverArt{UN RELATO DE LA COSTA SUMERGIDA}"
        )
        if cover_slogan not in cover:
            errors.append(f"{cover_path.relative_to(ROOT)}: cover-art caption is not localized.")
    combined = "\n".join(
        [
            source,
            *(part.read_text(encoding="utf-8") for part in required_parts if part.is_file()),
            *chapter_sources,
        ]
    )
    for marker in (
        r"\tableofcontents",
        r"\begin{multicols}{2}",
        r"\lettrine",
        r"\begin{quote}",
        r"\begin{fieldnote}",
        r"\begin{tabularx}",
        r"\PulpCoverArt",
        r"\PulpBarcode",
    ):
        if marker not in combined:
            errors.append(f"{language}: required book-layout marker is missing: {marker}")
    if r"\includegraphics" in combined:
        errors.append(
            f"{language}: external image references are not allowed; use built-in TikZ art"
        )
    back_cover = (language_root / "back-matter" / "back-cover.tex")
    back_cover_text = back_cover.read_text(encoding="utf-8") if back_cover.is_file() else ""
    if language == "es" and "¡EL HORROR BAJO LAS OLAS!" not in back_cover_text:
        errors.append("Spanish edition is missing localized back-cover copy.")
    if language == "en" and "THE HORROR BENEATH THE WAVES!" not in back_cover_text:
        errors.append("English edition is missing localized back-cover copy.")
    sample = SAMPLES[language]
    if not sample.is_file():
        errors.append(f"samples/{language}-two-chapters.tex is missing.")
    else:
        sample_source = sample.read_text(encoding="utf-8")
        sample_chapters = re.findall(
            r"\\input\{" + re.escape(language) + r"/chapters/([^}]+)\}", sample_source
        )
        expected_chapters = ["03-story-chart", "04-story-cellar-door"]
        if sample_chapters != expected_chapters:
            errors.append(
                f"samples/{language}-two-chapters.tex must include the two story chapters in order."
            )
        for component in ("front-matter/cover", "back-matter/back-cover"):
            if rf"\input{{{language}/{component}}}" not in sample_source:
                errors.append(
                    f"samples/{language}-two-chapters.tex must include {component}."
                )
    return errors


def compile_document(
    language: str, path: Path, engine: str, *, runs: int, minimum_pages: int
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix=f"necronomicon-{language}-") as temp_dir:
        environment = os.environ.copy()
        existing_texinputs = environment.get("TEXINPUTS", "")
        environment["TEXINPUTS"] = f"{ROOT / 'styles'}:{existing_texinputs}"
        for _ in range(runs):
            process = subprocess.run(
                [
                    engine,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    f"-output-directory={temp_dir}",
                    str(path),
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            if process.returncode:
                return [
                    f"{language} XeLaTeX compilation failed:\n"
                    f"{process.stdout[-4000:]}\n{process.stderr[-2000:]}"
                ]
        pdf_path = Path(temp_dir) / f"{path.stem}.pdf"
        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            return [f"{language} edition did not produce a non-empty PDF."]
        pdfinfo = shutil.which("pdfinfo")
        if pdfinfo:
            details = subprocess.run(
                [pdfinfo, str(pdf_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            match = re.search(r"^Pages:\s+(\d+)\s*$", details.stdout, re.MULTILINE)
            if not match or int(match.group(1)) < minimum_pages:
                return [f"{path.relative_to(ROOT)} produced fewer than {minimum_pages} pages."]
            if path == EDITIONS[language]["path"]:
                PAGE_COUNTS[language] = int(match.group(1))
        return []


def compile_edition(language: str, config: dict[str, object], engine: str) -> list[str]:
    path = config["path"]
    assert isinstance(path, Path)
    return compile_document(language, path, engine, runs=2, minimum_pages=10)


def compile_sample(language: str, engine: str) -> list[str]:
    return compile_document(language, SAMPLES[language], engine, runs=1, minimum_pages=3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile both language editions with XeLaTeX into temporary directories.",
    )
    args = parser.parse_args()
    errors: list[str] = []
    for language, config in EDITIONS.items():
        errors.extend(validate_source(language, config))
    if args.compile:
        engine = shutil.which("xelatex")
        if not engine:
            errors.append("XeLaTeX is required for --compile but was not found.")
        else:
            for language, config in EDITIONS.items():
                errors.extend(compile_edition(language, config, engine))
                errors.extend(compile_sample(language, engine))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    status = "source and XeLaTeX compilation" if args.compile else "source"
    print(f"Book {status} checks passed for English and Spanish editions.")
    if args.compile:
        for language, count in PAGE_COUNTS.items():
            print(f"  {language}: {count} PDF pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
