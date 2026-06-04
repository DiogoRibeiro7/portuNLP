# portuNLP

`portuNLP` is a Python package for Portuguese NLP tasks built on spaCy.
The current implementation includes native helpers for normalization,
tokenization, stopwords, slang cleaning, dictionary loading, and POS-tag
mapping, plus spaCy-backed lemmatization and tagging. Python 3.10 to 3.12 is
required.

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
from portunlp import (
    clean_social,
    get_stopwords,
    normalize_text,
    spacy_lemmatize,
    spacy_pos_tag,
    spacy_tokenize,
    tokenize_text,
)

text = "Os gatos bonitos comem peixe."

normalized = normalize_text("Acção", correct=True)
simple_tokens = tokenize_text("Olá, mundo! Tudo bem?")
tokens = spacy_tokenize(text)
lemmas = spacy_lemmatize(text)
tags = spacy_pos_tag(text)
social = clean_social("vc tá 😊", custom_map={"tá": "está"})
stopwords = get_stopwords(extra={"novapalavra"})
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
