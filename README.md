# portuNLP

`portuNLP` is a Python package for Portuguese NLP tasks built on spaCy.
The current implementation exposes helpers for tokenization, lemmatization,
and part-of-speech tagging. Python 3.10 to 3.12 is required.

## Installation

Install dependencies with Poetry:

```bash
poetry install
```

Install the Portuguese spaCy model separately:

```bash
poetry run python -m spacy download pt_core_news_sm
```

## Usage

```python
from portunlp import spacy_lemmatize, spacy_pos_tag, spacy_tokenize

text = "Os gatos bonitos comem peixe."

tokens = spacy_tokenize(text)
lemmas = spacy_lemmatize(text)
tags = spacy_pos_tag(text)
```

## Development

Run the Python checks with:

```bash
poetry run python -m pytest portunlp/tests -q
poetry run python -m mypy portunlp
pre-commit run --all-files
```

If you are working on the standalone C++ tokenizer, build and test it with:

```bash
mkdir -p build && cd build
cmake ..
make
ctest --output-on-failure
```

See `ROADMAP.md` for historical planning context.
