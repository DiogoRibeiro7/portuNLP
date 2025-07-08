#!/usr/bin/env bash
# Setup script for portuNLP
set -euo pipefail

# Install Python dependencies using Poetry
if command -v poetry >/dev/null 2>&1; then
    poetry install
else
    echo "Poetry is not installed. Please install Poetry to manage Python dependencies." >&2
fi

# Install R and LaTeX if missing, then package dependencies
if ! command -v R >/dev/null 2>&1; then
    echo "R is not installed. Installing via apt-get..." >&2
    apt-get update
    apt-get install -y --no-install-recommends r-base r-base-dev
fi

if ! command -v pdflatex >/dev/null 2>&1; then
    echo "pdflatex is not available. Installing TeX Live..." >&2
    apt-get update
    apt-get install -y --no-install-recommends texlive-latex-base texlive-fonts-extra
fi

if command -v R >/dev/null 2>&1; then
    apt-get update
    apt-get install -y --no-install-recommends \
        r-cran-stringi r-cran-reticulate r-cran-testthat
fi
