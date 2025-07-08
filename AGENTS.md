# Coding Guidelines for portuNLP

This repository contains an R package with an accompanying Python helper
module.  All future work should comply with the following rules.

## Documentation and Style

- **Python**: Every function must include a docstring formatted using the
  Google style guide.  Provide inline comments where needed.
- **R**: Use roxygen2 comments for all exported functions.
- Keep the README and NEWS files current with each new feature.

## Project Structure

- Python code is managed with Poetry.  Update `pyproject.toml` and run
  `poetry install` after dependency changes.
- R package metadata lives in `DESCRIPTION`.  Regenerate `NAMESPACE` via
  roxygen2.

## Testing

- Run `R CMD check .` at the project root after modifications.  It may fail
  if the environment lacks R or required dependencies.
- If Python tests are added, execute them with `poetry run pytest`.

## Owner Information

- Name: Diogo Ribeiro
- Username: DiogoRibeiro7
- Personal email: diogo.debastos.ribeiro@gmail.com
- Professional email: dfr@esmad.ipp.pt
- Affiliation: ESMAD - Instituto Politécnico do Porto
- ORCID: https://orcid.org/0009-0001-2022-7072

## Roadmap Awareness

Follow the development stages described in `ROADMAP.md`.  Ensure each
implemented feature remains consistent with previous steps.

## Setup

Run `./setup.sh` from the repository root to install R, a minimal TeX
distribution, and all project dependencies.  The script only requires
`poetry` to be preinstalled.

## Pull Requests

Before opening a pull request, execute `R CMD check .` and `poetry run
pytest`.  Include a short summary of changes and test results in the PR
description.
