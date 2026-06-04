#!/usr/bin/env bash
# Setup script for portuNLP
set -euo pipefail

# Install Python dependencies using Poetry
if command -v poetry >/dev/null 2>&1; then
    poetry install
else
    echo "Poetry is not installed. Please install Poetry to manage Python dependencies." >&2
fi

# Ensure pre-commit is available for Git hooks
if ! command -v pre-commit >/dev/null 2>&1; then
    pip install pre-commit
fi

# Install C++ build tools if missing
if ! command -v cmake >/dev/null 2>&1; then
    apt-get update
    apt-get install -y --no-install-recommends cmake build-essential clang-format
fi
