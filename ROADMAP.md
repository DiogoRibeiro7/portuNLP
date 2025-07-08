# Portuguese-Centric Text Processing for R: Roadmap

## Package Name & Description

**Name:** portuNLP

**Description:** A comprehensive R toolkit for Portuguese text processing. It wraps high-performance C++/Python libraries (FreeLing, spaCy), offering normalization, tokenization, lemmatization, POS tagging, plus social-media cleaning (emoji removal, accent normalization, slang mapping), and built-in Portuguese resources.

## Overview

This document details the development plan to build and publish **portuNLP** on CRAN. The package will provide end-to-end support for processing Portuguese text in R.

## Prerequisites

* Proficiency in R package development and CRAN policies.
* Experience with Rcpp and/or **reticulate** for C++/Python integration.
* Familiarity with Portuguese linguistics: morphology, orthography, slang.
* Understanding of external NLP libraries (FreeLing, spaCy).

## Phase 1: Project Kickoff & Research (Weeks 1–2)

1. **Repository Initialization**

   * Create Git repo, define branching model.
   * Use `usethis::create_package()` to scaffold.
   * Add `.gitignore`, LICENSE (MIT), README stub, CODE\_OF\_CONDUCT.
   * Set up CI via GitHub Actions (R-CMD-check on multiple platforms).

2. **Dependency Survey**

   * Evaluate wrappers: **Rcpp**, **reticulate**, **httr**, **stringi**, **data.table**.
   * Assess FreeLing and spaCy capabilities for Portuguese.
   * Draft DESCRIPTION with `Imports:` and `Suggests:`.

3. **API & Resource Planning**

   * Define core functions: `normalize_pt()`, `tokenize_pt()`, `lemmatize_pt()`, `pos_tag_pt()`.
   * Specify interfaces for social-media cleaners: `remove_emoji()`, `normalize_accents()`, `map_slang()`.
   * List built-in assets: stopwords, dictionaries, orthographic rules.

## Phase 2: Core NLP Wrappers (Weeks 3–6)

1. **Library Integration**

   * **FreeLing**: Wrap C++ commands via Rcpp.
   * **spaCy**: Use **reticulate** to call Python models if FreeLing missing.

2. **Normalization Module**

   * `normalize_text(text, lower = TRUE, remove_punct = FALSE)`.
   * Implement accent folding (`stringi::stri_trans_general`).
   * Spell correction hooks using orthographic rules.

3. **Tokenization & Lemmatization**

   * `tokenize_pt(text, type = c("word", "sentence"))`.
   * `lemmatize_pt(tokens)`: return lemma vector.

4. **POS Tagging**

   * `pos_tag_pt(tokens)`: return tags using FreeLing or spaCy.
   * Standardize tagset and provide mapping table.

## Phase 3: Portuguese Resources (Weeks 7–8)

1. **Stopword Lists**

   * Curate default stopwords from multiple sources.
   * Allow custom additions/removals.

2. **Dictionaries & Rules**

   * Include orthographic rule set for European and Brazilian variants.
   * Custom dictionary loader: `load_dict(path)`.

## Phase 4: Social Media Cleaning (Weeks 9–10)

1. **Emoji Removal**

   * `remove_emoji(text)` leveraging Unicode ranges.

2. **Accent Normalization**

   * `normalize_accents(text)` to strip or standardize.

3. **Slang & Abbreviation Mapping**

   * Provide built-in slang map.
   * `map_slang(text, custom_map = NULL)`.

4. **Pipeline Function**

   * `clean_social(text, emoji = TRUE, accents = TRUE, slang = TRUE)`.

## Phase 5: Documentation & Examples (Weeks 11–12)

1. **Roxygen2 Comments**

   * Fully document all functions with `@param`, `@return`, `@examples`.

2. **Vignettes**

   * Quickstart tutorial for text normalization.
   * End-to-end example: social-media corpus cleaning.

3. **Pkgdown Site**

   * Configure **pkgdown**; add badges.

## Phase 6: Testing & Quality Assurance (Weeks 13–14)

1. **Unit Tests (`testthat`)**

   * Edge cases: empty strings, non-UTF8 input.
   * Consistency checks between FreeLing and spaCy.

2. **Integration Tests**

   * Real Portuguese sentences: EU Portuguese vs. BR Portuguese.

3. **Performance Benchmarks**

   * Measure throughput for large corpora.

4. **CRAN Checks**

   * Resolve NOTES, WARNINGS, ERRORS on Windows, macOS, Linux.

## Phase 7: Release & Maintenance (Week 15+)

1. Prepare NEWS.md and version bump.
2. Build source package and submit to CRAN.
3. Monitor CRAN incoming, fix issues.
4. Plan future enhancements: slang learning, Shiny dashboard, additional languages.

---

*Roadmap generated on July 8, 2025.*
