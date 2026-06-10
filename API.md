# portuNLP Public API Reference

This document defines the **stable public API** of `portuNLP` as of **1.0.0**.

Everything listed in `portunlp.__all__` (and re-exported from the top-level
`portunlp` package) is covered by semantic versioning:

- **Patch** releases (`1.0.x`): bug fixes only, no signature changes.
- **Minor** releases (`1.x.0`): backwards-compatible additions.
- **Major** releases (`2.0.0`): may remove or change anything below, announced
  in `NEWS.md` ahead of time.

Anything **not** listed here — modules or names prefixed with `_`
(`portunlp.text._*`, `portunlp._spacy`, `portunlp._data`, the compiled
`portunlp._portunlp_cpp` backend) — is **internal** and may change at any time.

> **1.0 note:** the legacy aliases `tokenize_pt`, `load_dict`, `clean_social`,
> and `apply_orth_rules` were removed in 1.0.0. Use the canonical names below.

```python
import portunlp
portunlp.__version__  # "1.0.0"
```

---

## 1. High-level analysis (recommended entry points)

| Name | Summary |
|------|---------|
| `analyze_text(text, *, correct=False, remove_punct=True, social=False, custom_map=None, remove_stopwords=False, use_spacy=False, keyword_top_k=10, include_spacy=False, include_spacy_lexicon=False, include_spacy_collocations=False, collocation_size=2) -> TextAnalysis` | Composed analysis of a single text: preprocessing, metrics, keywords, optional spaCy summaries. |
| `analyze_texts(texts, *, ..., ngram_size=2, ...) -> CorpusAnalysis` | Composed analysis of a corpus: per-document preprocessing, aggregate statistics, IDF, optional spaCy summaries. |
| `analysis_to_dict(value) -> dict` | Convert a `TextAnalysis`/`CorpusAnalysis` to JSON-safe nested data. |
| `analysis_to_json(value, *, indent=2) -> str` | Serialize a `TextAnalysis`/`CorpusAnalysis` to JSON. |

**Result types:** `TextAnalysis`, `CorpusAnalysis`.

```python
from portunlp import analyze_text, analysis_to_json

result = analyze_text("Os gatos comem peixe.", remove_stopwords=True, keyword_top_k=5)
print(analysis_to_json(result))
```

---

## 2. Native text helpers (pure Python, no spaCy required)

### Normalization & cleaning
| Name | Summary |
|------|---------|
| `normalize_text(text, *, lower=True, remove_punct=False, correct=False) -> str` | Lowercase, optional punctuation removal, optional orthographic correction, accent folding. |
| `normalize_accents(text) -> str` | Fold accented characters to ASCII. |
| `remove_emoji(text) -> str` | Strip emoji characters. |
| `apply_orthographic_rules(text, rules=None) -> str` | Apply built-in (or supplied) orthographic replacement rules. |
| `map_slang(text, custom_map=None) -> str` | Replace slang terms with standard forms. |
| `clean_social_text(text, *, emoji=True, accents=True, slang=True, custom_map=None) -> str` | Combined social-media cleaning pipeline. |

### Tokenization & stopwords
| Name | Summary |
|------|---------|
| `tokenize_text(text, *, kind="word") -> list[str]` | Lightweight native word/sentence tokenizer (uses the C++ backend when available). |
| `get_stopwords(*, extra=None, omit=None) -> list[str]` | Built-in Portuguese stopwords with optional additions/removals. |
| `filter_stopwords(tokens, *, stopwords=None, normalize=False) -> list[str]` | Remove stopwords from a token sequence. |
| `load_dictionary(path) -> list[str]` | Load a newline-delimited dictionary file. |

### Counting & n-grams
| Name | Summary |
|------|---------|
| `generate_ngrams(tokens, n) -> list[tuple[str, ...]]` | Contiguous n-grams. |
| `term_frequencies(tokens) -> dict[str, int]` | Token frequency counts. |
| `map_pos_tags(tags) -> list[str]` | Map spaCy POS tags through the bundled tagset. |
| `cpp_acceleration_available() -> bool` | Whether the optional compiled backend is loaded. |

### Preprocessing, statistics & similarity
| Name | Summary |
|------|---------|
| `preprocess_text(text, *, correct=False, remove_punct=True, social=False, custom_map=None, remove_stopwords=False, use_spacy=False) -> ProcessedText` | High-level preprocessing pipeline. |
| `analyze_corpus(texts, *, ..., ngram_size=2) -> CorpusStatistics` | Aggregate token and n-gram statistics. |
| `analyze_text_metrics(text, *, ...) -> TextStatistics` | Descriptive + readability metrics. |
| `compute_inverse_document_frequency(texts, *, ...) -> dict[str, float]` | Smoothed IDF values. |
| `extract_keywords(text, *, corpus=None, top_k=10, ...) -> list[KeywordScore]` | TF-IDF-style keyword extraction. |
| `compare_texts(text, other_text, *, corpus=None, ...) -> float` | Cosine similarity over TF-IDF vectors. |
| `rank_similar_texts(query, texts, *, top_k=5, ...) -> list[SimilarityScore]` | Rank documents by similarity to a query. |

**Result types:** `ProcessedText`, `CorpusStatistics`, `TextStatistics`,
`KeywordScore`, `SimilarityScore`.

### C++ acceleration (optional, transparent)

When the compiled backend is installed, `tokenize_text` and `term_frequencies`
use it automatically; otherwise the pure-Python paths run and produce identical
results. `cpp_acceleration_available()` reports which path is active. The native
tokenizer handles ASCII and Latin-1 letters (covering Portuguese accents);
other scripts transparently fall back to Python.

On Windows, set the `PORTUNLP_DLL_DIRECTORIES` environment variable (using the
OS path separator) to point at any directories holding the backend's runtime
DLLs if it fails to load. Run `python scripts/benchmark_tokenizer.py` to compare
throughput on your machine (tokenization is ~5× faster; n-gram building stays in
Python by design).

---

## 3. spaCy-backed helpers (require `pt_core_news_sm`)

These load the Portuguese spaCy model on first use:

```bash
python -m spacy download pt_core_news_sm
```

### Convenience wrappers (return plain lists)
| Name | Summary |
|------|---------|
| `lemmatize_pt(text) -> list[str]` | Lemmas. |
| `pos_tag_pt(text, *, universal=False) -> list[str]` | POS tags, optionally mapped through the bundled tagset. |
| `tokenize_spacy_pt(text) -> list[str]` | spaCy tokens. |
| `spacy_tokenize` / `spacy_lemmatize` / `spacy_pos_tag` / `spacy_sentencize` | Lower-level list-returning equivalents. |

### Structured analysis (return dataclasses)
| Name | Result type |
|------|-------------|
| `spacy_analyze(text)` | `list[SpacyToken]` |
| `spacy_document(text)` | `SpacyDocument` |
| `spacy_corpus(texts)` | `SpacyCorpus` |
| `spacy_morphology(text)` | `SpacyMorphology` |
| `spacy_entities(text)` | `SpacyEntities` |
| `spacy_dependencies(text)` | `SpacyDependencies` |
| `spacy_noun_chunks(text)` | `SpacyNounChunks` |
| `spacy_sentences(text)` | `SpacySentences` |
| `spacy_lexicon(text)` / `spacy_lexicon_corpus(texts)` | `SpacyLexicon` / `SpacyLexiconCorpus` |
| `spacy_collocations(text, n=2)` / `spacy_collocations_corpus(texts, n=2)` | `SpacyCollocations` / `SpacyCollocationCorpus` |
| `spacy_concordance(...)` / `spacy_concordance_corpus(...)` | `SpacyConcordance` / `SpacyConcordanceCorpus` |

### spaCy serialization
| Name | Summary |
|------|---------|
| `spacy_to_dict(value) -> Any` | Convert any spaCy result dataclass to JSON-safe data. |
| `spacy_to_json(value, *, indent=2) -> str` | Serialize a spaCy result dataclass to JSON. |

**Result dataclasses:** `SpacyToken`, `SpacyMorphToken`, `SpacyMorphology`,
`SpacyEntity`, `SpacyEntities`, `SpacyDependencyToken`, `SpacyDependencies`,
`SpacyNounChunk`, `SpacyNounChunks`, `SpacySentence`, `SpacySentences`,
`SpacyDocument`, `SpacyCorpus`, `SpacyLexicon`, `SpacyLexiconCorpus`,
`SpacyCollocation`, `SpacyCollocations`, `SpacyCollocationCorpus`,
`SpacyConcordanceEntry`, `SpacyConcordance`, `SpacyConcordanceCorpus`.

---

## 4. Bundled resources (read-only data)

| Name | Type |
|------|------|
| `PORTUGUESE_STOPWORDS` | `tuple[str, ...]` |
| `SLANG_MAP` | `dict[str, str]` |
| `ORTHOGRAPHIC_RULES` | `tuple[tuple[str, str], ...]` |
| `POS_TAG_MAP` | `dict[str, str]` |

---

## 5. Command-line interface

```bash
portunlp text "A casa bonita" --remove-stopwords
portunlp texts "A casa bonita" "A casa azul" --remove-stopwords --compact
```

The CLI mirrors `analyze_text` / `analyze_texts` and emits JSON. Run
`portunlp text --help` or `portunlp texts --help` for the full flag list.
