# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# English documentation
html-en:
	@$(SPHINXBUILD) -b html -c en "en" "$(BUILDDIR)/en" $(SPHINXOPTS) $(O)

# Chinese documentation
html-zh:
	@$(SPHINXBUILD) -b html -c zh "zh" "$(BUILDDIR)/zh" $(SPHINXOPTS) $(O)

# Build both versions
html-all: html-en html-zh

# Clean build directory
clean:
	rm -rf $(BUILDDIR)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)