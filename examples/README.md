# portuNLP examples

Runnable scripts demonstrating the public API. Run them from the repository
root, e.g.:

```bash
python examples/01_quickstart.py
```

| Script | Shows |
|--------|-------|
| [`01_quickstart.py`](01_quickstart.py) | The `analyze_text` / `analyze_texts` facade and JSON output. |
| [`02_preprocessing.py`](02_preprocessing.py) | Normalization, slang mapping, contraction expansion, tokenization, stopwords, n-grams. |
| [`03_similarity_and_keywords.py`](03_similarity_and_keywords.py) | TF-IDF keyword extraction, `compare_texts`, and `rank_similar_texts`. |
| [`04_spacy.py`](04_spacy.py) | spaCy-backed morphology and entities (requires `pt_core_news_sm`). |

The first three run on the pure-Python core with no extra setup. `04_spacy.py`
needs the Portuguese model:

```bash
python -m spacy download pt_core_news_sm
```

See [`../API.md`](../API.md) for the full public API reference.
