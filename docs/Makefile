# docs/Makefile

# Default target: build HTML docs
.PHONY: help html clean linkcheck serve api

SPHINXBUILD = sphinx-build
SOURCEDIR = .
BUILDDIR = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)"
	@rm -rf "$(BUILDDIR)"

linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" -W --keep-going

# Build autosummary stubs before HTML (optional convenience)
api:
	python3 -c "import pathlib; p=pathlib.Path('_autosummary'); p.mkdir(exist_ok=True)"
	@echo "API directory created. Use 'make html' to build documentation with API references."

# Local autoreload dev server (requires sphinx-autobuild)
serve:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" \
		--watch ../dictutils \
		--open-browser \
		--port 8010

