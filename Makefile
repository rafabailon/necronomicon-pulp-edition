# Necronomicon Pulp Edition - Build System

TEXINPUTS := styles:
LATEX := xelatex
LATEXFLAGS := -interaction=nonstopmode -halt-on-error

.PHONY: all en es samples test lint clean distclean help

all: en es samples

en:
	@mkdir -p build/en
	$(LATEX) $(LATEXFLAGS) -output-directory=build/en en/necronomicon-pulp.tex
	$(LATEX) $(LATEXFLAGS) -output-directory=build/en en/necronomicon-pulp.tex

es:
	@mkdir -p build/es
	$(LATEX) $(LATEXFLAGS) -output-directory=build/es es/necronomicon-pulp.tex
	$(LATEX) $(LATEXFLAGS) -output-directory=build/es es/necronomicon-pulp.tex

samples:
	@mkdir -p build/samples
	$(LATEX) $(LATEXFLAGS) -output-directory=build/samples samples/en-two-chapters.tex
	$(LATEX) $(LATEXFLAGS) -output-directory=build/samples samples/es-two-chapters.tex

test:
	python3 -m unittest discover -s tests -v

lint:
	python3 scripts/lint_book.py

lint-compile:
	python3 scripts/lint_book.py --compile

clean:
	rm -rf build
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" \
		-o -name "*.xdv" -o -name "*.synctex.gz" -o -name "*.fls" -o -name "*.fdb_latexmk" | \
		xargs -r rm -f

distclean: clean
	rm -f en/*.pdf es/*.pdf samples/*.pdf

help:
	@echo "Necronomicon Pulp Edition - Available targets:"
	@echo "  make all        - Build English and Spanish editions plus samples"
	@echo "  make en         - Build English edition"
	@echo "  make es         - Build Spanish edition"
	@echo "  make samples    - Build two-chapter samples"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run structural lint checks"
	@echo "  make lint-compile - Run lint with compilation checks"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make distclean  - Remove all generated PDFs"
