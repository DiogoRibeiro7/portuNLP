# portuNLP News

## 1.3.0

Add Portuguese stemming.

### Added
* `stem_word()`, `stem_tokens()`, and `stem_text()` implementing the Snowball
  (Porter2) Portuguese stemming algorithm. The implementation is validated to
  match NLTK's `SnowballStemmer("portuguese")` across thousands of words.

## 1.2.0

Expand the Portuguese language resources and add contraction handling.

### Added
* `expand_contractions()` and the `PORTUGUESE_CONTRACTIONS` dataset, expanding
  preposition contractions (`do` → `de o`, `na` → `em a`, `àquele` → `a aquele`).
* Documented provenance for the bundled resources in `portunlp/_data.py`.

### Changed
* `PORTUGUESE_STOPWORDS` expanded from ~40 to ~200 entries (curated from NLTK
  and stopwords-iso), including the common conjugations of *ser*/*estar*/
  *haver*/*ter*.
* `SLANG_MAP` expanded with more frequent internet abbreviations.
* `ORTHOGRAPHIC_RULES` extended with more pre-/post-AO90 spellings.

### Fixed
* Stopword removal in the preprocessing pipeline is now accent-insensitive, so
  accented stopwords such as `não`, `à`, and `você` are removed from the
  accent-folded token stream (previously they leaked through).

## 1.1.0

Invest in the native acceleration layer.

### Added
* `cpp_acceleration_available()` to report whether the compiled backend is in use.
* C++ Unicode tokenizer test and Python equivalence tests covering Portuguese
  accented text.
* `scripts/benchmark_tokenizer.py` comparing the native and pure-Python paths.

### Changed
* The native tokenizer now handles Latin-1 letters (Portuguese accents) and
  lowercases them, matching the pure-Python path exactly; previously accented
  text always fell back to Python. Tokenization is ~5× faster with the backend.
* Frequency counting and n-gram generation now route to whichever
  implementation is faster: counting uses C++ when available; n-gram building
  stays in Python (returning nested lists from C++ measured slower).

## 1.0.0

First stable release. The public API is now frozen and documented in
[`API.md`](API.md); see that file for the semantic-versioning policy.

### Breaking changes
* Removed the legacy duplicate aliases in favor of the canonical, descriptive
  names:
  * `tokenize_pt()` → `tokenize_text()`
  * `load_dict()` → `load_dictionary()`
  * `clean_social()` → `clean_social_text()`
  * `apply_orth_rules()` → `apply_orthographic_rules()`

### Added
* `portunlp.__version__`.
* `API.md` public API reference and stability policy.
* GitHub Actions CI (pytest + mypy matrix, pre-commit lint).
* `PORTUNLP_DLL_DIRECTORIES` environment variable to supply extra Windows DLL
  search directories for the optional C++ backend.

### Fixed
* The optional C++ backend now degrades gracefully to the pure-Python path when
  it is missing or ABI-incompatible, instead of breaking `import portunlp`.

### Changed
* Removed the hardcoded `C:/Strawberry/c/bin` path from the backend loader.
* Refreshed `AGENTS.md`, `.gitignore`, and project metadata for the
  Python + C++ layout (dropped leftover R references).

---

## 0.0.0.9000 (historical, pre-1.0 R-era notes)

The notes below describe the original R package and the early Python migration.
They are retained for provenance only and do not reflect the current API.

## 0.0.0.9000

* Removed the legacy R package implementation and its generated assets.
* Kept the Python spaCy helpers as the primary supported interface.
* Simplified setup and documentation around the Python workflow.
* Historical R-focused release notes from the initial package stage follow.
*
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
* Exposed C++ tokenizer via `tokenize_cpp()` using Rcpp.
* Expanded sample datasets (`stopwords_pt`, `slang_map`, `pos_map`) with
  references to NLTK and social-media corpora.
* C++ tokenizer now uses a regex-based engine that lowercases tokens.
* Dataset documentation cites `stopwords-iso`, `slang-dict`, and the UD tagset.
* README clarifies CI prerequisites and points to `./setup.sh` for installing R.
* Added regression tests covering punctuation and contractions for the C++ tokenizer.
* Documented spaCy model caching and load errors and added edge-case tests for lemmatization and POS tagging.
* Fixed `map_slang()` to replace only whole-word matches using Perl word boundaries.

