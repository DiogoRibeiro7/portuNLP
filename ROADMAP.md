# portuNLP Roadmap

## Current Direction

`portuNLP` is now a Python-first library for Portuguese NLP workflows.
The current scope is:

- Native text helpers for normalization, tokenization, slang cleaning,
  stopwords, and dictionary loading.
- spaCy-backed lemmatization, POS tagging, and tokenization for Portuguese.
- A small standalone C++ tokenizer kept as an optional low-level component.

## Near Term

1. Stabilize the Python API.
   - Keep public function names coherent and typed.
   - Tighten packaging so only library artifacts ship in built distributions.
   - Expand tests for edge cases and compatibility behavior.

2. Improve language resources.
   - Expand orthographic rules.
   - Curate broader stopword and slang datasets.
   - Add clearer provenance for bundled lexical resources.

3. Strengthen tokenization.
   - Compare the native tokenizer against spaCy behavior.
   - Decide whether the C++ tokenizer should remain standalone or gain a Python binding.
   - Add more coverage for punctuation, contractions, and mixed Unicode text.

## Medium Term

1. Add richer NLP helpers.
   - Sentence segmentation helpers.
   - Optional morphology-oriented utilities built on spaCy outputs.
   - Higher-level preprocessing pipelines for Portuguese corpora.

2. Improve developer experience.
   - Add release automation for Python distributions.
   - Add CI focused on Python tests, typing, and wheel builds.
   - Publish a cleaner API reference and usage examples.

## Resolved Decisions

- **API stability (1.0.0):** the public API is frozen and documented in
  `API.md` under a semantic-versioning policy.
- **Compatibility aliases:** removed in 1.0.0. The canonical descriptive names
  (`tokenize_text`, `load_dictionary`, `clean_social_text`,
  `apply_orthographic_rules`) are the supported API.

## Open Decisions

- Whether to expose the C++ tokenizer directly in Python as a supported helper.
- Whether bundled resources should remain in code or move to dedicated data files.
