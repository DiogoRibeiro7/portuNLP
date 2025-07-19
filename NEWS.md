# portuNLP News

## 0.0.0.9000

* Initial package skeleton created.
* Added `setup.sh` script for installing dependencies and updated
  documentation.
* Added built-in Portuguese stopword list and `get_stopwords()` helper.
* Added `load_dict()` function for reading custom dictionaries and included sample `orth_rules` dataset.
* Added social-media cleaning helpers: `remove_emoji()`,
  `normalize_accents()`, `map_slang()`, and the combined `clean_social()`
  function with a minimal `slang_map` dataset.
* Added `tokenize_spacy_pt()` wrapper to access spaCy tokenization from R.
* Enhanced `lemmatize_pt()` and `pos_tag_pt()` to call spaCy for lemmatization and part-of-speech tagging.
* Rewrote README to summarize package features and setup instructions.
* Added `apply_orth_rules()` for optional spell correction using `orth_rules`.
* `normalize_text()` gains a `correct` argument to apply orthographic rules.
* Included `pos_map` dataset mapping spaCy POS tags to Universal tags.
* Added `map_pos_tags()` helper to convert spaCy tags to the Universal tagset.
* `pos_tag_pt()` gains a `universal` argument to optionally return Universal POS tags.
* Added introductory vignettes for text normalization and social-media
  cleaning and a basic `pkgdown` configuration.
* Continuous integration workflow now runs only when changes merge to `main`.
* Added unit tests covering `tokenize_pt()`.
* Setup script now installs a minimal TeX distribution so `R CMD check` can
  build manuals without errors.
* Added `texlive-fonts-extra` to ensure the `inconsolata` font is available.
* Setup script now installs R dependencies via apt to avoid compilation errors.
* Setup script installs `pre-commit` to run code formatting hooks.
* Added a simple C++ tokenizer with CMake build and `ctest` integration.
* Raised minimum Python version to 3.10 and documented the change.
* Expanded `pos_map` dataset with additional tag mappings.
* Expanded Portuguese stopword list and exported as `stopwords_pt`.
* Added more orthographic variants to `orth_rules`.
* Added benchmark script for tokenization performance.
* `benchmark_tokenize()` now reports tokens-per-second throughput.
* Added tests for non-UTF8 input.
* Added GitHub Actions workflow for R CMD check.
