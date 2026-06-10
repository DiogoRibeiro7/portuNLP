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

## API reference & stability

The complete public API and its semantic-versioning policy are documented in
[`API.md`](API.md). As of 1.0.0 the public surface is stable; anything prefixed
with `_` is internal and may change without notice.

## Development

Run the Python checks with:

```bash
poetry run python -m pytest portunlp/tests -q
poetry run python -m mypy portunlp
pre-commit run --all-files
```

### Optional C++ acceleration

An optional compiled backend transparently accelerates tokenization (~5×) and
frequency counting; when it is absent, identical pure-Python paths are used.
Check which is active with `cpp_acceleration_available()` and benchmark with:

```bash
python scripts/benchmark_tokenizer.py
```

On Windows, set `PORTUNLP_DLL_DIRECTORIES` to the directory holding the
backend's runtime DLLs if the extension fails to load.

To build and test the C++ component directly:

```bash
mkdir -p build && cd build
cmake ..
make
ctest --output-on-failure
```

See `ROADMAP.md` for historical planning context.
