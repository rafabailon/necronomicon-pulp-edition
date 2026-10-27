# Necronomicon Pulp Edition

A bilingual, original pulp-horror book project laid out in LaTeX. The English and Spanish editions share a typographic style package while keeping their manuscripts separate. Covers, decorative rules, and barcode illustrations are drawn locally with TikZ; no external image assets are required.

## Editions

- English master: `en/necronomicon-pulp.tex`
- Spanish master: `es/necronomicon-pulp.tex`

Both editions use `scrbook`, XeLaTeX, `fontspec`, and `polyglossia`. Each master file assembles separate cover, credits, contents, chapter, and back-cover files. The ten chapter fragments are ordered as two gazette pieces, two story chapters, two transcript chapters, two field-note chapters, and two appendix chapters.

### Choose a language

Compile the English master to produce the English edition, or the Spanish master for the Spanish edition. The language is set in each master using `polyglossia`; there is no runtime language selector.

```sh
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error en/necronomicon-pulp.tex
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error es/necronomicon-pulp.tex
```

Run the command twice for the selected edition to populate its table of contents and cross-references.

### Using Make

A `Makefile` is provided for convenience:

```sh
make en          # Build English edition
make es          # Build Spanish edition
make all         # Build both editions and samples
make samples     # Build two-chapter layout proofs
make test        # Run all tests
make lint        # Run structural lint
make clean       # Clean build artifacts
```

### Book layout and chapter files

```text
en/ or es/
  necronomicon-pulp.tex       Edition master: language and assembly order
  front-matter/
    cover.tex                 Front cover
    credits.tex               Credits, imprint, and fictional notice
    contents.tex              Table of contents
  chapters/
    01-gazette-dispatch.tex
    ...
    10-appendix-readers-caution.tex
  back-matter/
    back-cover.tex             Back-cover copy and barcode
styles/pulp-book.sty           Shared typography and layout components
samples/
  en-two-chapters.tex          English layout proof: story chapters 3 and 4
  es-two-chapters.tex          Spanish layout proof: story chapters 3 and 4
  previews/
    en-two-chapters.pdf        Compiled English proof
    es-two-chapters.pdf        Compiled Spanish proof
scripts/lint_book.py           Structural checks and optional XeLaTeX compilation
tests/test_book.py             Python unittest suite
Makefile                       Build automation
```

Each `chapters/*.tex` file is one complete, independently editable chapter fragment. To copy or move one, copy the whole file and add or change its `\input{...}` line in the appropriate edition master. Chapter fragments use the shared `\ChapterPage` and style macros, so do not copy the document preamble into a chapter file. Cover, credits, contents, and back cover can be edited independently in their named files.

Compile the two-chapter layout proofs without building the full books:

```sh
mkdir -p /tmp/necronomicon-en-sample /tmp/necronomicon-es-sample
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/necronomicon-en-sample samples/en-two-chapters.tex
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/necronomicon-es-sample samples/es-two-chapters.tex
```

The sample files include the actual English or Spanish cover, chapters 3 and 4, and matching back cover. They are layout previews, not alternate masters.
Prebuilt previews are provided as PDFs in `samples/previews/`; regenerate them after changing the source with the commands below.

```sh
mkdir -p samples/previews
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error -output-directory=samples/previews samples/en-two-chapters.tex
TEXINPUTS="styles:" xelatex -interaction=nonstopmode -halt-on-error -output-directory=samples/previews samples/es-two-chapters.tex
```

## Requirements

- XeLaTeX
- TeX Live packages: KOMA-Script, fontspec, polyglossia, fancyhdr, multicol, lettrine, tcolorbox, TikZ/PGF, booktabs, tabularx, microtype, hyperref, and TeX Gyre fonts
- Python 3.10 or newer for source linting and tests

On Debian/Ubuntu, the full TeX Live distribution provides the packages used here:

```bash
sudo apt install texlive-xetex texlive-latex-extra texlive-fonts-recommended
```

## Tests and source lint

Run standard-library tests, including actual XeLaTeX compilation of both full books and both two-chapter samples:

```bash
python3 -m unittest discover -s tests -v
```

Run the lightweight source lint without compiling:

```bash
python3 scripts/lint_book.py
```

Run structural lint and compile both editions in temporary directories:

```bash
python3 scripts/lint_book.py --compile
```

The `--compile` mode builds both full editions and both two-chapter layout proofs in temporary directories.

The test and lint scripts do not install packages. Compiled PDFs and auxiliary files are generated in temporary directories during automated tests.

## Project structure

```text
en/                        English master, front matter, 10 chapters, back cover
es/                        Spanish master, front matter, 10 chapters, back cover
samples/                   English and Spanish two-chapter layout proofs
styles/pulp-book.sty       Shared page design, typography, and TikZ illustrations
scripts/lint_book.py       Structural checks and optional XeLaTeX compilation
tests/test_book.py         Python unittest suite
Makefile                   Build automation
```

## Credits and fictional notices

The author, publisher, ISBN, and 1928 imprint are fictional elements of the pulp design. The story and its characters are original. No external book text or image is included.

## License

MIT. See [LICENSE](LICENSE).
