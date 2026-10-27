#!/usr/bin/env python3
"""Build all editions and samples into the build/ directory."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"

EDITIONS = {
    "en": ROOT / "en" / "necronomicon-pulp.tex",
    "es": ROOT / "es" / "necronomicon-pulp.tex",
}
SAMPLES = {
    "en": ROOT / "samples" / "en-two-chapters.tex",
    "es": ROOT / "samples" / "es-two-chapters.tex",
}


def build(target: Path, outdir: Path, runs: int = 2) -> bool:
    outdir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    existing = env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = f"{ROOT / 'styles'}:{existing}"
    engine = shutil.which("xelatex")
    if not engine:
        print("xelatex not found", file=sys.stderr)
        return False
    for i in range(runs):
        proc = subprocess.run(
            [engine, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={outdir}", str(target)],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            print(proc.stdout[-2000:], file=sys.stderr)
            print(proc.stderr[-1000:], file=sys.stderr)
            return False
    pdf = outdir / f"{target.stem}.pdf"
    if not pdf.exists() or pdf.stat().st_size == 0:
        print(f"Missing/empty PDF: {pdf}", file=sys.stderr)
        return False
    print(f"Built: {pdf}")
    return True


def main() -> int:
    ok = True
    for lang, path in EDITIONS.items():
        ok = build(path, BUILD / lang, runs=2) and ok
    for lang, path in SAMPLES.items():
        ok = build(path, BUILD / "samples", runs=1) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
