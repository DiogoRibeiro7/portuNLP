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
from portunlp import analyze_text, analyze_texts

text_result = analyze_text(
    "Os gatos bonitos comem peixe.",
    remove_stopwords=True,
    keyword_top_k=5,
)

corpus_result = analyze_texts(
    ["A casa bonita", "A casa azul"],
    remove_stopwords=True,
)
```

You can also use the CLI:

```bash
poetry run portunlp text "A casa bonita" --remove-stopwords
poetry run portunlp texts "A casa bonita" "A casa azul" --remove-stopwords --compact
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
